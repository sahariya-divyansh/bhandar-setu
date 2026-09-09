from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import (
    AlertExplanationResponse,
    OfficerBriefingResponse,
    TranslateRequest,
    TranslateResponse,
)

import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parents[3]
ml_dir = root_dir / "ml"
if str(ml_dir) not in sys.path:
    sys.path.insert(0, str(ml_dir))

from ml.src.predict import predict_facility_medicine, rank_stockout_risks
from app.services.redistribution import recommend_redistributions
from app.services import gemini_service

router = APIRouter(prefix="/insights", tags=["GenAI Insights Core"])


@router.get("/alert-explanation/{facility_id}/{medicine_id}", response_model=AlertExplanationResponse)
def get_alert_explanation(facility_id: str, medicine_id: str, db: Session = Depends(get_db)):
    """Generate plain-language clinical explanation of WHY a stock-out risk was flagged for a facility-medicine pair."""
    try:
        forecast_data = predict_facility_medicine(facility_id, medicine_id, db)
        explanation = gemini_service.explain_risk_alert(
            facility_name=forecast_data["facility_name"],
            medicine_name=forecast_data["medicine_name"],
            forecast_data=forecast_data,
        )
        return AlertExplanationResponse(
            facility_id=facility_id,
            medicine_id=medicine_id,
            explanation=explanation,
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating risk explanation: {str(e)}")


@router.get("/officer-briefing", response_model=OfficerBriefingResponse)
def get_officer_briefing(
    district: str = Query(..., description="Target District name for executive briefing"),
    db: Session = Depends(get_db),
):
    """Generate a concise executive briefing for District Health Officers (DHO) summarizing top risks and transfers."""
    try:
        risk_summary_items = rank_stockout_risks(db, district=district)
        high_risk_count = sum(1 for item in risk_summary_items if item["risk_band"] in ["red", "orange"])

        risk_summary_data = {
            "district": district,
            "high_risk_count": high_risk_count,
            "total_items_evaluated": len(risk_summary_items),
        }

        recs = recommend_redistributions(db, district=district)

        briefing_text = gemini_service.generate_officer_briefing(
            district=district,
            risk_summary=risk_summary_data,
            recommendations=recs,
        )

        return OfficerBriefingResponse(
            district=district,
            briefing=briefing_text,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating officer briefing: {str(e)}")


@router.post("/translate", response_model=TranslateResponse)
def translate_alert_text(payload: TranslateRequest):
    """Translate clinical supply chain alert text into target language (default: Hindi 'hi')."""
    try:
        translated = gemini_service.translate_alert(
            text_content=payload.text,
            target_language=payload.target_language,
        )
        return TranslateResponse(
            target_language=payload.target_language,
            translated_text=translated,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating alert text: {str(e)}")
