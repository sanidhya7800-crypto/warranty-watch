"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------
class MessageOut(BaseModel):
    message: str


class ModeOut(BaseModel):
    mode: str  # "live" | "demo"


class KeyStatusOut(BaseModel):
    key_present: bool
    key_length: int = 0
    mode: str


# ---------------------------------------------------------------------------
# Warranty status (computed from stored dates)
# ---------------------------------------------------------------------------
class WarrantyStatusOut(BaseModel):
    status: str  # Active / Expiring Soon / Expired / Unknown
    days_to_expiry: Optional[int] = None
    coverage_end: Optional[date] = None
    coverage_basis: Optional[str] = None  # warranty / extended / none
    amc_status: Optional[str] = None
    amc_days_to_expiry: Optional[int] = None
    amc_expiry: Optional[date] = None


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
class ProductBase(BaseModel):
    name: str
    category: str
    manufacturer: str
    model_number: str
    serial_number: Optional[str] = None
    purchase_date: date
    purchase_price: Optional[float] = None
    warranty_duration_months: Optional[int] = None
    warranty_expiry_date: Optional[date] = None
    extended_warranty_expiry: Optional[date] = None
    amc_expiry_date: Optional[date] = None
    notes: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    warranty_duration_months: Optional[int] = None
    warranty_expiry_date: Optional[date] = None
    extended_warranty_expiry: Optional[date] = None
    amc_expiry_date: Optional[date] = None
    notes: Optional[str] = None


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_filename: Optional[str] = None
    has_invoice: bool = False
    created_at: datetime
    updated_at: datetime
    warranty: WarrantyStatusOut


# ---------------------------------------------------------------------------
# Service requests
# ---------------------------------------------------------------------------
class ServiceRequestBase(BaseModel):
    product_id: int
    manufacturer: str
    issue_description: str
    complaint_number: Optional[str] = None
    service_portal_url: Optional[str] = None
    request_date: date
    status: str = "Draft"
    notes: Optional[str] = None


class ServiceRequestCreate(ServiceRequestBase):
    pass


class ServiceRequestUpdate(BaseModel):
    issue_description: Optional[str] = None
    complaint_number: Optional[str] = None
    service_portal_url: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ServiceRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    manufacturer: str
    issue_description: str
    complaint_number: Optional[str] = None
    service_portal_url: Optional[str] = None
    request_date: date
    status: str
    last_checked: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Recalls / alerts
# ---------------------------------------------------------------------------
class RecallAlertBase(BaseModel):
    title: str
    manufacturer: str
    affected_model: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    date_detected: Optional[date] = None
    severity: str = "Medium"
    related_product_ids: Optional[list[int]] = None


class RecallAlertCreate(RecallAlertBase):
    pass


class RecallAlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    manufacturer: str
    affected_model: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None
    date_detected: Optional[date] = None
    severity: str
    related_product_ids: list[int] = []
    created_at: datetime


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    message: str
    product_id: Optional[int] = None
    severity: str
    is_read: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# TinyFish activity
# ---------------------------------------------------------------------------
class TinyFishActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    capability: str
    status: str
    mode: str
    task_description: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_summary: Optional[str] = None
    source_url: Optional[str] = None
    error: Optional[str] = None
    detail: Optional[Any] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Monitors
# ---------------------------------------------------------------------------
class MonitorCreate(BaseModel):
    name: str
    monitor_type: str  # "search" | "fetch"
    target: str  # url (fetch) or query (search)
    schedule_cron: str
    purpose: Optional[str] = None
    product_id: Optional[int] = None


class MonitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tinyfish_monitor_id: Optional[str] = None
    name: str
    monitor_type: str
    target: str
    schedule_cron: str
    status: str
    purpose: Optional[str] = None
    product_id: Optional[int] = None
    last_run_at: Optional[datetime] = None
    last_change_summary: Optional[str] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# TinyFish capability result envelopes (unified across capabilities)
# ---------------------------------------------------------------------------
class SearchHitOut(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    site_name: Optional[str] = None
    date: Optional[str] = None


class FetchResultOut(BaseModel):
    url: str
    final_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    links: list[str] = []
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    not_modified: Optional[bool] = None
    latency_ms: Optional[float] = None


class AgentResultOut(BaseModel):
    status: str
    run_id: Optional[str] = None
    num_of_steps: Optional[int] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    error_category: Optional[str] = None


class BrowserSessionOut(BaseModel):
    session_id: str
    cdp_url: str
    base_url: str


class MonitorRunOut(BaseModel):
    monitor_id: Optional[str] = None
    run_type: Optional[str] = None
    is_baseline: Optional[bool] = None
    result_count: Optional[int] = None
    new_result_positions: list[int] = []
    new_results: list[SearchHitOut] = []
    fetched_text: Optional[str] = None
    changed: Optional[bool] = None
    raw: Optional[Any] = None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardOut(BaseModel):
    total_products: int
    active_warranties: int
    expiring_warranties: int
    expired_warranties: int
    open_service_requests: int
    alert_count: int
    upcoming_expiries: list[ProductOut]
    recent_activity: list[TinyFishActivityOut]
    warranty_breakdown: dict[str, int]
    category_breakdown: dict[str, int]
