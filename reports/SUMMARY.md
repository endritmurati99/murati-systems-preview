# Murati Systems — Gate 1 Summary

## Current State
- Run ID: `run-1782558154740275835`
- Status: Gate 1 picked, direction 2 refined
- Claude Design status: quota-blocked, so this run used the manual Lux fallback path.
- Final preview: `http://100.88.90.70:8801`

## Directions
1. Founder Systems — `http://100.88.90.70:8801`
   - Founder-led, precise, technical systems-studio direction.
2. Orbital Core — `http://100.88.90.70:8802`
   - Cinematic black-space/system-core direction based on the user's visual reference DNA.
3. Operator Console — `http://100.88.90.70:8803`
   - Practical IT partner direction with dashboard/workflow surfaces.

## Verification
- `node /data/lux-engine/scripts/playwright-check.mjs http://127.0.0.1:8801 /data/lux-webflow/projects/murati-systems/reports/check-01` — green
- `node /data/lux-engine/scripts/playwright-check.mjs http://127.0.0.1:8802 /data/lux-webflow/projects/murati-systems/reports/check-02` — green
- `node /data/lux-engine/scripts/playwright-check.mjs http://127.0.0.1:8803 /data/lux-webflow/projects/murati-systems/reports/check-03` — green
- Checks covered desktop 1280, mobile 390, console errors, horizontal overflow, broken anchors, and basic axe rules.

## Refined Direction 2
- Removed internal planning stats and diagnostics (`40-60h`, `DACH+`, progress bars, core diagnostics).
- Removed the four hero tiles.
- Re-centered the hero copy inside the orbital core.
- Added a custom orbital `M` brand mark and split `Murati / Systems` wordmark.
- Changed the primary CTA to `WhatsApp anfragen` with white/cyan/dark styling instead of WhatsApp green.
- Added stronger landing sections: Leistungen, Innovation, Wer wir sind, Ablauf, Kontakt.
- Saved GPT review prompt at `prompts/2026-06-27-gpt-content-review-refined.md`.

## Content Pass 1
- ChatGPT project `Murati Digital` is reachable through Lux Chrome/CDP and was used for the latest content review.
- Hero now leads with `Mehr als eine Website. Ein digitales System.`
- Generic chips and abstract `Signal` copy were removed.
- Replacement structure: `Was entsteht`, concrete offer rows, stronger process/contact sections, repeated CTA.
- Top-left brandmark is now an inline orbital `M` SVG instead of a simple text mark.
- Added cursor-reactive glow/particles/orbital movement in the hero.
- Added private-preview legal placeholder pages: `impressum.html`, `datenschutz.html`.
- Latest preview remains `http://100.88.90.70:8801/?v=content-pass-2`.

## Remaining Before Public Domain
- Collect real legal details for Impressum and Datenschutzerklaerung.
- Wire WhatsApp CTA to the final number.
- Move from Tailwind CDN prototype to production build before handoff.

## Feedback Loop 2
- Owner clarified that the site must sell IT/system services, not appear like a website-only offer.
- Separate ChatGPT project chat used for naming/positioning review; source prompt saved at `prompts/2026-06-27-feedback-loop-2-positioning-naming.md`.
- Page now uses neutral working identity `Systems Studio` while final naming remains open.
- Hero now reads `IT-Systeme, die Kunden gewinnen und Arbeit ordnen.`
- `Wer wir sind` is team-based and no longer names Endrit as the visible core.
- Lower sections have higher contrast, clearer service cards, and repeated WhatsApp/contact CTAs.
- Latest preview: `http://100.88.90.70:8801/?v=feedback-loop-2-final`.

## Feedback Loop 3
- Owner pushed for more proof, more calls to action, clearer examples, and a better answer to: what do we stand for, what can visitors see, and what happens after they click?
- Added an honest `Beispiel-Setups` section with five project-type cards instead of invented references or logos.
- Added `Review-Einstieg`, explaining the click path: describe the issue, review web presence/process/system need, receive a start direction.
- Added `Wofür wir stehen` with four principles: system before single page, clarity before show, visible start, operation considered from the beginning.
- CTA density increased to 20 detectable action links, including review, examples, direct inquiry, system idea, and email fallback.
- Latest preview: `http://100.88.90.70:8801/?v=feedback-loop-3-final`.
- Verification screenshots: `reports/feedback-loop-3-desktop.png`, `reports/feedback-loop-3-mobile.png`.
