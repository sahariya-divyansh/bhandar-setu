import os
from pathlib import Path
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set test environment database before importing app modules
test_db_path = Path(__file__).resolve().parent / "test_bhandar_setu.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path.as_posix()}"

import app.db as db_module
from app.db import get_db, Base
from app.main import app
from app.models.entities import (
    Facility,
    MedicineCatalog,
    MedicineInventory,
    PatientVisits,
    StaffAttendance,
)

test_engine = create_engine(
    f"sqlite:///{test_db_path.as_posix()}",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch db_module globals so any direct engine/session calls in services hit test_db
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def test_db():
    """Create fresh test database tables and populate small isolated test data."""
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass

    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()

    # 1. Seed Facilities
    f1 = Facility(
        facility_id="PHC_SEHORE_01",
        facility_name="PHC Sehore Town",
        state="Madhya Pradesh",
        district="Sehore",
        latitude=23.2000,
        longitude=77.0800,
        facility_type="PHC",
        bed_capacity=6,
    )
    f2 = Facility(
        facility_id="PHC_ASHTA_01",
        facility_name="PHC Ashta",
        state="Madhya Pradesh",
        district="Sehore",
        latitude=23.0200,
        longitude=76.5500,
        facility_type="PHC",
        bed_capacity=6,
    )
    f3 = Facility(
        facility_id="PHC_RAISEN_01",
        facility_name="PHC Raisen Central",
        state="Madhya Pradesh",
        district="Raisen",
        latitude=23.3300,
        longitude=77.7800,
        facility_type="PHC",
        bed_capacity=10,
    )
    f4 = Facility(
        facility_id="PHC_RAIPUR_01",
        facility_name="PHC Raipur",
        state="Chhattisgarh",
        district="Raipur",
        latitude=21.2500,
        longitude=81.6300,
        facility_type="PHC",
        bed_capacity=12,
    )
    db.add_all([f1, f2, f3, f4])

    # 2. Seed Medicine Catalog
    m1 = MedicineCatalog(
        medicine_id="MED_PARACETAMOL_500",
        medicine_name="Paracetamol 500mg",
        unit="Tablets",
        category="Analgesics & Antipyretics",
        criticality="critical",
        minimum_stock_days=30,
    )
    m2 = MedicineCatalog(
        medicine_id="MED_AMOXICILLIN_250",
        medicine_name="Amoxicillin 250mg",
        unit="Capsules",
        category="Antibiotics",
        criticality="high",
        minimum_stock_days=20,
    )
    db.add_all([m1, m2])
    db.commit()

    # 3. Seed Inventory & Visits History (Last 30 days)
    today = date.today()
    for day_offset in range(30, -1, -1):
        dt = today - timedelta(days=day_offset)

        # PHC Sehore: High consumption, low stock (Shortage deficit)
        # Closing stock on today = 50 tablets, avg daily burn = 25 -> 2 days remaining (Red alert)
        c_stock_f1 = max(50, 800 - (30 - day_offset) * 25)
        db.add(
            MedicineInventory(
                facility_id="PHC_SEHORE_01",
                medicine_id="MED_PARACETAMOL_500",
                date=dt,
                opening_stock=c_stock_f1 + 25,
                received_quantity=0,
                dispensed_quantity=25,
                damaged_quantity=0,
                closing_stock=c_stock_f1,
                expiry_date=today + timedelta(days=180),
            )
        )

        # PHC Ashta: High stock, moderate consumption (Surplus donor)
        # Closing stock on today = 3000 tablets, avg daily burn = 15 -> 200 days remaining
        db.add(
            MedicineInventory(
                facility_id="PHC_ASHTA_01",
                medicine_id="MED_PARACETAMOL_500",
                date=dt,
                opening_stock=3015,
                received_quantity=0,
                dispensed_quantity=15,
                damaged_quantity=0,
                closing_stock=3000,
                expiry_date=today + timedelta(days=365),
            )
        )

        # Patient Visits
        db.add(
            PatientVisits(
                facility_id="PHC_SEHORE_01",
                date=dt,
                total_visits=45,
                fever_cases=18,
                diarrhoea_cases=5,
                respiratory_cases=12,
                maternal_cases=4,
            )
        )
        db.add(
            PatientVisits(
                facility_id="PHC_ASHTA_01",
                date=dt,
                total_visits=30,
                fever_cases=10,
                diarrhoea_cases=3,
                respiratory_cases=8,
                maternal_cases=2,
            )
        )

    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=test_engine)
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass


@pytest.fixture(scope="function")
def client(test_db: Session):
    """FastAPI TestClient with overridden database session."""
    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
