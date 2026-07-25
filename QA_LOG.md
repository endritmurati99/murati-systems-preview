# QA Log — Murati Systems

## 2026-06-27 Gate 1 Directions
- Chrome/CDP prepared with `bash /data/.openclaw/scripts/chrome-up.sh lux`.
- Claude Design attempted but blocked by weekly quota reset. Fallback path used.
- Generated three single-file Tailwind directions in `out/`.
- Served previews on tailnet ports `8801`, `8802`, `8803`.
- Verified all three with Playwright desktop/mobile checks:
  - no console errors
  - no horizontal overflow at 1280 or 390
  - no broken in-page anchors
  - no failing axe subset violations

## 2026-06-27 Direction 2 Refinement
- User selected direction 2 (`Orbital Core`).
- Refined the selected direction based on feedback: removed internal notes/stats, strengthened brand mark, centered hero in the orbital core, added WhatsApp CTA without green styling, and expanded the landing-page content.
- Final preview served at `http://100.88.90.70:8801`.
- Verification:
  - `node /data/lux-engine/scripts/playwright-check.mjs http://127.0.0.1:8801 /data/lux-webflow/projects/murati-systems/reports/final-check-refined-copy`
  - Result: green, no console errors, no horizontal overflow, no broken anchors, no failing axe subset violations.

## 2026-06-27 Content Pass 1
- Submitted the current Orbital Core state and latest owner feedback into the existing ChatGPT project `Murati Digital` through Lux Chrome/CDP.
- Applied the strongest content direction:
  - hero changed to `Mehr als eine Website. Ein digitales System.`
  - removed the four generic hero chips (`Core Web Presence`, `Flow Automation`, `Internal Tools`, `AI Agents`)
  - replaced `Signal ansehen` and the `Signal` section with a concrete `Angebot / Was entsteht` section
  - strengthened CTA language to `Projekt besprechen`, `Was wir bauen`, `WhatsApp: Projekt klären`
  - replaced the top-left mark with an inline orbital `M` SVG brandmark
  - added cursor-reactive glow, star drift, orbital offset, and particle response
  - added placeholder `impressum.html` and `datenschutz.html` pages for the private preview only
- Verification via Playwright connected to Lux Chrome CDP `100.87.46.95:9225`, not headless:
  - desktop `1366x900` and mobile `390x844`
  - no horizontal overflow
  - old generic hero labels absent
  - primary CTA scrolls to `#kontakt`
  - cursor CSS variables update on mouse movement
  - screenshots saved under `reports/content-pass-2-*.png`
- Known remaining items:
  - Tailwind CDN warning remains because this is still a single-file prototype, not production build.
  - Real WhatsApp number is needed before wiring the CTA to `wa.me`.
  - Public domain requires complete legal owner data for Impressum and a proper Datenschutzerklaerung before launch.

## 2026-06-27 Feedback Loop 2
- Owner requested a stronger shift away from website-only positioning toward real IT/system services, stronger CTA density, more contrast below the hero, team copy instead of solo founder copy, and naming kept open.
- Opened a separate ChatGPT project chat for positioning/naming and supplied UX sources:
  - NN/g link labels and generic CTA guidance
  - NN/g readability guidance
  - W3C WCAG 1.4.3 contrast guidance
  - Baymard homepage orientation guidance
- Applied the updated direction:
  - top-left wordmark now neutral `Systems / Studio`; footer says `Systems Studio - Arbeitsname offen`
  - hero changed to `IT-Systeme, die Kunden gewinnen und Arbeit ordnen.`
  - removed visible solo-founder copy and old `Murati Systems` page copy
  - offer reframed as IT/system services: Kundenanfragen, Automatisierung, interne Systeme, Betrieb
  - lower sections redesigned with stronger contrast panels and repeated specific CTAs
  - WhatsApp language changed to `Vorhaben per WhatsApp senden` / `Vorhaben klären`
- Verification via Playwright connected to Lux Chrome CDP `100.87.46.95:9225`:
  - desktop `1366x900` and mobile `390x844`
  - no horizontal overflow
  - old solo and weak CTA terms absent
  - 10 CTA/link entry points detected
  - primary hero CTA scrolls to `#kontakt`
  - no console errors
  - screenshots saved under `reports/feedback-loop-2-*.png`

## 2026-06-27 Feedback Loop 3
- Owner wanted a more critical sales/proof pass: more calls to action, clearer examples of possible work, visible explanation of what happens after a click, and stronger statement of what the team stands for.
- Opened the ChatGPT project chat `Landingpage Verbesserung Ideen` in Lux Chrome/CDP and supplied the latest critique. The answer did not finish in the visible UI during the implementation window, so the page was updated from the prompt direction and prior UX research instead of waiting on a stalled response.
- Applied the updated direction:
  - added `Beispiel-Setups` with five honest project-type cards, explicitly avoiding invented customer references or logos
  - added a `Review-Einstieg` section explaining what happens after a click
  - added a `Wofür wir stehen` section with four operating principles
  - increased CTA entry points from 10 to 20
  - changed the hero secondary CTA to `Beispiele ansehen`
  - changed the hero eyebrow to `Digitale IT-Dienstleistungen`
  - contact card now explains what a visitor should send and uses an email fallback until the WhatsApp Business link exists
- Verification via Playwright connected to Lux Chrome CDP `100.87.46.95:9225`:
  - desktop `1366x900` and mobile `390x844`
  - no horizontal overflow
  - sections `#beispiele`, `#review`, `#prinzipien`, `#wir`, `#kontakt` present
  - five example cards detected
  - 20 CTA/link entry points detected
  - `#beispiele` and `#review` anchor navigation works
  - no console errors
  - screenshots saved under `reports/feedback-loop-3-desktop.png` and `reports/feedback-loop-3-mobile.png`
