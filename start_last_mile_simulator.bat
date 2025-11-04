@echo off
REM =============================================================================
REM Last-Mile Delivery GPS Simulator Launcher
REM =============================================================================
REM 
REM Simulates realistic last-mile deliveries in Beaumont with:
REM   - Stop-by-stop progression
REM   - Traffic delays and variations
REM   - Service time at each stop
REM   - Real-time GPS updates
REM
REM Usage:
REM   start_last_mile_simulator.bat [route] [vehicle] [start_stop]
REM
REM Examples:
REM   start_last_mile_simulator.bat                         (default: ROUTE-DW-001, vehicle 1)
REM   start_last_mile_simulator.bat ROUTE-RES-001 2        (residential route, vehicle 2)
REM   start_last_mile_simulator.bat ROUTE-FULL-001 3 5     (full route, vehicle 3, start from stop 5)
REM
REM =============================================================================

echo.
echo ========================================================================
echo   LAST-MILE DELIVERY GPS SIMULATOR
echo ========================================================================
echo.

REM Get parameters or use defaults
set ROUTE=%1
set VEHICLE=%2
set START_STOP=%3

if "%ROUTE%"=="" set ROUTE=ROUTE-RETAIL-001
if "%VEHICLE%"=="" set VEHICLE=1
if "%START_STOP%"=="" set START_STOP=0

echo Configuration:
echo   Route........: %ROUTE%
echo   Vehicle ID...: %VEHICLE%
echo   Start Stop...: %START_STOP%
echo   Update Rate..: 5 seconds
echo.
echo Available Routes:
echo   ROUTE-RETAIL-001  - Retail Express Route (5 stops)
echo   ROUTE-HEALTH-001  - Healthcare ^& Education Route (6 stops)
echo   ROUTE-IND-001     - Industrial ^& Logistics Route (7 stops)
echo.
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

REM Check if backend is running
echo Checking backend connection...
python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Backend not running!
    echo Please start the backend first: start_backend.bat
    echo.
    pause
    exit /b 1
)
echo Backend OK
echo.

REM Run simulator
echo Starting last-mile simulator...
echo Press Ctrl+C to stop
echo.
python simulate_last_mile.py --route %ROUTE% --vehicle %VEHICLE% --start %START_STOP%

echo.
echo ========================================================================
echo Simulator stopped
echo ========================================================================
echo.
pause
