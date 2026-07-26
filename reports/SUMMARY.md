# Murati Systems — Current Quality Report

## Status

- Date: 2026-07-26
- Direction: refined Orbital Core
- Branch: `codex/murati-150-anti-slop`
- Publication: preview-ready, owner gate required before production

## Quality Result

- AI-slop formula: 100/100 core
- Excellence evidence: 50/50
- Combined reference score: 150/150
- Browser gate: green on desktop and mobile
- Lux engine: 78/78 tests passed

## Material Changes

- Static, pinned Tailwind build instead of runtime Play CDN.
- Versioned CSS and JavaScript assets instead of a 941-line single-file page.
- Asymmetric hero with one primary action.
- Two intentional gradients instead of 27 decorative gradients.
- Editorial lists replace repeated service, founder, and process cards.
- Section-specific links replace nine copies of the same call to action.
- Unverified email removed; the preview now states that a verified contact route is required before launch.

## Current Owner Gates

- Confirm the final brand name.
- Choose and register a domain.
- Provide the verified contact route.
- Approve complete legal owner data and privacy text.
- Approve production publication.

## Reproduction

```bash
npm ci
npm run build
python3 -m http.server 8812 --directory build
```

Then run from the Lux engine:

```bash
node scripts/ai-slop-review.mjs \
  /home/hermes/.hermes/profiles/lux/workspace/lux-webflow/projects/murati-systems/build/index.html \
  --gate
node scripts/playwright-check.mjs \
  http://127.0.0.1:8812 \
  /tmp/murati-150-browser
```
