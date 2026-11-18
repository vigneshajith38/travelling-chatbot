@echo off
cd /d "C:\Users\DELL\Desktop\chatbot"

echo.
echo ========================================================
echo   WANDERWISE - AI-Powered Smart Travel Chatbot
echo ========================================================
echo.

set "PY=C:\Python314\python.exe"
if not exist "%PY%" set "PY=python"

echo [1/2] Starting FastAPI Backend on port 8000...
start "WanderWise BACKEND (keep open)" cmd /k "%PY% run_backend.py"

timeout /t 4 /nobreak >nul

echo [2/2] Starting Vite React Frontend on port 5173...
start "WanderWise FRONTEND (keep open)" cmd /k "cd /d C:\Users\DELL\Desktop\chatbot\frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================================
echo   BOTH SERVERS ARE NOW RUNNING!
echo.
echo   Opening in your browser...
echo   --^> http://localhost:8000  (Unified App - Backend + Chatbot UI)
echo   --^> http://localhost:5173  (Vite React Dev Server)
echo.
echo   DO NOT CLOSE the two black command windows!
echo ========================================================
echo.

start http://localhost:8000

pause
