# Murati Systems: Design und wiederverwendbare Prüfroutine

Stand: 25.09.2026. Maßgeblich bleiben `handoff.md` und `business-context.md` im übergeordneten Projektordner.

## Aktueller Stand ab 25.09.2026: Lux-Richtung

Arbeitsweise und dauerhafte Regeln des Inhabers stehen im Skill `lux` (`/home/hermes/Murati-Systems/.agents/skills/lux/SKILL.md`): keine Nummerierung als Gestaltungsmittel, keine leeren oder generischen Abschnitte, lebendig ohne Video, mobil zuerst, WhatsApp grün mit Symbol, keine Ortslabels als Deko. Seiten werden einzeln überarbeitet, zuerst die Startseite.

Richtung: warmes Papierweiß und tiefes Graphit im Wechsel, Orange als Licht und Handlungsfarbe, große, eng gesetzte Schibsted Grotesk. Bilder sind echte Projekt-Screenshots in Geräterahmen, echte Fotos und im Code gebaute UI-Szenen, die zeigen, was die Leistung tut. Bewegung: wechselndes Wort im Hero, Check-Karte baut sich auf, Laufband, Einblenden beim Scrollen; bei reduzierter Bewegung ruhig.

| Rolle | CSS-Variable | Wert |
| --- | --- | --- |
| Papier (Seitenhintergrund) | `--bg` | `#fafaf7` |
| Stein (Wechselflächen) | `--stone` | `#f1f0ec` |
| Graphit (dunkle Bühnen, Footer) | `--graphite` | `#111111` |
| Text | `--text` | `#242424` |
| Signal-Orange (Aktionen, Licht) | `--signal` | `#ec4e14`, Text darauf `--signal-ink` `#141414` |
| Orange als Schrift auf Weiß | `--signal-deep` | `#b93a0a` |
| WhatsApp | `--wa`, `--wa-ink` | `#25d366`, Text `#07301a` |

Bausteine der Startseite (CSS ab `/* Startseite */`): `hero` mit `rotator` und `url-form` (GET an `website-check.html`, `assets/main.js` übernimmt die Adresse), `scan`-Karte, `marquee`, `problem` mit `device-phone` und `flag`, `bento` mit `tile`-Szenen (am Handy als Wisch-Karussell), `stage` mit `devices` (Laptop und Handy), `path` für Abläufe ohne Nummern, `id-card`, `faq-teaser`, `finale`. Globale Bausteine: `button wa` und `wa-i` (WhatsApp-Symbol als CSS-Maske), dunkler Footer, Cookie-Dialog mit Status-Badges, `reveal` für Einblenden per `animation-timeline: view()`.

Offen: Die Lighthouse-Angabe in der `id-card` nach jeder größeren Änderung neu messen. Die Angaben zur Person („Wer dahintersteckt“) stammen aus dem Lebenslauf vom März 2025 und sind vom Inhaber zu bestätigen.

### Alle Seiten im Lux-Stil (25.09.2026, Branch `design/alle-seiten`, Design-Chat)
- **Farbeinsatz:** Orange nur für die Hauptaktion und kleine Akzente. Abschlussflächen (`.finale`), die Kopf-Aktion (`.header-cta`) und die mobile Aktionsleiste sind dunkel. WhatsApp-Grün steht nie als gleich große Fläche neben Orange. Lichtscheine nutzen `color-mix(in srgb, var(--signal) …, transparent)`, ein Akzentwechsel braucht deshalb nur die `--signal*`-Variablen. Farbrichtung A „Orange leiser“ ist gewählt (Inhaber, 25.09.2026); B (Signalgelb) und C (dunkler Einstieg) liegen nur noch als Overlays in `design/varianten/`.
- **Logo:** Variante 3 „kompakt“ (Inhaber, 25.09.2026): M-Zeichen plus „Murati“ in einer Zeile, ab 700 px „Systems“ in gleicher Größe und `--muted` daneben; am Handy nur Zeichen und „Murati“, der volle Name steht im `aria-label`. Vorher stand „Murati“ über einem gesperrten „SYSTEMS“ in 9 px.
- **Navigation:** `.jump` ist eine feste Themenleiste mit allen Punkten auf 390 px; `main.js` markiert den sichtbaren Abschnitt (`aria-current`). `.mobile-contact` ist eine dunkle Schwebeleiste (WhatsApp schmal und grün, Website-Check hell) und fehlt auf Check- und Danke-Seite; dort fehlt auch die Kopf-Aktion zum Check.
- **Bausteine:** `.price-sheet` (Preisübersicht im Hero), `.offer` mit `.alt`, `.dark`, `.flip` und `.offer-art`-Szenen (`art-devices` mit Kundenprojekt, `art-inbox` mit `.mail` nach der echten Eingangsbestätigung, `art-report` mit `.report`, `art-ki` mit `.approve`), `.plans`/`.plan`/`.ticks`, `.steps`, `.inbox` (vorsortierter Posteingang), Kachelszenen `art-sort`, `art-voice`, `art-sync`, `.rules` (Grenzen), `.it-card`, `.tracker-list`, `.needs`, `.finding`, `.before-after` mit `.new-site`, `.promise-grid`, `.ways`, `.gets`, `.branch-phone`, `.project-mini`. Jede Unterseite endet mit `.finale` (Adressfeld oder Nachricht, darunter WhatsApp).
- **Beispiele:** Jede Szene trägt „Beispiel“ oder zeigt echte Arbeit (Dautibau, ESD Bau nur mit Status). Materialliste auf Arbeitsweise stammt aus `murati-projekt/references/vorlagen.md`.
- **Porträt:** `.id-photo` oben in der Visitenkarte `.id-card` auf Startseite und Kontakt, quadratisch, unten weich in Graphit ausgeblendet (`assets/endrit-murati-480.webp`, `-800.webp`). KI-Porträt aus Fotos des Inhabers, von ihm am 25.09.2026 ausgewählt; Originale und Profilbilder privat in `brand/profilbild/`, nicht im Repository.
- **Gelöscht statt gestapelt:** `.callout`, `.price-grid`/`.price-card`, `.timeline`, `.flow`, `.contact-card`, `.project-photo` und weitere ungenutzte Regeln.

## Historisch: neutrale Gestaltung und Datenschutzprüfung

Auch die warme Farbpalette wurde vom Inhaber verworfen. Die aktive Gestaltung ist nun weiß, hellgrau und anthrazit, ohne farbige Akzente; Überschriften verwenden die vorhandene Sans-Schrift statt Georgia. Farbwerte ausschließlich aus der aktuellen CSS-Datei übernehmen. Alle neun Seiten haben einen erreichbaren Cookie-Informationsdialog, der keine Auswahl speichert. Es sind keine optionalen Dienste aktiv. Die rechtliche Prüfung und noch offene Betreiberangaben stehen in LEGAL-REVIEW.md. Datenschutzerklärung und Impressum sind ausdrücklich Entwürfe, keine Veröffentlichungsfreigabe.

Prüfungen zusätzlich: `node tests/check_privacy.cjs`; Browser mit deaktiviertem JavaScript (E-Mail-Fallback, Cookie-Link auf Datenschutz), Dialog öffnen/schließen/Escape/Fokusrückgabe. Die schärfere CSP im Deployment-Template ist nur vorbereitet, nicht produktiv aktiviert.

## Historisch: Korrektur nach Nutzerfeedback

Der Inhaber bewertete den Kobalt-Entwurf mit 10/100 und lehnte Blau ausdrücklich ab. Außerdem wirkten die Bilder uneinheitlich groß. Die aktive Richtung ist jetzt warm und editorial: zentrierter Einstieg, Serif-Akzent, zwei kompakte Visualisierungen im gleichen Format. Keine großen abstrakten Bildflächen auf Start- oder Unterseiten.

## Ein gemeinsames Farbsystem

Papierweiß, Anthrazit und dunkles Rostrot ersetzen den verworfenen Kobalt-Entwurf. Die aktiven Regeln stehen in `assets/redesign.css`; neue Seiten verwenden diese Datei, keine zusätzlichen Farbsysteme.

| Rolle | CSS-Variable | Wert |
| --- | --- | --- |
| Hintergrund | `--bg` | `#f6f4ef` |
| Inhaltsfläche | `--surface` | `#fffdf8` |
| Text | `--text` | `#262522` |
| Sekundärtext | `--muted` | `#65615c` |
| Aktion und Akzent | `--accent` | `#763d35` |
| Helle Akzentfläche | `--accent-soft`, `--raised` | `#ece5da` |
| Trennlinie | `--line` | `#d8d0c5` |

Schibsted Grotesk wird lokal geladen. Native HTML-Elemente, CSS Grid und das vorhandene kleine JavaScript reichen für Navigation und Website-Check; dieser Durchlauf führt keine neue Abhängigkeit ein. Leistungszeilen, klare Trenner und kurze Texte halten die Seiten übersichtlich. Eine Hauptaktion pro Abschnitt; WhatsApp bleibt eine erkennbare Alternative. Fokusmarkierungen, mobile Kontaktleiste und reduzierte Bewegung gehören zum gemeinsamen Muster.

Die Galerie unter `/design/` (`design/index.html`) zeigt Farben, Typografie, Aktionen, Bilder und Links zu echten Anwendungsmustern. Sie lädt dieselbe CSS-Datei wie die Website und ist keine zweite Komponentenbibliothek.

## Bilder, Zeichen und Sprache

Die beiden blauen Architektur-Bilder sind verworfene Entwurfsassets und werden nicht mehr auf den aktiven Seiten geladen. Die neue Startseite zeigt zwei gleich große, native HTML-/SVG-Muster: eine ausdrücklich beispielhafte Handwerker-Website und einen möglichen Anfrageablauf. Auf Desktop sind beide Ansichten 280 Pixel hoch, mobil 220 Pixel. Das Logo ist monochrom. Die Unterseiten verwenden kompakte Textköpfe ohne Dekobild. Ein lokaler Georgia-Serif-Fallback ergänzt die vorhandene Schibsted-Schrift; keine externen Schriften.

Der Humanizer-Skill wurde auf die sichtbaren Texte der vier Unterseiten angewendet: Wiederholungen streichen, konkrete Tätigkeiten nennen, keine neuen Leistungsversprechen ergänzen. Wortzählung innerhalb von `<main>` nach dieser Copy-Runde:

| Seite | Vorher | Nachher |
| --- | ---: | ---: |
| KI und IT | 409 | 264 |
| Leistungen | 277 | 214 |
| Arbeitsweise | 116 | 108 |
| Kontakt | 63 | 51 |

Freigegebene Preise, bestehende Kontaktziele, Paketgrenzen, die Kennzeichnung fiktiver Beispiele und die KI-Sicherheitsgrenzen blieben erhalten. Der Website-Check erstellt ausschließlich einen `mailto:`-Entwurf. Er sendet und speichert keine Anfrage und ist kein CRM.

## Drei Durchläufe für künftige Änderungen

1. **Recherche und Fakten:** Handoff, Zielgruppe, bestätigte Angebote und reale Kontaktwege lesen. Referenzen auf Komposition und Nutzeraufgabe prüfen. Fakten, Annahmen und offene Punkte getrennt festhalten; keine Referenzen oder Ergebnisse erfinden.
2. **Ein visueller Entwurf:** Ein Farbsystem, eine Typografie und eine passende Bildsprache auf Startseite, Unterseite und Formular anwenden. Vorhandene HTML-/CSS-Muster wiederverwenden. Neue Muster zuerst in der Galerie zeigen; Texte auf konkrete Kundenaufgaben kürzen.
3. **Gerenderte Kritik und Korrektur:** Die tatsächlichen Seiten bei 375, 768 und 1440 Pixeln Breite ansehen. Hierarchie, Umbrüche, Überläufe, Bildausschnitte und Kontrast prüfen. Navigation und Formular mit Tastatur bedienen; Fokus, Fehlermeldungen, Zurück/Weiter und den ehrlichen E-Mail-Entwurf kontrollieren. Datenschutzverhalten und `noindex` prüfen. Befunde nach Wirkung priorisieren, korrigieren und betroffene Ansichten erneut ansehen.

Die Trennung von Recherche, Entwurf und belegter Prüfung übernimmt die Disziplin der Lux-Arbeitsweise. In dieser Runde wird die Lux-Pipeline nicht aufgerufen; daraus folgt auch kein grüner Lux-Lauf. [21st.dev](https://21st.dev/) dient als Sammlung von Layout- und Aktionsmustern. [Impeccable critique](https://impeccable.style/docs/critique/) liefert Anregungen für eine priorisierte Designkritik. Beides sind hier Recherchequellen, keine installierten oder ausgeführten Werkzeuge. Der genannte „Simple-Skill“ wurde nicht eindeutig identifiziert; „Unpackable“ wurde als vermutlich gemeintes Impeccable eingeordnet, nicht als ausgeführter Skill ausgegeben.

Aus `website/` ausführen:

```sh
python3 tests/check_site.py
git diff --check
```

Der statische Check prüft Vorschauseiten, lokale Link-/Assetziele, `noindex`, eine Hauptüberschrift, lokale Skripte und Fonts, Preise sowie parsebares JSON-LD. Er ersetzt weder Browserprüfung noch Rechtsprüfung. Für jeden Durchlauf geprüfte Seiten und Breiten, konkrete Befunde und verbleibende Grenzen im Handoff festhalten.

## Datenschutz, Suchmaschinen und Veröffentlichung

Die aktive Vorschau bindet keine Tracking-Skripte ein und setzt keinen Cookie-Banner ein. Das Formular nutzt keinen dauerhaften Browserspeicher. Werden später Cookies, andere Speicherzugriffe, Analytics oder Einbettungen ergänzt, muss deren Zweck vor Einbau neu geprüft werden. [§ 25 TDDDG](https://www.gesetze-im-internet.de/ttdsg/__25.html) verlangt grundsätzlich Einwilligung für Speicherung oder Zugriff auf Endgeräte; die gesetzlichen Ausnahmen sind zweckgebunden. Produktionshosting und seine tatsächlichen Datenflüsse sind damit noch nicht geprüft.

Für lokale Auffindbarkeit und GEO stehen verständliche Leistungsseiten, Dortmund/Ruhrgebiet und überprüfbare Unternehmensangaben im Vordergrund. Die [Google-Hinweise zu generativer Suche](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) stützen klare technische Strukturen und hilfreiche Inhalte; spezielle KI-Dateien und Sonder-Markup sind dafür nicht erforderlich. Es wird kein Ranking versprochen.

Organization-JSON-LD auf der Startseite sowie Textmetadaten zum Teilen sind vorbereitet. Die Vorschau bleibt absichtlich `noindex`. Die Open-Graph-Bildverweise des verworfenen Entwurfs wurden entfernt. Vor Veröffentlichung müssen Hosting, rechtliche Angaben und tatsächliche Kontaktziele bestätigt und die Produktionsmetadaten geprüft werden. Veröffentlichung und Entfernen von `noindex` sind ein eigener Schritt.
