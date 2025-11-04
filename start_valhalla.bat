@echo off
REM ==============================================================================
REM Valhalla Routing Engine - Docker Startup Script
REM ==============================================================================
REM 
REM This script starts the Valhalla routing engine in a Docker container.
REM First run will download Texas OSM data and build tiles (10-15 minutes).
REM Subsequent runs will start immediately using cached tiles.
REM 
REM ==============================================================================

echo.
echo =============================================================================
echo   VALHALLA ROUTING ENGINE - DOCKER SETUP
echo =============================================================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found. Please install Docker Desktop:
    echo   https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [INFO] Docker is installed
echo.

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] docker-compose not found, using 'docker compose' command
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

echo [INFO] Using command: %COMPOSE_CMD%
echo.

REM Create valhalla_data directory if it doesn't exist
if not exist "valhalla_data" (
    echo [INFO] Creating valhalla_data directory...
    mkdir valhalla_data
)

REM Check if Valhalla is already running
docker ps | findstr "eta-tracker-valhalla" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Valhalla container is already running!
    echo.
    echo Options:
    echo   1. Stop and restart
    echo   2. Keep running
    echo   3. Exit
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        echo [INFO] Stopping existing container...
        docker stop eta-tracker-valhalla
        docker rm eta-tracker-valhalla
    ) else if "%choice%"=="2" (
        echo [INFO] Keeping existing container running
        echo [INFO] Valhalla is available at: http://localhost:8002
        pause
        exit /b 0
    ) else (
        echo [INFO] Exiting...
        exit /b 0
    )
)

echo =============================================================================
echo   STARTING VALHALLA ROUTING ENGINE
echo =============================================================================
echo.
echo [INFO] This will:
echo   1. Download Valhalla Docker image (if needed)
echo   2. Download Texas OSM data (if needed, ~150 MB)
echo   3. Build routing tiles (if needed, 10-15 minutes)
echo   4. Start Valhalla server on port 8002
echo.
echo [NOTE] First run will take 15-20 minutes. Please be patient!
echo [NOTE] Subsequent runs will start in seconds.
echo.

pause

echo.
echo [INFO] Starting Valhalla with Docker Compose...
%COMPOSE_CMD% -f docker-compose.valhalla.yml up -d

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start Valhalla container!
    echo.
    echo Troubleshooting:
    echo   1. Make sure Docker Desktop is running
    echo   2. Check if port 8002 is available
    echo   3. Check Docker logs: docker logs eta-tracker-valhalla
    echo.
    pause
    exit /b 1
)

echo.
echo =============================================================================
echo   VALHALLA STARTUP IN PROGRESS
echo =============================================================================
echo.
echo [INFO] Container started successfully!
echo.

REM Wait for Valhalla to be ready
echo [INFO] Waiting for Valhalla to initialize...
echo [INFO] This may take a few minutes on first run...
echo.

set RETRY_COUNT=0
set MAX_RETRIES=60

:check_health
set /a RETRY_COUNT+=1
timeout /t 5 /nobreak >nul

REM Check if container is still running
docker ps | findstr "eta-tracker-valhalla" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Container stopped unexpectedly!
    echo [INFO] Checking logs...
    docker logs eta-tracker-valhalla --tail 50
    echo.
    pause
    exit /b 1
)

REM Try to access Valhalla status endpoint
curl -s http://localhost:8002/status >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Valhalla is ready!
    goto :success
)

if %RETRY_COUNT% GEQ %MAX_RETRIES% (
    echo.
    echo [ERROR] Valhalla did not start within 5 minutes!
    echo [INFO] Check logs with: docker logs eta-tracker-valhalla
    echo.
    pause
    exit /b 1
)

echo [INFO] Still initializing... (attempt %RETRY_COUNT%/%MAX_RETRIES%)
goto :check_health

:success
echo.
echo =============================================================================
echo   VALHALLA ROUTING ENGINE - READY!
echo =============================================================================
echo.
echo [SUCCESS] Valhalla is now running!
echo.
echo Connection Details:
echo   URL........: http://localhost:8002
echo   Status.....: http://localhost:8002/status
echo   Route API..: http://localhost:8002/route
echo.
echo Container Management:
echo   View logs..: docker logs eta-tracker-valhalla
echo   Stop.......: docker stop eta-tracker-valhalla
echo   Restart....: docker restart eta-tracker-valhalla
echo   Remove.....: docker rm eta-tracker-valhalla
echo.
echo Next Steps:
echo   1. Update your .env file:
echo      VALHALLA_URL=http://localhost:8002
echo   2. Restart the backend: start_backend.bat
echo   3. Test routing in the dashboard
echo.
echo =============================================================================

REM Test a simple route request
echo [INFO] Testing Valhalla with a sample route...
curl -s -X POST http://localhost:8002/route ^
  -H "Content-Type: application/json" ^
  -d "{\"locations\":[{\"lat\":30.08,\"lon\":-94.126},{\"lat\":30.063,\"lon\":-94.134}],\"costing\":\"auto\"}" | findstr "trip" >nul 2>&1

if not errorlevel 1 (
    echo [SUCCESS] Valhalla routing test successful!
) else (
    echo [WARN] Valhalla routing test failed. Check the logs.
)

echo.
pause
