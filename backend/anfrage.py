"""Website-Check-Anfragen für muratisystems.de.

Nimmt das native HTML-Formular per POST /api/anfrage an, prüft die Felder,
hängt die Anfrage an eine JSON-Lines-Datei an und leitet sie per SMTP an das
Postfach weiter, sobald SMTP-Zugangsdaten gesetzt sind. Die Anfrage wird immer
zuerst gespeichert, damit ein Mailfehler keine Anfrage verliert. IP-Adressen
werden nur flüchtig im Speicher für die Ratenbegrenzung gehalten.
"""
import html
import json
import os
import re
import smtplib
import sys
import threading
import time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

DATA_FILE = os.environ.get("DATA_FILE", "/data/anfragen.jsonl")
MAIL_TO = os.environ.get("MAIL_TO", "info@muratisystems.de")
MAX_BODY = 20_000
RATE_LIMIT = 5          # Anfragen je IP ...
RATE_WINDOW = 600       # ... in 10 Minuten

PROBLEMS = {
    "Unsere Website wirkt veraltet",
    "Wir bekommen zu wenige Anfragen",
    "Auf dem Handy funktioniert sie schlecht",
    "Anfragen landen an der falschen Stelle",
    "Wir haben noch keine Website",
}
GOALS = {
    "Mehr passende Anfragen",
    "Leistungen verständlicher zeigen",
    "Abläufe nach der Anfrage vereinfachen",
    "Erst Orientierung bekommen",
}
CHANNELS = {"E-Mail", "WhatsApp"}
LIMITS = {"name": 100, "email": 254, "telefon": 40, "website": 250, "hinweis": 1000}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_hits = {}
_lock = threading.Lock()


def rate_limited(ip, now=None):
    # ponytail: in-memory per process, resets on restart; fine for one small container.
    now = now or time.time()
    with _lock:
        recent = [t for t in _hits.get(ip, []) if now - t < RATE_WINDOW]
        recent.append(now)
        _hits[ip] = recent
        if len(_hits) > 5000:
            _hits.clear()
        return len(recent) > RATE_LIMIT


def validate(form):
    """Return (clean_dict, None) or (None, error_message)."""
    one = lambda key: (form.get(key) or [""])[0].strip()
    data = {key: one(key) for key in LIMITS}
    data["problem"] = [p for p in form.get("problem", []) if p in PROBLEMS]
    data["ziel"] = one("ziel")
    data["kanal"] = one("kanal") or "E-Mail"
    for key, limit in LIMITS.items():
        if len(data[key]) > limit:
            return None, "Eine Angabe ist zu lang."
    if not data["name"]:
        return None, "Bitte geben Sie Ihren Namen an."
    if not EMAIL_RE.match(data["email"]):
        return None, "Bitte geben Sie eine gültige E-Mail-Adresse an."
    if data["ziel"] not in GOALS:
        return None, "Bitte wählen Sie aus, was sich zuerst verbessern soll."
    if data["kanal"] not in CHANNELS:
        return None, "Bitte wählen Sie E-Mail oder WhatsApp als Antwortweg."
    if data["kanal"] == "WhatsApp" and not data["telefon"]:
        return None, "Für eine Antwort per WhatsApp benötigen wir Ihre Nummer."
    return data, None


def store(data):
    fd = os.open(DATA_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def mail_text(data):
    return "\n".join([
        "Neuer Website-Check über muratisystems.de",
        "",
        "Website: " + (data["website"] or "-"),
        "Probleme: " + ("; ".join(data["problem"]) or "Keine Auswahl"),
        "Ziel: " + data["ziel"],
        "Hinweis: " + (data["hinweis"] or "-"),
        "",
        "Name: " + data["name"],
        "E-Mail: " + data["email"],
        "Telefon/WhatsApp: " + (data["telefon"] or "-"),
        "Bevorzugte Antwort: " + data["kanal"],
        "Eingang: " + data["eingang"],
    ])


def send_mail(data):
    host, user, password = (os.environ.get(k) for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS"))
    if not (host and user and password):
        print("SMTP nicht konfiguriert, Anfrage nur gespeichert", file=sys.stderr)
        return
    msg = EmailMessage()
    msg["Subject"] = "Website-Check: " + data["name"].replace("\n", " ")
    msg["From"] = user
    msg["To"] = MAIL_TO
    msg["Reply-To"] = data["email"]
    msg.set_content(mail_text(data))
    with smtplib.SMTP_SSL(host, int(os.environ.get("SMTP_PORT", "465")), timeout=20) as smtp:
        smtp.login(user, password)
        smtp.send_message(msg)


def mail_safely(data):
    try:
        send_mail(data)
    except Exception as exc:  # gespeichert ist sie trotzdem
        print("Mailversand fehlgeschlagen:", exc, file=sys.stderr)


PAGE = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/redesign.css"><title>Angabe prüfen – Murati Systems</title></head>
<body><main class="legal"><div class="shell legal-shell"><p class="eyebrow">Website-Check</p>
<h1>Bitte kurz prüfen.</h1><p>{msg}</p><p>Tipp: Mit der Zurück-Taste Ihres Browsers bleiben Ihre Eingaben meist erhalten.</p>
<p><a class="button primary" href="/website-check.html#formular">Zum Formular</a></p>
<p>Oder direkt per E-Mail: <a href="mailto:info@muratisystems.de">info@muratisystems.de</a></p>
</div></main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "anfrage"
    sys_version = ""

    def _page(self, code, msg):
        body = PAGE.format(msg=html.escape(msg)).encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, where):
        self.send_response(303)
        self.send_header("Location", where)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(204)
            self.end_headers()
        else:
            self._redirect("/website-check.html")

    def do_POST(self):
        if self.path.split("?")[0] != "/api/anfrage":
            return self._page(404, "Diese Adresse gibt es nicht.")
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            return self._page(413, "Die Anfrage ist zu groß.")
        form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        if (form.get("homepage") or [""])[0]:
            return self._redirect("/danke.html")   # Honeypot: Bots still ins Leere
        ip = (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[0].strip()
        if rate_limited(ip):
            return self._page(429, "Zu viele Anfragen in kurzer Zeit. Bitte versuchen Sie es später erneut.")
        data, error = validate(form)
        if error:
            return self._page(400, error)
        data["eingang"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
        store(data)
        threading.Thread(target=mail_safely, args=(data,), daemon=True).start()
        self._redirect("/danke.html")

    def log_message(self, fmt, *args):
        pass  # keine Zugriffsprotokolle mit IP-Adressen


def selftest():
    ok = {"name": ["Max"], "email": ["max@example.de"], "ziel": ["Mehr passende Anfragen"],
          "problem": ["Wir haben noch keine Website", "erfunden"]}
    data, err = validate(ok)
    assert err is None and data["problem"] == ["Wir haben noch keine Website"] and data["kanal"] == "E-Mail"
    assert validate({**ok, "email": ["kaputt"]})[1]
    assert validate({**ok, "ziel": ["x"]})[1]
    assert validate({**ok, "kanal": ["WhatsApp"]})[1]
    assert validate({**ok, "kanal": ["WhatsApp"], "telefon": ["0162"]})[1] is None
    assert validate({**ok, "hinweis": ["x" * 1001]})[1]
    assert not any(rate_limited("t", now=1000 + i) for i in range(RATE_LIMIT))
    assert rate_limited("t", now=1010)
    assert not rate_limited("t", now=5000)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    else:
        ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
