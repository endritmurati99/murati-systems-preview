#!/bin/sh
# Manual release helper. Never run automatically (no cron/CI/hook calls this).
# Builds, tests, and rsyncs dist/ to the live site directory - nothing more.
#
# Usage: sh deploy/release.sh [live-commit-for-equality-check]
set -eu
cd "$(dirname "$0")/.."

BASE="${1:-}"

python3 tools/build.py
python3 tests/check_site.py dist
node tests/check_privacy.cjs dist
if [ -n "$BASE" ]; then
  python3 tests/check_dist_equals_live.py dist --base "$BASE"
fi

echo "Build and tests OK. About to rsync dist/ -> /srv/murati-website/site/"
echo "Make sure a backup of /srv/murati-website/site/ exists, then confirm."
printf "Continue? [y/N] "
read -r answer
case "$answer" in
  y|Y) ;;
  *) echo "Aborted, nothing deployed."; exit 1 ;;
esac

sudo rsync -rt --delete --chown=root:root --chmod=D755,F644 dist/ /srv/murati-website/site/
echo "Deployed. Restart Caddy if it needs to pick up moved/removed files:"
echo "  cd /srv/murati-website && docker compose up -d --force-recreate caddy"
