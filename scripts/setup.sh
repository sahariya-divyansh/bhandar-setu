#!/usr/bin/env bash
set -e

echo "=================================================="
echo "      Bhandar Setu — One-Command Environment Setup "
echo "=================================================="

# 1. Install Backend Dependencies
echo "[1/4] Installing Python Backend dependencies..."
pip install -r backend/requirements.txt
pip install pytest httpx

# 2. Seed Multi-State Database
echo "[2/4] Generating realistic multi-state dataset (65 facilities, 400K+ records)..."
python ml/src/generate_multistate_data.py

# 3. Train Demand Forecaster & Federated Learning Models
echo "[3/4] Training demand forecasting ML model & federated learning simulation..."
python ml/src/train.py
python ml/src/federated_train.py

# 4. Install Frontend Dependencies
echo "[4/4] Installing Node.js frontend dependencies..."
cd frontend
npm install
cd ..

echo "=================================================="
echo " Setup Completed Successfully!"
echo " Run 'make run' or 'bash scripts/run.sh' to launch."
echo "=================================================="
