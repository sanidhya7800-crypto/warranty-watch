"""ORM -> schema converters (computed fields like warranty status added here)."""
from __future__ import annotations

from models import Notification, Product, RecallAlert, ServiceRequest, TinyFishActivity
from schemas import (
    NotificationOut,
    ProductOut,
    RecallAlertOut,
    ServiceRequestOut,
    TinyFishActivityOut,
    WarrantyStatusOut,
)
from services.tinyfish.activity import serialize_activity
from warranty_service import warranty_status


def product_to_out(p: Product) -> ProductOut:
    w = warranty_status(p)
    return ProductOut(
        id=p.id,
        name=p.name,
        category=p.category,
        manufacturer=p.manufacturer,
        model_number=p.model_number,
        serial_number=p.serial_number,
        purchase_date=p.purchase_date,
        purchase_price=p.purchase_price,
        warranty_duration_months=p.warranty_duration_months,
        warranty_expiry_date=p.warranty_expiry_date,
        extended_warranty_expiry=p.extended_warranty_expiry,
        amc_expiry_date=p.amc_expiry_date,
        notes=p.notes,
        invoice_filename=p.invoice_filename,
        has_invoice=bool(p.invoice_filename),
        created_at=p.created_at,
        updated_at=p.updated_at,
        warranty=WarrantyStatusOut(**w),
    )


def service_request_to_out(s: ServiceRequest) -> ServiceRequestOut:
    return ServiceRequestOut.model_validate(s)


def recall_to_out(a: RecallAlert) -> RecallAlertOut:
    ids = [int(x) for x in (a.related_product_ids or "").split(",") if x.strip().isdigit()]
    return RecallAlertOut(
        id=a.id,
        title=a.title,
        manufacturer=a.manufacturer,
        affected_model=a.affected_model,
        description=a.description,
        source_url=a.source_url,
        date_detected=a.date_detected,
        severity=a.severity,
        related_product_ids=ids,
        created_at=a.created_at,
    )


def notification_to_out(n: Notification) -> NotificationOut:
    return NotificationOut.model_validate(n)


def activity_to_out(a: TinyFishActivity) -> TinyFishActivityOut:
    return TinyFishActivityOut(**serialize_activity(a))
