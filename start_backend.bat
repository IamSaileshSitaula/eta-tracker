@echo off
echo ========================================
echo   ETA Tracker - Backend Server
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

echo [OK] .env file found
echo Starting Flask backend on port 5000...
echo.

REM Run Python from project root so .env loads correctly
python backend\app.py

echo.
echo Backend stopped.
pause
