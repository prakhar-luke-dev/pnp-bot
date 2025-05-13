#!/bin/bash
pip install -r requirements.txt
set -e

# Run setup first
python3 app/main.py

# Start server with multiple workers
cd app_vida
exec uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4