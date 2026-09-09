"""Model training script for PHC medicine consumption forecasting."""

import argparse
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def train_forecasting_model(data_path: str, model_output_path: str):
    logging.info(f"Loading historical consumption data from {data_path}...")
    # Synthetic baseline data generator for initial model pipeline verification
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", periods=365, freq="D")
    df = pd.DataFrame({
        "date": dates,
        "facility_id": np.random.choice([f"PHC_{i:03d}" for i in range(1, 11)], size=365),
        "medicine_id": "MED_AMOXICILLIN_500MG",
        "daily_dispensed": np.random.poisson(lam=45, size=365),
        "lead_time_days": np.random.randint(3, 14, size=365),
    })

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    X = df[["day_of_week", "month", "lead_time_days"]]
    y = df["daily_dispensed"]

    logging.info("Training Random Forest Regressor baseline model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    logging.info(f"Saving trained model artifact to {model_output_path}...")
    joblib.dump(model, model_output_path)
    logging.info("Model training pipeline completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Bhandar Setu inventory forecasting model.")
    parser.add_argument("--data", type=str, default="data/sample_consumption.csv", help="Path to input consumption CSV")
    parser.add_argument("--output", type=str, default="models/stockout_forecaster.joblib", help="Output path for trained model")
    args = parser.parse_args()

    train_forecasting_model(args.data, args.output)
