"""TinyFish Activity Centre: every real and demo operation, with provenance."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import TinyFishActivity
from schemas import TinyFishActivityOut
from serialize import activity_to_out

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("", response_model=list[TinyFishActivityOut])
def list_activity(limit: int = 100, db: Session = Depends(get_db)):
    rows = (
        db.query(TinyFishActivity)
        .order_by(TinyFishActivity.created_at.desc())
        .limit(limit)
        .all()
    )
    return [activity_to_out(a) for a in rows]
