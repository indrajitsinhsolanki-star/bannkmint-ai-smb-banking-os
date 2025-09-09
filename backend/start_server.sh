#!/bin/bash
cd /app/backend
exec /root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1