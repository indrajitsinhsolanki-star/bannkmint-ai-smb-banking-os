import requests

print("=== YOUR RESTAURANT FILE RESULTS ===")

# Test reconcile
r = requests.get("http://localhost:8001/api/reconcile/inbox")
data = r.json()
print(f"Total transactions: {len(data['transactions'])}")
for t in data['transactions'][:4]:
    print(f"  {t['description']}: ${t['amount']:.2f} - {t['category']}")

print("\n=== FORECAST RESULTS ===")
r = requests.get("http://localhost:8001/api/forecast")
forecast = r.json()
print(f"Current Cash: ${forecast['current_cash']:.2f}")
print(f"Total Inflows: ${forecast['business_metrics']['total_inflows']:.2f}")
print(f"Total Outflows: ${forecast['business_metrics']['total_outflows']:.2f}")
print(f"Week 4 Projection: ${forecast['daily_projections'][3]['projected_balance']:.2f}")