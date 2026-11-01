"""TinyFish integration health. Performs one cheap, non-billed reachability call."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config import has_tinyfish_key, tinyfish_api_key
from database import get_db
from settings_service import get_mode

router = APIRouter(prefix="/api/tinyfish", tags=["tinyfish"])

_CAPS = ["search", "fetch", "agent", "browser", "monitor"]


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    key_val = tinyfish_api_key()
    key_present = bool(key_val)
    key_length = len(key_val) if key_val else 0
    mode = get_mode(db)

    api_reachable = None
    api_error = None
    error_category = None

    if key_present:
        try:
            from services.tinyfish.client import get_client
            from tinyfish import AuthenticationError, PaymentRequiredError, APIConnectionError

            # monitors.list() is free (no baseline run / no billing) and verifies auth + endpoint.
            get_client().monitors.list()
            api_reachable = True
        except AuthenticationError as exc:
            api_reachable = False
            error_category = "authentication"
            api_error = f"Authentication failed: {exc}"
        except PaymentRequiredError as exc:
            api_reachable = False
            error_category = "quota_exceeded"
            api_error = f"Quota reached: {exc}"
        except APIConnectionError as exc:
            api_reachable = False
            error_category = "network_error"
            api_error = f"Network connection error: {exc}"
        except Exception as exc:  # do not leak secrets
            api_reachable = False
            error_category = "unknown_error"
            api_error = str(exc)

    if api_error and key_val and key_val in api_error:
        api_error = api_error.replace(key_val, "[REDACTED_API_KEY]")

    capabilities = {c: ("live" if (mode == "live" and api_reachable) else "demo") for c in _CAPS}
    return {
        "key_present": key_present,
        "key_length": key_length,
        "mode": mode,
        "api_reachable": api_reachable,
        "api_error": api_error,
        "error_category": error_category,
        "capabilities": capabilities,
        "note": "api_reachable uses monitors.list() (non-billed) to verify auth and endpoint.",
    }
