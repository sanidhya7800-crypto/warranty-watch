"""TinyFish Monitor management: create / list / run / cancel."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import MessageOut, MonitorCreate, MonitorOut
from services.tinyfish import monitor as tf_monitor

router = APIRouter(prefix="/api/monitors", tags=["monitors"])


@router.get("", response_model=list[MonitorOut])
def list_monitors(db: Session = Depends(get_db)):
    return [MonitorOut.model_validate(m) for m in tf_monitor.list_monitors(db)]


@router.post("")
def create_monitor(payload: MonitorCreate, db: Session = Depends(get_db)) -> dict:
    res = tf_monitor.create_monitor(
        db,
        name=payload.name,
        monitor_type=payload.monitor_type,
        target=payload.target,
        schedule_cron=payload.schedule_cron,
        purpose=payload.purpose,
        product_id=payload.product_id,
    )
    if "error" in res and "monitor" not in res:
        raise HTTPException(400, res["error"])
    return res


@router.post("/{mid}/run")
def run_monitor(mid: int, db: Session = Depends(get_db)) -> dict:
    res = tf_monitor.run_monitor(db, mid)
    if res.get("error"):
        raise HTTPException(404, res["error"])
    return res


@router.delete("/{mid}", response_model=MessageOut)
def cancel_monitor(mid: int, db: Session = Depends(get_db)):
    res = tf_monitor.cancel_monitor(db, mid)
    if res.get("error"):
        raise HTTPException(404, res["error"])
    return MessageOut(message="deleted")
