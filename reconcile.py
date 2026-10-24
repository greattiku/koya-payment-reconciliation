#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""

"""Reconcile payments using the latest attempt for each transaction."""

import json
from decimal import Decimal

latest_attempts = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line_number, line in enumerate(f):
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        timestamp = event.get("ts")
        if not isinstance(timestamp, str):
            continue

        previous = latest_attempts.get(txn_id)


        if previous is None or (
            timestamp, line_number
        ) > (
            previous["ts"], previous["_line_number"]
        ):
            event["_line_number"] = line_number
            latest_attempts[txn_id] = event

successful_payments = [
    event
    for event in latest_attempts.values()
    if event.get("status") == "success"
]

total = Decimal("0")

for event in successful_payments:
    amount = str(event["amount"]).replace(",", "")
    total += Decimal(amount)

count = len(successful_payments)

with open("expected.txt", encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(
        f"Check failed: counted {count} successful payments, "
        f"expected {expected}."
    )
    print(
        "Something in the data isn't being handled the way "
        "the README describes."
    )
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")