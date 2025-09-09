"""
SQLite database setup and models for BannkMint AI
"""
import sqlite3
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

# Database connection
DATABASE_URL = "sqlite:///./transactions.db"

# Initialize database on import
def init_database():
    """Initialize the database with required tables"""
    conn = sqlite3.connect("transactions.db")
    cursor = conn.cursor()
    
    # Create accounts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            date TIMESTAMP NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            confidence REAL DEFAULT 0.0,
            explanation TEXT,
            original_csv_row INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts (id)
        )
    ''')
    
    # Create rules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id TEXT PRIMARY KEY,
            description_pattern TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create corrections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS corrections (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL,
            old_category TEXT NOT NULL,
            new_category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Compatibility functions for server.py
def create_tables():
    """Create database tables - compatibility function"""
    init_database()

def init_default_data():
    """Initialize default data - compatibility function"""
    pass

def get_db():
    """Mock database session for compatibility - not used with SQLite approach"""
    return None

# Pydantic models for API responses
class Account(BaseModel):
    id: str
    name: str
    account_type: str
    balance: float
    created_at: datetime

class Transaction(BaseModel):
    id: str
    account_id: str
    date: datetime
    description: str
    amount: float
    category: Optional[str] = None
    confidence: float = 0.0
    explanation: Optional[str] = None
    original_csv_row: Optional[int] = None
    created_at: datetime

class Rule(BaseModel):
    id: str
    description_pattern: str
    category: str
    confidence: float
    created_at: datetime

class Correction(BaseModel):
    id: str
    transaction_id: str
    old_category: str
    new_category: str
    created_at: datetime

# Raw database operations using sqlite3 directly
def execute_query(query: str, params: tuple = ()) -> List[Dict[Any, Any]]:
    """Execute a query and return results as list of dictionaries"""
    conn = sqlite3.connect("transactions.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params)
        if query.strip().lower().startswith('select'):
            results = [dict(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            results = []
        return results
    finally:
        conn.close()

# Helper functions
def generate_id() -> str:
    """Generate a unique UUID string"""
    return str(uuid.uuid4())

def get_or_create_account(name: str, account_type: str = "checking") -> str:
    """Get existing account or create new one"""
    # Check if account exists
    existing_accounts = execute_query(
        "SELECT id FROM accounts WHERE name = ?", (name,)
    )
    
    if existing_accounts:
        return existing_accounts[0]['id']
    
    # Create new account
    account_id = generate_id()
    execute_query(
        "INSERT INTO accounts (id, name, account_type, balance) VALUES (?, ?, ?, ?)",
        (account_id, name, account_type, 0.0)
    )
    
    return account_id

# Initialize database when module is imported
init_database()