from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
import uuid
from io import StringIO
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DB_PATH = '/app/data/simple.db'

@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.post("/api/ingest")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Clear database
        os.makedirs('/app/data', exist_ok=True)
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        
        # Read CSV
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE transactions (id TEXT, description TEXT, amount REAL, category TEXT)')
        
        for _, row in df.iterrows():
            # Handle different possible column names
            description = str(row.get('Description', row.get('description', row.get('DESCRIPTION', ''))))
            
            # Get amount from different possible column names and handle the format properly
            amount_value = row.get('Amount', row.get('amount', row.get('AMOUNT', 0)))
            amount_str = str(amount_value).replace('$', '').replace(',', '').replace('"', '').strip()
            
            # Handle negative amounts (credits are negative, debits are positive in restaurant context)
            transaction_type = str(row.get('Type', row.get('type', ''))).lower()
            if amount_str.startswith('-') or '(' in amount_str:
                amount = -abs(float(amount_str.replace('(', '').replace(')', '').replace('-', '')))
            else:
                amount = float(amount_str)
                # If it's a Credit type, make it negative (money going out)
                if 'credit' in transaction_type:
                    amount = -abs(amount)
            
            # Better categorization based on description
            desc_lower = description.lower()
            if any(w in desc_lower for w in ['restaurant', 'square', 'food', 'sysco', 'supplier']):
                category = "Restaurant Operations"
            elif any(w in desc_lower for w in ['payroll', 'processing']):
                category = "Payroll & Benefits"
            elif any(w in desc_lower for w in ['rent', 'utilities', 'gas']):
                category = "Rent & Utilities"
            else:
                category = "Business Expense"
                
            cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?)", 
                         (str(uuid.uuid4()), description, amount, category))
        
        conn.commit()
        conn.close()
        return {"success": True, "imported": len(df)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/reconcile/inbox")
async def get_transactions():
    if not os.path.exists(DB_PATH):
        return {"transactions": []}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [{"id": r[0], "posted_at": "2024-01-01", "description": r[1], "amount": r[2], "category": r[3], "confidence": 0.9, "why": "Auto-categorized"} for r in rows]
    return {"transactions": transactions, "total": len(transactions)}

@app.get("/api/forecast")
async def get_forecast():
    if not os.path.exists(DB_PATH):
        return {"current_cash": 0.0, "business_metrics": {}, "daily_projections": []}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM transactions")
    amounts = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not amounts:
        return {"current_cash": 0.0, "business_metrics": {}, "daily_projections": []}
    
    total_inflow = sum(a for a in amounts if a > 0)
    total_outflow = sum(abs(a) for a in amounts if a < 0)
    current_cash = total_inflow - total_outflow
    net_weekly = (total_inflow - total_outflow) / 4
    
    projections = []
    balance = current_cash
    for week in range(1, 9):
        balance += net_weekly
        projections.append({"week": week, "projected_balance": balance, "net_flow": net_weekly, "confidence": 0.75})
    
    return {
        "current_cash": current_cash,
        "business_metrics": {"total_inflows": total_inflow, "total_outflows": total_outflow, "net_flow": total_inflow - total_outflow},
        "daily_projections": projections,
        "crisis_alerts": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)