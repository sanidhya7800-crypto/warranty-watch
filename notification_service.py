"""Generate warranty / recall notifications without creating duplicates."""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from models import Notification, Product, RecallAlert
from warranty_service import warranty_status


def _ensure(db: Session, ntype: str, product_id: int | None, severity: str, message: str) -> bool:
    existing = (
        db.query(Notification)
        .filter(Notification.type == ntype, Notification.product_id == product_id)
        .first()
    )
    if existing:
        existing.message = message  # keep message fresh, preserve read state + id
        existing.severity = severity
        return False
    else:
        db.add(Notification(type=ntype, message=message, product_id=product_id, severity=severity))
        return True


def regenerate_notifications(db: Session) -> int:
    today = date.today()
    created = 0
    for p in db.query(Product).all():
        w = warranty_status(p, today)
        if w["status"] == "Expired":
            if _ensure(db, "warranty_expired", p.id, "critical", f"{p.name}: warranty has expired."):
                created += 1
        elif w["days_to_expiry"] is not None and w["days_to_expiry"] <= 7:
            if _ensure(db, "warranty_7", p.id, "warning", f"{p.name}: warranty expires in {w['days_to_expiry']} day(s)."):
                created += 1
        elif w["days_to_expiry"] is not None and w["days_to_expiry"] <= 30:
            if _ensure(db, "warranty_30", p.id, "info", f"{p.name}: warranty expires in {w['days_to_expiry']} day(s)."):
                created += 1

        if w["amc_status"] == "Expired":
            if _ensure(db, "amc_expired", p.id, "warning", f"{p.name}: AMC has expired."):
                created += 1
        elif w["amc_days_to_expiry"] is not None and w["amc_days_to_expiry"] <= 30:
            if _ensure(db, "amc_expiry", p.id, "info", f"{p.name}: AMC expires in {w['amc_days_to_expiry']} day(s)."):
                created += 1

    for a in db.query(RecallAlert).all():
        rel_ids = [int(x) for x in (a.related_product_ids or "").split(",") if x.strip().isdigit()]
        sev = "critical" if a.severity in ("High", "Critical") else "warning"
        for pid in rel_ids:
            if _ensure(db, f"recall_{a.id}", pid, sev, f"Recall alert: {a.title}"):
                created += 1

    db.commit()
    return created
