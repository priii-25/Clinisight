@echo off
echo Starting Clinisight Application...

REM Activate virtual environment and start backend
echo ========================================
echo Starting Backend (Flask)...
echo ========================================
start "Clinisight Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python app.py"

REM Wait a moment then start frontend
timeout /t 3

echo ========================================
echo Starting Frontend (React)...
echo ========================================
start "Clinisight Frontend" cmd /k "cd /d %~dp0\frontend && npm start"

echo.
echo ========================================
echo Clinisight Application Started!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul