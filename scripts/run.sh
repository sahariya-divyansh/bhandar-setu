#!/usr/bin/env bash
set -e

echo "=================================================="
echo "      Bhandar Setu — Launching Application Services"
echo "=================================================="
echo "Backend API: http://localhost:8000/docs"
echo "Frontend Web App: http://localhost:5173"
echo "=================================================="

python -c "import subprocess, sys; p1 = subprocess.Popen(['uvicorn', 'app.main:app', '--reload', '--port', '8000'], cwd='backend'); p2 = subprocess.Popen(['npm', 'run', 'dev'], cwd='frontend'); p1.wait(); p2.wait()"
