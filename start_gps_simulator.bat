@echo off
echo ========================================================================
echo   UNIFIED GPS SIMULATOR - ETA Tracker
echo ========================================================================
echo.
echo This simulates a complete delivery journey:
echo   Phase 1: Long-haul (Dallas → Houston → Beaumont) ~440 km
echo   Phase 2: Last-mile (Beaumont area deliveries)
echo.
echo Available Last-Mile Routes:
echo   ROUTE-RETAIL-001  - Retail stores (5 stops)
echo   ROUTE-HEALTH-001  - Hospitals and schools (6 stops)
echo   ROUTE-IND-001     - Port and industrial (7 stops)
echo.
echo ========================================================================
echo.

REM Check if route parameter provided
if "%1"=="" (
    echo Starting with default route: ROUTE-RETAIL-001
    echo.
    python unified_gps_simulator.py
) else if "%1"=="--help" (
    python unified_gps_simulator.py --help
) else (
    echo Starting with route: %1
    echo.
    python unified_gps_simulator.py --route %1
)

echo.
echo ========================================================================
echo Simulator stopped
echo ========================================================================
pause
