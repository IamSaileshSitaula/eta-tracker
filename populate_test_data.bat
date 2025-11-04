@echo off
REM =============================================================================
REM Test Data Population Script
REM =============================================================================
REM 
REM Populates PostgreSQL database with comprehensive test data:
REM   - 2 Organizations (logistics companies)
REM   - 5 Vehicles (trucks and vans)
REM   - 4 Shipment routes with 20+ stops
REM   - Initial GPS positions at Beaumont DC
REM
REM Routes Created:
REM   ROUTE-DW-001   : Downtown + West End Express (5 stops)
REM   ROUTE-RES-001  : Residential Delivery Route (8 stops)
REM   ROUTE-NS-001   : North-South Corridor (6 stops)
REM   ROUTE-FULL-001 : Full City Coverage (10 stops)
REM
REM Prerequisites:
REM   - PostgreSQL running with database 'eta_tracker'
REM   - Backend database schema initialized
REM
REM =============================================================================

echo.
echo ========================================================================
echo   TEST DATA POPULATION
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check for required packages
echo Checking dependencies...
python -c "import psycopg2" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] psycopg2 not found. Installing...
    pip install psycopg2-binary
)

python -c "from dotenv import load_dotenv" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] python-dotenv not found. Installing...
    pip install python-dotenv
)

echo Dependencies OK
echo.

REM Check database connection
echo Checking database connection...
python -c "import os; from dotenv import load_dotenv; import psycopg2; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL'))" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Cannot connect to database!
    echo.
    echo Please ensure:
    echo   1. PostgreSQL is running
    echo   2. Database 'eta_tracker' exists
    echo   3. .env file has correct DATABASE_URL
    echo   4. Database schema is initialized
    echo.
    echo Example DATABASE_URL:
    echo   DATABASE_URL=postgresql://postgres:password@localhost:5432/eta_tracker
    echo.
    pause
    exit /b 1
)
echo Database connected
echo.

REM Confirm before proceeding
echo ========================================================================
echo   WARNING: This will create test data in the database
echo ========================================================================
echo.
echo This will create:
echo   - 2 Organizations
echo   - 5 Vehicles
echo   - 4 Shipments with 20+ delivery stops
echo   - Initial GPS positions
echo.
set /p CONFIRM="Continue? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo.
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo ========================================================================
echo   Creating test data...
echo ========================================================================
echo.

REM Run the test data creation script
python create_test_data.py

if errorlevel 1 (
    echo.
    echo [ERROR] Test data creation failed!
    echo Check error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo   TEST DATA CREATED SUCCESSFULLY
echo ========================================================================
echo.
echo You can now:
echo   1. Start the backend:    start_backend.bat
echo   2. Run a simulator:      start_last_mile_simulator.bat
echo   3. View the dashboard:   npm run dev
echo.
echo Example simulator commands:
echo   start_last_mile_simulator.bat ROUTE-DW-001 1
echo   start_last_mile_simulator.bat ROUTE-RES-001 2
echo   start_last_mile_simulator.bat ROUTE-FULL-001 3
echo.
pause
