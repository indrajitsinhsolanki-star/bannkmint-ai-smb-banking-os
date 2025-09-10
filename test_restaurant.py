#!/usr/bin/env python3
import requests
import json

# Test the reconcile inbox
response = requests.get("http://localhost:8001/api/reconcile/inbox")
data = response.json()

print("=== RESTAURANT TRANSACTIONS IN RECONCILIATION VIEW ===")
print("Total transactions:", data['total'])
print()

for t in data['transactions']:
    print(f"{t['posted_at'][:10]} | {t['description']} | ${t['amount']} | {t['category']}")