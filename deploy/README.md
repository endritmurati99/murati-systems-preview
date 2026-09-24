# Deployment muratisystems.de

Live seit 2026-09-23 auf dem Hostinger-VPS (KVM 2, Frankfurt, 76.13.154.245).

- Pfad auf dem VPS: `/srv/murati-website/` (Caddyfile, docker-compose.yml, `site/`)
- Container: `murati-website` (caddy:2-alpine), nur an die öffentliche IP gebunden, weil Port 443
  auf der Tailscale-Adresse von `tailscaled` belegt ist.
- HTTPS: Let's Encrypt, automatisch durch Caddy. Keine Zugriffsprotokolle.
- DNS (Hostinger): A `@` → 76.13.154.245 (TTL 60), CNAME `www` → muratisystems.de. Mail-Einträge unverändert.

## Vorschau vom 24.09.2026: noch nicht veröffentlichen

Der Branch `codex/website-redesign` enthält eine neue Mehrseiten-Website und rechtliche Entwürfe. Vor jeder Veröffentlichung `../LEGAL-REVIEW.md` abarbeiten: Betreiber-/Vertragsangaben, Hosting-/Mailanbieter, Auftragsverarbeitung, Löschpraxis und B2B/Verbraucher-Vertragsweg bestätigen. Die aktuelle Live-Website verwendet Theme-localStorage; die neue Vorschau verwendet keinen dauerhaften Browserspeicher. Rechtstexte nicht ungeprüft zwischen den Ständen kopieren.

Das Caddyfile in diesem Branch ist für die neue Vorschau verschärft: keine Inline-Skripte, keine connect-/frame-/object-Zugriffe, keine Base-URL-Umschreibung. Diese Datei wurde nur mit `caddy adapt --validate` geprüft und nicht aktiviert. Die alte Live-Seite hat ein Inline-Theme-Skript; das neue Template darf nicht isoliert auf sie angewendet werden.

Für einen später freigegebenen Release müssen alle acht Hauptseiten und deren benötigte Assets gemeinsam ausgeliefert werden. `design/`, `tests/`, `deploy/`, interne Markdown-Prüfnotizen sowie die alten Prototypen `hell/` und `light/` gehören nicht in den öffentlichen Release. Die bisherige Kopieranweisung mit nur Start/Impressum/Datenschutz ist für die Mehrseiten-Version unvollständig und wurde entfernt.

Vor Umschaltung: externes Backup des bisherigen Releases, lokale Vorschautests, Cookie-/Netzwerkinventar, Legal-Freigabe und Prüfung der endgültigen Canonicals/Indexierung. Danach erst den ausdrücklich freigegebenen Stand atomar veröffentlichen und HTTPS, Header, Navigation, Formular, Rechtstexte und echte Kontaktzustellung produktiv prüfen. Ein Restart ist für reine Dateiinhalte nicht erforderlich; eine Caddy-Konfigurationsänderung ist separat kontrolliert zu aktivieren.
