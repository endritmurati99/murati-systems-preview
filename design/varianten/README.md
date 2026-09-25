# Varianten zur Auswahl (Design-Chat, 25.09.2026)

Overlays auf `assets/redesign.css`, nicht ausgeliefert. Farbe A („Orange leiser“) ist im Code umgesetzt und vom Inhaber gewählt.

- `farbe-b-signalgelb.css`: Akzent Gelb statt Orange (dazu `favicon.svg` mit `#FFC21A`).
- `farbe-c-dunkler-einstieg.css`: Kopf und Hero der Startseite auf Graphit.
- `logo-2-nur-schriftzug.css`: verworfene Logo-Variante. Logo 3 „kompakt“ ist gewählt (Inhaber, 25.09.2026) und in `assets/redesign.css` übernommen, das Overlay ist deshalb gelöscht. Logo 1 („Murati“ über „SYSTEMS“) war der Stand davor.

Vorschau bauen: Overlay an eine Kopie von `assets/redesign.css` anhängen (siehe `deploy/preview.sh`, Ordner `vorschau/<variante>/`, noindex).

Screenshots: `werkzeuge/shot.cjs` nutzt Playwright unter Windows (`%APPDATA%/npm/node_modules/@playwright/cli/…`, Chromium in `%LOCALAPPDATA%/ms-playwright`), weil Node 18 auf dem VPS für Playwright 1.62 zu alt ist. Vorschau-Server auf dem VPS: `python3 -m http.server 8766 --bind 127.0.0.1 --directory ~/Murati-Systems/website`, dazu Tunnel `ssh -N -L 8766:127.0.0.1:8766 murati-vps`. Aufruf: `node shot.cjs <ordner> <overlay.css|-> "seite.html@390" "seite.html@1440!#abschnitt"`. `compose.cjs` rendert eine lokale Vergleichsseite als PNG.
