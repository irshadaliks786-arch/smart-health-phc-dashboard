"""
Deterministic data-access layer.

Every read goes through here. Behaviour is intentionally boring and
predictable (that's the "Deterministic UX" requirement flowing all the
way back to the data layer):

  - Same input -> same output, every time. No randomness anywhere.
  - If Firestore is configured (USE_FIRESTORE=true) and reachable, read
    from there.
  - Otherwise, read from the bundled CSV snapshot in data_cache/. This
    means the API works identically with or without live Google Cloud
    credentials, which matters for demoing/judging offline.
  - Firestore documents are written by scripts/seed_firestore.py from the
    same CSV files, so the two paths always return the same shape.
"""
import os
import math
import pandas as pd
from functools import lru_cache
from typing import Optional

from app.config import settings

_FILES = {
    "kpi_scores": "kpi_scores.csv",
    "district_summary": "district_summary.csv",
    "flagged_phcs": "flagged_phcs.csv",
    "forecast_bed_occupancy": "forecast_bed_occupancy.csv",
    "forecast_medicine_consumption": "forecast_medicine_consumption.csv",
    "forecast_patient_footfall": "forecast_patient_footfall.csv",
    "redistribution_recommendations": "redistribution_recommendations.csv",
    "phc_master": "phc_master.csv",
}

_firestore_client = None


def _get_firestore_client():
    global _firestore_client
    if _firestore_client is not None:
        return _firestore_client
    if not settings.use_firestore:
        return None
    try:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=settings.firebase_project_id or None)
        return _firestore_client
    except Exception:
        # Never let a missing/broken Firestore connection break the API —
        # deterministic fallback to CSV cache instead.
        return None


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Replace NaN with None so FastAPI/JSON serialization is well-defined."""
    return df.where(pd.notnull(df), None)


@lru_cache(maxsize=None)
def _load_csv(name: str) -> pd.DataFrame:
    path = os.path.join(settings.data_cache_dir, _FILES[name])
    return _clean(pd.read_csv(path))


def get_table(name: str, collection: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch a named table. Tries Firestore collection `collection` (defaults
    to `name`) first if configured, otherwise returns the local CSV.
    """
    if name not in _FILES:
        raise KeyError(f"Unknown table: {name}")

    client = _get_firestore_client()
    if client is not None:
        try:
            coll = collection or name
            docs = list(client.collection(coll).stream())
            if docs:
                records = [d.to_dict() for d in docs]
                return _clean(pd.DataFrame.from_records(records))
        except Exception:
            pass  # fall through to CSV — deterministic, never a hard failure

    return _load_csv(name)


def records(name: str) -> list[dict]:
    df = get_table(name)
    return df.to_dict(orient="records")


def known_phc_ids() -> set[str]:
    return set(get_table("phc_master")["phc_id"].astype(str).tolist())


def known_districts() -> set[str]:
    return set(get_table("phc_master")["district"].astype(str).tolist())
