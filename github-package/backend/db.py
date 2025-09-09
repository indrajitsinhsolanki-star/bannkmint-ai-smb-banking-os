"""
SQLite database setup and models for BannkMint AI
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os
from pathlib import Path

# Create data directory if it doesn't exist
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite database path
DATABASE_URL = f"sqlite:///{DATA_DIR}/bannkmint.db"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Account(Base):
    """Bank accounts table"""
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    institution = Column(String)
    currency = Column(String, default="USD")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    """Bank transactions table"""
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    posted_at = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    balance = Column(Float, nullable=True)
    raw_hash = Column(String)  # For deduplication
    source = Column(String)  # Source file/system
    category = Column(String, nullable=True)
    vendor = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)  # AI confidence score
    why = Column(Text, nullable=True)  # Explanation for categorization
    is_transfer = Column(Integer, default=0)  # Internal transfer flag
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")
    corrections = relationship("Correction", back_populates="transaction")

class Rule(Base):
    """Categorization rules table"""
    __tablename__ = "rules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scope = Column(String, default="company")  # company or global
    match_type = Column(String, nullable=False)  # regex, contains, exact
    pattern = Column(String, nullable=False)
    set_category = Column(String, nullable=True)
    set_vendor = Column(String, nullable=True)
    priority = Column(Integer, default=100)  # Lower = higher priority
    active = Column(Integer, default=1)  # Active flag
    hits = Column(Integer, default=0)  # Usage counter
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Correction(Base):
    """User corrections for learning"""
    __tablename__ = "corrections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    txn_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    old_category = Column(String)
    new_category = Column(String)
    old_vendor = Column(String)
    new_vendor = Column(String)
    reason = Column(Text)
    user = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="corrections")

class Vendor(Base):
    """Vendor normalization table"""
    __tablename__ = "vendors"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name_canonical = Column(String, nullable=False, unique=True)
    aliases = Column(Text)  # JSON array of aliases
    category_suggestion = Column(String)  # Most common category
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

def init_default_data():
    """Initialize database with default accounts and rules"""
    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(Account).count() > 0:
            return
        
        # Create default account
        default_account = Account(
            name="Main Business Account",
            institution="Bank of Business",
            currency="USD"
        )
        db.add(default_account)
        
        # Create default categorization rules
        default_rules = [
            Rule(match_type="contains", pattern="aws", set_category="Software & Technology", priority=10),
            Rule(match_type="contains", pattern="amazon web services", set_category="Software & Technology", priority=10),
            Rule(match_type="contains", pattern="google ads", set_category="Marketing & Advertising", priority=10),
            Rule(match_type="contains", pattern="facebook ads", set_category="Marketing & Advertising", priority=10),
            Rule(match_type="contains", pattern="stripe", set_category="Payment Processing Fees", priority=10),
            Rule(match_type="contains", pattern="paypal", set_category="Payment Processing Fees", priority=10),
            Rule(match_type="contains", pattern="uber", set_category="Transportation", priority=20),
            Rule(match_type="contains", pattern="starbucks", set_category="Meals & Entertainment", priority=20),
            Rule(match_type="contains", pattern="office depot", set_category="Office Supplies", priority=20),
            Rule(match_type="contains", pattern="staples", set_category="Office Supplies", priority=20),
            Rule(match_type="contains", pattern="irs", set_category="Taxes", priority=5),
            Rule(match_type="contains", pattern="state department of revenue", set_category="Taxes", priority=5),
            Rule(match_type="contains", pattern="gusto", set_category="Payroll", priority=10),
            Rule(match_type="contains", pattern="adp", set_category="Payroll", priority=10),
            Rule(match_type="contains", pattern="paychex", set_category="Payroll", priority=10),
        ]
        
        for rule in default_rules:
            db.add(rule)
        
        db.commit()
        print("Default data initialized successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing default data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    init_default_data()