@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo GeoAnomaly Pro - Local Development
echo ==========================================
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  py -3.14 -m venv .venv
  if errorlevel 1 (
    echo Python 3.14 was not found. Install Python and try again.
    pause
    exit /b 1
  )
)
echo Installing/updating backend dependencies...
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)
start "GeoAnomaly Pro Backend" cmd /k ""%~dp0.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 >nul
start "GeoAnomaly Pro Frontend" cmd /k "cd /d "%~dp0frontend" && "%~dp0.venv\Scripts\python.exe" -m http.server 5500 --bind 127.0.0.1"
timeout /t 2 >nul
start "" "http://127.0.0.1:5500/"
echo.
echo Frontend: http://127.0.0.1:5500/
echo Backend:  http://127.0.0.1:8000/
echo API docs: http://127.0.0.1:8000/docs
echo.
echo Keep both black terminal windows open while using the program.
pause
