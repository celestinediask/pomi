#!/usr/bin/env python3
"""Place an equity order via the Dhan v2 API.

Env (via .env): DHAN_CLIENT_ID, DHAN_ACCESS_TOKEN
Example:
  python3 place_order.py --security-id 1333 --side BUY --qty 1 --type LIMIT --price 1500
"""
import argparse
import os
import sys

import requests
from dotenv import load_dotenv

# Loads .env from the script's directory (real env vars take precedence)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
for _k in ("DHAN_CLIENT_ID", "DHAN_ACCESS_TOKEN"):
    if not os.environ.get(_k):
        sys.exit(f"{_k} not set. Add it to .env (see .env.example).")
BASE = os.environ.get("DHAN_BASE_URL", "https://api.dhan.co/v2")  # sandbox: https://sandbox.dhan.co/v2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--security-id", required=True, help="from Dhan instrument master CSV")
    p.add_argument("--side", required=True, choices=["BUY", "SELL"])
    p.add_argument("--qty", required=True, type=int)
    p.add_argument("--type", default="MARKET", choices=["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"])
    p.add_argument("--price", type=float, default=0.0)
    p.add_argument("--trigger-price", type=float, default=0.0)
    p.add_argument("--product", default="CNC", choices=["CNC", "INTRADAY", "MARGIN", "MTF"])
    p.add_argument("--exchange", default="NSE_EQ", choices=["NSE_EQ", "BSE_EQ"])
    p.add_argument("--validity", default="DAY", choices=["DAY", "IOC"])
    p.add_argument("--yes", action="store_true", help="skip confirmation prompt")
    a = p.parse_args()

    if a.type in ("LIMIT", "STOP_LOSS") and a.price <= 0:
        sys.exit("--price is required for LIMIT/STOP_LOSS orders")
    if a.type in ("STOP_LOSS", "STOP_LOSS_MARKET") and a.trigger_price <= 0:
        sys.exit("--trigger-price is required for STOP_LOSS orders")

    order = {
        "dhanClientId": os.environ["DHAN_CLIENT_ID"],
        "transactionType": a.side,
        "exchangeSegment": a.exchange,
        "productType": a.product,
        "orderType": a.type,
        "validity": a.validity,
        "securityId": a.security_id,
        "quantity": a.qty,
    }
    if a.price:
        order["price"] = a.price
    if a.trigger_price:
        order["triggerPrice"] = a.trigger_price

    print("Order:", order)
    if not a.yes and input("Place this order? [y/N] ").strip().lower() != "y":
        sys.exit("Aborted.")

    r = requests.post(
        f"{BASE}/orders",
        headers={"access-token": os.environ["DHAN_ACCESS_TOKEN"], "Content-Type": "application/json", "Accept": "application/json"},
        json=order,
        timeout=10,
    )
    print(r.status_code, r.text)
    sys.exit(0 if r.ok else 1)


if __name__ == "__main__":
    main()
