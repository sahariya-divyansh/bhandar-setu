"""Seed script for initializing database schema and populating realistic synthetic data.

Usage:
    python -m app.seed
"""

import sys
from pathlib import Path

# Add project root and ml directory to Python path for seamless imports
root_path = Path(__file__).resolve().parent.parent.parent
ml_path = root_path / "ml"
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(ml_path))

from app.db import init_db, SessionLocal
from app.models import (
    Facility,
    MedicineCatalog,
    MedicineInventory,
    PatientVisits,
    StaffAttendance,
    Delivery,
)
from ml.src.generate_synthetic_data import generate_data


def main():
    print("==================================================")
    print("  Bhandar Setu — Database Initialization & Seed   ")
    print("==================================================")

    print("1. Initializing database schema...")
    init_db()

    session = SessionLocal()
    try:
        print("2. Generating synthetic healthcare & supply chain data...")
        generate_data(session, days=540)

        # Print summary metrics
        facility_count = session.query(Facility).count()
        medicine_count = session.query(MedicineCatalog).count()
        inventory_count = session.query(MedicineInventory).count()
        patient_count = session.query(PatientVisits).count()
        staff_count = session.query(StaffAttendance).count()
        delivery_count = session.query(Delivery).count()

        print("\n--------------------------------------------------")
        print("Database Seed Summary:")
        print(f" - Facilities:         {facility_count:,}")
        print(f" - Medicines Catalog:  {medicine_count:,}")
        print(f" - Inventory Records:  {inventory_count:,}")
        print(f" - Patient Visit Logs: {patient_count:,}")
        print(f" - Staff Logs:         {staff_count:,}")
        print(f" - Consignment Orders: {delivery_count:,}")
        print("--------------------------------------------------")
        print("Database successfully seeded.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    main()
