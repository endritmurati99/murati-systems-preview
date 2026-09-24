#!/usr/bin/env python3
"""Fast static checks for the Murati Systems preview. Run: python3 tests/check_site.py"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CORE_PAGES = (
    "index.html",
    "leistungen.html",
    "website-check.html",
    "arbeitsweise.html",
    "kontakt.html",
    "ki-automatisierung.html",
    "impressum.html",
    "datenschutz.html",
)
REQUIRED_PRICES = ("790 €", "1.490 €", "690 €", "2.500 €", "49 €", "79 €")
EXTERNAL = re.compile(r"^(?:https?:)?//", re.I)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.h1_count = 0
        self.external_scripts: list[str] = []
        self.external_fonts: list[str] = []
        self.jsonld: list[str] = []
        self._in_jsonld = False
        self._jsonld_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
        if tag in {"a", "link"} and data.get("href"):
            self.links.append(("href", data["href"]))
        if tag in {"img", "script", "source"} and data.get("src"):
            self.links.append(("src", data["src"]))
        if tag == "script" and data.get("src") and EXTERNAL.match(data["src"]):
            self.external_scripts.append(data["src"])
        if tag == "link" and data.get("href") and EXTERNAL.match(data["href"]):
            rel = (data.get("rel") or "").lower()
            href = data["href"].lower()
            if "stylesheet" in rel or "font" in href:
                self.external_fonts.append(data["href"])
        if tag == "script" and (data.get("type") or "").lower() == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._jsonld_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._jsonld_chunks))
            self._in_jsonld = False


def local_target(page: Path, value: str) -> Path | None:
    value = value.strip()
    if not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return None
    if EXTERNAL.match(value):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    target = (ROOT / path.lstrip("/")) if path.startswith("/") else page.parent / path
    return target.resolve()


def check_target(page: Path, kind: str, value: str, errors: list[str]) -> None:
    target = local_target(page, value)
    if target is not None and not target.exists():
        errors.append(f"{page.relative_to(ROOT)}: missing {kind} target {value}")


def main() -> int:
    errors: list[str] = []
    pages = [ROOT / name for name in CORE_PAGES if (ROOT / name).exists()]
    design_page = ROOT / "design" / "index.html"
    if design_page.exists():
        pages.append(design_page)

    if not pages:
        errors.append("no core pages found")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        parser = PageParser()
        parser.feed(text)
        if "noindex" in text and page.parent == ROOT:
            errors.append(f"{page.relative_to(ROOT)}: live page must not be noindex")
        if parser.h1_count != 1:
            errors.append(f"{page.relative_to(ROOT)}: expected one h1, got {parser.h1_count}")
        for kind, value in parser.links:
            check_target(page, kind, value, errors)
        for value in parser.external_scripts:
            errors.append(f"{page.relative_to(ROOT)}: external script {value}")
        for value in parser.external_fonts:
            errors.append(f"{page.relative_to(ROOT)}: external stylesheet/font {value}")
        for block in parser.jsonld:
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                errors.append(f"{page.relative_to(ROOT)}: invalid JSON-LD ({exc.msg})")

    css_files = [ROOT / "assets" / "redesign.css"]
    if design_page.exists():
        css_files.extend(design_page.parent.glob("*.css"))
    for css in css_files:
        if not css.exists():
            continue
        for value in re.findall(r"url\(\s*['\"]?([^'\"\)]+)", css.read_text(encoding="utf-8")):
            check_target(css, "CSS url()", value, errors)

    prices = (ROOT / "leistungen.html").read_text(encoding="utf-8") if (ROOT / "leistungen.html").exists() else ""
    for price in REQUIRED_PRICES:
        if price not in prices:
            errors.append(f"leistungen.html: approved price missing: {price}")

    if errors:
        print("Site check failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Site check passed: {len(pages)} preview page(s), local targets, indexable, h1, local assets, prices, JSON-LD.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
