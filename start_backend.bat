@echo off
set DATABASE_URL=postgresql://neondb_owner:npg_XYhRk2Jts9HM@ep-wild-wave-aqox6lif-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require^&channel_binding=require
set ML_PIPELINE_PATH=..\ml
set SECRET_KEY=dev-secret-change-in-production
set ENVIRONMENT=development
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
