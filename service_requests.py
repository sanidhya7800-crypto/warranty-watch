"""Service request tracker. Browser capability powers the status check."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import ServiceRequest
from notification_service import regenerate_notifications
from schemas import MessageOut, ServiceRequestCreate, ServiceRequestOut, ServiceRequestUpdate
from serialize import service_request_to_out
from services.tinyfish import browser

router = APIRouter(prefix="/api/service-requests", tags=["service-requests"])


@router.get("", response_model=list[ServiceRequestOut])
def list_sr(db: Session = Depends(get_db)):
    return [
        service_request_to_out(s)
        for s in db.query(ServiceRequest).order_by(ServiceRequest.created_at.desc()).all()
    ]


@router.post("", response_model=ServiceRequestOut)
def create_sr(payload: ServiceRequestCreate, db: Session = Depends(get_db)):
    s = ServiceRequest(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    regenerate_notifications(db)
    return service_request_to_out(s)


@router.put("/{sid}", response_model=ServiceRequestOut)
def update_sr(sid: int, payload: ServiceRequestUpdate, db: Session = Depends(get_db)):
    s = db.query(ServiceRequest).filter(ServiceRequest.id == sid).first()
    if not s:
        raise HTTPException(404, "Service request not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    s.last_checked = datetime.utcnow()
    db.commit()
    db.refresh(s)
    if payload.status:
        regenerate_notifications(db)
    return service_request_to_out(s)


@router.delete("/{sid}", response_model=MessageOut)
def delete_sr(sid: int, db: Session = Depends(get_db)):
    s = db.query(ServiceRequest).filter(ServiceRequest.id == sid).first()
    if not s:
        raise HTTPException(404, "Service request not found")
    db.delete(s)
    db.commit()
    return MessageOut(message="deleted")


@router.post("/{sid}/check-status")
def check_status(sid: int, db: Session = Depends(get_db)) -> dict:
    """Open the manufacturer service portal in a TinyFish remote browser session.

    The user completes any login / OTP / submission themselves in the live browser;
    nothing is submitted automatically.
    """
    s = db.query(ServiceRequest).filter(ServiceRequest.id == sid).first()
    if not s:
        raise HTTPException(404, "Service request not found")
    if not s.service_portal_url:
        raise HTTPException(400, "This service request has no portal URL to open.")
    res = browser.open_portal(db, s.service_portal_url, name=f"Service request {s.complaint_number or s.id}")
    s.last_checked = datetime.utcnow()
    db.commit()
    return res
