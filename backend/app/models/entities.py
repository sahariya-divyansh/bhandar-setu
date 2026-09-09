from datetime import date
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Date,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Facility(Base):
    """Primary Health Centre (PHC), Community Health Centre (CHC), or Sub-Centre (SC)."""

    __tablename__ = "facilities"

    facility_id = Column(String(64), primary_key=True, index=True)
    facility_name = Column(String(128), nullable=False)
    state = Column(String(64), nullable=False, index=True)
    district = Column(String(64), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    facility_type = Column(String(16), nullable=False)  # PHC, CHC, SC
    bed_capacity = Column(Integer, nullable=False, default=6)

    # Relationships
    inventories = relationship("MedicineInventory", back_populates="facility", cascade="all, delete-orphan")
    patient_visits = relationship("PatientVisits", back_populates="facility", cascade="all, delete-orphan")
    staff_attendance = relationship("StaffAttendance", back_populates="facility", cascade="all, delete-orphan")
    outbound_deliveries = relationship("Delivery", foreign_keys="Delivery.source_facility_id", back_populates="source_facility")
    inbound_deliveries = relationship("Delivery", foreign_keys="Delivery.destination_facility_id", back_populates="destination_facility")

    def __repr__(self):
        return f"<Facility(id='{self.facility_id}', name='{self.facility_name}', district='{self.district}')>"


class MedicineCatalog(Base):
    """Essential Medicines List (NLEM) catalog at PHC/CHC level."""

    __tablename__ = "medicine_catalog"

    medicine_id = Column(String(64), primary_key=True, index=True)
    medicine_name = Column(String(128), nullable=False)
    unit = Column(String(32), nullable=False)  # Tablets, Capsules, Bottles, Vials, Sachets
    category = Column(String(64), nullable=False)
    criticality = Column(String(16), nullable=False)  # low, medium, high, critical
    minimum_stock_days = Column(Integer, nullable=False, default=30)

    # Relationships
    inventories = relationship("MedicineInventory", back_populates="medicine", cascade="all, delete-orphan")
    deliveries = relationship("Delivery", back_populates="medicine")

    def __repr__(self):
        return f"<MedicineCatalog(id='{self.medicine_id}', name='{self.medicine_name}', criticality='{self.criticality}')>"


class MedicineInventory(Base):
    """Daily facility-level medicine stock balance log."""

    __tablename__ = "medicine_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(String(64), ForeignKey("facilities.facility_id"), nullable=False, index=True)
    medicine_id = Column(String(64), ForeignKey("medicine_catalog.medicine_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    opening_stock = Column(Integer, nullable=False, default=0)
    received_quantity = Column(Integer, nullable=False, default=0)
    dispensed_quantity = Column(Integer, nullable=False, default=0)
    damaged_quantity = Column(Integer, nullable=False, default=0)
    closing_stock = Column(Integer, nullable=False, default=0)
    expiry_date = Column(Date, nullable=True)

    # Relationships
    facility = relationship("Facility", back_populates="inventories")
    medicine = relationship("MedicineCatalog", back_populates="inventories")

    __table_args__ = (
        Index("idx_inventory_facility_date", "facility_id", "date"),
        Index("idx_inventory_facility_medicine_date", "facility_id", "medicine_id", "date"),
    )

    def __repr__(self):
        return f"<MedicineInventory(facility='{self.facility_id}', medicine='{self.medicine_id}', date='{self.date}', closing='{self.closing_stock}')>"


class PatientVisits(Base):
    """Daily outpatient disease surveillance & footfall record."""

    __tablename__ = "patient_visits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(String(64), ForeignKey("facilities.facility_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    total_visits = Column(Integer, nullable=False, default=0)
    fever_cases = Column(Integer, nullable=False, default=0)
    diarrhoea_cases = Column(Integer, nullable=False, default=0)
    respiratory_cases = Column(Integer, nullable=False, default=0)
    maternal_cases = Column(Integer, nullable=False, default=0)

    # Relationships
    facility = relationship("Facility", back_populates="patient_visits")

    __table_args__ = (
        Index("idx_patient_visits_facility_date", "facility_id", "date"),
    )

    def __repr__(self):
        return f"<PatientVisits(facility='{self.facility_id}', date='{self.date}', total='{self.total_visits}')>"


class StaffAttendance(Base):
    """Daily clinical and administrative healthcare worker availability."""

    __tablename__ = "staff_attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(String(64), ForeignKey("facilities.facility_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    staff_role = Column(String(64), nullable=False)  # Medical Officer, Pharmacist, ANM, Staff Nurse
    scheduled_count = Column(Integer, nullable=False, default=1)
    present_count = Column(Integer, nullable=False, default=1)

    # Relationships
    facility = relationship("Facility", back_populates="staff_attendance")

    def __repr__(self):
        return f"<StaffAttendance(facility='{self.facility_id}', role='{self.staff_role}', date='{self.date}')>"


class Delivery(Base):
    """Inter-facility stock redistribution & district supply consignment tracking."""

    __tablename__ = "deliveries"

    delivery_id = Column(String(64), primary_key=True, index=True)
    source_facility_id = Column(String(64), ForeignKey("facilities.facility_id"), nullable=True, index=True)
    destination_facility_id = Column(String(64), ForeignKey("facilities.facility_id"), nullable=False, index=True)
    medicine_id = Column(String(64), ForeignKey("medicine_catalog.medicine_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    dispatch_date = Column(Date, nullable=False)
    expected_arrival_date = Column(Date, nullable=False)
    status = Column(String(32), nullable=False, default="Pending")  # Pending, In-Transit, Delivered, Delayed, Cancelled

    # Relationships
    source_facility = relationship("Facility", foreign_keys=[source_facility_id], back_populates="outbound_deliveries")
    destination_facility = relationship("Facility", foreign_keys=[destination_facility_id], back_populates="inbound_deliveries")
    medicine = relationship("MedicineCatalog", back_populates="deliveries")

    def __repr__(self):
        return f"<Delivery(id='{self.delivery_id}', dest='{self.destination_facility_id}', medicine='{self.medicine_id}', status='{self.status}')>"
