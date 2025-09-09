# BannkMint AI SMB Banking OS - Production Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- **Server**: Ubuntu 20.04+ with 4GB RAM minimum
- **Domain**: SSL certificate required for bank-grade security
- **Database**: PostgreSQL 13+ for production (SQLite for development)
- **Node.js**: 18+ LTS version
- **Python**: 3.11+ with pip

## 🐳 Docker Production Setup

### 1. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bannkmint_prod
      POSTGRES_USER: bannkmint
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://bannkmint:${DB_PASSWORD}@postgres:5432/bannkmint_prod
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${FRONTEND_URL}
    depends_on:
      - postgres
    ports:
      - "8001:8001"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - REACT_APP_BACKEND_URL=${BACKEND_URL}
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### 2. Environment Variables

```bash
# .env.production
DATABASE_URL=postgresql://bannkmint:password@localhost:5432/bannkmint_prod
SECRET_KEY=your-super-secret-key
CORS_ORIGINS=https://yourdomain.com
REACT_APP_BACKEND_URL=https://yourdomain.com/api
```

## 🚀 Deployment Steps

### 1. Clone Repository
```bash
git clone https://github.com/bannkmint/bannkmint-ai.git
cd bannkmint-ai
```

### 2. Configure Environment
```bash
cp .env.example .env.production
# Edit with your production values
```

### 3. Deploy with Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Verify Deployment
```bash
curl https://yourdomain.com/api/health
```

## 🎯 Go-Live Checklist

- [ ] Domain and SSL certificate configured
- [ ] Production database setup and migrated
- [ ] Environment variables configured
- [ ] Docker containers deployed and healthy
- [ ] Monitoring and alerting setup
- [ ] Backup strategy implemented

---

*BannkMint AI Production Deployment Guide v0.2.0*