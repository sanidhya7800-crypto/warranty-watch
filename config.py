"""Application configuration.

No secrets are ever logged or exposed by this module.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import dotenv_values, load_dotenv

# backend/ lives one level below the project root.
BASE_DIR = Path(__file__).resolve().parent.parent  # project root (Tinyfish/)
BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
UPLOAD_DIR = BACKEND_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BACKEND_DIR / "warrantywatch.db"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Load variables from the existing .env (preserves the user's key).
load_dotenv(ENV_FILE)

PRODUCT_CATEGORIES = [
    "Refrigerator",
    "Air Conditioner",
    "Washing Machine",
    "Television",
    "Laptop",
    "Smartphone",
    "Microwave",
    "Water Purifier",
    "Geyser",
    "Dishwasher",
    "Other",
]

SERVICE_REQUEST_STATUSES = [
    "Draft",
    "Submitted",
    "Pending",
    "Technician Assigned",
    "In Progress",
    "Resolved",
    "Rejected",
    "Unknown",
]

ALERT_SEVERITIES = ["Low", "Medium", "High", "Critical"]

# Invoice upload validation.
ALLOWED_INVOICE_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
}
ALLOWED_INVOICE_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
MAX_INVOICE_BYTES = 10 * 1024 * 1024  # 10 MB


def tinyfish_api_key() -> str | None:
    """Return the configured key (or None). Never logged by callers.
    Always loads latest .env with override=True and strips whitespace and quotes.
    """
    load_dotenv(ENV_FILE, override=True)
    raw = os.environ.get("TINYFISH_API_KEY")
    if not raw:
        vals = dotenv_values(ENV_FILE)
        raw = vals.get("TINYFISH_API_KEY")
    if not raw:
        return None
    cleaned = raw.strip().strip('"').strip("'").strip()
    return cleaned or None


def has_tinyfish_key() -> bool:
    key = tinyfish_api_key()
    return bool(key)
