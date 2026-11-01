"""Dashboard aggregates."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Product, RecallAlert, ServiceRequest, TinyFishActivity
from schemas import DashboardOut
from serialize import activity_to_out, product_to_out

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

_RESOLVED = ("Resolved", "Rejected")


@router.get("", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    outs = [product_to_out(p) for p in products]

    active = sum(1 for o in outs if o.warranty.status == "Active")
    expiring = sum(1 for o in outs if o.warranty.status == "Expiring Soon")
    expired = sum(1 for o in outs if o.warranty.status == "Expired")
    unknown = sum(1 for o in outs if o.warranty.status == "Unknown")

    open_sr = (
        db.query(ServiceRequest)
        .filter(~ServiceRequest.status.in_(_RESOLVED))
        .count()
    )
    alert_count = db.query(RecallAlert).count()

    upcoming = sorted(
        [o for o in outs if o.warranty.days_to_expiry is not None and o.warranty.days_to_expiry >= 0],
        key=lambda o: (o.warranty.days_to_expiry, o.id),
    )[:5]

    recent_activity = [
        activity_to_out(a)
        for a in db.query(TinyFishActivity).order_by(TinyFishActivity.created_at.desc()).limit(10).all()
    ]

    warranty_breakdown = {
        "Active": active,
        "Expiring Soon": expiring,
        "Expired": expired,
        "Unknown": unknown,
    }
    category_breakdown: dict[str, int] = {}
    for o in outs:
        category_breakdown[o.category] = category_breakdown.get(o.category, 0) + 1

    return DashboardOut(
        total_products=len(outs),
        active_warranties=active,
        expiring_warranties=expiring,
        expired_warranties=expired,
        open_service_requests=open_sr,
        alert_count=alert_count,
        upcoming_expiries=upcoming,
        recent_activity=recent_activity,
        warranty_breakdown=warranty_breakdown,
        category_breakdown=category_breakdown,
    )
