"""Demand Forecasting Training Module for Bhandar Setu.

Trains baseline moving average and machine learning (RandomForestRegressor) models
to predict next-14-day medicine consumption per facility-medicine pair.
"""

import json
import logging
import sqlite3
from datetime import datetime, date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_db_path() -> Path:
    """Resolve absolute path to SQLite database."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    db_path = base_dir / "backend" / "bhandar_setu.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}. Run 'python -m app.seed' first.")
    return db_path


def load_dataset() -> pd.DataFrame:
    """Load and merge medicine inventory, patient visits, and facility metadata."""
    db_path = get_db_path()
    logging.info(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(str(db_path))

    query = """
        SELECT 
            i.facility_id,
            i.medicine_id,
            i.date,
            i.opening_stock,
            i.received_quantity,
            i.dispensed_quantity,
            i.closing_stock,
            f.bed_capacity,
            f.facility_type,
            f.district,
            v.total_visits,
            v.fever_cases,
            v.diarrhoea_cases,
            v.respiratory_cases,
            v.maternal_cases
        FROM medicine_inventory i
        JOIN facilities f ON i.facility_id = f.facility_id
        LEFT JOIN patient_visits v ON i.facility_id = v.facility_id AND i.date = v.date
        ORDER BY i.facility_id, i.medicine_id, i.date
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['date'] = pd.to_datetime(df['date'])
    logging.info(f"Loaded {len(df):,} historical daily records.")
    return df


def engineer_features(df: pd.DataFrame):
    """Compute rolling features, seasonal flags, and target 14-day cumulative demand."""
    logging.info("Performing feature engineering...")
    df = df.sort_values(by=['facility_id', 'medicine_id', 'date']).reset_index(drop=True)

    # Date / Calendar features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_monsoon'] = df['month'].isin([6, 7, 8, 9]).astype(int)
    df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)

    # Rolling lagged consumption metrics
    grouped = df.groupby(['facility_id', 'medicine_id'])['dispensed_quantity']
    df['rolling_7d_dispensed'] = grouped.transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean()).fillna(0)
    df['rolling_30d_dispensed'] = grouped.transform(lambda x: x.shift(1).rolling(30, min_periods=1).mean()).fillna(0)

    # Target Variable: Cumulative dispensed quantity over the next 14 days
    def calc_future_14d_sum(series: pd.Series) -> pd.Series:
        # Sum next 14 days of dispensed_quantity
        rev = series.iloc[::-1]
        rolling_sum = rev.rolling(window=14, min_periods=14).sum().iloc[::-1]
        return rolling_sum.shift(-14)

    df['target_14d_demand'] = grouped.transform(calc_future_14d_sum)

    # Encode categorical variables
    med_encoder = LabelEncoder()
    df['medicine_encoded'] = med_encoder.fit_transform(df['medicine_id'])

    # Drop incomplete target rows (the last 14 days of historical dataset)
    clean_df = df.dropna(subset=['target_14d_demand']).copy()
    logging.info(f"Dataset prepared with {len(clean_df):,} valid samples.")
    return clean_df, med_encoder


def train_and_evaluate():
    """Train baseline and ML models, evaluate on held-out test split, and save artifacts."""
    df = load_dataset()
    data, med_encoder = engineer_features(df)

    # Time-based split: last 60 days (2 months) held out for testing
    max_date = data['date'].max()
    cutoff_date = max_date - pd.Timedelta(days=60)

    train_data = data[data['date'] < cutoff_date].copy()
    test_data = data[data['date'] >= cutoff_date].copy()

    min_date_str = data['date'].min().strftime('%Y-%m-%d')
    max_date_str = max_date.strftime('%Y-%m-%d')
    cutoff_str = cutoff_date.strftime('%Y-%m-%d')

    logging.info(f"Train/Test Split | Train: {min_date_str} to {cutoff_str} ({len(train_data):,} rows) | Test: {cutoff_str} to {max_date_str} ({len(test_data):,} rows)")

    # --- 1. Baseline Model Evaluation ---
    # Baseline predicts next 14-day demand as 14 * rolling 30-day average daily consumption
    baseline_predictions = test_data['rolling_30d_dispensed'] * 14.0
    baseline_mae = float(mean_absolute_error(test_data['target_14d_demand'], baseline_predictions))

    # --- 2. Machine Learning Model Training ---
    feature_cols = [
        'bed_capacity',
        'day_of_week',
        'month',
        'is_monsoon',
        'is_winter',
        'rolling_7d_dispensed',
        'rolling_30d_dispensed',
        'fever_cases',
        'diarrhoea_cases',
        'respiratory_cases',
        'maternal_cases',
        'medicine_encoded',
    ]

    X_train = train_data[feature_cols]
    y_train = train_data['target_14d_demand']
    X_test = test_data[feature_cols]
    y_test = test_data['target_14d_demand']

    logging.info("Training RandomForestRegressor model...")
    ml_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
        n_jobs=-1
    )
    ml_model.fit(X_train, y_train)

    ml_predictions = ml_model.predict(X_test)
    ml_mae = float(mean_absolute_error(y_test, ml_predictions))

    improvement_pct = float(((baseline_mae - ml_mae) / baseline_mae) * 100.0)

    print("\n==================================================")
    print("      Demand Forecasting Evaluation Results       ")
    print("==================================================")
    print(f"Data Range:         {min_date_str} to {max_date_str}")
    print(f"Evaluation Window:  Last 60 days ({len(test_data):,} test samples)")
    print(f"Baseline MAE:       {baseline_mae:.2f} units")
    print(f"RandomForest MAE:   {ml_mae:.2f} units")
    print(f"MAE Improvement:    {improvement_pct:.2f}%")
    print("==================================================\n")

    # Save trained model and artifacts
    models_dir = Path(__file__).resolve().parent.parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_artifact_path = models_dir / "demand_forecaster.joblib"
    artifact_payload = {
        "model": ml_model,
        "med_encoder": med_encoder,
        "features": feature_cols,
    }
    joblib.dump(artifact_payload, model_artifact_path)
    logging.info(f"Saved model artifact to {model_artifact_path}")

    # Log summary to training_log.json
    log_payload = {
        "timestamp": datetime.now().isoformat(),
        "data_range": {"min": min_date_str, "max": max_date_str},
        "train_samples": len(train_data),
        "test_samples": len(test_data),
        "baseline_mae": round(baseline_mae, 4),
        "ml_mae": round(ml_mae, 4),
        "mae_improvement_pct": round(improvement_pct, 2),
        "features": feature_cols,
    }
    log_path = models_dir / "training_log.json"
    with open(log_path, "w") as f:
        json.dump(log_payload, f, indent=2)

    logging.info(f"Saved training summary log to {log_path}")
    return baseline_mae, ml_mae, improvement_pct


if __name__ == "__main__":
    train_and_evaluate()
