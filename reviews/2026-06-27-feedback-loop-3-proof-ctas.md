# Feedback Loop 3 — Proof, Examples, CTAs

## Owner Critique
- The page looks good, but still does not catch strongly enough.
- It needs more calls to action and more concrete example/proof views.
- Visitors should understand what the team stands for, what happens after a click, and what kind of work can be seen.
- No fake references or client logos should be invented.

## ChatGPT Project Loop
- Project: `Murati Digital`
- Chat: `Landingpage Verbesserung Ideen`
- Prompt focus:
  - honest trust/proof elements without invented references
  - example project cards
  - review/analysis CTA language
  - principles section
  - click-path microcopy
- The visible ChatGPT answer stalled at `Antwort wird fertiggestellt`, so implementation used the prompt direction plus prior CTA/readability research.

## Implemented Decisions
- Added `Beispiel-Setups` with five honest project-type cards:
  - Anfrage-System für Dienstleister
  - Interne Übersicht statt Tabellenchaos
  - Automatisierter Erstkontakt
  - Betrieb und Weiterentwicklung
  - Review: Webauftritt und Ablauf
- Added `Review-Einstieg` with three click-path steps.
- Added `Wofür wir stehen` with four principles.
- Increased action links to 20 detectable CTA entries.
- Changed hero secondary CTA to `Beispiele ansehen`.
- Contact card now explains what visitors should send and uses email as the current fallback until WhatsApp Business is ready.

## Verification
- Preview: `http://100.88.90.70:8801/?v=feedback-loop-3-final`
- Playwright via Lux Chrome CDP `100.87.46.95:9225`.
- Desktop `1366x900`, mobile `390x844`.
- No console errors.
- No horizontal overflow.
- Anchor navigation to `#beispiele` and `#review` works.
- Screenshots:
  - `reports/feedback-loop-3-desktop.png`
  - `reports/feedback-loop-3-mobile.png`

## Remaining Risk
- Real client proof still needs real projects, logos, screenshots, or permissioned references.
- WhatsApp CTA needs the final WhatsApp Business number before public launch.
- Legal pages remain placeholders and need real company/legal details before production.
