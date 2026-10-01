#!/usr/bin/env bash
# =========================================================================
# LegalEase - Linux / macOS Startup Script
# Launches FastAPI Backend and Streamlit Frontend
# =========================================================================

set -e

echo "========================================================================="
echo "              LegalEase - AI Legal Document Generator                    "
echo "========================================================================="

if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
fi

echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo "[INFO] Installing dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "[WARNING] .env not found. Copying .env.example to .env..."
        cp .env.example .env
        echo "[ACTION REQUIRED] Please edit .env and insert your real GEMINI_API_KEY!"
    fi
fi

echo "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..."
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 2

echo "[2/2] Starting Streamlit Frontend on http://localhost:8501..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

echo "[SUCCESS] LegalEase services running! Press Ctrl+C to stop."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait
