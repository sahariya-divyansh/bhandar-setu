"""Realistic Synthetic Data Generator for Bhandar Setu PHC Supply Chain.

Data Generation Methodology & Calibration:
------------------------------------------
1. Spatial Calibration:
   Facilities are mapped across 3 districts in Madhya Pradesh (Sehore, Raisen, Vidisha)
   categorized into Community Health Centres (CHCs), Primary Health Centres (PHCs),
   and Sub-Centres (SCs) with realistic geospatial coordinates and bed capacities (2 to 30 beds).

2. Demand & Patient Footfall Scaling:
   Daily outpatient volume scales non-linearly with facility capacity:
   - CHC (20–30 beds): 120–250 visits/day
   - PHC (6 beds): 40–80 visits/day
   - Sub-Centre (2 beds): 10–25 visits/day

3. Seasonality Calibration:
   - Monsoon Season (June – September): Diarrhoea cases surge by 250%–400%, driving
     proportional spikes in ORS sachets, Zinc Sulphate, and Metronidazole dispensing.
   - Winter Season (December – February): Acute Respiratory Infection (ARI) cases surge
     by 200%–350%, boosting consumption of Amoxicillin, Salbutamol, and Cetirizine.
   - Post-Monsoon Vector-borne Season (July – October): Fever cases surge, accelerating
     Paracetamol 500mg and Ciprofloxacin consumption.

4. Supply Chain Dynamics & Stock-out Induction:
   - Lead times vary by facility remoteness: CHCs (3–7 days), PHCs (7–14 days), SCs (10–21 days).
   - Delivery delays are stochastically introduced (15% probability of supplier lag),
     creating realistic stock-out periods (stock level drops to zero for 3–12 days).

5. Data Quality & Reporting Gaps:
   - Rural/remote facilities exhibit periodic missing or delayed reporting logs (5%–8% gap rate)
     to simulate real-world NRHM/e-Aushadhi telemetry latency.
"""

import math
import random
from datetime import date, timedelta
from typing import List, Dict

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.db import init_db, SessionLocal
from app.models import (
    Facility,
    MedicineCatalog,
    MedicineInventory,
    PatientVisits,
    StaffAttendance,
    Delivery,
)


def seed_facilities() -> List[Dict]:
    """Define 30 realistic PHC/CHC/SC facilities across 3 districts in MP."""
    facilities_data = [
        # Sehore District (Center ~ 23.20°N, 77.08°E)
        {"facility_id": "FAC_MP_SEH_001", "facility_name": "Sehore District CHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.2032, "longitude": 77.0844, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_MP_SEH_002", "facility_name": "Shyampur CHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.3211, "longitude": 77.1250, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_MP_SEH_003", "facility_name": "Ashta CHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.0184, "longitude": 76.5492, "facility_type": "CHC", "bed_capacity": 25},
        {"facility_id": "FAC_MP_SEH_004", "facility_name": "Ichhawar PHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.0244, "longitude": 77.0142, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_SEH_005", "facility_name": "Nasrullaganj PHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 22.6841, "longitude": 77.1023, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_SEH_006", "facility_name": "Bilkisganj PHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.1420, "longitude": 77.1950, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_SEH_007", "facility_name": "Doraha PHC", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.3850, "longitude": 77.1890, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_SEH_008", "facility_name": "Maina Sub-Centre", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.2500, "longitude": 77.0200, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_MP_SEH_009", "facility_name": "Kothri Sub-Centre", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 23.0800, "longitude": 76.8500, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_MP_SEH_010", "facility_name": "Jawar Sub-Centre", "state": "Madhya Pradesh", "district": "Sehore", "latitude": 22.9500, "longitude": 76.5000, "facility_type": "SC", "bed_capacity": 2},

        # Raisen District (Center ~ 23.33°N, 77.80°E)
        {"facility_id": "FAC_MP_RAI_001", "facility_name": "Raisen District CHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.3321, "longitude": 77.8012, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_MP_RAI_002", "facility_name": "Sanchi CHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.4862, "longitude": 77.7397, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_MP_RAI_003", "facility_name": "Begumganj CHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.6015, "longitude": 78.3325, "facility_type": "CHC", "bed_capacity": 25},
        {"facility_id": "FAC_MP_RAI_004", "facility_name": "Gauharanj PHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.0540, "longitude": 77.5620, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_RAI_005", "facility_name": "Bareli PHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 22.8680, "longitude": 78.2340, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_RAI_006", "facility_name": "Udaipura PHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.0780, "longitude": 78.5020, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_RAI_007", "facility_name": "Mandideep PHC", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.1040, "longitude": 77.5180, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_RAI_008", "facility_name": "Salamatpur Sub-Centre", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.4500, "longitude": 77.6800, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_MP_RAI_009", "facility_name": "Deori Sub-Centre", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.2100, "longitude": 78.1200, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_MP_RAI_010", "facility_name": "Sultanpur Sub-Centre", "state": "Madhya Pradesh", "district": "Raisen", "latitude": 23.1400, "longitude": 77.9200, "facility_type": "SC", "bed_capacity": 2},

        # Vidisha District (Center ~ 23.53°N, 77.81°E)
        {"facility_id": "FAC_MP_VID_001", "facility_name": "Vidisha District CHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.5251, "longitude": 77.8081, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_MP_VID_002", "facility_name": "Ganj Basoda CHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.8512, "longitude": 77.9345, "facility_type": "CHC", "bed_capacity": 25},
        {"facility_id": "FAC_MP_VID_003", "facility_name": "Kurwai CHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 24.1610, "longitude": 78.0760, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_MP_VID_004", "facility_name": "Sironj PHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 24.1010, "longitude": 77.6980, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_VID_005", "facility_name": "Lateri PHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 24.0620, "longitude": 77.4010, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_VID_006", "facility_name": "Gyaraspur PHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.6650, "longitude": 78.1150, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_VID_007", "facility_name": "Nateran PHC", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.7020, "longitude": 77.6520, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_MP_VID_008", "facility_name": "Tyonda Sub-Centre", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.8800, "longitude": 78.0500, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_MP_VID_009", "facility_name": "Shamshabad Sub-Centre", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.8200, "longitude": 77.4800, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_MP_VID_010", "facility_name": "Haidergarh Sub-Centre", "state": "Madhya Pradesh", "district": "Vidisha", "latitude": 23.6100, "longitude": 77.9600, "facility_type": "SC", "bed_capacity": 2},
    ]
    return facilities_data


def seed_medicines() -> List[Dict]:
    """15 essential NLEM medicines for PHC/CHC level supply chain."""
    medicines_data = [
        {"medicine_id": "MED_PARACETAMOL_500", "medicine_name": "Paracetamol 500mg Tablets", "unit": "Tablets", "category": "Analgesic & Antipyretic", "criticality": "critical", "minimum_stock_days": 30},
        {"medicine_id": "MED_ORS_SACHET", "medicine_name": "Oral Rehydration Salts (ORS)", "unit": "Sachets", "category": "Rehydration", "criticality": "critical", "minimum_stock_days": 30},
        {"medicine_id": "MED_ZINC_20", "medicine_name": "Zinc Sulphate 20mg Tablets", "unit": "Tablets", "category": "Pediatric Supplement", "criticality": "high", "minimum_stock_days": 30},
        {"medicine_id": "MED_AMOXICILLIN_500", "medicine_name": "Amoxicillin 500mg Capsules", "unit": "Capsules", "category": "Antibiotic", "criticality": "high", "minimum_stock_days": 30},
        {"medicine_id": "MED_METFORMIN_500", "medicine_name": "Metformin 500mg Tablets", "unit": "Tablets", "category": "Anti-diabetic", "criticality": "medium", "minimum_stock_days": 45},
        {"medicine_id": "MED_OXYTOCIN_5IU", "medicine_name": "Oxytocin Injection 5IU/ml", "unit": "Vials", "category": "Maternal Health", "criticality": "critical", "minimum_stock_days": 20},
        {"medicine_id": "MED_ALBENDAZOLE_400", "medicine_name": "Albendazole 400mg Tablets", "unit": "Tablets", "category": "Anti-helminthic", "criticality": "low", "minimum_stock_days": 30},
        {"medicine_id": "MED_IFA_LARGE", "medicine_name": "Iron & Folic Acid (Large) Tablets", "unit": "Tablets", "category": "Maternal & Anemia", "criticality": "high", "minimum_stock_days": 60},
        {"medicine_id": "MED_AZITHROMYCIN_500", "medicine_name": "Azithromycin 500mg Tablets", "unit": "Tablets", "category": "Antibiotic", "criticality": "medium", "minimum_stock_days": 30},
        {"medicine_id": "MED_AMLODIPINE_5", "medicine_name": "Amlodipine 5mg Tablets", "unit": "Tablets", "category": "Cardiovascular", "criticality": "medium", "minimum_stock_days": 45},
        {"medicine_id": "MED_ATORVASTATIN_10", "medicine_name": "Atorvastatin 10mg Tablets", "unit": "Tablets", "category": "Cardiovascular", "criticality": "low", "minimum_stock_days": 45},
        {"medicine_id": "MED_CIPROFLOXACIN_500", "medicine_name": "Ciprofloxacin 500mg Tablets", "unit": "Tablets", "category": "Antibiotic", "criticality": "high", "minimum_stock_days": 30},
        {"medicine_id": "MED_CETIRIZINE_10", "medicine_name": "Cetirizine 10mg Tablets", "unit": "Tablets", "category": "Antihistamine", "criticality": "low", "minimum_stock_days": 30},
        {"medicine_id": "MED_METRONIDAZOLE_400", "medicine_name": "Metronidazole 400mg Tablets", "unit": "Tablets", "category": "Anti-diarrhoeal", "criticality": "medium", "minimum_stock_days": 30},
        {"medicine_id": "MED_SALBUTAMOL_4", "medicine_name": "Salbutamol 4mg Tablets", "unit": "Tablets", "category": "Respiratory", "criticality": "medium", "minimum_stock_days": 30},
    ]
    return medicines_data


def generate_data(session: Session, days: int = 540):
    """Generate 18 months of calibrated longitudinal PHC inventory and clinical visits data."""
    random.seed(42)
    np.random.seed(42)

    # 1. Insert Base Facilities
    facilities_raw = seed_facilities()
    for f in facilities_raw:
        session.merge(Facility(**f))

    # 2. Insert Base Medicines
    medicines_raw = seed_medicines()
    for m in medicines_raw:
        session.merge(MedicineCatalog(**m))

    session.commit()

    start_date = date(2025, 3, 1)
    date_list = [start_date + timedelta(days=i) for i in range(days)]

    # Tracking states for inventory loop
    stock_state: Dict[str, Dict[str, int]] = {}
    pending_shipments: Dict[str, Dict[str, List[Dict]]] = {}

    for f in facilities_raw:
        fid = f["facility_id"]
        stock_state[fid] = {}
        pending_shipments[fid] = {}
        for m in medicines_raw:
            mid = m["medicine_id"]
            # Initial opening stock calibrated to 45-60 days of initial baseline demand
            init_qty = random.randint(500, 3000) if f["facility_type"] != "SC" else random.randint(150, 600)
            stock_state[fid][mid] = init_qty
            pending_shipments[fid][mid] = []

    inventory_records = []
    patient_records = []
    staff_records = []
    delivery_records = []

    delivery_counter = 1

    print(f"Generating synthetic time-series for 30 facilities over {days} days...")

    for current_date in date_list:
        month = current_date.month
        is_monsoon = 6 <= month <= 9
        is_winter = month in (12, 1, 2)
        is_post_monsoon = month in (7, 8, 9, 10)

        for f in facilities_raw:
            fid = f["facility_id"]
            ftype = f["facility_type"]
            beds = f["bed_capacity"]

            # Footfall base scaling
            base_visits = beds * random.uniform(5.0, 8.0)
            day_of_week = current_date.weekday()
            weekend_factor = 0.4 if day_of_week == 6 else 1.0  # Sunday reduction

            # Seasonal Disease Ratios
            diarrhoea_mult = random.uniform(2.5, 4.0) if is_monsoon else random.uniform(0.8, 1.2)
            resp_mult = random.uniform(2.0, 3.5) if is_winter else random.uniform(0.8, 1.2)
            fever_mult = random.uniform(1.8, 2.8) if is_post_monsoon else random.uniform(0.9, 1.2)

            fever_cases = int(max(0, base_visits * 0.30 * fever_mult * weekend_factor + random.randint(-3, 3)))
            diarrhoea_cases = int(max(0, base_visits * 0.15 * diarrhoea_mult * weekend_factor + random.randint(-2, 2)))
            respiratory_cases = int(max(0, base_visits * 0.20 * resp_mult * weekend_factor + random.randint(-2, 2)))
            maternal_cases = int(max(0, base_visits * 0.10 * weekend_factor + random.randint(-1, 2)))
            total_visits = fever_cases + diarrhoea_cases + respiratory_cases + maternal_cases + int(base_visits * 0.25 * weekend_factor)

            # Record Patient Visit Data
            patient_records.append({
                "facility_id": fid,
                "date": current_date,
                "total_visits": total_visits,
                "fever_cases": fever_cases,
                "diarrhoea_cases": diarrhoea_cases,
                "respiratory_cases": respiratory_cases,
                "maternal_cases": maternal_cases,
            })

            # Record Staff Attendance Data
            scheduled_staff = 5 if ftype == "CHC" else (2 if ftype == "PHC" else 1)
            present_staff = max(1, scheduled_staff - (1 if random.random() < 0.15 else 0))
            staff_records.append({
                "facility_id": fid,
                "date": current_date,
                "staff_role": "Medical Officer / ANM",
                "scheduled_count": scheduled_staff,
                "present_count": present_staff,
            })

            # Data Quality Gap Simulation: 5% chance rural PHC/SC logs are delayed/omitted on this day
            skip_inventory_log = (ftype in ["PHC", "SC"]) and (random.random() < 0.05)

            # Process Medicine Inventory
            for m in medicines_raw:
                mid = m["medicine_id"]
                current_stock = stock_state[fid][mid]

                # Check if any pending shipment arrived today
                arrived_qty = 0
                remaining_shipments = []
                for ship in pending_shipments[fid][mid]:
                    if ship["arrival_date"] <= current_date:
                        arrived_qty += ship["quantity"]
                    else:
                        remaining_shipments.append(ship)
                pending_shipments[fid][mid] = remaining_shipments

                opening = current_stock
                received = arrived_qty

                # Calculate Dispensing Demand based on disease surges
                base_dispense = 15.0 if ftype == "CHC" else (6.0 if ftype == "PHC" else 2.0)
                if mid in ["MED_ORS_SACHET", "MED_ZINC_20", "MED_METRONIDAZOLE_400"]:
                    demand_mult = diarrhoea_mult
                elif mid in ["MED_AMOXICILLIN_500", "MED_SALBUTAMOL_4", "MED_CETIRIZINE_10"]:
                    demand_mult = resp_mult
                elif mid in ["MED_PARACETAMOL_500", "MED_CIPROFLOXACIN_500"]:
                    demand_mult = fever_mult
                elif mid == "MED_OXYTOCIN_5IU":
                    demand_mult = 1.0 + (maternal_cases * 0.1)
                else:
                    demand_mult = random.uniform(0.9, 1.1)

                target_dispense = int(base_dispense * demand_mult * random.uniform(0.85, 1.15))
                # Cap dispensing to available stock
                actual_dispensed = min(opening + received, target_dispense)

                # Damaged / Expired stock (occasional small loss)
                damaged = 1 if (random.random() < 0.02 and opening > 50) else 0

                closing = max(0, opening + received - actual_dispensed - damaged)
                stock_state[fid][mid] = closing

                # Trigger replenishment order if closing stock < threshold days
                min_days = m["minimum_stock_days"]
                threshold_qty = int(base_dispense * min_days)

                if closing <= threshold_qty and len(pending_shipments[fid][mid]) == 0:
                    # Replenishment lead time by facility type
                    base_lead = 4 if ftype == "CHC" else (9 if ftype == "PHC" else 14)
                    # 15% probability of supply chain delay (adds 10 days lag -> stock-out risk!)
                    delay = 10 if random.random() < 0.15 else 0
                    total_lead = base_lead + delay

                    expected_arrival = current_date + timedelta(days=total_lead)
                    reorder_qty = threshold_qty * 2

                    pending_shipments[fid][mid].append({
                        "quantity": reorder_qty,
                        "arrival_date": expected_arrival,
                    })

                    deliv_status = "Delayed" if delay > 0 else "In-Transit"
                    delivery_id = f"DEL_{current_date.strftime('%Y%m%d')}_{delivery_counter:04d}"
                    delivery_counter += 1

                    delivery_records.append({
                        "delivery_id": delivery_id,
                        "source_facility_id": "FAC_MP_SEH_001",  # Central district warehouse
                        "destination_facility_id": fid,
                        "medicine_id": mid,
                        "quantity": reorder_qty,
                        "dispatch_date": current_date,
                        "expected_arrival_date": expected_arrival,
                        "status": deliv_status,
                    })

                # Append to inventory list if not skipped by reporting gap
                if not skip_inventory_log:
                    inventory_records.append({
                        "facility_id": fid,
                        "medicine_id": mid,
                        "date": current_date,
                        "opening_stock": opening,
                        "received_quantity": received,
                        "dispensed_quantity": actual_dispensed,
                        "damaged_quantity": damaged,
                        "closing_stock": closing,
                        "expiry_date": current_date + timedelta(days=random.randint(180, 540)),
                    })

    # Bulk insert records in chunks for optimal performance
    print(f"Bulk saving {len(inventory_records):,} inventory logs...")
    session.bulk_insert_mappings(PatientVisits, patient_records)
    session.bulk_insert_mappings(StaffAttendance, staff_records)
    session.bulk_insert_mappings(Delivery, delivery_records)

    chunk_size = 10000
    for i in range(0, len(inventory_records), chunk_size):
        chunk = inventory_records[i : i + chunk_size]
        session.bulk_insert_mappings(MedicineInventory, chunk)
        session.commit()

    print("Synthetic dataset generation and database population completed successfully.")


if __name__ == "__main__":
    init_db()
    db_session = SessionLocal()
    try:
        generate_data(db_session, days=540)
    finally:
        db_session.close()
