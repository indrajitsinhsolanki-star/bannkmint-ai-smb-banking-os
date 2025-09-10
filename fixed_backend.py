#!/usr/bin/env python3
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
import uuid
from datetime import datetime, timedelta
from io import StringIO
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DB_PATH = '/app/transactions.db'

def categorize_transaction(description, amount):
    desc = str(description).lower()
    if any(word in desc for word in ['restaurant', 'pizza', 'starbucks', 'coffee', 'mcdonald', 'subway', 'chipotle', 'domino', 'kfc', 'taco bell', 'buffalo wild', 'olive garden']):
        return "Meals & Entertainment", 0.95
    elif any(word in desc for word in ['aws', 'software', 'microsoft']):
        return "Software & Technology", 0.90
    elif any(word in desc for word in ['payroll', 'salary', 'gusto']):
        return "Payroll & Benefits", 0.90
    elif amount > 0:
        return "Revenue - Sales", 0.60
    else:
        return "Other Expenses", 0.50

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "BankMint AI"}

@app.post("/api/ingest")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Delete old database completely
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        
        # Read CSV
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        
        # Create fresh database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE transactions (id TEXT, date TEXT, description TEXT, amount REAL, category TEXT, confidence REAL)')
        
        # Insert only new data
        for _, row in df.iterrows():
            category, confidence = categorize_transaction(row.get('description', ''), float(row.get('amount', 0)))
            cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?)", 
                         (str(uuid.uuid4()), str(row.get('date', '')), str(row.get('description', '')), 
                          float(row.get('amount', 0)), category, confidence))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "imported": len(df), "skipped": 0, "total_processed": len(df), "categorized_pct": 100.0}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.get("/api/reconcile/inbox")
async def get_inbox():
    if not os.path.exists(DB_PATH):
        return {"transactions": [], "total": 0}
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [{"id": r[0], "posted_at": r[1], "description": r[2], "amount": r[3], "category": r[4], "confidence": r[5], "why": f"Auto-categorized as {r[4]}"} for r in rows]
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