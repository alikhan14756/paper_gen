@echo off
title ExamForge AI - Offline Examination Paper Generator
color 0F

echo ======================================================================
echo          ExamForge AI - Desktop Software (Offline Mode)
echo    Bilingual & BISEP Board Examination Paper Generator for Schools
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Check Python virtual environment
if not exist "backend\venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found in backend\venv.
    echo Please ensure Python is configured properly.
    pause
    exit /b 1
)

:: 2. Launch Desktop Application via Python runner
echo [*] Launching ExamForge AI Offline Desktop Software...
echo [*] Initializing local database and document processing engine...
echo [*] Opening desktop application window...
echo.

backend\venv\Scripts\python.exe desktop\run_desktop.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Fallback: Launching standalone browser app window...
    start msedge --app=http://localhost:3000
)

exit /b 0
