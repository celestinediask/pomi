# pomi (testing)

- `place_order.py` – place an equity order via Dhan v2 API (CLI).
- `postback_server.py` – receives Dhan order-update postbacks, logs to `postbacks.jsonl`.

## Setup
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && chmod 600 .env   # fill in values
```

## Order
```bash
.venv/bin/python place_order.py --security-id 1333 --side BUY --qty 1 --type LIMIT --price 1500
```
Use `DHAN_BASE_URL=https://sandbox.dhan.co/v2` to test against the sandbox.

## Postback server (VPS)
1. `sudo cp deploy/dhan-postback.service /etc/systemd/system/` (edit User/paths), then `sudo systemctl enable --now dhan-postback`.
2. Put `deploy/Caddyfile.example` (with your domain) in `/etc/caddy/Caddyfile`, reload Caddy.
3. Dhan postback URL: `https://<domain>/postback/<POSTBACK_SECRET>`
4. Test: `curl -i -X POST https://<domain>/postback/<secret> -H 'Content-Type: application/json' -d '{"dhanClientId":"<id>","orderId":"1","orderStatus":"TRADED"}'`
