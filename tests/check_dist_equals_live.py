#!/usr/bin/env python3
"""Proves the build is behaviourally a no-op: every dist/*.html must contain
the same content as the live baseline commit, ignoring whitespace and the
cache-busting ?v= query (numeric on live, 8-hex after the build).

Usage: python3 tests/check_dist_equals_live.py [dist] [--base 603288a]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGES = [
    "index.html", "leistungen.html", "ki-automatisierung.html", "website-check.html",
    "arbeitsweise.html", "kontakt.html", "faq.html",
    "website-handwerk-dortmund.html", "website-praxis-dortmund.html", "website-dienstleister-dortmund.html",
    "impressum.html", "datenschutz.html", "danke.html", "404.html",
]


def normalize(html: str) -> str:
    html = re.sub(r"\?v=[0-9a-fA-F]+", "?v=X", html)
    # B55/B40: the build adds cache-busting to assets that previously had none
    # (e.g. privacy.js). Normalize "file" and "file?v=X" to the same thing so
    # the comparison checks content, not who already had a version query.
    html = re.sub(r'"((?:/)?assets/[\w.-]+\.(?:css|js|svg))"', r'"\1?v=X"', html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


def live_content(base: str, name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{base}:{name}"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return result.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dist", nargs="?", default="dist")
    ap.add_argument("--base", default="603288a")
    args = ap.parse_args()
    dist_dir = ROOT / args.dist

    failures = []
    for name in PAGES:
        dist_path = dist_dir / name
        if not dist_path.exists():
            failures.append(f"{name}: missing in {args.dist}/")
            continue
        built = normalize(dist_path.read_text(encoding="utf-8"))
        live = normalize(live_content(args.base, name))
        if built != live:
            # Find the first differing character to give a useful pointer.
            i = 0
            while i < min(len(built), len(live)) and built[i] == live[i]:
                i += 1
            failures.append(
                f"{name}: differs at offset {i}\n"
                f"  live:  ...{live[max(0, i - 40):i + 60]!r}\n"
                f"  built: ...{built[max(0, i - 40):i + 60]!r}"
            )

    if failures:
        print(f"Equality check FAILED ({len(failures)} page(s) differ from {args.base}):")
        for f in failures:
            print(f"- {f}")
        return 1
    print(f"Equality check passed: {len(PAGES)} page(s) match live baseline {args.base} "
          f"(ignoring whitespace and ?v= values).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
