# BannkMint AI SMB Banking OS - API Documentation

## Overview

BannkMint AI provides a comprehensive RESTful API for SMB financial management, including AI-powered transaction categorization, cash flow forecasting, and banking integration.

**Base URL:** `http://your-domain.com/api`
**Version:** v0.2.0

## Authentication

Currently, the API operates without authentication for development and testing purposes. In production, implement proper authentication mechanisms.

## Common Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "BannkMint AI"
}
```

## Error Handling

Error responses include:

```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Health Check Endpoints

### GET /api/health

**Description:** Check API health status

**Response:**
```json
{
  "ok": true,
  "version": "0.2.0",
  "service": "BannkMint AI"
}
```

### GET /api/

**Description:** Root endpoint with welcome message

**Response:**
```json
{
  "message": "BannkMint AI v0.2 - Financial Intelligence Platform"
}
```

## Data Ingestion Endpoints

### POST /api/upload-csv

**Description:** Upload and process CSV transaction data

**Request Format:** `multipart/form-data`

**Parameters:**
- `file` (file): CSV file containing transaction data
- `account_name` (string, optional): Name for the account (default: "Default Account")
- `account_type` (string, optional): Type of account (default: "checking")

**CSV Format Requirements:**
- Required columns: `date`, `description`
- Amount columns: Either `amount` OR both `debit` and `credit`
- Optional columns: `category`, `balance`

**Response:**
```json
{
  "success": true,
  "account_id": "uuid-string",
  "processed_count": 150,
  "duplicate_count": 5,
  "total_rows": 155,
  "date_range": {
    "earliest": "2024-01-01",
    "latest": "2024-01-31"
  },
  "amount_summary": {
    "total_credits": 15000.00,
    "total_debits": -8500.00,
    "net_amount": 6500.00
  },
  "categories_detected": {
    "Office Expenses": 25,
    "Revenue - Sales": 10,
    "Software & Technology": 8
  }
}
```

### GET /api/upload-history

**Description:** Get recent upload history

**Parameters:**
- `limit` (integer, optional): Number of entries to return (default: 10)

**Response:**
```json
[
  {
    "account_name": "Business Checking",
    "upload_date": "2024-01-31",
    "transaction_count": 45,
    "total_credits": 5000.00,
    "total_debits": -2500.00,
    "net_amount": 2500.00,
    "date_range": {
      "earliest": "2024-01-01",
      "latest": "2024-01-31"
    }
  }
]
```

## Transaction Management Endpoints

### GET /api/transactions

**Description:** Retrieve all transactions

**Parameters:**
- `limit` (integer, optional): Number of transactions to return
- `offset` (integer, optional): Number of transactions to skip
- `category` (string, optional): Filter by category
- `start_date` (string, optional): Filter by start date (YYYY-MM-DD)
- `end_date` (string, optional): Filter by end date (YYYY-MM-DD)

**Response:**
```json
[
  {
    "id": "uuid-string",
    "account_id": "uuid-string",
    "date": "2024-01-15T00:00:00Z",
    "description": "Coffee Shop Purchase",
    "amount": -4.50,
    "category": "Meals & Entertainment",
    "confidence": 0.85,
    "explanation": "Matched pattern: 'coffee'",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST /api/categorize-transaction

**Description:** Categorize a single transaction

**Request Body:**
```json
{
  "description": "Microsoft Office 365 Subscription",
  "amount": -29.99
}
```

**Response:**
```json
{
  "category": "Software & Technology",
  "confidence": 0.92,
  "explanation": "Matched pattern: 'microsoft.*365'"
}
```

### POST /api/correct-transaction

**Description:** Record a user correction for learning

**Request Body:**
```json
{
  "transaction_id": "uuid-string",
  "old_category": "Other Expenses",
  "new_category": "Software & Technology"
}
```

**Response:**
```json
{
  "success": true,
  "correction_id": "uuid-string",
  "message": "Correction recorded and applied"
}
```

## Rules Management Endpoints

### GET /api/rules

**Description:** Get all categorization rules

**Response:**
```json
[
  {
    "id": "uuid-string",
    "description_pattern": "starbucks|coffee",
    "category": "Meals & Entertainment",
    "confidence": 0.90,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### POST /api/create-rule

**Description:** Create a new categorization rule

**Request Body:**
```json
{
  "description_pattern": "uber|lyft|taxi",
  "category": "Travel & Transportation",
  "confidence": 0.95
}
```

**Response:**
```json
{
  "success": true,
  "rule_id": "uuid-string",
  "message": "Rule created successfully"
}
```

### GET /api/category-suggestions

**Description:** Get category suggestions for autocomplete

**Parameters:**
- `partial` (string): Partial category name for suggestions

**Response:**
```json
[
  "Office Expenses",
  "Software & Technology",
  "Marketing & Advertising"
]
```

## Cash Flow Forecasting Endpoints

### POST /api/forecast

**Description:** Generate cash flow forecast

**Request Body:**
```json
{
  "weeks": 8,
  "scenario": "base",
  "include_seasonal": true
}
```

**Parameters:**
- `weeks` (integer): Forecast period in weeks (4, 6, 8, or 13)
- `scenario` (string): Forecast scenario ("optimistic", "base", "pessimistic")
- `include_seasonal` (boolean): Include seasonal adjustments

**Response:**
```json
{
  "forecast_period": "8 weeks",
  "scenario": "base",
  "current_balance": 15000.00,
  "projections": [
    {
      "week": 1,
      "date": "2024-01-22",
      "projected_inflows": 5000.00,
      "projected_outflows": 3500.00,
      "net_flow": 1500.00,
      "projected_balance": 16500.00,
      "confidence": 0.78
    }
  ],
  "key_metrics": {
    "total_projected_inflows": 40000.00,
    "total_projected_outflows": 28000.00,
    "net_cash_flow": 12000.00,
    "weekly_burn_rate": -1000.00,
    "cash_runway_weeks": 15.5,
    "ending_balance": 27000.00
  },
  "crisis_alerts": [
    {
      "week": 6,
      "date": "2024-02-26",
      "projected_balance": 800.00,
      "severity": "high",
      "message": "Low balance warning in Week 6: Balance projected at $800.00"
    }
  ],
  "recommendations": [
    {
      "type": "planning",
      "priority": "medium",
      "title": "Build Cash Reserves",
      "description": "Aim for 3-6 months of operating expenses in cash reserves"
    }
  ]
}
```

## Banking Integration Endpoints

### POST /api/connect-bank

**Description:** Simulate bank connection (demo purposes)

**Request Body:**
```json
{
  "bank_name": "Chase Bank",
  "credentials": {
    "username": "user@example.com",
    "password": "secure_password"
  }
}
```

**Response:**
```json
{
  "success": true,
  "bank_name": "Chase Bank",
  "account_id": "uuid-string",
  "account_type": "business_checking",
  "last_sync": "2024-01-15T10:30:00Z",
  "available_features": [
    "transaction_sync",
    "balance_monitoring",
    "payment_initiation"
  ]
}
```

### GET /api/executive-dashboard

**Description:** Get executive dashboard data

**Response:**
```json
{
  "summary": {
    "total_balance": 25000.00,
    "total_accounts": 2,
    "net_cash_flow_30d": 3500.00,
    "total_transactions_30d": 87
  },
  "cash_flow": {
    "inflows_30d": 12000.00,
    "outflows_30d": 8500.00,
    "net_flow_30d": 3500.00,
    "daily_burn_rate": 283.33,
    "days_of_cash": 88.2
  },
  "top_categories": [
    {
      "category": "Revenue - Sales",
      "transaction_count": 15,
      "total_amount": 8500.00,
      "percentage": 41.5
    }
  ],
  "alerts": [
    {
      "type": "cash_runway",
      "severity": "medium",
      "message": "Cash runway extends 88 days at current burn rate"
    }
  ],
  "recommendations": [
    {
      "type": "optimization",
      "priority": "medium",
      "title": "Optimize Software & Technology Spending",
      "description": "Review $1,200 monthly software expenses for optimization opportunities"
    }
  ]
}
```

## Reporting Endpoints

### GET /api/month-end-report

**Description:** Generate month-end financial report

**Parameters:**
- `year` (integer, optional): Report year (default: current year)
- `month` (integer, optional): Report month (default: current month)
- `include_comparisons` (boolean, optional): Include previous month comparisons (default: true)

**Response:**
```json
{
  "report_period": {
    "year": 2024,
    "month": 1,
    "month_name": "January",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "executive_summary": {
    "financial_health": "positive",
    "health_message": "Profitable month with $5,500.00 net income",
    "key_highlights": [
      "Generated $18,500.00 in revenue",
      "Positive cash flow of $5,500.00",
      "Healthy expense ratio of 70.3%"
    ],
    "critical_issues": [],
    "total_alerts": 1
  },
  "income_statement": {
    "total_revenue": 18500.00,
    "total_expenses": 13000.00,
    "net_income": 5500.00,
    "gross_margin": 29.7,
    "revenue_breakdown": [
      {
        "category": "Revenue - Sales",
        "amount": 15000.00,
        "transaction_count": 12,
        "percentage_of_revenue": 81.1
      }
    ],
    "expense_breakdown": [
      {
        "category": "Office Expenses",
        "amount": 2500.00,
        "transaction_count": 15,
        "percentage_of_expenses": 19.2
      }
    ]
  },
  "cash_flow_summary": {
    "total_cash_inflows": 18500.00,
    "total_cash_outflows": 13000.00,
    "net_cash_flow": 5500.00,
    "average_daily_inflow": 596.77,
    "average_daily_outflow": 419.35
  },
  "period_comparisons": {
    "revenue_change": {
      "amount_change": 2500.00,
      "percentage_change": 15.6
    },
    "expense_change": {
      "amount_change": -500.00,
      "percentage_change": -3.7
    }
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_CSV_FORMAT` | CSV file format is invalid or corrupt |
| `MISSING_REQUIRED_COLUMNS` | Required columns are missing from CSV |
| `TRANSACTION_NOT_FOUND` | Transaction ID not found |
| `INVALID_DATE_RANGE` | Invalid date range specified |
| `BANK_CONNECTION_FAILED` | Bank connection simulation failed |
| `INSUFFICIENT_DATA` | Not enough data for forecast generation |
| `INVALID_SCENARIO` | Invalid forecast scenario specified |

## Rate Limits

- Standard endpoints: 100 requests per minute
- File upload endpoints: 10 requests per minute
- Forecast generation: 20 requests per minute

## Data Models

### Transaction
```json
{
  "id": "string (UUID)",
  "account_id": "string (UUID)",
  "date": "string (ISO 8601)",
  "description": "string",
  "amount": "number",
  "category": "string (optional)",
  "confidence": "number (0-1)",
  "explanation": "string (optional)",
  "original_csv_row": "integer (optional)",
  "created_at": "string (ISO 8601)"
}
```

### Account
```json
{
  "id": "string (UUID)",
  "name": "string",
  "account_type": "string",
  "balance": "number",
  "created_at": "string (ISO 8601)"
}
```

### Rule
```json
{
  "id": "string (UUID)",
  "description_pattern": "string (regex)",
  "category": "string",
  "confidence": "number (0-1)",
  "created_at": "string (ISO 8601)"
}
```

## SDK and Integration Examples

### Python Example
```python
import requests

# Upload CSV
with open('transactions.csv', 'rb') as f:
    files = {'file': f}
    data = {'account_name': 'Business Account'}
    response = requests.post('http://api.bankmint.ai/api/upload-csv', 
                           files=files, data=data)
    print(response.json())

# Get forecast
forecast_data = {'weeks': 8, 'scenario': 'base'}
response = requests.post('http://api.bankmint.ai/api/forecast', 
                        json=forecast_data)
print(response.json())
```

### JavaScript Example
```javascript
// Upload CSV
const formData = new FormData();
formData.append('file', csvFile);
formData.append('account_name', 'Business Account');

fetch('/api/upload-csv', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// Get transactions
fetch('/api/transactions?limit=50')
.then(response => response.json())
.then(transactions => console.log(transactions));
```

## Webhooks (Future Feature)

BannkMint AI will support webhooks for real-time notifications:

- `transaction.created` - New transaction processed
- `forecast.alert` - Cash flow alert triggered  
- `report.generated` - Monthly report completed

## Support

For API support and questions:
- Documentation: https://docs.bankmintai.com
- Support: api-support@bankmintai.com
- GitHub Issues: https://github.com/bankmintai/api-issues

---

**BannkMint AI SMB Banking OS API v0.2.0**  
*Empowering SMB Financial Intelligence*