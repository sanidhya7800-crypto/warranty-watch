"""Recall & alert centre. Search capability discovers recall notices."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import RecallAlert
from schemas import MessageOut, RecallAlertCreate, RecallAlertOut
from serialize import recall_to_out
from services.tinyfish import search

router = APIRouter(prefix="/api/recalls", tags=["recalls"])


@router.get("", response_model=list[RecallAlertOut])
def list_recalls(db: Session = Depends(get_db)):
    return [
        recall_to_out(a)
        for a in db.query(RecallAlert).order_by(RecallAlert.created_at.desc()).all()
    ]


@router.post("", response_model=RecallAlertOut)
def create_recall(payload: RecallAlertCreate, db: Session = Depends(get_db)):
    a = RecallAlert(
        title=payload.title,
        manufacturer=payload.manufacturer,
        affected_model=payload.affected_model,
        description=payload.description,
        source_url=payload.source_url,
        date_detected=payload.date_detected,
        severity=payload.severity,
        related_product_ids=",".join(str(i) for i in (payload.related_product_ids or [])),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    from notification_service import regenerate_notifications
    regenerate_notifications(db)
    return recall_to_out(a)


@router.delete("/{rid}", response_model=MessageOut)
def delete_recall(rid: int, db: Session = Depends(get_db)):
    a = db.query(RecallAlert).filter(RecallAlert.id == rid).first()
    if not a:
        raise HTTPException(404, "Recall alert not found")  # noqa: F821
    db.delete(a)
    db.commit()
    return MessageOut(message="deleted")


class DiscoverIn(BaseModel):
    manufacturer: str
    model_number: str | None = None


@router.post("/discover")
def discover(payload: DiscoverIn, db: Session = Depends(get_db)) -> dict:
    """Use TinyFish Search to discover recall / safety notices for a product."""
    return search.search_manufacturer_info(
        db, payload.manufacturer, payload.model_number, kind="recall"
    )



