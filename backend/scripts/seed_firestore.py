"""
Push the local CSV snapshot into Firestore so the API can run with
USE_FIRESTORE=true against live Google Cloud storage instead of the
bundled cache.

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    export FIREBASE_PROJECT_ID=your-project-id
    python scripts/seed_firestore.py

Re-run any time the pipeline (00_Scripts/run_pipeline.py in the original
solution) regenerates the output CSVs — this script is idempotent, it
just overwrites documents keyed by row index / phc_id.
"""
import os
import sys
import pandas as pd
from google.cloud import firestore

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.config import settings  # noqa: E402
from app.data_store import _FILES  # noqa: E402

KEY_COLUMN = {
    "kpi_scores": "phc_id",
    "district_summary": "district",
    "flagged_phcs": "phc_id",
    "phc_master": "phc_id",
}


def main():
    client = firestore.Client(project=settings.firebase_project_id or None)
    for collection, filename in _FILES.items():
        path = os.path.join(settings.data_cache_dir, filename)
        df = pd.read_csv(path)
        df = df.where(pd.notnull(df), None)
        key_col = KEY_COLUMN.get(collection)
        batch = client.batch()
        count = 0
        for i, row in df.iterrows():
            doc_id = f"{row[key_col]}_{i}" if key_col else str(i)
            ref = client.collection(collection).document(doc_id)
            batch.set(ref, row.to_dict())
            count += 1
            if count % 400 == 0:  # Firestore batch limit is 500
                batch.commit()
                batch = client.batch()
        batch.commit()
        print(f"Seeded {count} docs into collection '{collection}'")


if __name__ == "__main__":
    main()
