from fastapi import APIRouter
from app import data_store

router = APIRouter(prefix="/api/forecasts", tags=["forecasts"])


@router.get("/bed-occupancy")
def bed_occupancy(phc_id: str | None = None):
    rows = data_store.records("forecast_bed_occupancy")
    if phc_id:
        rows = [r for r in rows if r["phc_id"] == phc_id]
    return rows


@router.get("/patient-footfall")
def patient_footfall(phc_id: str | None = None):
    rows = data_store.records("forecast_patient_footfall")
    if phc_id:
        rows = [r for r in rows if r["phc_id"] == phc_id]
    return rows


@router.get("/medicine-consumption")
def medicine_consumption(phc_id: str | None = None, medicine_name: str | None = None):
    rows = data_store.records("forecast_medicine_consumption")
    if phc_id:
        rows = [r for r in rows if r["phc_id"] == phc_id]
    if medicine_name:
        rows = [r for r in rows if r["medicine_name"] == medicine_name]
    return rows
