# Deployment muratisystems.de

Live seit 2026-09-23 auf dem Hostinger-VPS (KVM 2, Frankfurt, 76.13.154.245).

- Pfad auf dem VPS: `/srv/murati-website/` (Caddyfile, docker-compose.yml, `site/`)
- Container: `murati-website` (caddy:2-alpine), nur an die öffentliche IP gebunden, weil Port 443
  auf der Tailscale-Adresse von `tailscaled` belegt ist.
- HTTPS: Let's Encrypt, automatisch durch Caddy. Keine Zugriffsprotokolle.
- DNS (Hostinger): A `@` → 76.13.154.245 (TTL 60), CNAME `www` → muratisystems.de. Mail-Einträge unverändert.

## Build-Schritt vor jedem Release (ab 26.09.2026)

Die 14 Root-Seiten sind Quellen, kein Auslieferungsstand mehr. Header, Footer, Mobil-Menü und die
mobile Kontaktleiste stehen nur noch einmal in `tools/build.py`; jede Seite trägt lediglich
Platzhalter (`<!-- @header -->`, `<!-- @footer -->`, `<!-- @mobile-contact -->`, `<!-- @cookie-dialog -->`)
und eine Kopfzeile `<!-- @page current="…" wa="…" [prefix="/"] -->` mit den Unterschieden dieser
Seite (aktiver Navigationspunkt, vorausgefüllter WhatsApp-Text, bei `404.html` absolute Pfade).

Build und Tests in einem Schritt, immer aus `website/` (bzw. dem jeweiligen Arbeits-Worktree):

```sh
python3 tools/build.py && python3 tests/check_site.py dist && node tests/check_privacy.cjs dist
```

- `tools/build.py` rendert die 14 Seiten aus den Quellen nach `dist/` (gitignored), ersetzt
  Verweise auf `redesign.css`, `formular.css`, `main.js`, `anfrage.js`, `privacy.js` und
  `favicon.svg` durch einen 8-stelligen Inhalts-Hash (`?v=<hash>`) statt von Hand gepflegter
  Versionsnummern, und minifiziert nur die beiden CSS-Dateien (Kommentare und unwichtige
  Leerzeichen entfernt, keine Selektor-/Werte-Umschreibung). JavaScript bleibt unminifiziert nach
  `dist/` kopiert: ein Stdlib-Minifizierer ohne echten Parser kann Code nicht sicher von
  String-/Regex-Literalen unterscheiden, und ein kaputtes Formular-Skript wiegt schwerer als ein
  paar gesparte KB.
- `tests/check_site.py [verzeichnis]` und `node tests/check_privacy.cjs [verzeichnis]` laufen
  jetzt gegen ein beliebiges Verzeichnis (Default: Projektwurzel) und decken alle 14 Seiten ab,
  auch `danke.html` und `404.html`; ein fehlender `design/`-Ordner bricht nichts mehr ab.
- `tests/check_dist_equals_live.py [dist] [--base <commit>]` beweist, dass der Build inhaltlich
  ein No-op ist: jede `dist/*.html` wird normalisiert (Leerraum vereinheitlicht, `?v=…`
  ignoriert) gegen dieselbe Datei im angegebenen Live-Commit verglichen. Vor einem Release also:

```sh
python3 tools/build.py && python3 tests/check_site.py dist && node tests/check_privacy.cjs dist \
  && python3 tests/check_dist_equals_live.py dist --base <letzter-live-commit>
```

Release aus `dist/`, nicht mehr aus den Root-Dateien: vorher Backup von
`/srv/murati-website/site/` ziehen, dann

```sh
sudo rsync -a --delete dist/ /srv/murati-website/site/
```

(oder die bisherige manuelle Dateiliste aus dem Abschnitt „Redesign live seit 24.09.2026“, jetzt
aber aus `dist/` statt aus der Repo-Wurzel kopiert). `deploy/release.sh` bündelt Build, Tests und
diesen rsync-Schritt für den, der ihn von Hand auslöst; er läuft nie automatisch.

## Redesign live seit 24.09.2026

Auf Anweisung des Inhabers veröffentlicht (siehe `handoff.md`). Release = Root-`*.html` (inkl. Google-Verifizierung `googlee0ef753932ea7e7a.html`), Root-`*.txt` (`robots.txt`, IndexNow-Schlüssel), `BingSiteAuth.xml`, `sitemap.xml`, `assets/` ohne `site.css`/`site.js`/`tokens.css`; Dateien 644, Ordner 755. Backup vor jedem Release unter `/srv/murati-website-backups/`.

## Frühere Vorschau-Notiz (historisch)

Der Branch `codex/website-redesign` enthält eine neue Mehrseiten-Website und rechtliche Entwürfe. Vor jeder Veröffentlichung `../LEGAL-REVIEW.md` abarbeiten: Betreiber-/Vertragsangaben, Hosting-/Mailanbieter, Auftragsverarbeitung, Löschpraxis und B2B/Verbraucher-Vertragsweg bestätigen. Die aktuelle Live-Website verwendet Theme-localStorage; die neue Vorschau verwendet keinen dauerhaften Browserspeicher. Rechtstexte nicht ungeprüft zwischen den Ständen kopieren.

Das Caddyfile in diesem Branch ist für die neue Vorschau verschärft: keine Inline-Skripte, keine connect-/frame-/object-Zugriffe, keine Base-URL-Umschreibung. Diese Datei wurde nur mit `caddy adapt --validate` geprüft und nicht aktiviert. Die alte Live-Seite hat ein Inline-Theme-Skript; das neue Template darf nicht isoliert auf sie angewendet werden.

Für einen später freigegebenen Release müssen alle acht Hauptseiten und deren benötigte Assets gemeinsam ausgeliefert werden. `design/`, `tests/`, `deploy/`, interne Markdown-Prüfnotizen sowie die alten Prototypen `hell/` und `light/` gehören nicht in den öffentlichen Release. Die bisherige Kopieranweisung mit nur Start/Impressum/Datenschutz ist für die Mehrseiten-Version unvollständig und wurde entfernt.

Vor Umschaltung: externes Backup des bisherigen Releases, lokale Vorschautests, Cookie-/Netzwerkinventar, Legal-Freigabe und Prüfung der endgültigen Canonicals/Indexierung. Danach erst den ausdrücklich freigegebenen Stand atomar veröffentlichen und HTTPS, Header, Navigation, Formular, Rechtstexte und echte Kontaktzustellung produktiv prüfen. Ein Restart ist für reine Dateiinhalte nicht erforderlich; eine Caddy-Konfigurationsänderung ist separat kontrolliert zu aktivieren.

## Relaunch mit Formular-Backend (25.09.2026)

Zweiter Container `murati-anfrage` (python:3.13-alpine, nur internes Docker-Netz, read-only) aus `backend/anfrage.py`; Caddy leitet `/api/*` dorthin. Auf dem Server: `/srv/murati-website/backend/anfrage.py`, `anfragen/` (Eigentümer 1000, 0700) und `anfrage.env` (root, 0600, SMTP-Zugang, nie ins Repository). Nach einem Tausch des Ordners `site/` oder des Caddyfile den Caddy-Container mit `docker compose up -d --force-recreate caddy` neu erstellen, weil Bind-Mounts sonst auf die alten Dateien zeigen.

## Vorschau vor der Freigabe (ab 25.09.2026)

`sh deploy/preview.sh` kopiert den Arbeitsstand von `website/` nach `/srv/murati-website/site/vorschau/` und setzt dort auf allen Seiten `noindex, nofollow`. So kann der Inhaber eine Seite unter https://muratisystems.de/vorschau/ am eigenen Handy prüfen, bevor sie live geht. Die Live-Dateien im Wurzelverzeichnis bleiben dabei unverändert. Nach dem Release die Vorschau wieder löschen oder mit dem nächsten Stand überschreiben.
