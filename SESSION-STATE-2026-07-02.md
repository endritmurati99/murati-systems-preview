# Murati Systems — Session-State (2026-07-02, EOD)

Resume-Punkt für die nächste (frische) Session. Kontext: Endrits Website wurde von Fable 5 Max
+ ChatGPT reviewt, dann in 3 Richtungen zum Vergleich gebaut. **Owner will sich alle 3 später
ansehen und in neuer Session entscheiden.** Nichts ist verworfen.

## Die 3 Varianten (alle live + auf Disk)
| # | Was | Live-URL | Datei |
|---|-----|----------|-------|
| 1 | **Dark** (Original "Murati Systems") | https://endritmurati99.github.io/murati-systems-preview/ | `build/index.html` |
| 2 | **Helle Landing NEU** (Lux-Favorit) | https://endritmurati99.github.io/murati-systems-preview/light/ | `build/light/index.html` |
| 3 | **Aufgehellt** (Re-Theme des Originals, Bugs gefixt) | https://endritmurati99.github.io/murati-systems-preview/hell/ | `build/hell/index.html` |

Alle drei: 0 Konsolenfehler, kein h-Overflow (1366+390), AA+-Kontrast (lokal via Playwright geprüft).
Deploy-Repo: `endritmurati99/murati-systems-preview` (gh authed im Container; Pages an).

### Variante 2 (helle Landing) — Details
Blau #2F5BEA, Space Grotesk (Display) + Plus Jakarta Sans (Body). Sektionen: Nav (mit Mobile-Burger),
Hero ("Deine Website in wenigen Tagen – schnell, günstig, sauber"), **Galerie** (Branchen-Tabs
Handwerk/Gastro/Praxis, je 3 echte CSS-Mini-Website-Previews + "Live ansehen"), "So läuft's" (3 Schritte),
Preise (ab 490 / 890 € / auf Anfrage), Kontaktformular, Footer mit echter Identität.
**Noch Platzhalter:** "Live ansehen"-Demos nicht echt klickbar; Preise = Platzhalterzahlen; Formular nicht verdrahtet.

### Variante 3 (aufgehellt) — gefixte Bugs
Footer "Arbeitsname offen"→echte Identität; aria-label & mailto "Systems Studio"→"Murati Systems";
Inter korrekt geladen + font-weight 750→700; Mobile-Burger ergänzt; :focus-visible; Automationen→Automatisierung;
Orbital/Glow auf Hell stark reduziert.

## PENDING DECISION (Owner)
Welche Richtung weiterbauen: **1 / 2 / 3**. Lux-Empfehlung = **2 (helle Landing)**, weil sie das
Haupt-Problem beider Reviews (fehlender Proof) ehrlich über die Galerie löst und zu Endrits Stand passt.

## Nächste Schritte, sobald Richtung = 2 gewählt
1. Echte, klickbare **Demo-Sites** für die Galerie bauen (Start: 3 richtig gute — Handwerk/Gastro/Praxis),
   jede als eigene responsive Seite unter `build/light/demos/<slug>/`, mit fixer CTA-Leiste zurück zum Formular.
2. Kontaktformular verdrahten (Formspree o.ä.) + E-Mail als kopierbaren Text + WhatsApp-Link (wenn vorhanden).
3. Echte **Preise** einsetzen (Owner-Zahl abwarten).
4. Firmendaten scharf schalten (siehe unten) → Impressum + Datenschutz real ausformulieren.
5. Vor echtem Launch: Tailwind kompilieren (statt Play-CDN), Fonts self-hosten.

## Firma/Recht (Owner will einleiten)
0. Aufenthaltstitel-Check: erlaubt er "selbstständige Tätigkeit"? (falls kein EU-Pass) — einziges echtes Nadelöhr.
1. Gewerbeanmeldung Dortmund (dortmund.de, ~26 €, oft same-day) → als Einzelunternehmer, "Murati Systems" = Geschäftsbezeichnung.
2. Fragebogen steuerl. Erfassung via ELSTER → Kleinunternehmer §19 UStG (bis 25.000 €). Steuernummer 1–4 Wo (blockt Launch nicht).
3. WhatsApp Business + kontakt@murati.systems scharf schalten.
→ Danach Impressum trivial: Name, Anschrift Dortmund, Mail, "Kleinunternehmer gem. §19 UStG". Lux schreibt Impressum+Datenschutz, sobald Daten da.

## Reviews (Detail siehe Claude-memory murati-systems-review-2026-07-02.md)
Fable 5 Max 5,7/10 · ChatGPT 6,0/10 · beide "Launch-Readiness: nein" · Konsens #1 = fehlendes Vertrauen + Seite wirkt unfertig.
Transcripts: claude.ai/chat/a3c09d33-04cb-4811-b55e-7c6b8d301f33 · chatgpt.com/c/6a4644eb-1124-83eb-8970-17317d46dc2e

## Tooling zum Resume
chrome-up: `bash /data/.openclaw/scripts/chrome-up.sh lux` (CDP 100.87.46.95:9225, profil lux).
Render/Screenshot lokal: `node /tmp/shot2.cjs` (nutzt /data/lux-engine/node_modules/playwright, chromium --no-sandbox).
Deploy: Files nach /tmp/ms-deploy kopieren, git commit + push (repo murati-systems-preview), Pages rebaut ~1–2 Min.
