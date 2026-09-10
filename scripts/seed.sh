#!/usr/bin/env bash
set -e

echo "=================================================="
echo "      Bhandar Setu — Database & Model Seeding     "
echo "=================================================="

python ml/src/generate_multistate_data.py
python ml/src/train.py
python ml/src/federated_train.py

echo "=================================================="
echo " Database seeded and ML models updated!"
echo "=================================================="
