"""AI Service Assistant: Search -> Fetch -> Agent investigation of a reported issue."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from services.tinyfish import agent, fetch, search

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class InvestigateIn(BaseModel):
    product_id: int
    issue: str


def _normalize_diagnosis(
    agent_res: dict,
    product: dict,
    issue: str,
    top_url: str | None,
    search_res: dict | None,
    fetch_res: dict | None,
) -> dict:
    mode = agent_res.get("mode", "demo")
    agent_raw = agent_res.get("result") or {}
    inner = agent_raw.get("result") if isinstance(agent_raw, dict) else None

    # Handle stringified inner JSON if needed
    if isinstance(inner, str):
        try:
            import json
            inner = json.loads(inner)
        except Exception:
            inner = None

    status = (
        agent_raw.get("status")
        if isinstance(agent_raw, dict)
        else ("COMPLETED" if inner else "FAILED")
    )
    error = agent_res.get("error") or (agent_raw.get("error_message") if isinstance(agent_raw, dict) else None)

    # Collect official source links from Search, Fetch, and Agent
    official_sources = []
    if top_url:
        official_sources.append({"title": f"Official {product.get('manufacturer')} Portal", "url": top_url})
    if search_res and isinstance(search_res.get("results"), list):
        for r in search_res["results"][:3]:
            if r.get("url") and r.get("url") not in [s["url"] for s in official_sources]:
                official_sources.append({"title": r.get("title") or r.get("site_name") or "Manufacturer Support", "url": r["url"]})

    # If agent run failed or returned an error, return strict honest FAILED status without fabricated diagnosis
    if error or status == "FAILED" or not inner:
        return {
            "status": "FAILED",
            "mode": mode,
            "error": error or "TinyFish Agent live execution failed.",
            "issue_summary": f"{product.get('manufacturer')} {product.get('model_number')}: {issue}",
            "possible_causes": [],
            "recommended_next_steps": [
                f"Review official support documentation at: {top_url or 'OEM support portal'}",
                "Check TinyFish API account credentials and permissions in Settings.",
                "Switch to Demo Mode to test and demonstrate simulated agent triage.",
            ],
            "relevant_warranty_conditions": [],
            "potential_exclusions": [],
            "official_source_urls": [top_url] if top_url else [],
            "official_sources": official_sources,
            "may_be_covered": "Unavailable (Agent execution failed)",
            "confidence": "None - Live execution failed",
            "uncertainty_notes": f"TinyFish Agent failed to complete live investigation: {error or 'Unknown agent failure'}",
            "is_simulated": False,
        }

    return {
        "status": status or "COMPLETED",
        "mode": mode,
        "error": error,
        "issue_summary": inner.get("issue_summary") or f"{product.get('manufacturer')} {product.get('model_number')}: {issue}",
        "possible_causes": list(inner.get("possible_causes") or []),
        "recommended_next_steps": list(inner.get("recommended_next_steps") or []),
        "relevant_warranty_conditions": list(inner.get("relevant_warranty_conditions") or []),
        "potential_exclusions": list(inner.get("potential_exclusions") or []),
        "official_source_urls": list(inner.get("official_source_urls") or ([top_url] if top_url else [])),
        "official_sources": official_sources,
        "may_be_covered": inner.get("may_be_covered") or "Warranty coverage depends on technician diagnostics",
        "confidence": inner.get("confidence") or "High",
        "uncertainty_notes": inner.get("uncertainty_notes") or "Assessment based on official OEM documentation. Final claim requires physical hardware verification.",
        "is_simulated": mode == "demo",
    }


@router.post("/investigate")
def investigate(payload: InvestigateIn, db: Session = Depends(get_db)) -> dict:
    p = db.query(Product).filter(Product.id == payload.product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")

    product = {
        "id": p.id,
        "name": p.name,
        "manufacturer": p.manufacturer,
        "model_number": p.model_number,
        "category": p.category,
    }

    # 1. TinyFish Search: find official support / troubleshooting pages.
    search_res = search.search_manufacturer_info(
        db, p.manufacturer, p.model_number, p.category, kind="support"
    )
    results = search_res.get("results") or []
    top_url = results[0].get("url") if results else None

    # 2. TinyFish Fetch: extract relevant support content.
    fetch_res = None
    if top_url:
        fetch_res = fetch.fetch_url(
            db, top_url,
            purpose=f"Extract troubleshooting and warranty info for the issue: {payload.issue[:200]}",
        )

    # 3. TinyFish Agent: multi-step investigation on the official page.
    agent_res = agent.investigate_issue(db, product, payload.issue, url=top_url)

    # 4. Standardized, guaranteed diagnosis payload for the frontend
    diagnosis = _normalize_diagnosis(agent_res, product, payload.issue, top_url, search_res, fetch_res)

    return {
        "product": product,
        "issue": payload.issue,
        "search": search_res,
        "fetch": fetch_res,
        "agent": agent_res,
        "top_url": top_url,
        "diagnosis": diagnosis,
    }
