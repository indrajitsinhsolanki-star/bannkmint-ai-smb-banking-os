# BannkMint AI SMB Banking OS - Production Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- **Server**: Ubuntu 20.04+ with 4GB RAM minimum
- **Domain**: SSL certificate required for bank-grade security
- **Database**: PostgreSQL 13+ for production (SQLite for development)
- **Node.js**: 18+ LTS version
- **Python**: 3.11+ with pip

### Production Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Application    │    │    Database     │
│   (Nginx/SSL)   │────│   Server         │────│   PostgreSQL    │
│                 │    │   (Docker)       │    │   (Managed)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🐳 Docker Production Setup

### 1. Create Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: bankmint_prod
      POSTGRES_USER: bankmint
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://bankmint:${DB_PASSWORD}@postgres:5432/bankmint_prod
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${FRONTEND_URL}
    depends_on:
      - postgres
      - redis
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

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

### 2. Backend Production Dockerfile

```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash bankmint
RUN chown -R bankmint:bankmint /app
USER bankmint

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/health || exit 1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "server:app"]
```

### 3. Frontend Production Dockerfile

```dockerfile
# frontend/Dockerfile.prod  
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

### 4. Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8001;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Configuration
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;

        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🔧 Environment Configuration

### Production Environment Variables

```bash
# .env.production
# Database
DATABASE_URL=postgresql://bankmint:${DB_PASSWORD}@localhost:5432/bankmint_prod
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET=your-jwt-secret-here

# CORS
CORS_ORIGINS=https://yourdomain.com

# Frontend
REACT_APP_BACKEND_URL=https://yourdomain.com/api

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASSWORD=your-email-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

```python
# backend/monitoring.py
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def setup_monitoring():
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
    )

    logging.basicConfig(
        level=os.environ.get('LOG_LEVEL', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### 2. Health Checks

```python
# backend/health.py
from fastapi import APIRouter
from sqlalchemy import text
from db import SessionLocal

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    try:
        # Database health
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "0.2.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## 💾 Database Migration

### 1. Production Database Setup

```sql
-- Create production database
CREATE DATABASE bankmint_prod;
CREATE USER bankmint WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bankmint_prod TO bankmint;

-- Enable extensions
\c bankmint_prod;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 2. Migration Script

```python
# scripts/migrate_to_production.py
import os
from sqlalchemy import create_engine
from backend.db import Base

def migrate_database():
    # Production database URL
    database_url = os.environ['DATABASE_URL']
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database migration completed successfully")

if __name__ == "__main__":
    migrate_database()
```

## 🚀 Deployment Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/bankmint-ai.git
cd bankmint-ai

# Set up environment
cp .env.example .env.production
# Edit .env.production with your values

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose exec backend python scripts/migrate_to_production.py

# Verify deployment
curl https://yourdomain.com/api/health
```

### 3. SSL Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📈 Scaling Considerations

### 1. Horizontal Scaling

```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
    
  postgres:
    deploy:
      replicas: 1  # Use managed PostgreSQL for true scaling
```

### 2. Performance Optimization

```python
# backend/optimizations.py
from sqlalchemy.pool import QueuePool

# Database connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_recycle=3600
)

# Redis caching
import redis
redis_client = redis.from_url(REDIS_URL)

def cache_forecast(account_id: str, data: dict):
    redis_client.setex(f"forecast:{account_id}", 300, json.dumps(data))
```

## 🔒 Security Best Practices

### 1. Environment Security

```bash
# Set proper file permissions
chmod 600 .env.production
chown bankmint:bankmint .env.production

# Use secrets management
docker secret create db_password db_password.txt
docker secret create jwt_secret jwt_secret.txt
```

### 2. Application Security

```python
# backend/security.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

# Rate limiting
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(REDIS_URL)
    await FastAPILimiter.init(redis)

# Secure headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
```

## 📊 Backup Strategy

### 1. Database Backups

```bash
#!/bin/bash
# scripts/backup.sh
BACKUP_DIR="/backups"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create database backup
docker-compose exec postgres pg_dump -U bankmint bankmint_prod > $BACKUP_DIR/bankmint_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/bankmint_$DATE.sql s3://your-backup-bucket/

# Keep only last 30 backups
find $BACKUP_DIR -name "bankmint_*.sql" -mtime +30 -delete
```

### 2. Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/scripts/backup.sh
```

## 🎯 Go-Live Checklist

- [ ] Domain and SSL certificate configured
- [ ] Production database setup and migrated
- [ ] Environment variables configured
- [ ] Docker containers deployed and healthy
- [ ] Monitoring and alerting setup
- [ ] Backup strategy implemented
- [ ] Security audit completed
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Team trained on deployment procedures

## 📞 Support & Maintenance

### Monitoring URLs
- **Health Check**: https://yourdomain.com/api/health
- **Database Status**: Monitor connection pool and query performance
- **Application Logs**: Docker logs and Sentry integration

### Maintenance Windows
- **Database Updates**: Sunday 2-4 AM UTC
- **Application Deployments**: Rolling deployments with zero downtime
- **Security Updates**: As needed with emergency procedures

---

## 🚨 Emergency Procedures

### Rollback Process
```bash
# Quick rollback to previous version
docker-compose -f docker-compose.prod.yml down
git checkout previous-stable-tag
docker-compose -f docker-compose.prod.yml up -d
```

### Database Recovery
```bash
# Restore from backup
docker-compose exec postgres psql -U bankmint -d bankmint_prod < backup_file.sql
```

This deployment guide ensures your BannkMint AI SMB Banking OS runs reliably in production with enterprise-grade security, monitoring, and scalability.