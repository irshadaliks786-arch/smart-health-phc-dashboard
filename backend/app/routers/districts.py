from fastapi import APIRouter, HTTPException
from app import data_store
from app.schemas import DistrictSummaryRow, KPIRow

router = APIRouter(prefix="/api", tags=["districts"])


@router.get("/districts", response_model=list[DistrictSummaryRow])
def list_districts():
    return data_store.records("district_summary")


@router.get("/phcs", response_model=list[KPIRow])
def list_phcs(district: str | None = None, flagged_only: bool = False):
    rows = data_store.records("kpi_scores")
    if district:
        rows = [r for r in rows if r["district"].lower() == district.lower()]
    if flagged_only:
        rows = [r for r in rows if "UNDERPERFORMING" in r["flag_status"]]
    return rows


@router.get("/phcs/{phc_id}", response_model=KPIRow)
def get_phc(phc_id: str):
    rows = data_store.records("kpi_scores")
    for r in rows:
        if r["phc_id"] == phc_id:
            return r
    raise HTTPException(status_code=404, detail=f"PHC '{phc_id}' not found")
