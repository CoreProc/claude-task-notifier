# Future: Bitrise Build Notifications

## Problem

Bitrise CI runs in the cloud and can't reach `localhost:9876` on your PC.

## Solution: Cloudflare Tunnel

Cloudflare Tunnel exposes your local notifier to the internet via a stable public URL.

### Requirements (per PC)

1. Python + this notifier app running
2. `cloudflared` installed — https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
3. Cloudflare account (free)

### Setup Steps

1. Install cloudflared:
   ```
   winget install cloudflare-warp
   ```

2. Login:
   ```
   cloudflared tunnel login
   ```

3. Create a named tunnel:
   ```
   cloudflared tunnel create claude-notifier
   ```

4. Configure tunnel to point to the notifier:
   ```yaml
   # ~/.cloudflared/config.yml
   tunnel: claude-notifier
   credentials-file: ~/.cloudflared/<tunnel-id>.json
   ingress:
     - hostname: claude-notifier.yourdomain.com
       service: http://localhost:9876
     - service: http_status:404
   ```

5. Run the tunnel:
   ```
   cloudflared tunnel run claude-notifier
   ```

### Security

Before exposing to the internet, add a secret token check to the notifier server:
- Bitrise sends: `X-Secret: <your-token>` header
- Notifier rejects requests without a valid token

### Bitrise Integration

Add a step to `bitrise.yaml`:
```yaml
- script:
    title: Notify Windows
    inputs:
    - content: |
        curl -s --connect-timeout 5 \
          -X POST https://claude-notifier.yourdomain.com \
          -H "Content-Type: application/json" \
          -H "X-Secret: your-secret-token" \
          -d "{\"summary\": \"Build #$BITRISE_BUILD_NUMBER finished\", \"cwd\": \"$BITRISE_APP_TITLE\"}" \
          || true
```

### Alternatives

- **ngrok** — simpler but free tier URL changes on restart
- **Bitrise Slack step** — no infra needed, uses Slack for notifications
- **Bitrise email step** — built-in, zero setup
