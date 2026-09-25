#!/bin/sh
# Veröffentlicht den aktuellen Arbeitsstand von website/ als Vorschau unter /vorschau/ (noindex).
# Die Live-Seite im Wurzelverzeichnis bleibt unverändert.
set -e
cd /home/hermes/Murati-Systems/website
V=/srv/murati-website/site/vorschau
sudo rm -rf "$V.new"
sudo mkdir -p "$V.new"
sudo cp ./*.html "$V.new/"
sudo cp -r assets "$V.new/"
sudo rm -f "$V.new/assets/site.css" "$V.new/assets/site.js" "$V.new/assets/tokens.css" "$V.new"/google*.html
sudo sed -i 's#<meta charset="utf-8">#<meta charset="utf-8">\n  <meta name="robots" content="noindex, nofollow">#' "$V.new"/*.html
sudo find "$V.new" -type d -exec chmod 755 {} +
sudo find "$V.new" -type f -exec chmod 644 {} +
sudo chown -R root:root "$V.new"
sudo rm -rf "$V"
sudo mv "$V.new" "$V"
echo "Vorschau aktualisiert: https://muratisystems.de/vorschau/"
