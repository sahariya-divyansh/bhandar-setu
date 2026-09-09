from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db
from app.models import MedicineInventory, Facility
from app.schemas import InventoryItemResponse, InventoryHistoryResponse

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/{facility_id}", response_model=List[InventoryItemResponse])
def get_facility_inventory(facility_id: str, db: Session = Depends(get_db)):
    """Retrieve current stock balance across all medicines for a specific facility."""
    facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility '{facility_id}' not found.")

    # Get latest date per medicine for this facility
    query = text("""
        SELECT 
            i.facility_id,
            i.medicine_id,
            m.medicine_name,
            m.category,
            m.criticality,
            m.unit,
            i.date,
            i.closing_stock,
            i.expiry_date
        FROM medicine_inventory i
        JOIN medicine_catalog m ON i.medicine_id = m.medicine_id
        WHERE i.facility_id = :fid
        AND i.date = (
            SELECT MAX(date) FROM medicine_inventory 
            WHERE facility_id = :fid AND medicine_id = i.medicine_id
        )
        ORDER BY m.medicine_name
    """)

    results = db.execute(query, {"fid": facility_id}).fetchall()
    
    items = []
    for row in results:
        items.append(InventoryItemResponse(
            facility_id=row[0],
            medicine_id=row[1],
            medicine_name=row[2],
            category=row[3],
            criticality=row[4],
            unit=row[5],
            date=str(row[6]),
            closing_stock=row[7],
            expiry_date=str(row[8]) if row[8] else None,
        ))
    return items


@router.get("/{facility_id}/{medicine_id}/history", response_model=List[InventoryHistoryResponse])
def get_inventory_history(
    facility_id: str,
    medicine_id: str,
    limit: int = Query(30, ge=1, le=365, description="Number of historical days to fetch"),
    db: Session = Depends(get_db),
):
    """Retrieve daily inventory transaction history for a facility-medicine pair."""
    records = (
        db.query(MedicineInventory)
        .filter(MedicineInventory.facility_id == facility_id)
        .filter(MedicineInventory.medicine_id == medicine_id)
        .order_by(MedicineInventory.date.desc())
        .limit(limit)
        .all()
    )

    if not records:
        raise HTTPException(status_code=404, detail=f"No inventory records found for facility '{facility_id}' and medicine '{medicine_id}'.")

    response_items = []
    for r in records:
        response_items.append(InventoryHistoryResponse(
            id=r.id,
            facility_id=r.facility_id,
            medicine_id=r.medicine_id,
            date=str(r.date),
            opening_stock=r.opening_stock,
            received_quantity=r.received_quantity,
            dispensed_quantity=r.dispensed_quantity,
            damaged_quantity=r.damaged_quantity,
            closing_stock=r.closing_stock,
            expiry_date=str(r.expiry_date) if r.expiry_date else None,
        ))
    return response_items
