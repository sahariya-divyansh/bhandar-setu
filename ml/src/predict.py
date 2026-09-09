"""Inference and stock-out prediction module."""

import argparse
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def predict_stockouts(facility_id: str, days_ahead: int = 30):
    logging.info(f"Generating {days_ahead}-day stock-out forecast for facility: {facility_id}")
    # Demonstration forecast calculation
    predicted_daily_consumption = 42.5
    current_stock = 350
    days_until_stockout = current_stock / predicted_daily_consumption

    is_alert = days_until_stockout <= days_ahead

    result = {
        "facility_id": facility_id,
        "current_stock": current_stock,
        "predicted_daily_consumption": predicted_daily_consumption,
        "estimated_days_remaining": round(days_until_stockout, 1),
        "stockout_risk_30d": is_alert,
    }

    logging.info(f"Prediction result: {result}")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict stock-out risk for a given PHC facility.")
    parser.add_argument("--facility", type=str, default="PHC_001", help="Target PHC Facility ID")
    parser.add_argument("--days", type=int, default=30, help="Forecast horizon in days")
    args = parser.parse_args()

    predict_stockouts(args.facility, args.days)
