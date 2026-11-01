"""Persistent application settings (e.g. live vs demo mode)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from models import Setting

DEFAULT_MODE = "live"


def get_mode(db: Session) -> str:
    s = db.query(Setting).filter(Setting.key == "mode").first()
    return s.value if s else DEFAULT_MODE


def set_mode(db: Session, mode: str) -> str:
    if mode not in ("live", "demo"):
        raise ValueError("mode must be 'live' or 'demo'")
    s = db.query(Setting).filter(Setting.key == "mode").first()
    if s:
        s.value = mode
    else:
        db.add(Setting(key="mode", value=mode))
    db.commit()
    return mode
