# Murati Systems: Design und wiederverwendbare Prüfroutine

Stand: 24.09.2026. Arbeitsstand der unveröffentlichten Vorschau. Maßgeblich bleiben `handoff.md` und `business-context.md` im übergeordneten Projektordner.

## Ein gemeinsames Farbsystem

Porzellan, Graphit und Kobalt ersetzen die frühere Mischung aus Petrol, Salbei und Kupfer. Die aktiven Regeln stehen in `assets/redesign.css`; neue Seiten verwenden diese Datei, keine zusätzlichen Farbsysteme.

| Rolle | CSS-Variable | Wert |
| --- | --- | --- |
| Hintergrund | `--bg` | `#f7f8fa` |
| Inhaltsfläche | `--surface` | `#ffffff` |
| Text | `--text` | `#20242c` |
| Sekundärtext | `--muted` | `#576171` |
| Aktion und Akzent | `--accent` | `#284be8` |
| Helle Akzentfläche | `--accent-soft`, `--raised` | `#e9edff` |
| Trennlinie | `--line` | `#dce0e8` |

Schibsted Grotesk wird lokal geladen. Native HTML-Elemente, CSS Grid und das vorhandene kleine JavaScript reichen für Navigation und Website-Check; dieser Durchlauf führt keine neue Abhängigkeit ein. Leistungszeilen, klare Trenner und kurze Texte halten die Seiten übersichtlich. Eine Hauptaktion pro Abschnitt; WhatsApp bleibt eine erkennbare Alternative. Fokusmarkierungen, mobile Kontaktleiste und reduzierte Bewegung gehören zum gemeinsamen Muster.

Die Galerie unter `/design/` (`design/index.html`) zeigt Farben, Typografie, Aktionen, Bilder und Links zu echten Anwendungsmustern. Sie lädt dieselbe CSS-Datei wie die Website und ist keine zweite Komponentenbibliothek.

## Bilder, Zeichen und Sprache

`assets/system-hero.webp` und `assets/system-detail.webp` wurden für diesen Entwurf generiert: abstrakte Architektur aus weißen und kobaltblauen Flächen. Das erste Bild steht neben der Startseitenüberschrift, das zweite dient als dekorativer Hintergrund auf Unterseiten. Es sind weder Kundenreferenzen noch Fotografien eines realen Betriebs. Herkunft und Verwendungszweck sind in der Galerie sichtbar dokumentiert. `assets/favicon.svg` enthält das schlichte weiße M auf Kobaltblau und wird auch als Markenzeichen in der Navigation verwendet.

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

Organization-JSON-LD auf der Startseite sowie Metadaten zum Teilen sind vorbereitet. Die Vorschau bleibt absichtlich `noindex`. Das Open-Graph-Bild verweist bereits auf die spätere Produktionsadresse; das neue Asset ist dort erst nach einem Deployment verfügbar. Vor Veröffentlichung müssen Hosting, rechtliche Angaben und tatsächliche Kontaktziele bestätigt und die Produktionsmetadaten geprüft werden. Veröffentlichung und Entfernen von `noindex` sind ein eigener Schritt.
