"""Lokale Vorschau mit Formular-Backend: statische Seiten plus POST /api/anfrage.

Start im Ordner website/:  python backend/dev_server.py [port]   (Standard 8791)
Anfragen landen in einer temporären Datei. E-Mails werden nur ausgegeben, nie versendet.
Setzt dieselbe Content-Security-Policy wie die Produktion (deploy/Caddyfile).
"""
import functools
import os
import re
import smtplib
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["DATA_FILE"] = os.path.join(tempfile.gettempdir(), "murati-anfragen-dev.jsonl")
os.environ.update(SMTP_HOST="dev", SMTP_USER="info@muratisystems.de", SMTP_PASS="dev")
sys.path.insert(0, str(ROOT / "backend"))
import anfrage  # noqa: E402

CSP = re.search(r'Content-Security-Policy "([^"]+)"', (ROOT / "deploy" / "Caddyfile").read_text()).group(1)


class PrintSMTP:
    """Ersetzt den SMTP-Versand: zeigt die Mail im Terminal."""
    def __init__(self, *args, **kwargs): pass
    def __enter__(self): return self
    def __exit__(self, *exc): return False
    def login(self, *args): pass
    def send_message(self, msg):
        print(f"\n--- Mail an {msg['To']}: {msg['Subject']}\n{msg.get_content()}---", flush=True)


smtplib.SMTP_SSL = PrintSMTP


class DevHandler(anfrage.Handler, SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            return anfrage.Handler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
    print(f"http://localhost:{port}/website-check.html  (Anfragen: {os.environ['DATA_FILE']})", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), functools.partial(DevHandler, directory=str(ROOT))).serve_forever()
