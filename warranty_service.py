"""Warranty status calculations derived from stored dates (never hardcoded)."""
from __future__ import annotations

from datetime import date
from typing import Optional

from models import Product


def _coverage_end(p: Product) -> Optional[date]:
    ends = [e for e in (p.warranty_expiry_date, p.extended_warranty_expiry) if e]
    return max(ends) if ends else None


def warranty_status(p: Product, today: Optional[date] = None) -> dict:
    today = today or date.today()
    end = _coverage_end(p)

    if end == p.extended_warranty_expiry and p.extended_warranty_expiry and (
        not p.warranty_expiry_date or p.extended_warranty_expiry > p.warranty_expiry_date
    ):
        basis = "extended"
    elif end == p.warranty_expiry_date:
        basis = "warranty"
    else:
        basis = "none"

    if end is None:
        status = "Unknown"
        days = None
    else:
        days = (end - today).days
        if days < 0:
            status = "Expired"
        elif days <= 30:
            status = "Expiring Soon"
        else:
            status = "Active"

    amc = p.amc_expiry_date
    if amc:
        adays = (amc - today).days
        amc_status = "Expired" if adays < 0 else ("Expiring Soon" if adays <= 30 else "Active")
    else:
        adays = None
        amc_status = None

    return {
        "status": status,
        "days_to_expiry": days,
        "coverage_end": end,
        "coverage_basis": basis if end else None,
        "amc_status": amc_status,
        "amc_days_to_expiry": adays,
        "amc_expiry": amc,
    }
