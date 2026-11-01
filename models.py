"""SQLAlchemy ORM models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    model_number = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Float, nullable=True)
    warranty_duration_months = Column(Integer, nullable=True)
    warranty_expiry_date = Column(Date, nullable=True)
    extended_warranty_expiry = Column(Date, nullable=True)
    amc_expiry_date = Column(Date, nullable=True)
    invoice_filename = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    service_requests = relationship(
        "ServiceRequest", back_populates="product", cascade="all, delete-orphan"
    )


class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    manufacturer = Column(String, nullable=False)
    issue_description = Column(Text, nullable=False)
    complaint_number = Column(String, nullable=True)
    service_portal_url = Column(String, nullable=True)
    request_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="Draft")
    last_checked = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="service_requests")


class RecallAlert(Base):
    __tablename__ = "recall_alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    affected_model = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    date_detected = Column(Date, nullable=True)
    severity = Column(String, nullable=False, default="Medium")
    related_product_ids = Column(String, nullable=True)  # comma-separated product ids
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # warranty_30, warranty_7, warranty_expired, amc_expiry, recall, service_status, announcement
    message = Column(Text, nullable=False)
    product_id = Column(Integer, nullable=True)
    severity = Column(String, nullable=False, default="info")  # info / warning / critical
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TinyFishActivity(Base):
    __tablename__ = "tinyfish_activities"

    id = Column(Integer, primary_key=True, index=True)
    capability = Column(String, nullable=False)  # search / fetch / agent / browser / monitor
    status = Column(String, nullable=False)  # running / completed / failed / demo
    mode = Column(String, nullable=False, default="live")  # live / demo
    task_description = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result_summary = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    detail_json = Column(Text, nullable=True)  # JSON-serialised structured result
    created_at = Column(DateTime, default=datetime.utcnow)


class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    tinyfish_monitor_id = Column(String, nullable=True)  # id from TinyFish
    name = Column(String, nullable=False)
    monitor_type = Column(String, nullable=False)  # search / fetch
    target = Column(String, nullable=False)  # url (fetch) or query (search)
    schedule_cron = Column(String, nullable=False)
    status = Column(String, nullable=False, default="creating")  # creating/active/paused/failed
    purpose = Column(Text, nullable=True)
    product_id = Column(Integer, nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    last_change_summary = Column(Text, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
