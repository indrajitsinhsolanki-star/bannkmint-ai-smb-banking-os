# BannkMint AI SMB Banking OS - API Documentation

## 📋 Overview

BannkMint AI provides a comprehensive RESTful API for SMB financial management, including AI-powered transaction categorization, cash flow forecasting, and banking integration.

**Base URL**: `https://api.bannkmint.ai/api`
**API Version**: v0.2.0
**Authentication**: JWT Bearer Token (coming in v0.3.0)

## 🔐 Authentication

Currently in open beta. JWT authentication will be required in production:

```bash
# Future authentication header
Authorization: Bearer <your-jwt-token>
```

## 📊 Core Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "ok": true,
  "version": "0.2.0",
  "service": "BannkMint AI"
}
```

---

## 💰 Transaction Management

### Upload CSV Transactions

```http
POST /api/ingest
Content-Type: multipart/form-data
```

**Parameters:**
- `file` (required): CSV file containing transactions
- `account_id` (optional): Specific account ID

**CSV Format:**
```csv
date,description,amount,balance
2024-01-01,"Office Supplies",-150.00,5000.00
2024-01-02,"Client Payment",2500.00,7500.00
```

**Response:**
```json
{
  "success": true,
  "imported": 24,
  "skipped": 0,
  "total_processed": 24,
  "categorized_pct": 95.8
}
```

### Get Reconciliation Inbox

```http
GET /api/reconcile/inbox?min_conf=0.9&page=1&limit=50
```

**Response:**
```json
{
  "transactions": [
    {
      "id": "uuid",
      "posted_at": "2024-01-01T00:00:00Z",
      "description": "Unknown Merchant",
      "amount": -125.50,
      "category": "Uncategorized",
      "confidence": 0.6,
      "why": "none"
    }
  ],
  "total": 15,
  "page": 1,
  "pages": 1
}
```

---

## 📈 SMB Cash Flow Forecasting

### Get SMB Forecast

```http
GET /api/forecast?weeks=6&scenario=base
```

**Response:**
```json
{
  "forecast_period": "6_weeks",
  "scenario": "base",
  "current_cash": 49061.77,
  "crisis_threshold": 10000.0,
  "daily_projections": [...],
  "smb_patterns": [...],
  "crisis_alerts": [...],
  "business_metrics": {...},
  "scenario_analysis": {...},
  "recommendations": [...],
  "generated_at": "2024-01-01T12:00:00Z"
}
```

### Get Crisis Analysis

```http
GET /api/forecast/crisis-analysis?weeks=6
```

### Get Scenario Planning

```http
GET /api/forecast/scenario-planning?weeks=6
```

---

## 🏦 Banking Integration

### Get Supported Banks

```http
GET /api/banking/institutions
```

### Connect Bank

```http
POST /api/banking/connect?bank_id=chase_business&business_name=My%20Business
```

### Get Financial Overview

```http
GET /api/banking/overview
```

---

## 📊 Month-End Reporting

### Get Month-End Pack

```http
GET /api/reports/month-end?month=12&year=2023
```

---

*BannkMint AI API Documentation v0.2.0 - Built for SMB Financial Intelligence*