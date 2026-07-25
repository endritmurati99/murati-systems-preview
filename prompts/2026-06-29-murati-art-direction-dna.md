# Murati Systems — Art-Direction DNA (Sādhanā-structured)

Generation prompt **and** scoring rubric. Modeled on the owner-supplied Sādhanā Studio prompt
structure, translated to Murati's dark/orbital IT-systems brand. Honest content only — no fake
logos/metrics.

## Design intent
Design a founder-led technical systems studio landing — the antidote to the generic "AI agency"
page. It must make a visitor *believe Endrit can actually build real systems fast* (websites,
internal tools, workflow automation, AI-native software), not just claim it. Cinematic + engineered,
quiet confidence, proof by experience in the first viewport.

## Overall Vibe
Engineered, quiet, precise, credible — proof over hype. Confident, not loud.

## Visual Strategy
- **Imagery/Render:** no stock photos. A custom WebGL/canvas **orbital core** as the hero system
  signal — concentric orbital rings + drifting particles + a luminous core. Reads as a precise
  engineered system, not decorative blobs.
- **Texture:** fine SVG grain/noise overlay (~0.02 opacity) over the dark base for filmic depth.
- **Composition:** open negative space, editorial asymmetry, one idea per scroll viewport, strong
  above-the-fold impact. Mobile stays dramatic without text overlap.

## Color Palette (named scale — design harmony, don't improvise)
- **Base:** `void #07090C` → `graphite #0E1217` → `panel #161B22` (never flat pure black everywhere).
- **Foreground:** `white #F4F7FA`, `steel #8A97A6` (muted body), `dim #5A6573` (captions/labels).
- **Cool accent (signal):** restrained cyan `#5BD0D6` — for system cues, links, focus, the orbital.
- **Warm accent (ember, CTA only):** muted amber/coral `#E8915B` — carries the primary CTA, used sparingly.
- **Avoid:** purple-blue AI gradients as identity, neon, beige, decorative blobs, stock AI glow.

## Typography
- **Headings:** confident grotesk (Space Grotesk / General Sans / Satoshi), large + tight tracking,
  light-to-medium weight. Cinematic hero line.
- **Body:** Inter, airy line-height, restrained sizes in panels/service blocks.
- **Mono accent:** JetBrains Mono / Geist Mono — ONLY for proof chips, system labels, logs, metrics.
- **Layout:** generous margins (py-24/32), clear hierarchy, no nested cards.

## Page Structure (one idea per viewport)
1. **Hero** — wordmark + compact nav + ONE primary CTA; cinematic hero line + short subline; the
   orbital-core system signal centered/offset. Murati visible as trust anchor.
2. **Leistungen / Outcomes** — websites, automation, internal tools, AI workflow — framed as
   outcomes, not feature boxes.
3. **Beispiel-Setups** — honest project-type cards (no invented customers/logos).
4. **Ablauf / Review-Einstieg** — what happens after the click, step by step.
5. **Wofür wir stehen** — operating principles.
6. **Wer wir sind** — team-credible, Murati as anchor without solo-founder weakness.
7. **Kontakt** — serious, singular CTA (project inquiry); WhatsApp/email.
8. **Footer + Impressum/Datenschutz.**

## Interaction Details (the lever — concrete + timed, reduced-motion friendly)
- **Orbital core:** rings rotate slowly (40–60s/rev), core **pulse on a 4s cycle**, particles drift;
  cursor-reactive parallax glow (subtle).
- **Scroll reveal:** fade + translate-up, staggered, ~600ms ease — slow, never busy.
- **Typing reveal:** a mono "system line" (e.g. status/log/`> building…`) types out character-by-
  character when the hero/proof block enters view (parallels Sādhanā's typed teacher quotes).
- **ONE real interactive component:** a "Was wir bauen / Ablauf" explorer — tabs
  (Website / Automatisierung / Interne Tools / AI-Agenten) with expandable detail rows driven by a
  real JS data model (like Sādhanā's schedule), each showing a concrete outcome + honest example.
- **Nav:** transparent over hero → graphite blur + border on scroll.
- **Soul details:** custom scrollbar, `::selection` in signal cyan, visible focus rings, a tasteful
  toast on contact submit, proof chips in mono with a faint pulse.
- **Motion law:** slow + intentional; full `prefers-reduced-motion` fallback; no scroll-jacking.

## Verdict from rendering the Sādhanā reference (2026-06-29, viewed live)
What is the bar (keep): typographic hierarchy + serif/sans pairing reads genuinely premium;
2×2 practice cards with gradient overlays + tiny uppercase labels = editorial; disciplined warm
palette (one terracotta accent everywhere); the schedule (tabs + availability dots + rows) and the
free-class form are clean, real, conversion-grade.
What "könnte besser sein" (avoid for Murati):
1. **Placeholder imagery breaks the concept** — picsum random seeds rendered the "morning-light"
   hero as an electronics teardown and "teacher" portraits as a car interior / a rock. At this craft
   level curated real imagery carries the mood; random placeholders collapse it. (Murati's canvas
   orbital avoids stock dependency — good — but any photo must be deliberate.)
2. **Hero text contrast is marginal** over a busy image — subline washes out. → Murati: guarantee
   hero-copy contrast over the orbital canvas (scrim/vignette or text plate).
3. **Scroll-reveal with no fallback** — everything below fold is opacity:0 until IntersectionObserver
   fires; no-JS / reduced-motion / print / crawlers see blank. → Murati reveals MUST degrade visible.
4. **Toast fires unprompted** (a "welcome/sound" toast appears without user action) — intrusive. →
   Murati toasts only on real user action (e.g. contact submit).

## Craft Rubric (score each before "done")
- [ ] First viewport reads as a custom system visual, not a template; Murati present.
- [ ] Type pairing intentional (grotesk display + Inter body + mono accent), light large headlines.
- [ ] Named color scale applied; harmony explicitly good; one cool + one warm accent, no AI-slop.
- [ ] Motion reinforces "orbital/precision", slow, reduced-motion safe.
- [ ] At least one real interactive component, not static cards.
- [ ] Soul details present (grain, scrollbar, ::selection, focus, toast).
- [ ] Content honest (no fake logos/metrics); outcomes not feature boxes.
- [ ] Desktop + 390px mobile: no overflow, no overlap, no console errors.
- [ ] Production build: Tailwind compiled (no CDN), real assets, Next.js-portable.
