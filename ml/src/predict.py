"""Demand Forecasting & Stock-Out Risk Prediction Service.

Provides single-facility prediction and district-wide risk ranking.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

_model_artifact = None


def get_model_artifact():
    """Lazy load and cache model artifact from ml/models/demand_forecaster.joblib."""
    global _model_artifact
    if _model_artifact is None:
        models_dir = Path(__file__).resolve().parent.parent / "models"
        model_path = models_dir / "demand_forecaster.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"Trained model file not found at {model_path}. Run 'python ml/src/train.py' first.")
        logging.info(f"Loading ML model artifact from {model_path}...")
        _model_artifact = joblib.load(model_path)
    return _model_artifact


def calculate_risk_band(days_remaining: float) -> str:
    """Classify stock availability into standardized risk bands."""
    if days_remaining < 3.0:
        return "red"
    elif days_remaining <= 7.0:
        return "orange"
    elif days_remaining <= 21.0:
        return "yellow"
    else:
        return "green"


def predict_facility_medicine(facility_id: str, medicine_id: str, db: Session) -> Dict:
    """Generate 14-day demand forecast and stock-out risk for a facility x medicine pair."""
    artifact = get_model_artifact()
    model = artifact["model"]
    med_encoder = artifact["med_encoder"]
    features = artifact["features"]

    # 1. Fetch facility metadata
    fac_res = db.execute(
        text("SELECT facility_id, facility_name, state, district, facility_type, bed_capacity FROM facilities WHERE facility_id = :fid"),
        {"fid": facility_id}
    ).fetchone()

    if not fac_res:
        raise ValueError(f"Facility '{facility_id}' not found.")

    facility_id, facility_name, state, district, facility_type, bed_capacity = fac_res

    # 2. Fetch medicine catalog metadata
    med_res = db.execute(
        text("SELECT medicine_id, medicine_name, unit, category, criticality, minimum_stock_days FROM medicine_catalog WHERE medicine_id = :mid"),
        {"mid": medicine_id}
    ).fetchone()

    if not med_res:
        raise ValueError(f"Medicine '{medicine_id}' not found.")

    medicine_id, medicine_name, unit, category, criticality, minimum_stock_days = med_res

    # 3. Fetch latest inventory record
    inv_res = db.execute(
        text("""
            SELECT date, closing_stock, dispensed_quantity 
            FROM medicine_inventory 
            WHERE facility_id = :fid AND medicine_id = :mid 
            ORDER BY date DESC 
            LIMIT 30
        """),
        {"fid": facility_id, "mid": medicine_id}
    ).fetchall()

    if not inv_res:
        return {
            "facility_id": facility_id,
            "facility_name": facility_name,
            "district": district,
            "state": state,
            "medicine_id": medicine_id,
            "medicine_name": medicine_name,
            "criticality": criticality,
            "current_stock": 0,
            "avg_daily_consumption": 0.0,
            "forecast_14d_demand": 0.0,
            "days_of_stock_remaining": 0.0,
            "risk_band": "red",
            "last_updated": None,
        }

    latest_record = inv_res[0]
    last_date = latest_record[0]
    current_stock = latest_record[1]

    # Compute historical dispensed quantities
    dispensed_history = [row[2] for row in inv_res]
    avg_daily_consumption = round(float(sum(dispensed_history) / max(1, len(dispensed_history))), 2)

    # 4. Fetch latest patient visits for feature engineering
    visit_res = db.execute(
        text("""
            SELECT fever_cases, diarrhoea_cases, respiratory_cases, maternal_cases 
            FROM patient_visits 
            WHERE facility_id = :fid 
            ORDER BY date DESC 
            LIMIT 1
        """),
        {"fid": facility_id}
    ).fetchone()

    fever_cases = visit_res[0] if visit_res else 10
    diarrhoea_cases = visit_res[1] if visit_res else 5
    respiratory_cases = visit_res[2] if visit_res else 8
    maternal_cases = visit_res[3] if visit_res else 3

    # Feature vector preparation
    last_dt = pd.to_datetime(last_date)
    day_of_week = last_dt.dayofweek
    month = last_dt.month
    is_monsoon = 1 if month in [6, 7, 8, 9] else 0
    is_winter = 1 if month in [12, 1, 2] else 0
    rolling_7d_dispensed = float(sum(dispensed_history[:7]) / max(1, len(dispensed_history[:7])))
    rolling_30d_dispensed = avg_daily_consumption

    # Encode medicine
    try:
        med_encoded = med_encoder.transform([medicine_id])[0]
    except Exception:
        med_encoded = 0

    input_df = pd.DataFrame([{
        "bed_capacity": bed_capacity,
        "day_of_week": day_of_week,
        "month": month,
        "is_monsoon": is_monsoon,
        "is_winter": is_winter,
        "rolling_7d_dispensed": rolling_7d_dispensed,
        "rolling_30d_dispensed": rolling_30d_dispensed,
        "fever_cases": fever_cases,
        "diarrhoea_cases": diarrhoea_cases,
        "respiratory_cases": respiratory_cases,
        "maternal_cases": maternal_cases,
        "medicine_encoded": med_encoded,
    }])[features]

    predicted_14d = float(model.predict(input_df)[0])
    forecast_14d_demand = max(0.0, round(predicted_14d, 1))

    predicted_daily = forecast_14d_demand / 14.0 if forecast_14d_demand > 0 else (avg_daily_consumption if avg_daily_consumption > 0 else 1.0)
    days_remaining = round(current_stock / predicted_daily, 1) if predicted_daily > 0 else 999.0

    risk_band = calculate_risk_band(days_remaining)

    return {
        "facility_id": facility_id,
        "facility_name": facility_name,
        "district": district,
        "state": state,
        "medicine_id": medicine_id,
        "medicine_name": medicine_name,
        "criticality": criticality,
        "current_stock": current_stock,
        "avg_daily_consumption": avg_daily_consumption,
        "forecast_14d_demand": forecast_14d_demand,
        "days_of_stock_remaining": days_remaining,
        "risk_band": risk_band,
        "last_updated": str(last_date),
    }


def rank_stockout_risks(db: Session, state: Optional[str] = None, district: Optional[str] = None) -> List[Dict]:
    """Scan all facility-medicine pairs and rank by highest stock-out risk."""
    query_str = """
        SELECT f.facility_id, m.medicine_id
        FROM facilities f
        CROSS JOIN medicine_catalog m
        WHERE 1=1
    """
    params = {}
    if state:
        query_str += " AND f.state = :state"
        params["state"] = state
    if district:
        query_str += " AND f.district = :district"
        params["district"] = district

    pairs = db.execute(text(query_str), params).fetchall()

    results = []
    for fid, mid in pairs:
        try:
            pred = predict_facility_medicine(fid, mid, db)
            results.append(pred)
        except Exception as e:
            logging.warning(f"Error predicting for pair ({fid}, {mid}): {e}")

    # Risk priority order: red (3), orange (2), yellow (1), green (0)
    risk_priority = {"red": 0, "orange": 1, "yellow": 2, "green": 3}
    results.sort(key=lambda x: (risk_priority.get(x["risk_band"], 4), x["days_of_stock_remaining"]))

    return results
