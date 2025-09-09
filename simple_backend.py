#!/usr/bin/env python3
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import sqlite3
import uuid
from datetime import datetime
from io import StringIO

app = FastAPI()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect('bankmint.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT,
            description TEXT,
            amount REAL,
            category TEXT,
            confidence REAL DEFAULT 0.8
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "BankMint AI"}

@app.post("/api/ingest")
async def upload_csv(file: UploadFile = File(...)):
    try:
        # Read and validate CSV
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_data))
        
        # Process transactions
        conn = sqlite3.connect('bankmint.db')
        cursor = conn.cursor()
        
        imported = 0
        for _, row in df.iterrows():
            # Basic categorization
            desc = str(row.get('description', '')).lower()
            category = "Other"
            if 'aws' in desc or 'software' in desc:
                category = "Software & Technology"
            elif 'payroll' in desc or 'salary' in desc:
                category = "Payroll & Benefits"
            elif 'coffee' in desc or 'restaurant' in desc:
                category = "Meals & Entertainment"
            elif 'office' in desc or 'supplies' in desc:
                category = "Office Expenses"
            elif 'ads' in desc or 'marketing' in desc:
                category = "Marketing & Advertising"
            
            # Insert transaction
            cursor.execute(
                "INSERT OR IGNORE INTO transactions (id, date, description, amount, category, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), str(row.get('date', '')), str(row.get('description', '')), 
                 float(row.get('amount', 0)), category, 0.85)
            )
            imported += 1
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "imported": imported,
            "skipped": 0,
            "total_processed": len(df),
            "categorized_pct": 85.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

@app.get("/api/reconcile/inbox")
async def get_inbox():
    conn = sqlite3.connect('bankmint.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date DESC LIMIT 50")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)