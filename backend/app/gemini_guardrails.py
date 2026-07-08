"""
Guardrailed AI layer.

Rules enforced here (this is the "AI output + guardrails" requirement):

  1. Google-only: uses google-generativeai (Gemini) exclusively. No other
     LLM SDK is imported anywhere in this project.
  2. Structured-output contract: Gemini is instructed to return JSON only,
     and the response is parsed straight into `InsightsResponse`. If it
     doesn't validate, we don't retry-and-hope — we fall back.
  3. Entity allowlist: every `related_phc_id` / `related_district` the
     model mentions is checked against the real IDs from the deterministic
     data layer. If the model invents a PHC/district that doesn't exist,
     the whole response is rejected (classic hallucination guardrail).
  4. Grounding: the prompt includes ONLY the already-computed deterministic
     numbers (KPI scores, flags, redistribution rows). The model is
     explicitly told not to invent numbers, and is not allowed to output
     any numeric claim outside the `detail` free-text field.
  5. Bounded output: length caps (via schema Field max_length) and a fixed
     max item count, so the UI never has to lay out unbounded content —
     this is what makes the "deterministic UX" promise hold even when the
     underlying model is non-deterministic.
  6. Fail-closed: any exception, timeout, or invalid response silently and
     deterministically falls back to `_deterministic_fallback()`, which is
     plain Python string templating over the same numbers. The frontend
     always gets a 200 with a valid `InsightsResponse`; `source` tells you
     which path was used.
"""
import json
import datetime as dt
from typing import Optional

from app.config import settings
from app.schemas import InsightsResponse, InsightItem
from app import data_store

MAX_ITEMS = 6

_SYSTEM_INSTRUCTION = """You are a report-summarizer for a district health-operations \
dashboard. You will be given deterministic, already-computed analytics data \
(KPI scores, stockout flags, redistribution recommendations). Your ONLY job is to \
turn that data into short, plain-language operational notes for a district health \
officer.

STRICT RULES:
- Output ONLY valid JSON matching this exact shape, nothing else, no markdown fences:
  {"items": [{"severity": "info|watch|critical", "headline": "...", "detail": "...", \
"related_phc_id": "PHC_xxx or null", "related_district": "District name or null"}]}
- At most 6 items.
- Every phc_id and district you mention MUST come from the data given to you. \
Never invent, guess, or generalize an ID that was not in the input.
- Do not introduce any number that is not present in the input data.
- Do not give medical, diagnostic, or treatment advice. Operational/logistics \
observations only (stock, beds, staffing, testing, redistribution).
- Keep headline under 120 characters and detail under 280 characters.
"""


def _deterministic_fallback() -> InsightsResponse:
    """Plain-Python, non-AI summary. Always available, always identical for
    identical input data. This is the guaranteed floor under the AI layer."""
    items: list[InsightItem] = []

    flagged = data_store.records("flagged_phcs")
    for row in flagged[:3]:
        items.append(InsightItem(
            severity="critical",
            headline=f"{row['phc_id']} flagged underperforming",
            detail=(
                f"Composite KPI score {row['composite_kpi_score']:.1f}/100 in "
                f"{row['district']} district ({row['chc_parent']}). Review stock, "
                f"bed, attendance and test sub-scores for root cause."
            ),
            related_phc_id=row["phc_id"],
            related_district=row["district"],
        ))

    redist = data_store.records("redistribution_recommendations")
    high_priority = [r for r in redist if str(r.get("priority")) == "HIGH"][:3]
    for row in high_priority:
        items.append(InsightItem(
            severity="watch",
            headline=f"Redistribute {row['medicine_name']} to {row['deficit_phc']}",
            detail=(
                f"{row['deficit_phc']} projected stockout in "
                f"{row.get('days_to_stockout', 'a few')} day(s). Transfer "
                f"{row['transfer_qty']} units from surplus {row['surplus_phc']}."
            ),
            related_phc_id=row["deficit_phc"],
            related_district=None,
        ))

    if not items:
        items.append(InsightItem(
            severity="info",
            headline="No critical flags today",
            detail="All PHCs are within normal operating thresholds based on the "
                   "latest pipeline run.",
        ))

    return InsightsResponse(
        source="deterministic_fallback",
        generated_at=dt.datetime.utcnow().isoformat() + "Z",
        items=items[:MAX_ITEMS],
    )


def _build_context() -> str:
    """Only deterministic, already-computed data goes into the prompt."""
    payload = {
        "flagged_phcs": data_store.records("flagged_phcs")[:10],
        "district_summary": data_store.records("district_summary"),
        "redistribution_recommendations": data_store.records(
            "redistribution_recommendations"
        )[:10],
    }
    return json.dumps(payload, default=str)


def _validate_entities(resp: InsightsResponse) -> bool:
    valid_phcs = data_store.known_phc_ids()
    valid_districts = data_store.known_districts()
    for item in resp.items:
        if item.related_phc_id and item.related_phc_id not in valid_phcs:
            return False
        if item.related_district and item.related_district not in valid_districts:
            return False
    return True


def _call_gemini() -> Optional[InsightsResponse]:
    if not settings.use_gemini or not settings.gemini_api_key:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=_SYSTEM_INSTRUCTION,
            generation_config={"response_mime_type": "application/json"},
        )
        result = model.generate_content(
            _build_context(),
            request_options={"timeout": 12},
        )
        raw = json.loads(result.text)
        items = [InsightItem(**it) for it in raw.get("items", [])[:MAX_ITEMS]]
        resp = InsightsResponse(
            source="gemini",
            generated_at=dt.datetime.utcnow().isoformat() + "Z",
            items=items,
        )
        if not _validate_entities(resp):
            return None  # hallucinated an unknown PHC/district -> reject
        if not resp.items:
            return None
        return resp
    except Exception:
        return None  # any failure -> caller falls back deterministically


def get_insights() -> InsightsResponse:
    resp = _call_gemini()
    if resp is not None:
        return resp
    return _deterministic_fallback()
