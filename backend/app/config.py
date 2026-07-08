"""
Central configuration.

Compliance notes (per updated hackathon norms):
- Only Google technologies are wired in: Firebase/Firestore for storage,
  Gemini (google-generativeai) for the one AI-generated surface (insights).
- Everything else (KPI scoring, forecasting, redistribution) is plain
  deterministic Python/pandas — NOT AI — so the core UX never depends on
  a model call succeeding.
- If GOOGLE_APPLICATION_CREDENTIALS / GEMINI_API_KEY are not set, the app
  still runs fully off the local CSV cache + deterministic template text,
  so `docker compose up` works out of the box for judges without any keys.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "PHC/CHC Health Ops API"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Firebase / Firestore (Google) — optional; falls back to local CSV cache
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    use_firestore: bool = os.getenv("USE_FIRESTORE", "false").lower() == "true"

    # Gemini (Google) — optional; falls back to deterministic template insights
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    use_gemini: bool = os.getenv("USE_GEMINI", "false").lower() == "true"

    # CORS
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

    data_cache_dir: str = os.path.join(os.path.dirname(__file__), "data_cache")

    class Config:
        env_file = ".env"


settings = Settings()
