from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Facility
from app.schemas import FacilityResponse

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.get("", response_model=List[FacilityResponse])
def get_facilities(
    state: Optional[str] = Query(None, description="Filter facilities by State name"),
    district: Optional[str] = Query(None, description="Filter facilities by District name"),
    db: Session = Depends(get_db),
):
    """Retrieve list of healthcare facilities (PHCs, CHCs, SCs) filterable by location."""
    query = db.query(Facility)
    if state:
        query = query.filter(Facility.state == state)
    if district:
        query = query.filter(Facility.district == district)
    
    facilities = query.all()
    return facilities


@router.get("/{facility_id}", response_model=FacilityResponse)
def get_facility_by_id(facility_id: str, db: Session = Depends(get_db)):
    """Fetch metadata for a specific facility by ID."""
    facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility '{facility_id}' not found.")
    return facility
