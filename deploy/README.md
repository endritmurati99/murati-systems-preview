# Deployment muratisystems.de

Live seit 2026-09-23 auf dem Hostinger-VPS (KVM 2, Frankfurt, 76.13.154.245).

- Pfad auf dem VPS: `/srv/murati-website/` (Caddyfile, docker-compose.yml, `site/`)
- Container: `murati-website` (caddy:2-alpine), nur an die öffentliche IP gebunden, weil Port 443
  auf der Tailscale-Adresse von `tailscaled` belegt ist.
- HTTPS: Let's Encrypt, automatisch durch Caddy. Keine Zugriffsprotokolle.
- DNS (Hostinger): A `@` → 76.13.154.245 (TTL 60), CNAME `www` → muratisystems.de. Mail-Einträge unverändert.

## Aktualisieren

```bash
cd ~/Murati-Systems/website
tar cf - index.html impressum.html datenschutz.html assets | ssh vps 'cd /srv/murati-website/site && tar xf -'
```

Caddy liefert Änderungen sofort aus. Nur nach Änderungen am Caddyfile neu starten:
`ssh vps 'docker restart murati-website'`.
