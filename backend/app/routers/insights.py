from fastapi import APIRouter
from app.schemas import InsightsResponse
from app import gemini_guardrails

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("", response_model=InsightsResponse)
def get_insights():
    """
    The only AI-generated surface in this app.

    Always returns HTTP 200 with a schema-valid InsightsResponse — either
    `source: "gemini"` (validated, entity-checked model output) or
    `source: "deterministic_fallback"` (plain templated text over the same
    numbers). The frontend renders identically either way, so a slow/absent
    Gemini call never degrades the UX, only the `source` badge shown to the user.
    """
    return gemini_guardrails.get_insights()
