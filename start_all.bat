@echo off
REM ==============================================================================
REM ETA Tracker - Master Startup Script
REM ==============================================================================
REM 
REM This script starts ALL components in the correct order:
REM 1. PostgreSQL Database
REM 2. Valhalla Routing Engine
REM 3. Backend API
REM 4. Frontend (React)
REM 5. GPS Simulator (optional)
REM 
REM Each component runs in its own terminal window.
REM ==============================================================================

echo.
echo =============================================================================
echo   ETA TRACKER - STARTING ALL COMPONENTS
echo =============================================================================
echo.

REM Check if Docker is running
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop is not running!
    echo.
    echo Please start Docker Desktop first, then run this script again.
    echo.
    pause
    exit /b 1
)

echo [✓] Docker Desktop is running
echo.

REM ============================================================================
REM STEP 1: Start PostgreSQL Database
REM ============================================================================
echo [1/5] Starting PostgreSQL Database...
echo -----------------------------------------------

docker ps --filter name=eta-tracker-db --format "{{.Names}}" | findstr "eta-tracker-db" >nul 2>&1
if errorlevel 1 (
    echo Starting PostgreSQL container...
    docker compose up -d postgres
    echo Waiting 10 seconds for PostgreSQL to initialize...
    timeout /t 10 /nobreak >nul
    echo [✓] PostgreSQL started on port 5432
) else (
    echo [✓] PostgreSQL already running
)
echo.

REM ============================================================================
REM STEP 2: Start Valhalla Routing Engine
REM ============================================================================
echo [2/5] Starting Valhalla Routing Engine...
echo -----------------------------------------------

docker ps --filter name=eta-tracker-valhalla --format "{{.Names}}" | findstr "eta-tracker-valhalla" >nul 2>&1
if errorlevel 1 (
    echo Starting Valhalla in new terminal window...
    echo NOTE: First run will take 10-15 minutes to download OSM data
    start "Valhalla Routing Engine" cmd /k "start_valhalla.bat"
    timeout /t 5 /nobreak >nul
    echo [✓] Valhalla starting in separate window
) else (
    echo [✓] Valhalla already running on port 8002
)
echo.

REM ============================================================================
REM STEP 3: Start Backend API
REM ============================================================================
echo [3/5] Starting Backend API...
echo -----------------------------------------------

REM Check if backend is already running
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo Starting Flask backend in new terminal window...
    start "Backend API - Flask" cmd /k "python backend/app.py"
    timeout /t 3 /nobreak >nul
    echo [✓] Backend API starting on port 5000
) else (
    echo [✓] Backend API already running on port 5000
)
echo.

REM ============================================================================
REM STEP 4: Start Frontend (React)
REM ============================================================================
echo [4/5] Starting Frontend (React + Vite)...
echo -----------------------------------------------

REM Check if frontend is already running
netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo Starting React development server in new terminal window...
    start "Frontend - React + Vite" cmd /k "npm run dev"
    timeout /t 3 /nobreak >nul
    echo [✓] Frontend starting on port 3000
) else (
    echo [✓] Frontend already running on port 3000
)
echo.

REM ============================================================================
REM STEP 5: GPS Simulator (Optional)
REM ============================================================================
echo [5/5] GPS Simulator Options
echo -----------------------------------------------
echo.
echo The GPS Simulator is optional. Would you like to start it?
echo.
echo Available routes:
echo   1. ROUTE-RETAIL-001   (5 retail stops in Beaumont)
echo   2. ROUTE-HEALTH-001   (6 healthcare stops)
echo   3. ROUTE-IND-001      (7 industrial stops)
echo   4. Skip GPS Simulator
echo.

set /p GPS_CHOICE="Enter your choice (1-4): "

if "%GPS_CHOICE%"=="1" (
    echo Starting GPS Simulator with Retail Route...
    start "GPS Simulator - Retail Route" cmd /k "python unified_gps_simulator.py --route ROUTE-RETAIL-001"
    echo [✓] GPS Simulator started with ROUTE-RETAIL-001
) else if "%GPS_CHOICE%"=="2" (
    echo Starting GPS Simulator with Healthcare Route...
    start "GPS Simulator - Healthcare Route" cmd /k "python unified_gps_simulator.py --route ROUTE-HEALTH-001"
    echo [✓] GPS Simulator started with ROUTE-HEALTH-001
) else if "%GPS_CHOICE%"=="3" (
    echo Starting GPS Simulator with Industrial Route...
    start "GPS Simulator - Industrial Route" cmd /k "python unified_gps_simulator.py --route ROUTE-IND-001"
    echo [✓] GPS Simulator started with ROUTE-IND-001
) else (
    echo [⊘] GPS Simulator skipped
)

echo.
echo =============================================================================
echo   🎉 ALL COMPONENTS STARTED SUCCESSFULLY!
echo =============================================================================
echo.
echo Running Services:
echo   ✓ PostgreSQL Database    - Port 5432  (Docker container)
echo   ✓ Valhalla Routing       - Port 8002  (Docker container)
echo   ✓ Backend API            - Port 5000  (Python/Flask)
echo   ✓ Frontend               - Port 3000  (React/Vite)
if not "%GPS_CHOICE%"=="4" (
    echo   ✓ GPS Simulator          - Active    (Sending GPS updates^)
)
echo.
echo Access URLs:
echo   📊 Manager Dashboard:     http://localhost:3000
echo   📦 Customer Tracking:     http://localhost:3000/tracking/PO-98765
echo   🔧 Backend API:           http://localhost:5000
echo   🗺️  Valhalla Status:       http://localhost:8002/status
echo.
echo Each component is running in its own terminal window.
echo Close any terminal to stop that specific component.
echo.
echo Press Ctrl+C in this window to view shutdown options...
echo.

:MENU
echo =============================================================================
echo   CONTROL MENU
echo =============================================================================
echo.
echo   1. Check Status (all services)
echo   2. Open Manager Dashboard in browser
echo   3. Open Customer Tracking in browser
echo   4. Start GPS Simulator (if not running)
echo   5. Stop All Services
echo   6. Exit (keep services running)
echo.

set /p MENU_CHOICE="Enter your choice (1-6): "

if "%MENU_CHOICE%"=="1" goto CHECK_STATUS
if "%MENU_CHOICE%"=="2" goto OPEN_DASHBOARD
if "%MENU_CHOICE%"=="3" goto OPEN_TRACKING
if "%MENU_CHOICE%"=="4" goto START_GPS
if "%MENU_CHOICE%"=="5" goto STOP_ALL
if "%MENU_CHOICE%"=="6" goto EXIT_KEEP_RUNNING

echo Invalid choice. Please try again.
echo.
goto MENU

:CHECK_STATUS
echo.
echo Checking all services...
echo -----------------------------------------------
echo.

echo PostgreSQL Database:
docker ps --filter name=eta-tracker-db --format "  ✓ {{.Names}} - {{.Status}}"
if errorlevel 1 echo   ✗ Not running

echo.
echo Valhalla Routing Engine:
docker ps --filter name=eta-tracker-valhalla --format "  ✓ {{.Names}} - {{.Status}}"
if errorlevel 1 echo   ✗ Not running

echo.
echo Backend API (Port 5000):
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Not listening on port 5000
) else (
    echo   ✓ Listening on port 5000
)

echo.
echo Frontend (Port 3000):
netstat -ano | findstr ":3000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ✗ Not listening on port 3000
) else (
    echo   ✓ Listening on port 3000
)

echo.
echo -----------------------------------------------
echo.
goto MENU

:OPEN_DASHBOARD
echo.
echo Opening Manager Dashboard in browser...
start http://localhost:3000
echo.
goto MENU

:OPEN_TRACKING
echo.
echo Opening Customer Tracking in browser...
start http://localhost:3000/tracking/PO-98765
echo.
goto MENU

:START_GPS
echo.
echo Select GPS Simulator route:
echo   1. ROUTE-RETAIL-001
echo   2. ROUTE-HEALTH-001
echo   3. ROUTE-IND-001
echo.
set /p GPS_ROUTE_CHOICE="Enter route (1-3): "

if "%GPS_ROUTE_CHOICE%"=="1" (
    start "GPS Simulator - Retail" cmd /k "python unified_gps_simulator.py --route ROUTE-RETAIL-001"
) else if "%GPS_ROUTE_CHOICE%"=="2" (
    start "GPS Simulator - Healthcare" cmd /k "python unified_gps_simulator.py --route ROUTE-HEALTH-001"
) else if "%GPS_ROUTE_CHOICE%"=="3" (
    start "GPS Simulator - Industrial" cmd /k "python unified_gps_simulator.py --route ROUTE-IND-001"
)
echo.
goto MENU

:STOP_ALL
echo.
echo =============================================================================
echo   STOPPING ALL SERVICES
echo =============================================================================
echo.

echo Stopping Docker containers...
docker compose down
echo [✓] Docker containers stopped

echo.
echo Stopping Backend and Frontend...
echo (You may need to close the terminal windows manually)
echo.
echo To forcefully kill all Python and Node processes:
echo   taskkill /F /IM python.exe
echo   taskkill /F /IM node.exe
echo.

set /p FORCE_KILL="Force kill all Python and Node processes? (y/n): "
if /i "%FORCE_KILL%"=="y" (
    taskkill /F /IM python.exe 2>nul
    taskkill /F /IM node.exe 2>nul
    echo [✓] All processes killed
)

echo.
echo All services stopped.
pause
exit /b 0

:EXIT_KEEP_RUNNING
echo.
echo Services are still running in background windows.
echo To stop them later, run this script again and choose "Stop All Services"
echo.
pause
exit /b 0
