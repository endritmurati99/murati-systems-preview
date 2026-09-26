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


def confirmation_parts(data):
    """Fester Inhalt der Bestätigung: nur Vorgangsnummer und Werte aus festen Auswahllisten, nie Freitext."""
    weg = "per WhatsApp" if data["kanal"] == "WhatsApp" else "per E-Mail"
    if data["typ"] == "check":
        intro = "vielen Dank für Ihre Anfrage zum kostenlosen Website-Check. Sie ist bei uns angekommen."
        steps = ["Wir sehen uns Ihre Angaben und Ihre Website persönlich an.",
                 f"Wir melden uns {weg}, {ANTWORTZEIT}.",
                 "Sie bekommen drei Schwachstellen, drei schnelle Verbesserungen und eine Empfehlung. "
                 "Kostenlos und unverbindlich."]
        choice = [("Was trifft zu", "; ".join(data["problem"]) or "keine Auswahl"),
                  ("Zuerst verbessern", data["ziel"])]
    else:
        intro = "vielen Dank für Ihre Nachricht. Sie ist bei uns angekommen."
        steps = ["Wir lesen Ihre Nachricht persönlich.", f"Wir antworten {weg}, {ANTWORTZEIT}."]
        choice = [("Anliegen", data["anliegen"])]
    return intro, steps, choice
def confirmation_text(data):
    intro, steps, choice = confirmation_parts(data)
    lines = ["Guten Tag,", "", intro, "", "Vorgangsnummer: " + data["nr"], "", "So geht es weiter:"]
    lines += ["- " + step for step in steps]
    lines += ["", "Ihre Auswahl:"] + [f"{k}: {v}" for k, v in choice]
    lines += ["", "Sie möchten etwas ergänzen? Antworten Sie einfach auf diese E-Mail."]
    if WHATSAPP_NR:
        lines += ["Oder schreiben Sie uns per WhatsApp: https://wa.me/" + WHATSAPP_NR]
    lines += ["", "Freundliche Grüße", "Endrit Murati", "Murati Systems", "Telefon " + TELEFON,
              SITE, "",
              "Sie haben diese Anfrage nicht gestellt? Dann können Sie diese E-Mail ignorieren "
              "oder uns kurz Bescheid geben, wir löschen die Angaben dann.", "", ANSCHRIFT]
    return "\n".join(lines)
# HTML-Fassung: Tabellen und Inline-Styles, weil Mailprogramme kaum CSS können. Farben wie redesign.css.
SITE = "https://muratisystems.de"
TELEFON = "0152 33955912"
ANSCHRIFT = "Endrit Murati, handelnd unter Murati Systems, Enscheder Straße 5, 44145 Dortmund"
FONT = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
def _page(preheader, body):
    e = html.escape
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light"><title>Murati Systems</title></head>
<body style="margin:0;padding:0;background:#f1f0ec;{FONT}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{e(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f1f0ec"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #ddddda">
<tr><td style="background:#161616;padding:20px 28px"><table role="presentation" cellpadding="0" cellspacing="0"><tr>
<td style="vertical-align:middle"><img src="{SITE}/assets/logo.png" width="40" height="40" alt="M" style="display:block;border:0;border-radius:8px"></td>
<td style="vertical-align:middle;padding-left:12px;color:#ffffff;font-size:18px;font-weight:700;{FONT}">Murati Systems</td>
</tr></table></td></tr>
<tr><td style="height:4px;background:#ec4e14;line-height:4px;font-size:0">&nbsp;</td></tr>
<tr><td style="padding:32px 28px 8px;color:#242424;font-size:16px;line-height:1.55;{FONT}">{body}</td></tr>
</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px"><tr><td style="padding:18px 28px;color:#626262;font-size:12px;line-height:1.6;{FONT}">
{e(ANSCHRIFT)}<br><a href="{SITE}/impressum.html" style="color:#626262">Impressum</a> &middot; <a href="{SITE}/datenschutz.html" style="color:#626262">Datenschutz</a>
</td></tr></table>
</td></tr></table></body></html>"""
def _button(href, label, bg, ink):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 8px 10px 0;display:inline-table">'
            f'<tr><td style="background:{bg};border-radius:10px"><a href="{html.escape(href)}" '
            f'style="display:inline-block;padding:13px 20px;color:{ink};font-size:15px;font-weight:700;'
            f'text-decoration:none;{FONT}">{html.escape(label)}</a></td></tr></table>')
def _rows(pairs):
    return "".join(f'<tr><td style="padding:6px 14px 6px 0;color:#626262;font-size:14px;vertical-align:top;white-space:nowrap">{html.escape(k)}</td>'
                   f'<td style="padding:6px 0;font-size:15px;vertical-align:top">{v}</td></tr>' for k, v in pairs)
def confirmation_html(data):
    e = html.escape
    intro, steps, choice = confirmation_parts(data)
    title = "Ihre Anfrage ist angekommen." if data["typ"] == "check" else "Ihre Nachricht ist angekommen."
    step_rows = "".join(f'<tr><td style="padding:7px 12px 7px 0;vertical-align:top"><div style="width:10px;height:10px;'
                        f'margin-top:7px;background:#ec4e14;border-radius:3px"></div></td>'
                        f'<td style="padding:7px 0;font-size:16px">{e(x)}</td></tr>' for x in steps)
    buttons = ""
    if WHATSAPP_NR:
        text = f"Hallo Murati Systems, ich möchte meine Anfrage {data['nr']} ergänzen."
        buttons += _button(f"https://wa.me/{WHATSAPP_NR}?" + urlencode({"text": text}).replace("+", "%20"),
                           "Per WhatsApp ergänzen", "#25d366", "#07301a")
    buttons += _button(SITE, "muratisystems.de", "#242424", "#ffffff")
    tel = "+49" + TELEFON[1:].replace(" ", "")
    body = f"""<h1 style="margin:0 0 16px;font-size:26px;line-height:1.2;color:#161616">{title}</h1>
<p style="margin:0 0 20px">Guten Tag,<br>{e(intro)}</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 26px"><tr>
<td style="background:#fff0e9;border-left:4px solid #ec4e14;border-radius:8px;padding:14px 18px">
<div style="font-size:13px;color:#b93a0a;font-weight:700">Ihre Vorgangsnummer</div>
<div style="font-size:24px;font-weight:800;letter-spacing:.5px;color:#161616">{e(data["nr"])}</div></td></tr></table>
<h2 style="margin:0 0 8px;font-size:18px;color:#161616">So geht es weiter</h2>
<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px">{step_rows}</table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 26px"><tr>
<td style="background:#f1f0ec;border-radius:10px;padding:14px 18px"><div style="font-size:14px;font-weight:700;margin-bottom:4px">Ihre Auswahl</div>
<table role="presentation" cellpadding="0" cellspacing="0">{_rows((k, e(v).replace("; ", "<br>")) for k, v in choice)}</table></td></tr></table>
<p style="margin:0 0 16px">Sie möchten etwas ergänzen? Antworten Sie einfach auf diese E-Mail.</p>
<div style="margin:0 0 22px">{buttons}</div>
<p style="margin:0 0 24px">Freundliche Grüße<br><strong>Endrit Murati</strong><br>Murati Systems<br>
Telefon <a href="tel:{tel}" style="color:#242424">{TELEFON}</a></p>
<p style="margin:0 0 24px;padding-top:16px;border-top:1px solid #ddddda;font-size:13px;color:#626262">Sie haben diese Anfrage nicht gestellt?
Dann können Sie diese E-Mail ignorieren oder uns kurz Bescheid geben, wir löschen die Angaben dann.</p>"""
    return _page(f"Vorgangsnummer {data['nr']}. {steps[1]}", body)
def owner_html(data):
    """Weiterleitung an info@: enthält Freitext, darum alles escapen."""
    e = html.escape
    check = data["typ"] == "check"
    pairs = [("Vorgang", f"<strong>{e(data['nr'])}</strong>")]
    if check:
        pairs += [("Website", e(data["website"] or "-")),
                  ("Probleme", e("; ".join(data["problem"]) or "Keine Auswahl").replace("; ", "<br>")),
                  ("Ziel", e(data["ziel"])), ("Hinweis", e(data["hinweis"] or "-").replace("\n", "<br>"))]
    else:
        pairs += [("Anliegen", e(data["anliegen"])), ("Nachricht", e(data["nachricht"]).replace("\n", "<br>"))]
    pairs += [("Name", e(data["name"])), ("E-Mail", e(data["email"])), ("Telefon", e(data["telefon"] or "-")),
              ("Antwort per", e(data["kanal"])), ("Eingang", e(data["eingang"]))]
    subject = urlencode({"subject": f"Ihre Anfrage {data['nr']}"}).replace("+", "%20")
    buttons = _button(f"mailto:{data['email']}?{subject}", "Per E-Mail antworten", "#242424", "#ffffff")
    link = wa_link(data["telefon"]) if data["telefon"] else ""
    if link:
        buttons += _button(link, "WhatsApp-Chat öffnen", "#25d366", "#07301a")
    body = f"""<h1 style="margin:0 0 16px;font-size:22px;color:#161616">{"Neuer Website-Check" if check else "Neue Nachricht"}</h1>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px">{_rows(pairs)}</table>
<div style="margin:0 0 18px">{buttons}</div>
<p style="margin:0 0 24px;font-size:13px;color:#626262">Antworten auf diese E-Mail gehen direkt an {e(data["email"])}.</p>"""
    return _page(f"{data['nr']} von {data['name']}", body)
def mail(subject, text, to, reply_to=None, sender=None, auto=False, html_body=None):
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
    if html_body:
        msg.add_alternative(html_body, subtype="html")
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
                                        MAIL_TO, reply_to=data["email"], sender="Website muratisystems.de",
                                        html_body=owner_html(data)))]
    if confirm:
        messages.append(("Bestätigung", mail(f"Ihre Anfrage bei Murati Systems ({data['nr']})",
                                             confirmation_text(data), data["email"],
                                             sender="Murati Systems", auto=True,
                                             html_body=confirmation_html(data))))
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
    page = confirmation_html(data)
    assert "MS-260925-TEST" in page and "Kaufen" not in page and "spam.example" not in page
    evil = {**data, "name": "<script>x</script>", "hinweis": "<img src=x>"}
    assert "<script>x" not in owner_html(evil) and "&lt;img" in owner_html(evil)
    os.environ.setdefault("SMTP_USER", "info@example.de")
    msg = mail("s", confirmation_text(data), "a@example.de", html_body=page)
    assert [p.get_content_type() for p in msg.iter_parts()] == ["text/plain", "text/html"]

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
