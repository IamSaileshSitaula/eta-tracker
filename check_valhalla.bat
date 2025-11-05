@echo off
echo ================================================
echo Valhalla Routing Server Status Check
echo ================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check container status
echo Checking Valhalla container status...
docker ps -a --filter name=eta-tracker-valhalla --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

REM Check if container is running
docker ps --filter name=eta-tracker-valhalla --format "{{.Names}}" | findstr eta-tracker-valhalla >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Valhalla container is not running
    echo.
    echo Recent logs:
    docker logs eta-tracker-valhalla --tail 20
    exit /b 1
)

echo [OK] Valhalla container is running
echo.

REM Show recent logs
echo Recent activity (last 15 lines):
echo ------------------------------------------------
docker logs eta-tracker-valhalla --tail 15
echo ------------------------------------------------
echo.

REM Test the status endpoint
echo Testing Valhalla status endpoint...
curl -s http://localhost:8002/status >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Valhalla is still initializing (building tiles)
    echo This can take 10-20 minutes on first run.
    echo.
    echo To monitor progress, run: docker logs eta-tracker-valhalla -f
) else (
    echo [SUCCESS] Valhalla is ready and responding!
    echo.
    echo Status response:
    curl -s http://localhost:8002/status
    echo.
    echo.
    echo You can now use Valhalla routing in your application.
    echo Set VALHALLA_URL=http://localhost:8002 in your .env file
)

echo.
echo ================================================
