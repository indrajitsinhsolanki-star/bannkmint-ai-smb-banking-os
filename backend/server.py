from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Import our database and services
from db import create_tables, init_default_data, execute_query, get_or_create_account, generate_id, get_db, Transaction, Account, Rule
from services.ingest import ingestion_service, CSVIngestor
from services.categorize import categorization_service, TransactionCategorizer
from services.forecast import forecasting_service, SMBCashFlowForecaster as CashFlowForecaster
from services.banking import banking_service, BankingIntegrationService
from services.reporting import reporting_service, MonthEndReportingService

# Compatibility imports for FastAPI dependency injection
from fastapi import Depends

# Mock Session class for compatibility
class Session:
    def query(self, model):
        return MockQuery(model)
    def add(self, obj):
        pass
    def commit(self):
        pass
    def rollback(self):
        pass

class MockQuery:
    def __init__(self, model):
        self.model = model
    def filter(self, *args):
        return self
    def order_by(self, *args):
        return self
    def all(self):
        return []
    def first(self):
        return None
    def count(self):
        return 0
    def offset(self, n):
        return self
    def limit(self, n):
        return self

ROOT_DIR = Path(__file__).parent
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / '.env')

# Initialize database
create_tables()
try:
    init_default_data()
except:
    pass  # Ignore if already initialized

# Create the main app
app = FastAPI(title="BannkMint AI", version="0.2.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic models
class IngestResponse(BaseModel):
    success: bool
    imported: Optional[int] = None
    skipped: Optional[int] = None 
    total_processed: Optional[int] = None
    categorized_pct: Optional[float] = None
    error: Optional[str] = None
    suggestion: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    posted_at: datetime
    description: str
    amount: float
    currency: str
    balance: Optional[float]
    category: Optional[str]
    vendor: Optional[str]
    confidence: Optional[float]
    why: Optional[str]
    is_transfer: int
    
class RuleResponse(BaseModel):
    id: str
    match_type: str
    pattern: str
    set_category: Optional[str]
    set_vendor: Optional[str]
    priority: int
    active: int
    hits: int

class RuleCreate(BaseModel):
    match_type: str
    pattern: str
    set_category: Optional[str] = None
    set_vendor: Optional[str] = None
    priority: int = 100

class CategorizationRequest(BaseModel):
    category: str
    vendor: Optional[str] = None
    make_rule: bool = False
    pattern: Optional[str] = None

class ForecastResponse(BaseModel):
    forecast_period: str
    scenario: str
    current_cash: float
    crisis_threshold: float
    daily_projections: List[Dict[str, Any]]
    smb_patterns: List[Dict[str, Any]]
    crisis_alerts: List[Dict[str, Any]]
    business_metrics: Dict[str, Any]
    scenario_analysis: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    generated_at: str

# Health check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"ok": True, "version": "0.2.0", "service": "BannkMint AI"}

# Legacy endpoints for compatibility
@api_router.get("/")
async def root():
    """Legacy root endpoint"""
    return {"message": "BannkMint AI v0.2 - Financial Intelligence Platform"}

# Ingestion endpoints
@api_router.post("/ingest", response_model=IngestResponse)
async def ingest_csv(
    file: UploadFile = File(...),
    account_id: Optional[str] = Form(None)
):
    """Upload and process CSV file"""
    try:
        # Validate file
        if not file.filename.endswith('.csv'):
            return IngestResponse(
                success=False,
                error="Only CSV files are supported",
                suggestion="Please upload a CSV file with transaction data"
            )
        
        # Check file size (20MB limit)
        file_content = await file.read()
        if len(file_content) > 20 * 1024 * 1024:  # 20MB
            return IngestResponse(
                success=False,
                error="File too large",
                suggestion="Please upload files smaller than 20MB"
            )

        # Decode file content to string
        csv_content_str = file_content.decode('utf-8')
        
        # Process CSV using ingestion service
        result = ingestion_service.process_csv_upload(
            csv_content_str, 
            account_name=account_id or "Default Account"
        )
        
        if result['success']:
            return IngestResponse(
                success=True,
                imported=result.get('processed_count', 0),
                skipped=result.get('duplicate_count', 0),
                total_processed=result.get('total_rows', 0),
                categorized_pct=result.get('categories_detected', {}) and 80.0 or 0.0  # Estimate
            )
        else:
            return IngestResponse(
                success=False,
                error=result.get('error', 'Processing failed'),
                suggestion="Please check the file format and try again"
            )
            
    except Exception as e:
        return IngestResponse(
            success=False,
            error=str(e),
            suggestion="Please check the file format and try again"
        )

# Reconciliation endpoints
@api_router.get("/reconcile/inbox")
async def get_reconciliation_inbox(
    min_conf: float = 0.9,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get transactions needing review"""
    try:
        offset = (page - 1) * limit
        
        # Get transactions with low confidence or uncategorized
        query = db.query(Transaction).filter(
            (Transaction.confidence < min_conf) | 
            (Transaction.confidence.is_(None)) |
            (Transaction.category == 'Uncategorized')
        ).order_by(Transaction.posted_at.desc())
        
        total = query.count()
        transactions = query.offset(offset).limit(limit).all()
        
        return {
            "transactions": [
                TransactionResponse(
                    id=t.id,
                    account_id=t.account_id,
                    posted_at=t.posted_at,
                    description=t.description,
                    amount=t.amount,
                    currency=t.currency,
                    balance=t.balance,
                    category=t.category,
                    vendor=t.vendor,
                    confidence=t.confidence,
                    why=t.why,
                    is_transfer=t.is_transfer
                ) for t in transactions
            ],
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/transactions/{transaction_id}/categorize")
async def categorize_transaction(
    transaction_id: str,
    request: CategorizationRequest,
    db: Session = Depends(get_db)
):
    """Manually categorize a transaction"""
    try:
        categorizer = TransactionCategorizer(db)
        result = categorizer.learn_from_correction(
            transaction_id=transaction_id,
            new_category=request.category,
            new_vendor=request.vendor,
            make_rule=request.make_rule,
            pattern=request.pattern
        )
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rules endpoints
@api_router.get("/rules", response_model=List[RuleResponse])
async def get_rules(db: Session = Depends(get_db)):
    """Get all categorization rules"""
    try:
        rules = db.query(Rule).order_by(Rule.priority.asc()).all()
        return [
            RuleResponse(
                id=r.id,
                match_type=r.match_type,
                pattern=r.pattern,
                set_category=r.set_category,
                set_vendor=r.set_vendor,
                priority=r.priority,
                active=r.active,
                hits=r.hits
            ) for r in rules
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/rules", response_model=RuleResponse)
async def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Create a new categorization rule"""
    try:
        new_rule = Rule(
            match_type=rule.match_type,
            pattern=rule.pattern,
            set_category=rule.set_category,
            set_vendor=rule.set_vendor,
            priority=rule.priority
        )
        db.add(new_rule)
        db.commit()
        
        return RuleResponse(
            id=new_rule.id,
            match_type=new_rule.match_type,
            pattern=new_rule.pattern,
            set_category=new_rule.set_category,
            set_vendor=new_rule.set_vendor,
            priority=new_rule.priority,
            active=new_rule.active,
            hits=new_rule.hits
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str, db: Session = Depends(get_db)):
    """Delete a categorization rule"""
    try:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        db.delete(rule)
        db.commit()
        return {"success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Legacy compatibility endpoints
@api_router.post("/categorize-transactions")
async def legacy_categorize_transactions(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Legacy endpoint for compatibility"""
    # This would delegate to new categorization system
    return {"message": "Please use the new /api/ingest endpoint"}

@api_router.post("/clean-csv")
async def legacy_clean_csv(file: UploadFile = File(...)):
    """Legacy endpoint for compatibility"""
    return {"message": "Please use the new /api/ingest endpoint for CSV processing"}

# Forecast endpoints (Phase 3B - SMB-Focused)
@api_router.get("/forecast", response_model=ForecastResponse)
async def get_smb_cash_flow_forecast(
    weeks: int = 6,
    scenario: str = "base",
    account_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get SMB-focused 4-8 week cash flow forecast with crisis prevention"""
    try:
        forecaster = CashFlowForecaster(db)
        
        # Validate SMB-appropriate parameters
        weeks = max(4, min(weeks, 8))  # Force 4-8 week range
        scenario = scenario if scenario in ['optimistic', 'base', 'pessimistic'] else 'base'
        
        forecast_data = forecaster.generate_smb_forecast(
            weeks=weeks,
            account_id=account_id,
            scenario=scenario
        )
        
        return ForecastResponse(**forecast_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMB forecast generation failed: {str(e)}")

@api_router.get("/forecast/crisis-analysis")
async def get_crisis_analysis(
    weeks: int = 6,
    account_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get cash flow crisis analysis and prevention recommendations"""
    try:
        forecaster = CashFlowForecaster(db)
        forecast_data = forecaster.generate_smb_forecast(weeks=weeks, account_id=account_id)
        
        return {
            'crisis_threshold': forecaster.crisis_threshold,
            'current_cash': forecast_data['current_cash'],
            'crisis_alerts': forecast_data['crisis_alerts'],
            'business_metrics': forecast_data['business_metrics'],
            'recommendations': forecast_data['recommendations'],
            'cash_runway_days': forecast_data['business_metrics'].get('cash_runway_days', 0),
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crisis analysis failed: {str(e)}")

@api_router.get("/forecast/scenario-planning")
async def get_scenario_planning(
    weeks: int = 6,
    account_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get scenario planning analysis (optimistic/base/pessimistic)"""
    try:
        forecaster = CashFlowForecaster(db)
        
        scenarios = {}
        for scenario_name in ['optimistic', 'base', 'pessimistic']:
            forecast_data = forecaster.generate_smb_forecast(
                weeks=weeks,
                account_id=account_id,
                scenario=scenario_name
            )
            
            scenarios[scenario_name] = {
                'ending_cash': forecast_data['scenario_analysis'][scenario_name]['ending_cash'],
                'minimum_cash': forecast_data['scenario_analysis'][scenario_name]['minimum_cash'],
                'crisis_days': forecast_data['scenario_analysis'][scenario_name]['crisis_days'],
                'cash_change': forecast_data['scenario_analysis'][scenario_name]['cash_change']
            }
        
        return {
            'scenarios': scenarios,
            'current_cash': forecast_data['current_cash'],
            'forecast_period': f"{weeks}_weeks",
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario planning failed: {str(e)}")

@api_router.get("/forecast/patterns")
async def get_smb_recurring_patterns(
    account_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get SMB-specific recurring patterns with business criticality"""
    try:
        forecaster = CashFlowForecaster(db)
        patterns = forecaster._detect_smb_patterns(account_id)
        
        return {
            "patterns": patterns,
            "count": len(patterns),
            "critical_patterns": len([p for p in patterns if p['business_criticality'] > 0.8]),
            "high_confidence_patterns": len([p for p in patterns if p['confidence'] > 0.8]),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern detection failed: {str(e)}")

# Banking Integration endpoints (Phase 3A)
@api_router.get("/banking/institutions")
async def get_supported_banks():
    """Get list of supported banking institutions"""
    return {
        "supported_banks": [
            {
                "bank_id": "chase_business",
                "name": "Chase Business Complete Banking",
                "institution": "JPMorgan Chase Bank"
            },
            {
                "bank_id": "wells_fargo_business", 
                "name": "Wells Fargo Business Choice Checking",
                "institution": "Wells Fargo Bank"
            },
            {
                "bank_id": "bank_of_america_business",
                "name": "Bank of America Business Advantage", 
                "institution": "Bank of America"
            },
            {
                "bank_id": "mercury_banking",
                "name": "Mercury Business Banking",
                "institution": "Mercury Financial"
            }
        ]
    }

@api_router.post("/banking/connect")
async def connect_bank(
    bank_id: str,
    business_name: str = "My Business",
    db: Session = Depends(get_db)
):
    """Simulate bank connection (OAuth simulation)"""
    try:
        banking_service = BankingIntegrationService(db)
        result = banking_service.simulate_bank_connection(bank_id, business_name)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bank connection failed: {str(e)}")

@api_router.get("/banking/connections")
async def get_bank_connections(db: Session = Depends(get_db)):
    """Get all connected bank accounts"""
    try:
        banking_service = BankingIntegrationService(db)
        connections = banking_service.get_connected_banks()
        
        return {
            "connections": connections,
            "total_connections": len(connections)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")

@api_router.get("/banking/overview") 
async def get_financial_overview(db: Session = Depends(get_db)):
    """Get executive financial overview dashboard"""
    try:
        banking_service = BankingIntegrationService(db)
        overview = banking_service.get_financial_overview()
        
        return overview
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {str(e)}")

# Month-End Reporting endpoints (Phase 3A)
@api_router.get("/reports/month-end")
async def generate_month_end_pack(
    month: Optional[int] = None,
    year: Optional[int] = None,
    account_ids: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Generate comprehensive month-end reporting pack"""
    try:
        reporting_service = MonthEndReportingService(db)
        
        # Parse account_ids if provided
        account_list = account_ids.split(',') if account_ids else None
        
        report = reporting_service.generate_month_end_pack(
            month=month,
            year=year,
            account_ids=account_list
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@api_router.get("/reports/profit-loss")
async def get_profit_loss_report(
    month: Optional[int] = None,
    year: Optional[int] = None,
    account_ids: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get Profit & Loss report for specified period"""
    try:
        reporting_service = MonthEndReportingService(db)
        account_list = account_ids.split(',') if account_ids else None
        
        # Use current month if not specified
        if month is None or year is None:
            today = datetime.now()
            if today.month == 1:
                month = 12
                year = today.year - 1
            else:
                month = today.month - 1
                year = today.year
        
        # Get full month-end pack and extract P&L
        full_report = reporting_service.generate_month_end_pack(month, year, account_list)
        
        return {
            "report_period": full_report["report_period"],
            "profit_loss": full_report["profit_loss"],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P&L report generation failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # For file downloads
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


