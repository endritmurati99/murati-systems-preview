# Deployment muratisystems.de

Live seit 2026-09-23 auf dem Hostinger-VPS (KVM 2, Frankfurt, 76.13.154.245).

- Pfad auf dem VPS: `/srv/murati-website/` (Caddyfile, docker-compose.yml, `site/`)
- Container: `murati-website` (caddy:2-alpine), nur an die öffentliche IP gebunden, weil Port 443
  auf der Tailscale-Adresse von `tailscaled` belegt ist.
- HTTPS: Let's Encrypt, automatisch durch Caddy. Keine Zugriffsprotokolle.
- DNS (Hostinger): A `@` → 76.13.154.245 (TTL 60), CNAME `www` → muratisystems.de. Mail-Einträge unverändert.

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
