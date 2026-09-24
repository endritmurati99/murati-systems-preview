# Rechts- und Datenschutzprüfung der Website

**Stand:** 24. September 2026  
**Gegenstand:** Aktueller Vorschaupfad unter `website/`, einschließlich `design/index.html`.  
**Grenze:** Statische Code- und Dokumentensichtung plus Primärquellen. Diese Notiz ist keine Rechtsberatung und keine Freigabe zur Veröffentlichung.

## Stand gegenüber der ersten Prüfung

Die erste Fassung beschrieb inzwischen überholte Textstellen. Der aktuelle Entwurf ist klarer:

- `assets/redesign.js` und `assets/privacy.js` setzen keine Cookies, nutzen keinen Browser-Dauerspeicher und senden keine Netzwerkanfragen. Der Cookie-Dialog ist eine speicherfreie Information, kein Consent-Banner.
- Alle geprüften Kernseiten und die Designgalerie zeigen den Dialog über den Footer. Der Dialog erklärt die nicht vorhandenen optionalen Dienste; er erteilt oder speichert keine Einwilligung.
- Der Check ist bis zur JavaScript-Initialisierung verborgen; ohne JavaScript gibt es einen direkten E-Mail-Weg. Felder haben Begrenzungen; Daten gehen erst beim Absenden des Mail-Entwurfs an Murati Systems.
- Die Datenschutzerklärung kennzeichnet Hosting, Verträge, Empfänger und Löschroutine nun ausdrücklich als vor Veröffentlichung zu bestätigende Punkte. Sie trennt den Seitenaufruf vom WhatsApp-Klick und leitet keine pauschale Einwilligung aus dem Besuch ab.
- Das getrennte alte Live-Build lädt `assets/site.js` und verwendet eine Theme-Präferenz in `localStorage`. Das ist nicht Teil dieser Vorschau und benötigt, falls es weiterläuft, eine eigene Bewertung.
- `system-hero.webp`, `system-detail.webp` und `hero-workshop.webp` sind im aktuellen Root und in der Galerie nicht referenziert. Die Galerie verwendet klar bezeichnete HTML/SVG-Beispiele. Die lokale Schibsted-Grotesk-Schrift enthält eine SIL-OFL-1.1-Lizenz.

## Tatsächlicher Datenfluss im geprüften Vorschaucode

1. Seitenaufruf: lokale Assets; technisch unvermeidbare Verbindungsdaten am Webserver.
2. Cookie-Information: lokaler Dialog ohne Speicherung.
3. Website-Check: Eingaben bleiben bis zum Mail-Entwurf im Browser. Erst das Absenden im jeweiligen Mailprogramm übermittelt eine Anfrage.
4. WhatsApp: erst der Klick öffnet den externen Dienst und übermittelt technische Verbindungsdaten; erst eine Nachricht liefert Murati Systems Kontaktdaten und Inhalt.

Die geprüfte Produktionskonfiguration ist nicht die Python-Vorschau. Im Caddy-Setup ist kein HTTP-Access-Logger konfiguriert. Docker-Runtime-Logs sind größenbasiert auf höchstens drei Dateien zu jeweils 10 MB rotiert. Das beweist nicht, dass Host, Mailanbieter, Backups oder vorgeschaltete Dienste keine Protokolle führen oder keine personenbezogenen Daten verarbeiten.

## Anwendbarkeitsmatrix

| Thema | Status | Beleg im aktuellen Entwurf | Vor Veröffentlichung klären oder erledigen |
| --- | --- | --- | --- |
| § 5 DDG | **Teilweise umgesetzt** | Impressum enthält Name, Anschrift, Telefon, E-Mail und Kleinunternehmerhinweis. | Name, ladungsfähige Anschrift, laufend gelesene E-Mail und Telefon bestätigen. USt-IdNr./W-IdNr. nur ergänzen, wenn vorhanden; Register-, Zulassungs- und Berufsangaben nur falls einschlägig. |
| DL-InfoV § 2 | **Bedingt** | Dienstleistungsangebot und Kontakt sind sichtbar. | Die DL-InfoV verlangt bestimmte Angaben vor Vertrag bzw. Leistung. Sie schafft keine pauschale Pflicht zu AGB. Vor Angebot/Vertrag wesentliche Leistung, Preis/Preisbildung, etwaige Rechtswahl/Gerichtsstand, Garantien und vorhandene Berufshaftpflicht offenlegen. |
| MStV § 18 | **Derzeit nur Grundangaben relevant** | Kein journalistisch-redaktioneller News-/Ratgeberbereich geprüft. | Bei journalistisch-redaktionellem Angebot Verantwortlichen mit Name und Anschrift ergänzen. |
| VSBG §§ 36/37 | **Hinweis vorhanden, Voraussetzungen offen** | Impressum erklärt Nichtteilnahme/-pflicht. | Beschäftigtenzahl am 31.12. des Vorjahres, freiwillige Teilnahme und etwaige branchenspezifische Pflicht bestätigen. Nach einer nicht beigelegten Verbraucherstreitigkeit gilt § 37 als Einzelfallpflicht in Textform. |
| EU-OS/ODR | **Korrekt nicht genannt** | Kein Link im aktuellen Impressum. | Keinen alten Plattformlink oder Mustertext übernehmen. Die ODR-Plattform ist seit 20. Juli 2025 eingestellt. |
| Art. 13 DSGVO | **Inhaltlich verbessert, noch Entwurf** | Verantwortlicher, Zwecke, Rechtsgrundlagen, Rechte, Warnung für sensible Daten und Entwurfsvorbehalte sind vorhanden; Datenschutzlink liegt am Check. | Endfassung muss tatsächliche Empfänger, Transfers, Speicherfristen/Kriterien und den realen Mail-/Hostingbetrieb konkretisieren. |
| Art. 6, 28, 32, 44 DSGVO | **Offen, tatsächliche Dienstleister entscheiden** | WhatsApp-Klick und eigene Anfragebearbeitung sind getrennt erklärt. | Für Hosting, E-Mail, Backups und ggf. CRM Vertragspartner, Rollen, AVV, Unterauftragnehmer, Zugriffsschutz, Löschung und Drittlandtransfer prüfen. Keine unbewiesene Region-, Anbieter- oder „keine Logs“-Aussage veröffentlichen. |
| Art. 30, 33, 35, 37 DSGVO | **Organisationspflichten bedingt** | Keine Belege für Verzeichnis, Vorfallprozess, DPIA oder Datenschutzbeauftragten geprüft. | VVT nach Art. 30 anhand der realen Vorgänge bewerten; die Ausnahme unter 250 Personen gilt nicht pauschal, etwa bei nicht nur gelegentlicher Verarbeitung. Vorfallprozess für Art. 33 einrichten. DPIA nur bei voraussichtlich hohem Risiko; DSB nur bei den Voraussetzungen aus Art. 37, nicht automatisch für jedes kleine Unternehmen. |
| § 25 TDDDG | **Kein Consent erforderlich, solange der Stand bleibt** | Kein Cookie, keine aktive local-/sessionStorage-Nutzung, keine Analyse, keine externen Einbettungen; speicherfreier Informationsdialog. | Keine künstlichen Tracker/Banner hinzufügen. Bei Analytics, CRM-Widget, Maps, Videos, A/B-Test oder optionalem Speicher zuerst Zweck- und Dienstinventar; nicht notwendige Zugriffe erst nach Einwilligung laden und echte Einstellungen/Widerruf anbieten. |
| Preise, PAngV | **Bedingt** | „ab“-Preise, monatliche Betreuungspreise und § 19-UStG-Hinweis sind sichtbar. | B2B-Ausrichtung und echte Vertragspraxis festlegen. Werden Verbraucher adressiert, Gesamtpreis, Leistungseinheit, variable Zusatzkosten, Laufzeit und Kündigung klar ausweisen. „ab“ darf keinen Festpreis vortäuschen. |
| Fernabsatz, Widerruf, § 356a BGB | **Derzeit nicht als Online-Vertragsschluss umgesetzt** | Kein Checkout/Bestellbutton; Check und CTAs führen zu E-Mail/Gespräch. | Bei einem online abschließbaren Verbrauchervertrag Art. 246a EGBGB, §§ 312c, 312d, 312g und gegebenenfalls § 356a BGB einschließlich Widerrufsfunktion prüfen. |
| Betreuung als Dauerschuldverhältnis, § 312k BGB | **Derzeit nicht ausgelöst** | Betreuung ist preislich beschrieben, aber nicht online abschließbar. | Werden Verbraucherverträge über laufende Betreuung auf der Website elektronisch abgeschlossen, ist die Kündigungsschaltfläche nach § 312k zu prüfen. |
| BFSG/BFSGV | **Bedingt** | Skip-Link, semantische Formulare, Fehlerrückmeldungen, No-JS-Weg und Dialog sind angelegt. | Ohne online abschließbaren Verbrauchervertrag liegt kein geprüfter elektronischer Geschäftsverkehr im BFSG-Sinn vor. Bei späterer Anwendbarkeit § 3 Abs. 3 BFSG und Kleinstunternehmensstatus verifizieren; trotzdem Tastatur, Kontrast, Mobil und Formulare vor Launch testen. |
| Verträge, AGB, IP, AVV und Datenarten | **Vertragliche Grundlage offen** | Website verspricht keine automatisierte Patientendatenverarbeitung; Check warnt davor. | Keine blanket AGB-Pflicht ableiten. Für jedes Projekt aber Angebot/Vertrag mit Leistungsumfang, Abnahme, Vergütung, Änderungen, Rechten am Ergebnis, Kundenzulieferungen, Laufzeit/Kündigung, Support und Haftungsrahmen verwenden. Bei Verarbeitung im Auftrag des Kunden AVV und klare Grenzen zu Gesundheits-/Patientendaten und Zugangsdaten vereinbaren; keine solchen Daten über Check/WhatsApp anfordern. |
| Bilder, Schrift und KI | **Aktiver Stand unkritischer, Rechte bleiben Nachweispflicht** | Neue Rasterbilder werden nicht geladen; Galerie markiert Beispiele; lokale Schriftlizenz liegt bei. | Bei späterer Wiederverwendung von Bilddateien Quelle, Nutzungsrecht, Erstellungsweg und Freigabe privat dokumentieren. Keine Beispielgrafik als Kundenreferenz ausgeben. KI-Transparenz ist nicht pauschal für jedes stilisierte Bild abzuleiten; Deepfakes und KI-Text für öffentliche Angelegenheiten sind gesondert zu prüfen. |

## Launch-Blocker

1. **Anbieterangaben bestätigen:** E-Mail, Anschrift, Telefon, Kleinunternehmerstatus, USt-IdNr./W-IdNr., Beschäftigtenzahl und Schlichtungslage.
2. **Betrieb dokumentieren:** Produktionshost, Vertragspartner, AVV, Unterauftragnehmer, Mailrouting, Backups, Log-/Löschkonzept, Zugriffsrollen und Drittlandtransfers. Erst dann die Datenschutz-Vorschau in eine Endfassung überführen.
3. **Verbraucherpfad entscheiden:** Reine individuelle Angebotsphase beibehalten oder vollständigen B2C-Onlinevertrag mit Preis-, Widerrufs-, Kündigungs- und Bestellpflichten bauen.
4. **Vertragspaket festlegen:** Angebots-/Vertragsmuster, Abnahme, Nutzungsrechte, Support, Datenverarbeitung und Ausschluss sensibler Daten für das tatsächliche Leistungsmodell prüfen.
5. **Assetprovenienz fortführen:** Bei jedem später aktiv eingebundenen Bild die kommerzielle Nutzung und Kennzeichnung als Symbol-/Beispielbild dokumentieren.

## Inhaberfragen

1. Welche E-Mail-Adresse ist technisch eingerichtet und wird täglich bearbeitet: `info@`, `kontakt@` oder eine andere?
2. Ist die Anschrift veröffentlichbar und ladungsfähig? Gibt es USt-IdNr. oder W-IdNr.?
3. Werden ausschließlich Unternehmer beauftragt, oder können Verbraucher Leistungen erhalten und online abschließen?
4. Welche Betreuungspakete sind Laufzeitprodukte, wie wird gekündigt und soll irgendein Vertrag online geschlossen werden?
5. Welche Dienstleister verarbeiten tatsächlich Hosting-, E-Mail-, Backup-, Monitoring- und Logdaten; mit welchen Regionen, AVVs und Unterauftragnehmern?
6. Besteht eine Berufshaftpflichtversicherung? Wenn ja, welche Angaben sind nach DL-InfoV vor Vertrag bereitzustellen?
7. Wird WhatsApp Business genutzt, wer hat Zugriff und welcher reale Daten-/Transferweg gilt?
8. Gibt es künftig CRM, Kalender, Newsletter, Maps, Video, Chat, Analytics oder Zahlungen? Jeder dieser Dienste erfordert vor Einbindung eine neue Prüfung.
9. Werden bei Kundenprojekten personenbezogene Daten, insbesondere Gesundheits-/Patientendaten, verarbeitet? Falls ja: erst Prozess, AVV, TOMs, Berechtigungen und Trennung festlegen.

## Primärquellen, geprüft am 24. September 2026

- [§ 5 DDG](https://www.gesetze-im-internet.de/ddg/__5.html)
- [§ 2 DL-InfoV](https://www.gesetze-im-internet.de/dlinfov/__2.html)
- [§§ 36 und 37 VSBG](https://www.gesetze-im-internet.de/vsbg/BJNR025410016.html)
- [EU-Verordnung 2024/3228 zur ODR-Plattform](https://eur-lex.europa.eu/eli/reg/2024/3228/oj/eng?eliuri=eli%3Areg%3A2024%3A3228%3Aoj&locale=de)
- [DSGVO, Verordnung EU 2016/679](https://eur-lex.europa.eu/legal-content/DE/ALL/?tid=311189809&uri=celex%3A32016R0679)
- [§ 25 TDDDG](https://www.gesetze-im-internet.de/ttdsg/__25.html)
- [§ 3 PAngV](https://www.gesetze-im-internet.de/pangv_2022/__3.html)
- [§§ 312c und 312g BGB](https://www.gesetze-im-internet.de/bgb/BJNR001950896.html)
- [§ 312k BGB](https://www.gesetze-im-internet.de/bgb/__312k.html)
- [§ 356a BGB](https://www.gesetze-im-internet.de/bgb/BJNR001950896.html)
- [Art. 246a § 1 EGBGB](https://www.gesetze-im-internet.de/bgbeg/art_246a__1.html)
- [§ 2 BFSG](https://www.gesetze-im-internet.de/bfsg/__2.html)
- [§ 3 Abs. 3 BFSG](https://www.gesetze-im-internet.de/bfsg/__3.html)
- [§ 19 BFSGV](https://www.gesetze-im-internet.de/bfsgv/__19.html)
- [§ 18 MStV](https://www.die-medienanstalten.de/fileadmin/user_upload/Rechtsgrundlagen/Gesetze_Staatsvertraege/Medienstaatsvertrag_MStV.pdf)
- [UrhG, insbesondere §§ 31 und 72](https://www.gesetze-im-internet.de/urhg/BJNR012730965.html)
- [EU-Verordnung 2024/1689, KI-Transparenz](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/ita)
