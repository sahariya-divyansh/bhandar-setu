# Bhandar Setu — Machine Learning Subsystem

Forecasting models, feature engineering pipelines, and spatial redistribution algorithms.

## Directory Layout
- `src/`: Core Python modules for training and inference
- `notebooks/`: Exploratory data analysis & model validation notebooks
- `models/`: Serialized model artifacts (`.joblib`)

## Environment Setup & Execution

```bash
pip install -r requirements.txt
python src/train.py
python src/predict.py --facility PHC_001
```
