import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import ForecastResponse, RiskSummaryResponse

# Resolve monorepo root directory dynamically
# forecast.py -> routers -> app -> backend -> bhandar-setu (root)
root_dir = Path(__file__).resolve().parents[3]
ml_dir = root_dir / "ml"
if str(ml_dir) not in sys.path:
    sys.path.insert(0, str(ml_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from ml.src.predict import predict_facility_medicine, rank_stockout_risks

router = APIRouter(prefix="/forecast", tags=["Forecasting & Risk Engine"])


@router.get("/risk-summary", response_model=RiskSummaryResponse)
def get_risk_summary(
    state: Optional[str] = Query(None, description="Filter stock-out risks by State"),
    district: Optional[str] = Query(None, description="Filter stock-out risks by District"),
    db: Session = Depends(get_db),
):
    """Retrieve district-wide ranked list of facility-medicine pairs ordered by stock-out risk."""
    try:
        ranked_items = rank_stockout_risks(db, state=state, district=district)
        
        high_risk_count = sum(1 for item in ranked_items if item["risk_band"] in ["red", "orange"])
        unique_facilities = len(set(item["facility_id"] for item in ranked_items))

        forecast_responses = [ForecastResponse(**item) for item in ranked_items]

        return RiskSummaryResponse(
            total_facilities_monitored=unique_facilities,
            high_risk_count=high_risk_count,
            total_items_evaluated=len(ranked_items),
            items=forecast_responses,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating stock-out risk summary: {str(e)}")


@router.get("/{facility_id}/{medicine_id}", response_model=ForecastResponse)
def get_forecast_by_facility_medicine(
    facility_id: str,
    medicine_id: str,
    db: Session = Depends(get_db),
):
    """Fetch 14-day demand forecast and stock-out risk assessment for a specific facility-medicine pair."""
    try:
        prediction = predict_facility_medicine(facility_id, medicine_id, db)
        return ForecastResponse(**prediction)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting engine error: {str(e)}")
