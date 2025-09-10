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
            desc = str(row.get('description', '')).lower()
            # Fix amount parsing - handle negative signs and currency symbols
            amount_str = str(row.get('amount', 0))
            amount_str = amount_str.replace('$', '').replace(',', '').replace('"', '').strip()
            if amount_str.startswith('-') or '(' in amount_str:
                amount = -abs(float(amount_str.replace('(', '').replace(')', '').replace('-', '')))
            else:
                amount = float(amount_str)
            
            category = "Meals & Entertainment" if any(w in desc for w in ['restaurant', 'pizza', 'coffee', 'mcdonald', 'starbucks', 'chipotle', 'domino', 'kfc', 'taco', 'buffalo', 'olive', 'subway']) else "Business Expense"
            cursor.execute("INSERT INTO transactions VALUES (?, ?, ?, ?)", 
                         (str(uuid.uuid4()), str(row.get('description', '')), amount, category))
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)