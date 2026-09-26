#!/usr/bin/env python3
"""Build dist/ from the source pages.

- Renders shared chrome (header incl. mobile menu, footer, mobile contact bar,
  cookie dialog) from the templates below into every page, using the
  per-page `<!-- @page current="..." wa="..." prefix="/" -->` comment each
  source page carries right after `<!doctype html>`.
- Cache-busts redesign.css, formular.css, main.js, anfrage.js, privacy.js and
  favicon.svg with an 8-hex content-hash query, so nobody hand-edits `?v=N`.
- Minifies CSS (comments + insignificant whitespace only, no property/selector
  rewriting) so the shipped file is smaller without needing a bundler.
- JS is copied unminified: a stdlib-only regex minifier can't safely tell code
  from string/regex literals, and breaking backend-form JS is worse than
  saving a few KB. ponytail: revisit with a real JS parser if bytes matter.

Usage: python3 tools/build.py [--out dist]
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    "index.html", "leistungen.html", "ki-automatisierung.html", "website-check.html",
    "arbeitsweise.html", "kontakt.html", "faq.html",
    "website-handwerk-dortmund.html", "website-praxis-dortmund.html", "website-dienstleister-dortmund.html",
    "impressum.html", "datenschutz.html", "danke.html", "404.html",
]

# (key, href, desktop label, mobile label) - order matters, matches the live markup.
DESKTOP_NAV = [
    ("start", "index.html", "Start"),
    ("leistungen", "leistungen.html", "Leistungen"),
    ("ki", "ki-automatisierung.html", "KI &amp; IT"),
    ("arbeitsweise", "arbeitsweise.html", "Arbeitsweise"),
    ("kontakt", "kontakt.html", "Kontakt"),
]
MOBILE_NAV = [
    ("start", "index.html", "Start"),
    ("leistungen", "leistungen.html", "Leistungen"),
    ("ki", "ki-automatisierung.html", "KI &amp; IT-Beratung"),
    ("website-check", "website-check.html", "Website-Check"),
    ("arbeitsweise", "arbeitsweise.html", "Arbeitsweise"),
    ("kontakt", "kontakt.html", "Kontakt"),
]
FOOTER_NAV = [
    ("leistungen", "leistungen.html", "Leistungen"),
    ("ki", "ki-automatisierung.html", "KI &amp; IT-Beratung"),
    ("website-check", "website-check.html", "Website-Check"),
    ("kontakt", "kontakt.html", "Kontakt"),
    ("faq", "faq.html", "Häufige Fragen"),
    ("handwerk", "website-handwerk-dortmund.html", "Handwerk"),
    ("praxis", "website-praxis-dortmund.html", "Praxen"),
    ("dienstleister", "website-dienstleister-dortmund.html", "Dienstleister"),
    ("impressum", "impressum.html", "Impressum"),
    ("datenschutz", "datenschutz.html", "Datenschutz"),
]

ASSET_FILES = ["redesign.css", "formular.css", "main.js", "anfrage.js", "privacy.js", "favicon.svg"]

PAGE_MARKER_RE = re.compile(
    r'<!--\s*@page\s+current="([^"]*)"\s+wa="([^"]*)"(?:\s+prefix="([^"]*)")?\s*-->\n?'
)


def wa_link(text: str) -> str:
    return f"https://wa.me/4915233955912?text={quote(text, safe='')}"


def nav_links(items, current: str | None, prefix: str) -> str:
    out = []
    for key, href, label in items:
        cur = ' aria-current="page"' if key == current else ""
        out.append(f'<a href="{prefix}{href}"{cur}>{label}</a>')
    return "".join(out)


def render_header(prefix: str, current: str | None, wa_text: str) -> str:
    wa = wa_link(wa_text)
    desktop = nav_links(DESKTOP_NAV, current, prefix)
    mobile = nav_links(MOBILE_NAV, current, prefix)
    return (
        '<header class="site-header">\n'
        '    <div class="shell header-inner">\n'
        f'      <a class="brand" href="{prefix}index.html" aria-label="Murati Systems – Startseite">\n'
        f'        <img src="{prefix}assets/favicon.svg" alt="" width="36" height="36">\n'
        '        <span><strong>Murati</strong><small>Systems</small></span>\n'
        '      </a>\n'
        '      <nav class="desktop-nav" aria-label="Hauptnavigation">\n'
        f'        {desktop}\n'
        '      </nav>\n'
        f'      <a class="header-whatsapp" href="{wa}" target="_blank" rel="noopener noreferrer">'
        f'<span class="wa-i" aria-hidden="true"></span>WhatsApp</a>'
        f'<a class="header-cta" href="{prefix}website-check.html">Website-Check <span aria-hidden="true">→</span></a>\n'
        '      <details class="mobile-menu"><summary><span class="menu-label-closed">Menü</span>'
        '<span class="menu-label-open">Schließen</span></summary>'
        f'<nav aria-label="Mobile Navigation">{mobile}'
        f'<a href="{wa}" target="_blank" rel="noopener noreferrer">'
        '<span class="wa-i" aria-hidden="true"></span>WhatsApp</a></nav></details>\n'
        '    </div>\n'
        '  </header>'
    )


def render_footer(prefix: str, current: str | None) -> str:
    footer_nav = nav_links(FOOTER_NAV, current, prefix)
    return (
        '<footer class="site-footer"><div class="shell footer-inner">\n'
        f'    <div><a class="footer-brand" href="{prefix}index.html">Murati Systems</a>'
        '<p>Websites und digitale Abläufe für Betriebe, die gefunden werden wollen.</p></div>\n'
        f'    <nav aria-label="Footer">{footer_nav}</nav>\n'
        '    <span class="copyright">© 2026 Murati Systems</span>\n'
        f'  </div><div class="shell"><a class="cookie-settings" href="{prefix}datenschutz.html#cookies" '
        'data-cookie-info>Cookies &amp; Datenschutz</a></div></footer>'
    )


def render_mobile_contact(prefix: str, wa_text: str, current: str | None) -> str:
    wa = wa_link(wa_text)
    cur = ' aria-current="page"' if current == "website-check" else ""
    return (
        '<div class="mobile-contact">'
        f'<a class="wa" href="{wa}" target="_blank" rel="noopener noreferrer">'
        '<span class="wa-i" aria-hidden="true"></span>WhatsApp</a>'
        f'<a href="{prefix}website-check.html"{cur}>Website-Check</a></div>'
    )


def render_cookie_dialog(prefix: str) -> str:
    return (
        '<dialog id="cookie-dialog" class="cookie-dialog" aria-labelledby="cookie-title">\n'
        '<h2 id="cookie-title">Cookies &amp; Datenschutz</h2>\n'
        '<p>Diese Website verwendet keine Cookies und keine Analyse- oder Werbedienste. '
        'Schriftarten und Gestaltungselemente werden vom eigenen Server geladen.</p>\n'
        '<dl class="cookie-summary"><dt>Cookies und dauerhafter Browserspeicher</dt><dd>Nicht verwendet</dd>'
        '<dt>Statistik und Werbung</dt><dd>Nicht eingebunden</dd><dt>Externe Dienste</dt>'
        '<dd>WhatsApp öffnet sich erst, wenn Sie einen entsprechenden Link anklicken.</dd></dl>\n'
        '<p>Es sind keine optionalen Dienste aktiv. Deshalb gibt es aktuell keine Einwilligungseinstellungen. '
        'Dieser Dialog speichert keine Auswahl.</p>\n'
        f'<div class="cookie-actions"><a class="button subtle" href="{prefix}datenschutz.html#cookies">'
        'Datenschutz lesen</a><button type="button" class="button primary" data-cookie-close autofocus>'
        'Schließen</button></div>\n'
        '</dialog>'
    )


def render_page(src: str) -> str:
    m = PAGE_MARKER_RE.search(src)
    if not m:
        raise SystemExit("missing @page marker")
    current = m.group(1) or None
    wa_text = m.group(2)
    prefix = m.group(3) or ""
    out = src[: m.start()] + src[m.end():]

    out = out.replace("<!-- @header -->", render_header(prefix, current, wa_text), 1)
    out = out.replace("<!-- @footer -->", render_footer(prefix, current), 1)
    out = out.replace("<!-- @mobile-contact -->", render_mobile_contact(prefix, wa_text, current), 1)
    out = out.replace("<!-- @cookie-dialog -->", render_cookie_dialog(prefix), 1)
    return out


def minify_css(css: str) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"[ \t\r\n]+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    return css.strip()


def build_assets(out_dir: Path) -> dict[str, str]:
    """Copy assets/ into dist, minifying the two CSS files, and return the
    8-hex content hash of each cache-busted file (computed from the bytes we
    actually wrote, so ?v= always matches what's served)."""
    src_assets = ROOT / "assets"
    dst_assets = out_dir / "assets"
    if dst_assets.exists():
        shutil.rmtree(dst_assets)
    shutil.copytree(src_assets, dst_assets)

    hashes: dict[str, str] = {}
    for name in ASSET_FILES:
        f = dst_assets / name
        if not f.exists():
            continue
        if name.endswith(".css"):
            f.write_text(minify_css(f.read_text(encoding="utf-8")), encoding="utf-8")
        hashes[name] = hashlib.sha256(f.read_bytes()).hexdigest()[:8]
    return hashes


ASSET_REF_RE = re.compile(
    r'((?:href|src)=")(/?assets/(?:'
    + "|".join(re.escape(f) for f in ASSET_FILES)
    + r'))(?:\?v=[0-9a-fA-F]+)?"'
)


def cache_bust(html: str, hashes: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        attr, path = m.group(1), m.group(2)
        name = path.rsplit("/", 1)[-1]
        h = hashes.get(name)
        return f'{attr}{path}?v={h}"' if h else m.group(0)

    return ASSET_REF_RE.sub(repl, html)


STATIC_FILES = [
    "robots.txt", "sitemap.xml", "BingSiteAuth.xml",
    "48f0da7f644eb16318a0c3ca42892420.txt",  # search-console verification
    "googlee0ef753932ea7e7a.html",  # search-console verification
]


def copy_static(out_dir: Path) -> None:
    for name in STATIC_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, out_dir / name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    out_dir = ROOT / args.out
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    hashes = build_assets(out_dir)

    for name in PAGES:
        src = (ROOT / name).read_text(encoding="utf-8")
        html = render_page(src)
        html = cache_bust(html, hashes)
        (out_dir / name).write_text(html, encoding="utf-8")

    copy_static(out_dir)

    print(f"Built {len(PAGES)} pages into {out_dir} (assets hashed: {', '.join(hashes)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
