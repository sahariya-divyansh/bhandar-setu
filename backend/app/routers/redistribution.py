import logging
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import RedistributionListResponse, RedistributionRecommendationResponse
from app.services.redistribution import recommend_redistributions
from app.services.cache_service import ttl_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/redistribution", tags=["Redistribution Engine"])


from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

@router.get("/recommendations", response_model=RedistributionListResponse)
@ttl_cache(ttl_seconds=300)
def get_redistribution_recommendations(
    state: Optional[str] = Query(None, description="Filter recommendations by State"),
    district: Optional[str] = Query(None, description="Filter recommendations by District"),
    db: Session = Depends(get_db),
):
    """Calculate and return optimal cross-facility stock transfer recommendations for deficit facilities."""
    t0 = time.perf_counter()
    try:
        recs = recommend_redistributions(db, state=state, district=district)
        items = [RedistributionRecommendationResponse(**r) for r in recs]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        logger.info(f"[/redistribution/recommendations] Executed in {elapsed_ms:.2f} ms for state='{state}', district='{district}'")
        res_obj = RedistributionListResponse(
            total_recommendations=len(items),
            items=items,
        )
        return JSONResponse(content=jsonable_encoder(res_obj))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating redistribution recommendations: {str(e)}")
