"""Cross-facility stock redistribution engine using Haversine spatial optimization."""

import math
import sys
from pathlib import Path
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Ensure ML package is available
root_dir = Path(__file__).resolve().parents[3]
ml_dir = root_dir / "ml"
if str(ml_dir) not in sys.path:
    sys.path.insert(0, str(ml_dir))

from ml.src.predict import predict_facility_medicine, calculate_risk_band


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great-Circle distance between two geographic coordinates in kilometers."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def recommend_redistributions(
    db: Session,
    state: Optional[str] = None,
    district: Optional[str] = None,
    speed_km_per_day: float = 25.0,
) -> List[Dict]:
    """Identify high-risk deficit facilities and match with optimal nearby donor facilities with surplus stock.

    This service generates recommendations only and does NOT execute automated transfers.
    """
    # 1. Fetch facilities metadata lookup
    fac_query = "SELECT facility_id, facility_name, state, district, latitude, longitude, facility_type FROM facilities WHERE 1=1"
    params = {}
    if state:
        fac_query += " AND state = :state"
        params["state"] = state
    if district:
        fac_query += " AND district = :district"
        params["district"] = district

    fac_rows = db.execute(text(fac_query), params).fetchall()
    facilities_map = {
        row[0]: {
            "facility_id": row[0],
            "facility_name": row[1],
            "state": row[2],
            "district": row[3],
            "latitude": row[4],
            "longitude": row[5],
            "facility_type": row[6],
        }
        for row in fac_rows
    }

    if not facilities_map:
        return []

    # 2. Fetch all medicine catalog items
    med_rows = db.execute(text("SELECT medicine_id, medicine_name, unit, minimum_stock_days FROM medicine_catalog")).fetchall()
    medicines_map = {row[0]: {"medicine_name": row[1], "unit": row[2], "min_days": row[3]} for row in med_rows}

    # 3. Evaluate stock status for all facility-medicine combinations
    evaluations: List[Dict] = []
    for fid in facilities_map:
        for mid in medicines_map:
            try:
                pred = predict_facility_medicine(fid, mid, db)
                evaluations.append(pred)
            except Exception:
                continue

    # Split into Deficits (risk band red/orange) and Potential Donors (days remaining > 21)
    deficits = [e for e in evaluations if e["risk_band"] in ["red", "orange"]]
    donors = [e for e in evaluations if e["days_of_stock_remaining"] > 21.0]

    recommendations = []

    for def_item in deficits:
        dest_fid = def_item["facility_id"]
        med_id = def_item["medicine_id"]
        dest_info = facilities_map[dest_fid]
        med_info = medicines_map[med_id]

        dest_stock = def_item["current_stock"]
        dest_daily_cons = def_item["avg_daily_consumption"]
        days_left = def_item["days_of_stock_remaining"]

        # Calculate target stock deficit quantity for 30-day buffer
        target_buffer = max(1, int(30 * dest_daily_cons))
        needed_qty = max(10, target_buffer - dest_stock)

        # Search for potential donor facilities with surplus of the exact same medicine
        candidate_donors = [
            d for d in donors
            if d["medicine_id"] == med_id and d["facility_id"] != dest_fid
        ]

        best_donor = None
        best_score = -float("inf")
        best_details = None

        for d_item in candidate_donors:
            donor_fid = d_item["facility_id"]
            donor_info = facilities_map[donor_fid]

            donor_stock = d_item["current_stock"]
            donor_daily_cons = d_item["avg_daily_consumption"]
            donor_min_days = med_info["min_days"]

            # Calculate donor's true surplus (capped so donor retains minimum buffer)
            reserved_stock = int(donor_min_days * donor_daily_cons)
            available_surplus = max(0, donor_stock - reserved_stock)

            if available_surplus <= 0:
                continue

            # Compute Haversine distance
            dist_km = haversine_distance(
                donor_info["latitude"], donor_info["longitude"],
                dest_info["latitude"], dest_info["longitude"]
            )

            # Estimate transit days
            transit_days = max(1, math.ceil(dist_km / speed_km_per_day))

            # Feasibility Check: Will shipment arrive before destination experiences stock-out?
            # Arriving within projected days left gets bonus score
            is_timely = transit_days <= max(1, math.ceil(days_left) + 2)

            # Scoring Algorithm:
            # - Distance penalty: -1.0 per km
            # - Same district bonus: +50 points
            # - Timely delivery bonus: +100 points
            # - Surplus coverage ratio: up to +30 points
            same_district_bonus = 50.0 if donor_info["district"] == dest_info["district"] else 0.0
            timely_bonus = 100.0 if is_timely else 0.0
            coverage_ratio = min(1.0, available_surplus / max(1, needed_qty)) * 30.0

            score = timely_bonus + same_district_bonus + coverage_ratio - (dist_km * 0.8)

            if score > best_score:
                best_score = score
                best_donor = d_item
                suggested_qty = min(needed_qty, available_surplus)
                avoided_days = round(suggested_qty / max(0.1, dest_daily_cons), 1)

                best_details = {
                    "source_facility_id": donor_fid,
                    "source_facility_name": donor_info["facility_name"],
                    "source_district": donor_info["district"],
                    "source_state": donor_info["state"],
                    "source_current_stock": donor_stock,
                    "source_surplus_available": available_surplus,
                    "destination_facility_id": dest_fid,
                    "destination_facility_name": dest_info["facility_name"],
                    "destination_district": dest_info["district"],
                    "destination_state": dest_info["state"],
                    "destination_current_stock": dest_stock,
                    "days_of_stock_remaining": days_left,
                    "medicine_id": med_id,
                    "medicine_name": med_info["medicine_name"],
                    "unit": med_info["unit"],
                    "suggested_quantity": suggested_qty,
                    "distance_km": round(dist_km, 1),
                    "estimated_transit_days": transit_days,
                    "shortage_avoided_days": avoided_days,
                    "urgency": "critical" if days_left < 3.0 else "high",
                    "status": "Recommendation Generated",
                }

        if best_details:
            recommendations.append(best_details)

    # Sort recommendations by urgency (critical first, then shortest transit time)
    recommendations.sort(key=lambda r: (0 if r["urgency"] == "critical" else 1, r["estimated_transit_days"], r["distance_km"]))
    return recommendations
