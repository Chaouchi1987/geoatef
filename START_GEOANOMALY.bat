@echo off
setlocal EnableExtensions
title GeoAnomaly Pro - Local Launcher

cd /d "%~dp0"

echo ==========================================
echo        GeoAnomaly Pro - Local
echo ==========================================
echo.
echo Project folder:
echo %CD%
echo.

if not exist "%~dp0backend\main.py" (
    echo [ERROR] The complete project was not extracted.
    echo.
    echo You are probably running this BAT file directly from WinRAR/7-Zip.
    echo Please:
    echo   1. Close this window.
    echo   2. Right-click the ZIP file.
    echo   3. Choose "Extract All..."
    echo   4. Open the extracted GeoAnomalyPro folder.
    echo   5. Run START_GEOANOMALY.bat there.
    echo.
    pause
    exit /b 1
)

if not exist "%~dp0.env" (
    if exist "%~dp0.env.example" copy /Y "%~dp0.env.example" "%~dp0.env" >nul
    echo [INFO] Created local .env from .env.example.
    echo [INFO] Google OAuth still needs to be configured by the platform owner.
    echo.
)

if not exist "%~dp0requirements.txt" (
    echo [ERROR] requirements.txt is missing.
    echo The project extraction is incomplete.
    echo Please extract the ZIP again using "Extract All...".
    echo.
    pause
    exit /b 1
)

where py >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python launcher "py" was not found.
    echo Install Python 3.13 or 3.14 and enable the Python launcher.
    echo.
    pause
    exit /b 1
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3.14 -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo Python 3.14 was not available. Trying Python 3.13...
        py -3.13 -m venv "%~dp0.venv"
        if errorlevel 1 (
            echo [ERROR] Python 3.13/3.14 was not found.
            pause
            exit /b 1
        )
    )
)

echo.
echo Installing/updating backend dependencies...
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
"%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed.
    echo Copy the error above and send it to me.
    pause
    exit /b 1
)

echo.
echo Starting FastAPI backend...
start "GeoAnomaly Pro - Backend" cmd /k "cd /d ""%~dp0"" && ""%~dp0.venv\Scripts\python.exe"" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 4 /nobreak >nul

echo Starting frontend server...
start "GeoAnomaly Pro - Frontend" cmd /k "cd /d ""%~dp0frontend"" && ""%~dp0.venv\Scripts\python.exe"" -m http.server 5500 --bind 127.0.0.1"

timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo Frontend : http://127.0.0.1:5500/
echo Backend  : http://127.0.0.1:8000/
echo API Docs : http://127.0.0.1:8000/docs
echo ==========================================
echo.
echo Opening GeoAnomaly Pro...
start "" "http://127.0.0.1:5500/"

echo.
echo Keep the Backend and Frontend windows open.
echo Press any key to close this launcher only.
pause >nul
