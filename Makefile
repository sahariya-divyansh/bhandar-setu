.PHONY: setup seed test run run-backend run-frontend clean

setup:
	@echo "=== Setting up Bhandar Setu Environment ==="
	pip install -r backend/requirements.txt
	python ml/src/generate_multistate_data.py
	python ml/src/train.py
	python ml/src/federated_train.py
	cd frontend && npm install
	@echo "=== Setup Complete! Run 'make run' to start services. ==="

seed:
	@echo "=== Generating Multi-State Dataset & Training ML Models ==="
	python ml/src/generate_multistate_data.py
	python ml/src/train.py
	python ml/src/federated_train.py

test:
	@echo "=== Running Backend Pytest Test Suite ==="
	cd backend && python -m pytest

run-backend:
	cd backend && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

run:
	@echo "=== Starting Bhandar Setu Backend & Frontend ==="
	@echo "Backend API: http://localhost:8000/docs"
	@echo "Frontend Web App: http://localhost:5173"
	python -c "import subprocess, sys; p1 = subprocess.Popen(['uvicorn', 'app.main:app', '--reload', '--port', '8000'], cwd='backend'); p2 = subprocess.Popen(['npm', 'run', 'dev'], cwd='frontend'); p1.wait(); p2.wait()"

clean:
	rm -f backend/bhandar_setu.db backend/tests/test_bhandar_setu.db
	rm -rf backend/.pytest_cache ml/models/*.joblib ml/models/*.json
