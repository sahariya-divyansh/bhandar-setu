from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import RedistributionListResponse, RedistributionRecommendationResponse
from app.services.redistribution import recommend_redistributions

router = APIRouter(prefix="/redistribution", tags=["Redistribution Engine"])


@router.get("/recommendations", response_model=RedistributionListResponse)
def get_redistribution_recommendations(
    state: Optional[str] = Query(None, description="Filter recommendations by State"),
    district: Optional[str] = Query(None, description="Filter recommendations by District"),
    db: Session = Depends(get_db),
):
    """Calculate and return optimal cross-facility stock transfer recommendations for deficit facilities."""
    try:
        recs = recommend_redistributions(db, state=state, district=district)
        items = [RedistributionRecommendationResponse(**r) for r in recs]
        return RedistributionListResponse(
            total_recommendations=len(items),
            items=items,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating redistribution recommendations: {str(e)}")
