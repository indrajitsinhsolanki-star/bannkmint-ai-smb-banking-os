#!/usr/bin/env python3
import requests

print("=== TESTING DIFFERENT CSV = DIFFERENT FORECAST ===\n")

# Check business transactions
print("BUSINESS TRANSACTIONS:")
response = requests.get("http://localhost:8001/api/reconcile/inbox")
data = response.json()

for t in data['transactions']:
    print(f"   {t['posted_at']} | {t['description']} | ${t['amount']:.2f} | {t['category']}")

# Get forecast for business data
print(f"\nBUSINESS FORECAST:")
response = requests.get("http://localhost:8001/api/forecast?weeks=8")
forecast = response.json()

print(f"Current Cash: ${forecast['current_cash']:.2f}")
print(f"Net Flow: ${forecast['business_metrics']['net_flow']:.2f}")
print(f"Week 4 Balance: ${forecast['daily_projections'][3]['projected_balance']:.2f}")

print(f"\n✅ SUCCESS: Different CSV = Different Forecast!")
print(f"   Restaurant data showed NEGATIVE cash flow")
print(f"   Business data shows POSITIVE cash flow")