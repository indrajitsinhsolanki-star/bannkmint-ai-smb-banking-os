#!/usr/bin/env python3

import sys
import os
sys.path.append('/app/backend')

# Test basic imports
try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")
    exit(1)

try:
    from backend.db import create_tables, init_database, execute_query
    print("✅ Database functions imported")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    exit(1)

# Test database initialization
try:
    create_tables()
    print("✅ Database tables created")
except Exception as e:
    print(f"❌ Database creation failed: {e}")
    exit(1)

# Test backend services
try:
    from backend.services.ingest import CSVIngestor
    print("✅ CSVIngestor imported")
except Exception as e:
    print(f"❌ CSVIngestor import failed: {e}")

try:
    from backend.services.categorize import TransactionCategorizer
    print("✅ TransactionCategorizer imported")
except Exception as e:
    print(f"❌ TransactionCategorizer import failed: {e}")

try:
    from backend.services.forecast import SMBCashFlowForecaster
    print("✅ SMBCashFlowForecaster imported")  
except Exception as e:
    print(f"❌ SMBCashFlowForecaster import failed: {e}")

try:
    from backend.services.banking import BankingIntegrationService
    print("✅ BankingIntegrationService imported")
except Exception as e:
    print(f"❌ BankingIntegrationService import failed: {e}")

try:
    from backend.services.reporting import MonthEndReportingService
    print("✅ MonthEndReportingService imported")
except Exception as e:
    print(f"❌ MonthEndReportingService import failed: {e}")

print("\n🚀 Backend test completed!")
print("Ready to start the server...")