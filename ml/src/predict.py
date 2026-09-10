"""Demand Forecasting & Stock-Out Risk Prediction Service.

Provides single-facility prediction and district-wide risk ranking.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backend"))

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


def rank_stockout_risks(db: Session, state: Optional[str] = None, district: Optional[str] = None, top_k: Optional[int] = None) -> List[Dict]:
    """Scan facility-medicine pairs using batched SQL queries and vectorized ML inference.
    
    Eliminates N+1 query patterns (reducing 3,900 individual queries to 4 bulk queries).
    Uses heapq top-K selection for O(N log K) algorithmic performance.
    """
    import heapq

    # 1. Fetch facilities matching filter params (1 query)
    fac_query = "SELECT facility_id, facility_name, state, district, facility_type, bed_capacity FROM facilities WHERE 1=1"
    params = {}
    if state:
        fac_query += " AND state = :state"
        params["state"] = state
    if district:
        fac_query += " AND district = :district"
        params["district"] = district

    fac_rows = db.execute(text(fac_query), params).fetchall()
    if not fac_rows:
        return []

    facilities_dict = {
        row[0]: {
            "name": row[1],
            "state": row[2],
            "district": row[3],
            "type": row[4],
            "bed_capacity": row[5],
        }
        for row in fac_rows
    }
    facility_ids = tuple(facilities_dict.keys())

    # 2. Fetch medicine catalog metadata (1 query)
    med_rows = db.execute(
        text("SELECT medicine_id, medicine_name, unit, category, criticality, minimum_stock_days FROM medicine_catalog")
    ).fetchall()
    medicines_dict = {
        row[0]: {
            "name": row[1],
            "unit": row[2],
            "category": row[3],
            "criticality": row[4],
            "min_days": row[5],
        }
        for row in med_rows
    }

    # 3. Bulk fetch latest inventory logs (up to 30 dates per pair) using window function (1 query)
    inv_query = """
        SELECT facility_id, medicine_id, date, closing_stock, dispensed_quantity
        FROM (
            SELECT facility_id, medicine_id, date, closing_stock, dispensed_quantity,
                   ROW_NUMBER() OVER (PARTITION BY facility_id, medicine_id ORDER BY date DESC) as rn
            FROM medicine_inventory
        ) sub
        WHERE rn <= 30
    """
    inv_rows = db.execute(text(inv_query)).fetchall()

    # Organize inventory logs into dictionary keyed by (facility_id, medicine_id)
    inv_by_pair: Dict[Tuple[str, str], List[Tuple]] = {}
    for r in inv_rows:
        fid, mid, dt, closing, dispensed = r[0], r[1], r[2], r[3], r[4]
        if fid in facilities_dict:
            inv_by_pair.setdefault((fid, mid), []).append((dt, closing, dispensed))

    # 4. Bulk fetch latest patient visits per facility (1 query)
    visit_query = """
        SELECT facility_id, fever_cases, diarrhoea_cases, respiratory_cases, maternal_cases
        FROM (
            SELECT facility_id, fever_cases, diarrhoea_cases, respiratory_cases, maternal_cases,
                   ROW_NUMBER() OVER (PARTITION BY facility_id ORDER BY date DESC) as rn
            FROM patient_visits
        ) sub
        WHERE rn = 1
    """
    visit_rows = db.execute(text(visit_query)).fetchall()
    visits_dict = {
        row[0]: {
            "fever_cases": row[1],
            "diarrhoea_cases": row[2],
            "respiratory_cases": row[3],
            "maternal_cases": row[4],
        }
        for row in visit_rows
    }

    # Prepare model artifact
    artifact = get_model_artifact()
    model = artifact["model"]
    med_encoder = artifact["med_encoder"]
    features = artifact["features"]

    # Build feature matrix for vectorized inference
    records = []
    pairs_meta = []

    for fid in facilities_dict:
        fac_info = facilities_dict[fid]
        vis_info = visits_dict.get(fid, {"fever_cases": 10, "diarrhoea_cases": 5, "respiratory_cases": 8, "maternal_cases": 3})

        for mid in medicines_dict:
            med_info = medicines_dict[mid]
            inv_history = inv_by_pair.get((fid, mid), [])

            if not inv_history:
                # Default empty stock prediction
                records.append(None)
                pairs_meta.append({
                    "facility_id": fid,
                    "facility_name": fac_info["name"],
                    "district": fac_info["district"],
                    "state": fac_info["state"],
                    "medicine_id": mid,
                    "medicine_name": med_info["name"],
                    "criticality": med_info["criticality"],
                    "current_stock": 0,
                    "avg_daily_consumption": 0.0,
                    "forecast_14d_demand": 0.0,
                    "days_of_stock_remaining": 0.0,
                    "risk_band": "red",
                    "last_updated": None,
                })
                continue

            latest_record = inv_history[0]
            last_date, current_stock = latest_record[0], latest_record[1]

            dispensed_history = [row[2] for row in inv_history]
            avg_daily_consumption = round(float(sum(dispensed_history) / max(1, len(dispensed_history))), 2)

            last_dt = pd.to_datetime(last_date)
            day_of_week = last_dt.dayofweek
            month = last_dt.month
            is_monsoon = 1 if month in [6, 7, 8, 9] else 0
            is_winter = 1 if month in [12, 1, 2] else 0
            rolling_7d_dispensed = float(sum(dispensed_history[:7]) / max(1, len(dispensed_history[:7])))
            rolling_30d_dispensed = avg_daily_consumption

            try:
                med_encoded = med_encoder.transform([mid])[0]
            except Exception:
                med_encoded = 0

            records.append({
                "bed_capacity": fac_info["bed_capacity"],
                "day_of_week": day_of_week,
                "month": month,
                "is_monsoon": is_monsoon,
                "is_winter": is_winter,
                "rolling_7d_dispensed": rolling_7d_dispensed,
                "rolling_30d_dispensed": rolling_30d_dispensed,
                "fever_cases": vis_info["fever_cases"],
                "diarrhoea_cases": vis_info["diarrhoea_cases"],
                "respiratory_cases": vis_info["respiratory_cases"],
                "maternal_cases": vis_info["maternal_cases"],
                "medicine_encoded": med_encoded,
            })

            pairs_meta.append({
                "facility_id": fid,
                "facility_name": fac_info["name"],
                "district": fac_info["district"],
                "state": fac_info["state"],
                "medicine_id": mid,
                "medicine_name": med_info["name"],
                "criticality": med_info["criticality"],
                "current_stock": current_stock,
                "avg_daily_consumption": avg_daily_consumption,
                "last_updated": str(last_date),
            })

    # Execute vectorized prediction on all valid feature vectors
    valid_indices = [i for i, r in enumerate(records) if r is not None]
    if valid_indices:
        valid_df = pd.DataFrame([records[i] for i in valid_indices])[features]
        predictions = model.predict(valid_df)

        for idx, pred_val in zip(valid_indices, predictions):
            forecast_14d_demand = max(0.0, round(float(pred_val), 1))
            avg_cons = pairs_meta[idx]["avg_daily_consumption"]
            current_stk = pairs_meta[idx]["current_stock"]

            predicted_daily = forecast_14d_demand / 14.0 if forecast_14d_demand > 0 else (avg_cons if avg_cons > 0 else 1.0)
            days_remaining = round(current_stk / predicted_daily, 1) if predicted_daily > 0 else 999.0

            pairs_meta[idx]["forecast_14d_demand"] = forecast_14d_demand
            pairs_meta[idx]["days_of_stock_remaining"] = days_remaining
            pairs_meta[idx]["risk_band"] = calculate_risk_band(days_remaining)

    # Risk priority sorting: red (0), orange (1), yellow (2), green (3)
    risk_priority = {"red": 0, "orange": 1, "yellow": 2, "green": 3}

    if top_k and top_k < len(pairs_meta):
        # Heap selection for top-K items: O(N log K) complexity
        results = heapq.nsmallest(
            top_k,
            pairs_meta,
            key=lambda x: (risk_priority.get(x["risk_band"], 4), x["days_of_stock_remaining"])
        )
    else:
        results = sorted(
            pairs_meta,
            key=lambda x: (risk_priority.get(x["risk_band"], 4), x["days_of_stock_remaining"])
        )

    return results
