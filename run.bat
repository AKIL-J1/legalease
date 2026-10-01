@echo off
REM =========================================================================
REM LegalEase - One-Click Windows Startup Script
REM Launches FastAPI Backend and Streamlit Frontend
REM =========================================================================

echo.
echo =========================================================================
echo               LegalEase - AI Legal Document Generator
echo =========================================================================
echo.

IF NOT EXIST venv (
    echo [INFO] Virtual environment 'venv' not found. Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo [ERROR] Failed to create virtual environment. Ensure Python is installed.
        pause
        exit /b 1
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing / verifying dependencies from requirements.txt...
pip install -r requirements.txt

IF NOT EXIST .env (
    IF EXIST .env.example (
        echo [WARNING] .env not found. Copying .env.example to .env...
        copy .env.example .env
        echo [ACTION REQUIRED] Please edit .env and insert your real GEMINI_API_KEY!
    )
)

echo.
echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000...
start "LegalEase Backend (FastAPI)" cmd /k "venv\Scripts\activate.bat && uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

echo [WAIT] Pausing 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit Frontend on http://localhost:8501...
start "LegalEase Frontend (Streamlit)" cmd /k "venv\Scripts\activate.bat && streamlit run frontend/app.py"

echo.
echo [SUCCESS] LegalEase services launched!
echo - Backend API Docs: http://127.0.0.1:8000/docs
echo - Streamlit Web UI: http://localhost:8501
echo.
pause
