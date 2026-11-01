"""Smart Warranty Intelligence: Search official pages, then Fetch warranty terms."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from services.tinyfish import fetch, search

router = APIRouter(prefix="/api/warranty", tags=["warranty"])


class InvestigateIn(BaseModel):
    product_id: int
    manufacturer: str
    model_number: str | None = None
    category: str | None = None


@router.post("/investigate")
def investigate(payload: InvestigateIn, db: Session = Depends(get_db)) -> dict:
    # 1. TinyFish Search: discover official warranty pages.
    search_res = search.search_manufacturer_info(
        db, payload.manufacturer, payload.model_number, payload.category, kind="warranty"
    )
    # 2. TinyFish Fetch: extract warranty terms from the top official page.
    results = search_res.get("results") or []
    top_url = results[0].get("url") if results else None
    fetch_res = None
    if top_url:
        fetch_res = fetch.fetch_url(
            db, top_url,
            purpose=f"Extract warranty periods, exclusions and service terms for "
            f"{payload.manufacturer} {payload.model_number or ''}".strip(),
        )
    return {
        "product_id": payload.product_id,
        "search": search_res,
        "fetch": fetch_res,
        "top_url": top_url,
    }
