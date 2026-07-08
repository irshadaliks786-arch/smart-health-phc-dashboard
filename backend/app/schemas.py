from typing import Optional, Literal
from pydantic import BaseModel, Field


class KPIRow(BaseModel):
    phc_id: str
    stock_score: float
    bed_score: float
    attendance_score: float
    test_score: float
    footfall_score: float
    composite_kpi_score: float
    district: str
    chc_parent: str
    flag_status: str


class DistrictSummaryRow(BaseModel):
    district: str
    n_phcs: int
    avg_composite_score: float
    min_composite_score: float
    avg_stock_score: float
    avg_bed_score: float
    avg_attendance_score: float
    avg_test_score: float
    avg_footfall_score: float
    n_flagged: int
    n_watch: int


class RedistributionRow(BaseModel):
    medicine_name: str
    deficit_phc: str
    days_to_stockout: Optional[float] = None
    deficit_qty: float
    surplus_phc: str
    transfer_qty: float
    priority: str
    same_district: bool


# ---- Guardrailed AI insight contract -------------------------------------
# The model (Gemini) MUST return exactly this shape. Anything else is
# rejected by the guardrail layer and replaced with a deterministic
# template-generated fallback, so the frontend contract never breaks.

class InsightItem(BaseModel):
    severity: Literal["info", "watch", "critical"]
    headline: str = Field(max_length=120)
    detail: str = Field(max_length=280)
    related_phc_id: Optional[str] = None
    related_district: Optional[str] = None


class InsightsResponse(BaseModel):
    source: Literal["gemini", "deterministic_fallback"]
    generated_at: str
    items: list[InsightItem]
    disclaimer: str = (
        "AI-generated summary of the deterministic analytics below. "
        "Numbers always come from the pipeline, never from the model."
    )
