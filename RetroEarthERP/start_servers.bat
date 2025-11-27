@echo off
echo ==========================================
echo   Starting RetroEarthERP Servers 🚀
echo ==========================================
echo.

echo 1. Starting Backend Server (Port 8000)...
start "RetroEarthERP Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python.exe -m uvicorn main:app --reload"

echo.
echo 2. Starting Frontend Server (Port 5173)...
start "RetroEarthERP Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ==========================================
echo   Servers are starting in new windows!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ==========================================
pause
