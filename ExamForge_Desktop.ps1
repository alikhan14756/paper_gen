# ExamForge AI - PowerShell Desktop Launcher
$ErrorActionPreference = "SilentlyContinue"

$Workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Workspace

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "         ExamForge AI - Desktop Software (Offline Mode)" -ForegroundColor Yellow
Write-Host "   Bilingual & BISEP Board Examination Paper Generator for Schools" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$PythonExec = Join-Path $Workspace "backend\venv\Scripts\python.exe"
$Runner = Join-Path $Workspace "desktop\run_desktop.py"

if (-not (Test-Path $PythonExec)) {
    Write-Host "[ERROR] Virtual environment not found at $PythonExec" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[*] Starting local offline engine and desktop window..." -ForegroundColor Green
& $PythonExec $Runner
