from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import districts, forecasts, redistribution, insights

app = FastAPI(
    title=settings.app_name,
    description=(
        "Deterministic PHC/CHC health-ops analytics API. All numeric data "
        "(KPIs, forecasts, redistribution) is computed by a rule-based/"
        "statistical pipeline — not AI. The only AI-generated surface is "
        "/api/insights, and it is schema-validated + entity-checked with a "
        "deterministic fallback (see app/gemini_guardrails.py)."
    ),
    version="1.0.0",
)

origins = (
    ["*"] if settings.allowed_origins == "*" else settings.allowed_origins.split(",")
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(districts.router)
app.include_router(forecasts.router)
app.include_router(redistribution.router)
app.include_router(insights.router)


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }
