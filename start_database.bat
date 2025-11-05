@echo off
echo ========================================
echo  Starting PostgreSQL Database
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Start PostgreSQL
echo Starting PostgreSQL container...
docker compose up -d postgres

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start PostgreSQL
    pause
    exit /b 1
)

echo.
echo Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul

REM Check health status
docker compose ps postgres

echo.
echo ========================================
echo PostgreSQL is starting up!
echo ========================================
echo.
echo Connection Details:
echo   Host: localhost
echo   Port: 5432
echo   Database: eta_tracker
echo   Username: eta_user
echo   Password: eta_pass_dev_123
echo.
echo These credentials are already set in your .env file.
echo.
echo To stop: docker compose down
echo To view logs: docker compose logs postgres -f
echo.
pause
