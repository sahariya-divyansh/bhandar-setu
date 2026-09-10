"""Multi-State Synthetic Data Generator for Bhandar Setu.

Generates realistic health facility inventory and disease surveillance telemetry across 3 Indian states:
- Madhya Pradesh (MP): 30 facilities (18 months history)
- Chhattisgarh (CG): 20 facilities (18 months history)
- Rajasthan (RJ): 15 facilities (3 months history — simulates newly onboarded low-data node for federated learning demo)
"""

import random
from datetime import date, timedelta
from typing import List, Dict

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.db import init_db, SessionLocal, engine
from app.models import (
    Base,
    Facility,
    MedicineCatalog,
    MedicineInventory,
    PatientVisits,
    StaffAttendance,
    Delivery,
)
from ml.src.generate_synthetic_data import seed_medicines


def get_multistate_facilities() -> List[Dict]:
    """3 States, 7 Districts, 65 Total Healthcare Facilities."""
    facilities_data = [
        # --- STATE 1: MADHYA PRADESH (30 Facilities) ---
        # Sehore District
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

        # Raisen District
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

        # Vidisha District
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

        # --- STATE 2: CHHATTISGARH (20 Facilities) ---
        # Bastar District
        {"facility_id": "FAC_CG_BAS_001", "facility_name": "Jagdalpur District CHC", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.0744, "longitude": 82.0084, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_CG_BAS_002", "facility_name": "Bastanar CHC", "state": "Chhattisgarh", "district": "Bastar", "latitude": 18.9850, "longitude": 81.7500, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_CG_BAS_003", "facility_name": "Bakamand PHC", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.2100, "longitude": 81.9500, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_CG_BAS_004", "facility_name": "Lohandiguda PHC", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.1200, "longitude": 81.7800, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_CG_BAS_005", "facility_name": "Tokapal PHC", "state": "Chhattisgarh", "district": "Bastar", "latitude": 18.9600, "longitude": 81.8900, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_CG_BAS_006", "facility_name": "Kodialpal Sub-Centre", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.0500, "longitude": 82.1000, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_BAS_007", "facility_name": "Nanganur Sub-Centre", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.1500, "longitude": 82.0200, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_BAS_008", "facility_name": "Chitrakote Sub-Centre", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.2000, "longitude": 81.7000, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_BAS_009", "facility_name": "Karanpur Sub-Centre", "state": "Chhattisgarh", "district": "Bastar", "latitude": 18.9000, "longitude": 81.9900, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_BAS_010", "facility_name": "Paharapur Sub-Centre", "state": "Chhattisgarh", "district": "Bastar", "latitude": 19.3000, "longitude": 81.8500, "facility_type": "SC", "bed_capacity": 2},

        # Kanker District
        {"facility_id": "FAC_CG_KAN_001", "facility_name": "Kanker District CHC", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.2719, "longitude": 81.4932, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_CG_KAN_002", "facility_name": "Charama CHC", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.4500, "longitude": 81.3800, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_CG_KAN_003", "facility_name": "Bhanupratappur PHC", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.3100, "longitude": 81.0800, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_CG_KAN_004", "facility_name": "Narharpur PHC", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.3700, "longitude": 81.6500, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_CG_KAN_005", "facility_name": "Antagarh PHC", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.0800, "longitude": 81.1800, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_CG_KAN_006", "facility_name": "Pakhanjore Sub-Centre", "state": "Chhattisgarh", "district": "Kanker", "latitude": 19.9800, "longitude": 80.8500, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_KAN_007", "facility_name": "Sarona Sub-Centre", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.2000, "longitude": 81.5500, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_KAN_008", "facility_name": "Korear Sub-Centre", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.3500, "longitude": 81.4200, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_KAN_009", "facility_name": "Sambalpur Sub-Centre", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.1500, "longitude": 81.2500, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_CG_KAN_010", "facility_name": "Haradula Sub-Centre", "state": "Chhattisgarh", "district": "Kanker", "latitude": 20.4000, "longitude": 81.1500, "facility_type": "SC", "bed_capacity": 2},

        # --- STATE 3: RAJASTHAN (15 Facilities — Low-Data Node: 3 Months Data) ---
        # Jaipur Rural District
        {"facility_id": "FAC_RJ_JAI_001", "facility_name": "Kotputli CHC", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.7011, "longitude": 76.2012, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_RJ_JAI_002", "facility_name": "Shahpura CHC", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.3820, "longitude": 75.9610, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_RJ_JAI_003", "facility_name": "Chamu PHC", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.1500, "longitude": 75.7200, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_RJ_JAI_004", "facility_name": "Bairath PHC", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.4200, "longitude": 76.1800, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_RJ_JAI_005", "facility_name": "Manoharpur PHC", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.3000, "longitude": 75.9500, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_RJ_JAI_006", "facility_name": "Paota Sub-Centre", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.5200, "longitude": 76.1000, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_RJ_JAI_007", "facility_name": "Jali Sub-Centre", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.2500, "longitude": 75.8000, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_RJ_JAI_008", "facility_name": "Med Sub-Centre", "state": "Rajasthan", "district": "Jaipur Rural", "latitude": 27.4800, "longitude": 76.0200, "facility_type": "SC", "bed_capacity": 2},

        # Tonk District
        {"facility_id": "FAC_RJ_TON_001", "facility_name": "Tonk District CHC", "state": "Rajasthan", "district": "Tonk", "latitude": 26.1664, "longitude": 75.7885, "facility_type": "CHC", "bed_capacity": 30},
        {"facility_id": "FAC_RJ_TON_002", "facility_name": "Niwai CHC", "state": "Rajasthan", "district": "Tonk", "latitude": 26.3580, "longitude": 75.9320, "facility_type": "CHC", "bed_capacity": 20},
        {"facility_id": "FAC_RJ_TON_003", "facility_name": "Deoli PHC", "state": "Rajasthan", "district": "Tonk", "latitude": 25.7500, "longitude": 75.3800, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_RJ_TON_004", "facility_name": "Uniara PHC", "state": "Rajasthan", "district": "Tonk", "latitude": 25.9200, "longitude": 76.0200, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_RJ_TON_005", "facility_name": "Malpura PHC", "state": "Rajasthan", "district": "Tonk", "latitude": 26.2800, "longitude": 75.3800, "facility_type": "PHC", "bed_capacity": 6},
        {"facility_id": "FAC_RJ_TON_006", "facility_name": "Toda Sub-Centre", "state": "Rajasthan", "district": "Tonk", "latitude": 26.0200, "longitude": 75.5000, "facility_type": "SC", "bed_capacity": 2},
        {"facility_id": "FAC_RJ_TON_007", "facility_name": "Duni Sub-Centre", "state": "Rajasthan", "district": "Tonk", "latitude": 25.8500, "longitude": 75.6000, "facility_type": "SC", "bed_capacity": 2},
    ]
    return facilities_data


def generate_multistate_dataset(session: Session):
    """Clean slate seed & generate multi-state telemetry for MP, CG, and RJ."""
    random.seed(42)
    np.random.seed(42)

    # Recreate tables to ensure clean multi-state data
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    facilities_raw = get_multistate_facilities()
    for f in facilities_raw:
        session.add(Facility(**f))

    medicines_raw = seed_medicines()
    for m in medicines_raw:
        session.add(MedicineCatalog(**m))

    session.commit()

    start_date = date(2025, 3, 1)

    print(f"Generating multi-state time-series data for {len(facilities_raw)} facilities across MP, CG, and RJ...")

    patient_records = []
    staff_records = []
    inv_records = []

    for f in facilities_raw:
        fid = f["facility_id"]
        fstate = f["state"]
        ftype = f["facility_type"]
        beds = f["bed_capacity"]

        num_days = 90 if fstate == "Rajasthan" else 540
        date_list = [start_date + timedelta(days=i) for i in range(num_days)]

        stock_state = {}
        for m in medicines_raw:
            mid = m["medicine_id"]
            stock_state[mid] = random.randint(500, 3000) if ftype != "SC" else random.randint(150, 600)

        for current_date in date_list:
            month = current_date.month
            is_monsoon = 6 <= month <= 9
            is_winter = month in (12, 1, 2)
            is_post_monsoon = month in (7, 8, 9, 10)

            base_visits = beds * random.uniform(5.0, 8.0)
            weekend = 0.4 if current_date.weekday() == 6 else 1.0

            diarrhoea_mult = random.uniform(2.5, 4.0) if is_monsoon else random.uniform(0.8, 1.2)
            resp_mult = random.uniform(2.0, 3.5) if is_winter else random.uniform(0.8, 1.2)
            fever_mult = random.uniform(1.8, 2.8) if is_post_monsoon else random.uniform(0.9, 1.2)

            fever = int(max(0, base_visits * 0.30 * fever_mult * weekend + random.randint(-3, 3)))
            diarrhoea = int(max(0, base_visits * 0.15 * diarrhoea_mult * weekend + random.randint(-2, 2)))
            resp = int(max(0, base_visits * 0.20 * resp_mult * weekend + random.randint(-2, 2)))
            maternal = int(max(0, base_visits * 0.10 * weekend + random.randint(-1, 2)))
            total = fever + diarrhoea + resp + maternal + int(base_visits * 0.25 * weekend)

            patient_records.append({
                "facility_id": fid,
                "date": current_date,
                "total_visits": total,
                "fever_cases": fever,
                "diarrhoea_cases": diarrhoea,
                "respiratory_cases": resp,
                "maternal_cases": maternal,
            })

            scheduled_staff = 5 if ftype == "CHC" else (2 if ftype == "PHC" else 1)
            present_staff = max(1, scheduled_staff - (1 if random.random() < 0.15 else 0))
            staff_records.append({
                "facility_id": fid,
                "date": current_date,
                "staff_role": "Medical Officer / ANM",
                "scheduled_count": scheduled_staff,
                "present_count": present_staff,
            })

            skip_inv = (ftype in ["PHC", "SC"]) and (random.random() < 0.05)

            for m in medicines_raw:
                mid = m["medicine_id"]
                opening = stock_state[mid]

                base_dispense = 15.0 if ftype == "CHC" else (6.0 if ftype == "PHC" else 2.0)
                if mid in ["MED_ORS_SACHET", "MED_ZINC_20", "MED_METRONIDAZOLE_400"]:
                    demand_mult = diarrhoea_mult
                elif mid in ["MED_AMOXICILLIN_500", "MED_SALBUTAMOL_4", "MED_CETIRIZINE_10"]:
                    demand_mult = resp_mult
                elif mid in ["MED_PARACETAMOL_500", "MED_CIPROFLOXACIN_500"]:
                    demand_mult = fever_mult
                else:
                    demand_mult = random.uniform(0.9, 1.1)

                target_dispense = int(base_dispense * demand_mult * random.uniform(0.85, 1.15))
                actual_dispensed = min(opening, target_dispense)
                damaged = 1 if (random.random() < 0.02 and opening > 50) else 0

                closing = max(0, opening - actual_dispensed - damaged)
                stock_state[mid] = closing

                if not skip_inv:
                    inv_records.append({
                        "facility_id": fid,
                        "medicine_id": mid,
                        "date": current_date,
                        "opening_stock": opening,
                        "received_quantity": 0,
                        "dispensed_quantity": actual_dispensed,
                        "damaged_quantity": damaged,
                        "closing_stock": closing,
                        "expiry_date": current_date + timedelta(days=365),
                    })

    print(f"Bulk saving {len(inv_records):,} inventory records across 3 states...")
    session.bulk_insert_mappings(PatientVisits, patient_records)
    session.bulk_insert_mappings(StaffAttendance, staff_records)

    chunk_size = 10000
    for i in range(0, len(inv_records), chunk_size):
        session.bulk_insert_mappings(MedicineInventory, inv_records[i:i+chunk_size])
        session.commit()

    print("Multi-state database generation completed successfully.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        generate_multistate_dataset(db)
    finally:
        db.close()
