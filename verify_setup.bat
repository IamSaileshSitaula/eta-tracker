@echo off
REM =============================================================================
REM System Verification Script
REM =============================================================================
REM 
REM Checks that all components are properly configured:
REM   - Python and Node.js versions
REM   - Required packages installed
REM   - Database connection and schema
REM   - Test data populated
REM   - Backend server status
REM
REM Run this after initial setup to verify everything works.
REM
REM =============================================================================

echo.
echo ========================================================================
echo   SYSTEM VERIFICATION
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

echo Running verification checks...
echo.

REM Run verification script
python verify_setup.py

echo.
pause
