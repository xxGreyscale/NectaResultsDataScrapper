from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from gridfs import GridFS
from pymongo.database import Database

from infastructure import settings
from usecases.generate_results_csv import generate_acsee_results_csv, generate_csee_results_csv
from usecases.generate_results_summary_csv import results_summary_csv, results_summary_csee_csv


def _upload_to_gridfs(db: Database, file_path: str) -> ObjectId:
    fs = GridFS(db)
    with open(file_path, "rb") as handle:
        return fs.put(handle, filename=file_path)


def process_export(db: Database, export_type: str) -> dict:
    now = datetime.now(timezone.utc)
    if export_type == "results_acsee":
        file_path = generate_acsee_results_csv(settings.EXPORT_DIR)
    elif export_type == "results_csee":
        file_path = generate_csee_results_csv(settings.EXPORT_DIR)
    elif export_type == "summaries_acsee":
        file_path = results_summary_csv(settings.EXPORT_DIR)
    elif export_type == "summaries_csee":
        file_path = results_summary_csee_csv(settings.EXPORT_DIR)
    else:
        raise ValueError(f"Unknown export type: {export_type}")

    if not file_path:
        raise RuntimeError("Export generation failed")

    gridfs_id = _upload_to_gridfs(db, file_path)
    return {
        "filePath": file_path,
        "gridFsId": gridfs_id,
        "updatedAt": now,
        "status": "completed",
    }
