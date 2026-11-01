"""Settings: live/demo mode toggle and (non-secret) key status."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import has_tinyfish_key, tinyfish_api_key
from database import get_db
from schemas import KeyStatusOut, ModeOut
from settings_service import get_mode, set_mode

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=KeyStatusOut)
def get_settings(db: Session = Depends(get_db)):
    key = tinyfish_api_key()
    return KeyStatusOut(
        key_present=bool(key),
        key_length=len(key) if key else 0,
        mode=get_mode(db),
    )


class ModeIn(BaseModel):
    mode: str


@router.put("/mode", response_model=ModeOut)
def update_mode(payload: ModeIn, db: Session = Depends(get_db)):
    m = set_mode(db, payload.mode)
    return ModeOut(mode=m)


@router.get("/capabilities", response_model=list[str])
def capabilities():
    return ["search", "fetch", "agent", "browser", "monitor"]
