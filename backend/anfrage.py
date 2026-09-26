"""Anfragen über muratisystems.de: Website-Check und Kontaktformular.

Nimmt die nativen HTML-Formulare per POST /api/anfrage an, prüft die Felder,
vergibt eine Vorgangsnummer, hängt die Anfrage an eine JSON-Lines-Datei an und
leitet sie per SMTP an das Postfach weiter, sobald SMTP-Zugangsdaten gesetzt
sind. Die Anfrage wird immer zuerst gespeichert, damit ein Mailfehler keine
Anfrage verliert. Die anfragende Person bekommt eine Eingangsbestätigung mit
festem Text (CONFIRM_MAIL=0 schaltet sie ab). Freitexte aus dem Formular
stehen nie darin, damit das Formular nicht als Spam-Schleuder taugt.

Ohne JavaScript: 303 auf /danke.html, Fehler als kleine HTML-Seite.
Mit JavaScript (Accept: application/json): JSON, das Formular zeigt Erfolg und
Fehler direkt an. IP-Adressen werden nur flüchtig im Speicher für die
Ratenbegrenzung gehalten.
"""
import hashlib
import html
import json
import os
import re
import secrets
import smtplib
import sys
import threading
import time
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode

os.environ.setdefault("TZ", "CET-1CEST,M3.5.0,M10.5.0/3")  # deutsche Zeit, Alpine-Image hat kein tzdata
if hasattr(time, "tzset"):
    time.tzset()

DATA_FILE = os.environ.get("DATA_FILE", "/data/anfragen.jsonl")
MAIL_TO = os.environ.get("MAIL_TO", "info@muratisystems.de")
CONFIRM_MAIL = os.environ.get("CONFIRM_MAIL", "1") != "0"
CONFIRM_PER_HOUR = int(os.environ.get("CONFIRM_PER_HOUR", "30"))
WHATSAPP_NR = re.sub(r"\D", "", os.environ.get("WHATSAPP_NR", ""))  # z. B. 4916…; leer = nicht nennen
ANTWORTZEIT = "in der Regel innerhalb von zwei Werktagen"
MAX_BODY = 20_000
RATE_LIMIT = 5          # Anfragen je IP ...
RATE_WINDOW = 600       # ... in 10 Minuten
NONCE_TTL = 3600        # doppelt abgeschickte Formulare (gleiche Nonce) zählen eine Stunde lang einmal
DOUBLE_SUBMIT_TTL = 15  # B51: No-JS-Fallback ohne Client-Nonce, gleiche Daten+IP zaehlen nur kurz als Doppel-Submit

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
ANLIEGEN = {"Website", "Anfrage-Automatisierung", "KI & IT-Beratung", "Betreuung", "Etwas anderes"}
CHANNELS = {"E-Mail", "WhatsApp"}
TYPES = {"check", "kontakt"}
LIMITS = {"name": 100, "email": 254, "telefon": 40, "website": 250, "hinweis": 1000, "nachricht": 2000}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9 ()/.-]{6,40}$")
NONCE_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
NR_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # ohne 0/O und 1/I

_hits = {}
_done = {}
_confirmed = []
_confirmed_to = {}
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


def recall(nonce, now, ttl=NONCE_TTL):
    with _lock:
        hit = _done.get(nonce)
        return hit[1] if hit and now - hit[0] < ttl else None


def remember(nonce, result, now):
    with _lock:
        if len(_done) > 5000:
            _done.clear()
        _done[nonce] = (now, result)


def may_confirm(email, now=None):
    """Höchstens CONFIRM_PER_HOUR Bestätigungen je Stunde und eine je Adresse."""
    now = now or time.time()
    key = hashlib.sha256(email.lower().encode()).hexdigest()
    with _lock:
        _confirmed[:] = [t for t in _confirmed if now - t < 3600]
        last = _confirmed_to.get(key)
        if len(_confirmed) >= CONFIRM_PER_HOUR or (last and now - last < 3600):
            return False
        _confirmed.append(now)
        if len(_confirmed_to) > 5000:
            _confirmed_to.clear()
        _confirmed_to[key] = now
        return True


def clean(value, multiline=False):
    value = CONTROL_RE.sub("", value.replace("\r\n", "\n").replace("\r", "\n"))
    return value.strip() if multiline else " ".join(value.split())


def phone_ok(value):
    return bool(PHONE_RE.match(value)) and len(re.sub(r"\D", "", value)) >= 6


def wa_link(phone):
    """WhatsApp-Link zur Antwort; deutsche Nummern ohne Ländervorwahl bekommen +49."""
    phone = phone.replace("(0)", "").strip()
    digits = re.sub(r"\D", "", phone)
    if not phone.startswith("+"):
        digits = digits[2:] if digits.startswith("00") else "49" + digits[1:] if digits.startswith("0") else digits
    return "https://wa.me/" + digits if len(digits) >= 8 else ""


def validate(form):
    """Return (clean_dict, None, None) or (None, error_message, field_name)."""
    def one(key, multiline=False):
        return clean((form.get(key) or [""])[0], multiline)

    data = {"typ": one("typ") or "check"}
    if data["typ"] not in TYPES:
        return None, "Diese Anfrageart gibt es nicht.", None
    if data["typ"] == "check":
        data["website"] = one("website")
        data["problem"] = [p for p in form.get("problem", []) if p in PROBLEMS]
        data["ziel"] = one("ziel")
        data["hinweis"] = one("hinweis", multiline=True)
    else:
        data["anliegen"] = one("anliegen")
        data["nachricht"] = one("nachricht", multiline=True)
    for key in ("name", "email", "telefon"):
        data[key] = one(key)
    data["kanal"] = one("kanal") or "E-Mail"
    for key, limit in LIMITS.items():
        if len(data.get(key, "")) > limit:
            return None, "Eine Angabe ist zu lang.", key
    # Reihenfolge wie im Formular, damit der erste Fehler im frühesten Schritt liegt.
    if data["typ"] == "check" and data["ziel"] not in GOALS:
        return None, "Bitte wählen Sie aus, was sich zuerst verbessern soll.", "ziel"
    if data["typ"] == "kontakt" and data["anliegen"] not in ANLIEGEN:
        return None, "Bitte wählen Sie aus, worum es geht.", "anliegen"
    if data["typ"] == "kontakt" and not data["nachricht"]:
        return None, "Bitte schreiben Sie kurz Ihr Anliegen.", "nachricht"
    if not data["name"]:
        return None, "Bitte geben Sie Ihren Namen an.", "name"
    if not EMAIL_RE.match(data["email"]):
        return None, "Bitte geben Sie eine gültige E-Mail-Adresse an.", "email"
    if data["telefon"] and not phone_ok(data["telefon"]):
        return None, "Bitte prüfen Sie die Telefonnummer.", "telefon"
    if data["kanal"] not in CHANNELS:
        return None, "Bitte wählen Sie E-Mail oder WhatsApp als Antwortweg.", "kanal"
    if data["kanal"] == "WhatsApp" and not data["telefon"]:
        return None, "Für eine Antwort per WhatsApp benötigen wir Ihre Nummer.", "telefon"
    return data, None, None


def new_nr(now=None):
    stamp = time.strftime("%y%m%d", time.localtime(now))
    return "MS-" + stamp + "-" + "".join(secrets.choice(NR_ALPHABET) for _ in range(4))


def store(data):
    fd = os.open(DATA_FILE, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def owner_text(data):
    check = data["typ"] == "check"
    lines = ["Neuer Website-Check über muratisystems.de" if check else "Neue Nachricht über muratisystems.de",
             "Vorgangsnummer: " + data["nr"], ""]
    if check:
        lines += ["Website: " + (data["website"] or "-"),
                  "Probleme: " + ("; ".join(data["problem"]) or "Keine Auswahl"),
                  "Ziel: " + data["ziel"],
                  "Hinweis: " + (data["hinweis"] or "-")]
    else:
        lines += ["Anliegen: " + data["anliegen"], "Nachricht:", data["nachricht"]]
    lines += ["",
              "Name: " + data["name"],
              "E-Mail: " + data["email"],
              "Telefon/WhatsApp: " + (data["telefon"] or "-"),
              "Bevorzugte Antwort: " + data["kanal"],
              "Eingang: " + data["eingang"]]
    link = wa_link(data["telefon"]) if data["telefon"] else ""
    if link:
        lines += ["", "WhatsApp-Chat öffnen: " + link]
    lines += ["", "Antwort per E-Mail: einfach auf diese Nachricht antworten, sie geht an " + data["email"] + "."]
    return "\n".join(lines)


def confirmation_text(data):
    """Fester Text: nur Vorgangsnummer und Werte aus festen Auswahllisten, nie Freitext."""
    weg = "per WhatsApp" if data["kanal"] == "WhatsApp" else "per E-Mail"
    if data["typ"] == "check":
        intro = "vielen Dank für Ihre Anfrage zum kostenlosen Website-Check. Sie ist bei uns angekommen."
        steps = ["Wir sehen uns Ihre Angaben und Ihre Website persönlich an.",
                 f"Wir melden uns {weg}, {ANTWORTZEIT}.",
                 "Sie bekommen drei Schwachstellen, drei schnelle Verbesserungen und eine Empfehlung. "
                 "Kostenlos und unverbindlich."]
        choice = ["Was trifft zu: " + ("; ".join(data["problem"]) or "keine Auswahl"),
                  "Zuerst verbessern: " + data["ziel"]]
    else:
        intro = "vielen Dank für Ihre Nachricht. Sie ist bei uns angekommen."
        steps = ["Wir lesen Ihre Nachricht persönlich.", f"Wir antworten {weg}, {ANTWORTZEIT}."]
        choice = ["Anliegen: " + data["anliegen"]]
    lines = ["Guten Tag,", "", intro, "", "Vorgangsnummer: " + data["nr"], "", "So geht es weiter:"]
    lines += ["- " + step for step in steps]
    lines += ["", "Ihre Auswahl:"] + choice
    lines += ["", "Sie möchten etwas ergänzen? Antworten Sie einfach auf diese E-Mail."]
    if WHATSAPP_NR:
        lines += ["Oder schreiben Sie uns per WhatsApp: https://wa.me/" + WHATSAPP_NR]
    lines += ["", "Freundliche Grüße", "Murati Systems", "https://muratisystems.de", "",
              "Sie haben diese Anfrage nicht gestellt? Dann können Sie diese E-Mail ignorieren "
              "oder uns kurz Bescheid geben, wir löschen die Angaben dann."]
    return "\n".join(lines)


def mail(subject, text, to, reply_to=None, sender=None, auto=False):
    user = os.environ["SMTP_USER"]
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((sender, user)) if sender else user
    msg["To"] = to
    if reply_to:
        msg["Reply-To"] = reply_to
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=user.rsplit("@", 1)[-1])
    if auto:
        msg["Auto-Submitted"] = "auto-generated"   # RFC 3834: keine Abwesenheitsnotizen zurück
        msg["X-Auto-Response-Suppress"] = "All"
    msg.set_content(text)
    return msg


def smtp_ready():
    return all(os.environ.get(k) for k in ("SMTP_HOST", "SMTP_USER", "SMTP_PASS"))


def mail_safely(data, confirm):
    if not smtp_ready():
        print("SMTP nicht konfiguriert, Anfrage nur gespeichert:", data["nr"], file=sys.stderr)
        return
    what = "Website-Check" if data["typ"] == "check" else "Nachricht"
    topic = "" if data["typ"] == "check" else data["anliegen"] + " – "
    messages = [("Weiterleitung", mail(f"{what} {data['nr']}: {topic}{data['name']}", owner_text(data),
                                        MAIL_TO, reply_to=data["email"], sender="Website muratisystems.de"))]
    if confirm:
        messages.append(("Bestätigung", mail(f"Ihre Anfrage bei Murati Systems ({data['nr']})",
                                             confirmation_text(data), data["email"],
                                             sender="Murati Systems", auto=True)))
    try:
        with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "465")), timeout=20) as smtp:
            smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            for label, msg in messages:
                try:
                    smtp.send_message(msg)
                except smtplib.SMTPException as exc:
                    print(label, data["nr"], "fehlgeschlagen:", exc, file=sys.stderr)
    except Exception as exc:  # gespeichert ist sie trotzdem
        print("Mailversand fehlgeschlagen:", data["nr"], exc, file=sys.stderr)


PAGE = """<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/redesign.css"><title>Angabe prüfen – Murati Systems</title></head>
<body>
<header class="site-header"><div class="shell header-inner">
<a class="brand" href="/index.html" aria-label="Murati Systems – Startseite"><img src="/assets/favicon.svg?v=5" alt="" width="36" height="36"><span><strong>Murati</strong><small>Systems</small></span></a>
</div></header>
<main class="legal"><div class="shell legal-shell"><p class="eyebrow">{eyebrow}</p>
<h1>Bitte kurz prüfen.</h1><p>{msg}</p><p>Tipp: Mit der Zurück-Taste Ihres Browsers bleiben Ihre Eingaben meist erhalten.</p>
<p><a class="button primary" href="{back}">Zum Formular</a></p>
<p>Oder direkt per E-Mail: <a href="mailto:info@muratisystems.de">info@muratisystems.de</a></p>
</div></main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "anfrage"
    sys_version = ""
    json_mode = False

    def _send(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _page(self, code, msg, typ="check"):
        kontakt = typ == "kontakt"
        body = PAGE.format(msg=html.escape(msg), eyebrow="Kontakt" if kontakt else "Website-Check",
                           back="/kontakt.html#nachricht" if kontakt else "/website-check.html#formular")
        self._send(code, body.encode(), "text/html; charset=utf-8")

    def _json(self, code, payload):
        self._send(code, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def _redirect(self, where):
        self.send_response(303)
        self.send_header("Location", where)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _fail(self, code, msg, field=None, typ="check"):
        if self.json_mode:
            return self._json(code, {"ok": False, "fehler": msg, "feld": field})
        self._page(code, msg, typ)

    def _done(self, result):
        if self.json_mode:
            return self._json(200, {"ok": True, **result})
        self._redirect("/danke.html?" + urlencode({"nr": result["nr"], "typ": result["typ"],
                                                  "b": int(bool(result["bestaetigung"]))}))

    def do_GET(self):
        if self.path == "/api/health":
            self.send_response(204)
            self.end_headers()
        else:
            self._redirect("/website-check.html")

    def do_POST(self):
        self.json_mode = "application/json" in (self.headers.get("Accept") or "")
        if self.path.split("?")[0] != "/api/anfrage":
            return self._fail(404, "Diese Adresse gibt es nicht.")
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            return self._fail(413, "Die Anfrage ist zu groß.")
        form = parse_qs(self.rfile.read(length).decode("utf-8", "replace"))
        first = lambda key: (form.get(key) or [""])[0]
        typ = first("typ") if first("typ") in TYPES else "check"
        if first("homepage"):   # Honeypot: Bots bekommen Erfolg, gespeichert wird nichts
            print("Honeypot ausgelöst, Anfrage verworfen", file=sys.stderr)
            return self._done({"nr": new_nr(), "typ": typ, "kanal": "E-Mail", "bestaetigung": False})
        now = time.time()
        # Letzter Eintrag = von unserem Caddy gesetzt; die vorderen kann der Absender frei erfinden.
        ip = (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",")[-1].strip()
        nonce = first("nonce") if NONCE_RE.match(first("nonce")) else ""
        ttl = NONCE_TTL
        if not nonce:
            # B51: Ohne JavaScript liefert der Client keine Nonce (assets/anfrage.js Zeile 40-44
            # erzeugt sie nur per Skript). Fallback: Formulardaten + IP kurz hashen, damit ein
            # Doppelklick oder Zurueck-Button-Resubmit trotzdem dedupliziert wird, ohne dass zwei
            # verschiedene Besucher sich durch einen langlebigen, gemeinsamen Schluessel blockieren.
            raw = "&".join(sorted(f"{k}={v}" for k, values in form.items() if k != "nonce" for v in values))
            nonce = "auto-" + hashlib.sha256(f"{ip}|{raw}".encode()).hexdigest()
            ttl = DOUBLE_SUBMIT_TTL
        earlier = recall(nonce, now, ttl)
        if earlier:             # derselbe Versand noch einmal (Doppelklick, Rückfall ohne JS)
            return self._done(earlier)
        if rate_limited(ip, now):
            return self._fail(429, "Zu viele Anfragen in kurzer Zeit. Bitte versuchen Sie es später erneut. "
                                    "Oder schreiben Sie uns per WhatsApp oder E-Mail.", typ=typ)
        data, error, field = validate(form)
        if error:
            return self._fail(400, error, field, typ)
        data["nr"] = new_nr(now)
        data["eingang"] = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(now))
        store(data)
        confirm = CONFIRM_MAIL and smtp_ready() and may_confirm(data["email"], now)
        result = {"nr": data["nr"], "typ": data["typ"], "kanal": data["kanal"], "bestaetigung": confirm}
        remember(nonce, result, now)
        threading.Thread(target=mail_safely, args=(data, confirm), daemon=True).start()
        self._done(result)

    def log_message(self, fmt, *args):
        pass  # keine Zugriffsprotokolle mit IP-Adressen


def selftest():
    global DATA_FILE
    import tempfile
    import urllib.error
    import urllib.request

    ok = {"name": ["Max"], "email": ["max@example.de"], "ziel": ["Mehr passende Anfragen"],
          "problem": ["Wir haben noch keine Website", "erfunden"]}
    data, err, field = validate(ok)
    assert err is None and data["problem"] == ["Wir haben noch keine Website"] and data["kanal"] == "E-Mail"
    assert data["typ"] == "check"
    assert validate({**ok, "email": ["kaputt"]})[2] == "email"
    assert validate({**ok, "ziel": ["x"]})[2] == "ziel"
    assert validate({**ok, "kanal": ["WhatsApp"]})[2] == "telefon"
    assert validate({**ok, "kanal": ["WhatsApp"], "telefon": ["0162 1234567"]})[1] is None
    assert validate({**ok, "telefon": ["abc"]})[2] == "telefon"
    assert validate({**ok, "hinweis": ["x" * 1001]})[2] == "hinweis"
    assert validate({**ok, "typ": ["x"]})[1]
    assert validate({**ok, "name": ["Max\r\nBcc: x@y.de"]})[0]["name"] == "Max Bcc: x@y.de"
    kontakt = {"typ": ["kontakt"], "anliegen": ["Website"], "nachricht": ["Hallo\r\nWelt"],
               "name": ["Eva"], "email": ["eva@example.de"]}
    data, err, _ = validate(kontakt)
    assert err is None and data["nachricht"] == "Hallo\nWelt" and "ziel" not in data
    assert validate({**kontakt, "anliegen": ["x"]})[2] == "anliegen"
    assert validate({**kontakt, "nachricht": [" "]})[2] == "nachricht"
    assert re.fullmatch(r"MS-\d{6}-[A-HJ-NP-Z2-9]{4}", new_nr())
    assert wa_link("0152 33955912") == "https://wa.me/4915233955912"
    assert wa_link("+49 (0)152 339-55912") == "https://wa.me/4915233955912"
    assert wa_link("0049 152 33955912") == "https://wa.me/4915233955912"
    assert wa_link("12") == ""
    assert not any(rate_limited("t", now=1000 + i) for i in range(RATE_LIMIT))
    assert rate_limited("t", now=1010)
    assert not rate_limited("t", now=5000)
    assert may_confirm("a@example.de", now=100) and not may_confirm("A@example.de", now=200)
    assert may_confirm("a@example.de", now=3800)
    spam = {**ok, "name": ["Kaufen Sie jetzt"], "website": ["spam.example"], "hinweis": ["http://spam.example"]}
    data = validate(spam)[0]
    data.update(nr="MS-260925-TEST", eingang="jetzt")
    text = confirmation_text(data)
    assert "MS-260925-TEST" in text and "Kaufen" not in text and "spam.example" not in text
    assert "Kaufen Sie jetzt" in owner_text(data) and "wa.me" not in owner_text(data)

    # Durchstich über HTTP: JSON-Modus, Nonce, Fehlerfeld, Weiterleitung ohne JS, Honeypot.
    with tempfile.TemporaryDirectory() as tmp:
        DATA_FILE = os.path.join(tmp, "anfragen.jsonl")
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{server.server_address[1]}/api/anfrage"

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args):
                return None
        opener = urllib.request.build_opener(NoRedirect)

        def post(fields, accept="application/json"):
            body = urlencode(fields, doseq=True).encode()
            req = urllib.request.Request(url, body, {"Accept": accept, "X-Forwarded-For": "1.2.3.4, 10.0.0.9"})
            try:
                with opener.open(req) as resp:
                    return resp.status, resp.headers, resp.read()
            except urllib.error.HTTPError as exc:
                return exc.code, exc.headers, exc.read()

        form = {"name": "Max", "email": "max@example.de", "ziel": "Mehr passende Anfragen", "nonce": "test-nonce-1"}
        status, _, body = post(form)
        first_result = json.loads(body)
        assert status == 200 and first_result["ok"] and first_result["bestaetigung"] is False
        status, _, body = post(form)
        assert json.loads(body)["nr"] == first_result["nr"]
        status, _, body = post({**form, "nonce": "test-nonce-2", "email": "kaputt"})
        assert status == 400 and json.loads(body)["feld"] == "email"
        status, headers, _ = post({**form, "nonce": "test-nonce-3", "typ": "kontakt", "anliegen": "Website",
                                   "nachricht": "Hallo"}, accept="text/html")
        assert status == 303 and headers["Location"].startswith("/danke.html?nr=MS-")
        assert "&typ=kontakt&b=0" in headers["Location"]
        status, _, body = post({**form, "nonce": "test-nonce-4", "homepage": "bot"})
        assert status == 200 and json.loads(body)["ok"]
        server.shutdown()
        server.server_close()
        with open(DATA_FILE, encoding="utf-8") as f:
            stored = [json.loads(line) for line in f]
        assert [s["typ"] for s in stored] == ["check", "kontakt"], stored
        assert all("nonce" not in s and "homepage" not in s for s in stored)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    else:
        ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
