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

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = '/app/clean_bankmint.db'

def init_db():
    # Remove existing database to ensure clean start
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE transactions (
            id TEXT PRIMARY KEY,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            confidence REAL DEFAULT 0.8,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def categorize_transaction(description, amount):
    desc = str(description).lower()
    
    # Restaurant categorization
    restaurant_keywords = ['restaurant', 'pizza', 'starbucks', 'coffee', 'mcdonald', 'subway', 
                          'chipotle', 'domino', 'kfc', 'taco bell', 'buffalo wild', 'olive garden']
    
    if any(keyword in desc for keyword in restaurant_keywords):
        return "Meals & Entertainment", 0.95
    
    # Other categories
    if any(word in desc for word in ['aws', 'software', 'microsoft', 'adobe']):
        return "Software & Technology", 0.90
    elif any(word in desc for word in ['payroll', 'salary', 'gusto', 'adp']):
        return "Payroll & Benefits", 0.90
    elif any(word in desc for word in ['office', 'supplies', 'staples']):
        return "Office Expenses", 0.85
    elif any(word in desc for word in ['ads', 'marketing', 'google ads', 'facebook']):
        return "Marketing & Advertising", 0.85
    elif amount > 0:
        return "Revenue - Sales", 0.60
    else:
        return "Other Expenses", 0.50

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "BankMint AI - Working Backend"}

@app.post("/api/ingest")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Read and validate CSV
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_data))
        
        # CLEAR EXISTING DATA FIRST
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        
        # Process NEW transactions
        imported = 0
        for _, row in df.iterrows():
            # Categorize each transaction
            category, confidence = categorize_transaction(row.get('description', ''), 
                                                        float(row.get('amount', 0)))
            
            # Insert transaction
            cursor.execute(
                "INSERT INTO transactions (id, date, description, amount, category, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), str(row.get('date', '')), str(row.get('description', '')), 
                 float(row.get('amount', 0)), category, confidence)
            )
            imported += 1
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "imported": imported,
            "skipped": 0,
            "total_processed": len(df),
            "categorized_pct": 100.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.get("/api/reconcile/inbox")
async def get_inbox():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    transactions = []
    for row in rows:
        transactions.append({
            "id": row[0],
            "posted_at": row[1],
            "description": row[2],
            "amount": row[3],
            "category": row[4],
            "confidence": row[5],
            "why": f"Auto-categorized as {row[4]}"
        })
    
    return {"transactions": transactions, "total": len(transactions)}

@app.get("/api/forecast")
async def get_forecast(weeks: int = 8):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT amount, category FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return {
            "forecast_period": f"{weeks}_weeks",
            "scenario": "base",
            "current_cash": 0.0,
            "crisis_threshold": 1000.0,
            "daily_projections": [],
            "smb_patterns": [],
            "crisis_alerts": [],
            "business_metrics": {},
            "scenario_analysis": {},
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }
    
    # Calculate simple forecast based on actual transaction data
    total_inflow = sum(amount for amount, _ in rows if amount > 0)
    total_outflow = sum(abs(amount) for amount, _ in rows if amount < 0)
    net_weekly = (total_inflow - total_outflow) / 4  # Assume 4 weeks of data
    
    current_balance = total_inflow - total_outflow
    
    # Generate weekly projections
    projections = []
    running_balance = current_balance
    
    for week in range(1, weeks + 1):
        running_balance += net_weekly
        projections.append({
            "week": week,
            "date": (datetime.now() + timedelta(weeks=week)).strftime("%Y-%m-%d"),
            "projected_inflows": max(0, net_weekly),
            "projected_outflows": max(0, -net_weekly),
            "net_flow": net_weekly,
            "projected_balance": running_balance,
            "confidence": 0.75
        })
    
    # Crisis alerts
    crisis_alerts = []
    if running_balance < 1000:
        crisis_alerts.append({
            "week": weeks,
            "severity": "high",
            "message": f"Low balance projected: ${running_balance:.2f}"
        })
    
    return {
        "forecast_period": f"{weeks}_weeks",
        "scenario": "base", 
        "current_cash": current_balance,
        "crisis_threshold": 1000.0,
        "daily_projections": projections,
        "smb_patterns": [],
        "crisis_alerts": crisis_alerts,
        "business_metrics": {
            "total_inflows": total_inflow,
            "total_outflows": total_outflow,
            "net_flow": total_inflow - total_outflow
        },
        "scenario_analysis": {"base": {"ending_cash": running_balance}},
        "recommendations": [],
        "generated_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)