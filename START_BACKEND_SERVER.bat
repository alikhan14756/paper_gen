@echo off
title ExamForge AI - Centralized Backend Server
color 0A

echo ======================================================================
echo             ExamForge AI - Centralized Backend Server
echo           FastAPI + PostgreSQL/SQLite Authentication Engine
echo ======================================================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtualenv not found in backend\venv.
    echo Please run backend setup first.
    pause
    exit /b 1
)

set PYTHONPATH=.
echo [*] Starting FastAPI Authentication & Paper Generation Service on http://127.0.0.1:8000 ...
echo [*] Centralized Authentication API is ACTIVE.
echo [*] Press CTRL+C at any time to stop the server.
echo.

venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
