"""Notifications generated from warranty status and recalls."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Notification
from notification_service import regenerate_notifications
from schemas import MessageOut, NotificationOut
from serialize import notification_to_out

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    return [
        notification_to_out(n)
        for n in db.query(Notification).order_by(Notification.created_at.desc()).all()
    ]


@router.post("/regenerate", response_model=MessageOut)
def regenerate(db: Session = Depends(get_db)):
    count = regenerate_notifications(db)
    return MessageOut(message=f"regenerated; {count} new notification(s) created")


@router.post("/{nid}/read", response_model=NotificationOut)
def mark_read(nid: int, db: Session = Depends(get_db)):
    n = db.query(Notification).filter(Notification.id == nid).first()
    if not n:
        from fastapi import HTTPException
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return notification_to_out(n)


@router.post("/read-all", response_model=MessageOut)
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})  # noqa: E712
    db.commit()
    return MessageOut(message="all marked read")
