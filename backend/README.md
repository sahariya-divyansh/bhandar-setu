# Bhandar Setu — FastAPI Backend

FastAPI backend service providing endpoints for PHC inventory management, stock-out forecasting triggers, and cross-facility redistribution routing.

## Local Execution

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

Access swagger documentation at `http://localhost:8000/docs`.
