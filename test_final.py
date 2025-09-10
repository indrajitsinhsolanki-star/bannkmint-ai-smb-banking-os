import requests
r = requests.get("http://localhost:8001/api/reconcile/inbox")
data = r.json()
print("FIXED AMOUNTS:")
for t in data['transactions'][:3]:
    print(f"  {t['description']}: ${t['amount']}")

print("\nFORECAST:")
r = requests.get("http://localhost:8001/api/forecast")
forecast = r.json()
print(f"Current: ${forecast['current_cash']}")
print(f"Week 4: ${forecast['daily_projections'][3]['projected_balance']}")