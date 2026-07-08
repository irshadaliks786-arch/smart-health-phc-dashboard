from fastapi import APIRouter
from app import data_store
from app.schemas import RedistributionRow

router = APIRouter(prefix="/api/redistribution", tags=["redistribution"])


@router.get("", response_model=list[RedistributionRow])
def list_redistribution(priority: str | None = None):
    rows = data_store.records("redistribution_recommendations")
    if priority:
        rows = [r for r in rows if str(r["priority"]).upper() == priority.upper()]
    return rows
