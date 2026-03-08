from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from infastructure import settings


def enqueue_job(db: Database, payload: dict) -> dict:
    now = datetime.now(timezone.utc)
    payload.setdefault("createdAt", now)
    payload.setdefault("updatedAt", now)
    payload.setdefault("status", "queued")
    return db["jobs"].find_one_and_update(
        {"idempotencyKey": payload["idempotencyKey"]},
        {"$setOnInsert": payload},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )


def claim_next_job(db: Database, worker_id: str) -> dict | None:
    now = datetime.now(timezone.utc)
    lock_expiry = now + timedelta(minutes=settings.JOB_LOCK_MINUTES)
    return db["jobs"].find_one_and_update(
        {
            "status": "queued",
            "$or": [
                {"lockExpiresAt": {"$lte": now}},
                {"lockExpiresAt": {"$exists": False}},
            ],
        },
        {
            "$set": {
                "status": "running",
                "lockedBy": worker_id,
                "lockExpiresAt": lock_expiry,
                "updatedAt": now,
            }
        },
        sort=[("priority", -1), ("createdAt", 1)],
        return_document=ReturnDocument.AFTER,
    )


def update_job(db: Database, job_id: ObjectId, updates: dict[str, Any]) -> None:
    updates["updatedAt"] = datetime.now(timezone.utc)
    db["jobs"].update_one({"_id": job_id}, {"$set": updates})


def mark_job_complete(db: Database, job_id: ObjectId, progress: dict | None = None) -> None:
    update_job(db, job_id, {"status": "completed", "progress": progress})


def mark_job_failed(db: Database, job_id: ObjectId, error: str) -> None:
    update_job(db, job_id, {"status": "failed", "error": error})


def cancel_job(db: Database, job_id: ObjectId) -> dict | None:
    """Cancel a job that is still queued. Returns the updated doc or None."""
    now = datetime.now(timezone.utc)
    return db["jobs"].find_one_and_update(
        {"_id": job_id, "status": "queued"},
        {"$set": {"status": "cancelled", "updatedAt": now}},
        return_document=ReturnDocument.AFTER,
    )


def count_jobs(db: Database, query: dict) -> int:
    return db["jobs"].count_documents(query)

