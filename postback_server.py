#!/usr/bin/env python3
"""Receive Dhan order-update postbacks and append them to postbacks.jsonl.

Env (via .env): DHAN_CLIENT_ID, POSTBACK_SECRET, optional POSTBACK_PORT (default 8080)
Set the Dhan postback URL to: https://<your-public-host>/postback/<POSTBACK_SECRET>
"""
import hmac
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
for _k in ("DHAN_CLIENT_ID", "POSTBACK_SECRET"):
    if not os.environ.get(_k):
        sys.exit(f"{_k} not set. Add it to .env (see .env.example).")

CLIENT_ID = os.environ["DHAN_CLIENT_ID"]
PATH = f"/postback/{os.environ['POSTBACK_SECRET']}"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "postbacks.jsonl")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Dhan doesn't sign postbacks, so the secret path + client id check is the authentication.
        if not hmac.compare_digest(self.path, PATH):
            return self._reply(404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 65536:
                return self._reply(413)
            data = json.loads(self.rfile.read(length))
        except ValueError:
            return self._reply(400)
        if data.get("dhanClientId") != CLIENT_ID:
            return self._reply(403)

        with open(LOG, "a") as f:
            f.write(json.dumps({"received": time.time(), **data}) + "\n")
        print(
            f"{data.get('orderId')} {data.get('tradingSymbol')} {data.get('transactionType')} "
            f"{data.get('orderStatus')} filled={data.get('filled_qty')}/{data.get('quantity')} "
            f"{data.get('omsErrorDescription') or ''}",
            flush=True,
        )
        self._reply(200)

    def _reply(self, code):
        self.send_response(code)
        self.end_headers()

    def log_message(self, *args):  # keep the secret path out of access logs
        pass


if __name__ == "__main__":
    port = int(os.environ.get("POSTBACK_PORT", 8080))
    host = os.environ.get("POSTBACK_HOST", "127.0.0.1")  # behind a reverse proxy; set 0.0.0.0 to expose directly
    print(f"Listening on {host}:{port}")
    HTTPServer((host, port), Handler).serve_forever()
