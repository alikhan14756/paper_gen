# Launch Script for ExamForge AI
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " Starting ExamForge AI Development Stack " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check Python backend venv
if (Test-Path ".\backend\venv\Scripts\python.exe") {
    Write-Host "Starting Backend FastAPI on http://localhost:8000..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='backend'; .\backend\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"
} else {
    Write-Host "Backend virtualenv not found!" -ForegroundColor Red
}

# Start Frontend
Write-Host "Starting Frontend Next.js on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Both servers launched. Open http://localhost:3000 in your browser." -ForegroundColor Yellow
