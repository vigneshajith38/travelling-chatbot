@echo off
cd /d "%~dp0"

echo.
echo ========================================================
echo   WANDERWISE - AI-Powered Smart Travel Chatbot
echo ========================================================
echo.

:: 1. Auto-detect Python executable
set "PY=python"
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY=py"
    ) else if exist "C:\Python314\python.exe" (
        set "PY=C:\Python314\python.exe"
    ) else if exist "C:\Python312\python.exe" (
        set "PY=C:\Python312\python.exe"
    ) else if exist "C:\Python311\python.exe" (
        set "PY=C:\Python311\python.exe"
    ) else (
        echo [ERROR] Python was not found on your system PATH!
        echo Please make sure Python is installed and added to PATH.
        pause
        exit /b 1
    )
)

echo [OK] Using Python: %PY%

:: 2. Start Backend on port 8000
echo [1/2] Starting FastAPI Backend on port 8000...
start "WanderWise BACKEND (Keep Open)" cmd /k "cd /d ""%~dp0"" && %PY% run_backend.py"

timeout /t 4 /nobreak >nul

:: 3. Start Frontend on port 5173
echo [2/2] Starting Vite React Frontend on port 5173...
start "WanderWise FRONTEND (Keep Open)" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================================
echo   BOTH SERVERS ARE RUNNING!
echo.
echo   Opening http://localhost:8000 in your browser...
echo.
echo   NOTE: Keep the two server command windows open!
echo ========================================================
echo.

start http://localhost:8000
