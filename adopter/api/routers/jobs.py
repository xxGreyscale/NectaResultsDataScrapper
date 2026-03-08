from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from pymongo import ReturnDocument

from adopter.api.deps import get_db
from adopter.api.models import (
    ExportJobCreate,
    FullRebuildJobCreate,
    JobCreate,
    JobResponse,
    ResultsJobCreate,
)
from adopter.api.job_queue import cancel_job, count_jobs
from adopter.api.response_utils import pagination_meta, success_response
from adopter.api.serialization import to_jsonable

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _idempotency_key(job_type: str, exam_type: str, years: list[int], source_url: str | None) -> str:
    raw = f"{job_type}|{exam_type}|{sorted(years)}|{source_url}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _enqueue(db, payload: dict) -> tuple[dict, bool]:
    """Insert-or-return a job. Returns (doc, deduplicated)."""
    now = datetime.now(timezone.utc)
    payload.setdefault("createdAt", now)
    payload.setdefault("updatedAt", now)
    payload.setdefault("status", "queued")

    doc = db["jobs"].find_one_and_update(
        {"idempotencyKey": payload["idempotencyKey"]},
        {"$setOnInsert": payload},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    deduplicated = doc.get("createdAt") != now
    return doc, deduplicated


def _to_job_response(doc: dict, deduplicated: bool = False) -> dict:
    """Convert a raw Mongo doc into a frontend-friendly shape."""
    return {
        "id": str(doc["_id"]),
        "type": doc.get("type"),
        "examType": doc.get("examType"),
        "years": doc.get("years", []),
        "sourceUrl": doc.get("sourceUrl"),
        "priority": doc.get("priority"),
        "status": doc.get("status"),
        "idempotencyKey": doc.get("idempotencyKey"),
        "createdAt": doc.get("createdAt"),
        "updatedAt": doc.get("updatedAt"),
        "lockedBy": doc.get("lockedBy"),
        "progress": doc.get("progress"),
        "error": doc.get("error"),
        "deduplicated": deduplicated,
    }


# ---------------------------------------------------------------------------
# Task-specific create endpoints (frontend-facing)
# ---------------------------------------------------------------------------

@router.post("/jobs/results", status_code=201)
def create_results_job(body: ResultsJobCreate) -> dict:
    """Queue a *results* fetch job."""
    db = get_db()
    payload = {
        "type": "results",
        "examType": body.examType,
        "years": body.years,
        "sourceUrl": body.sourceUrl,
        "priority": body.priority,
        "idempotencyKey": _idempotency_key("results", body.examType, body.years, body.sourceUrl),
    }
    doc, dedup = _enqueue(db, payload)
    return success_response(_to_job_response(doc, dedup)).model_dump()


@router.post("/jobs/full-rebuild", status_code=201)
def create_full_rebuild_job(body: FullRebuildJobCreate) -> dict:
    """Queue a *full rebuild* job (deletes then re-fetches)."""
    db = get_db()
    payload = {
        "type": "full_rebuild",
        "examType": body.examType,
        "years": body.years,
        "sourceUrl": body.sourceUrl,
        "priority": body.priority,
        "idempotencyKey": _idempotency_key("full_rebuild", body.examType, body.years, body.sourceUrl),
    }
    doc, dedup = _enqueue(db, payload)
    return success_response(_to_job_response(doc, dedup)).model_dump()


@router.post("/jobs/export", status_code=201)
def create_export_job(body: ExportJobCreate) -> dict:
    """Queue a CSV export job."""
    db = get_db()
    job_type = f"export_{body.exportType}"
    payload = {
        "type": job_type,
        "examType": body.examType,
        "years": [],
        "priority": body.priority,
        "idempotencyKey": _idempotency_key(job_type, body.examType, [], None),
    }
    doc, dedup = _enqueue(db, payload)
    return success_response(_to_job_response(doc, dedup)).model_dump()


# ---------------------------------------------------------------------------
# Generic create (backward compat / scheduler)
# ---------------------------------------------------------------------------

@router.post("/jobs", status_code=201)
def create_job(job: JobCreate) -> dict:
    db = get_db()
    payload = job.model_dump()
    payload["idempotencyKey"] = _idempotency_key(job.type, job.examType, job.years, job.sourceUrl)
    doc, dedup = _enqueue(db, payload)
    return success_response(_to_job_response(doc, dedup)).model_dump()


# ---------------------------------------------------------------------------
# Read / list / cancel
# ---------------------------------------------------------------------------

@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    db = get_db()
    try:
        doc = db["jobs"].find_one({"_id": ObjectId(job_id)})
    except InvalidId:
        doc = None
    if not doc:
        raise HTTPException(status_code=404, detail="Job not found")
    return success_response(_to_job_response(doc)).model_dump()


@router.get("/jobs")
def list_jobs(
    status: str | None = Query(None, description="Filter by status: queued, running, completed, failed, cancelled"),
    type: str | None = Query(None, description="Filter by job type"),
    examType: str | None = Query(None, alias="examType", description="Filter by exam type: ACSEE or CSEE"),
    year: int | None = Query(None, description="Filter jobs that include this year"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=200),
) -> dict:
    db = get_db()
    query: dict = {}
    if status:
        query["status"] = status
    if type:
        query["type"] = type
    if examType:
        query["examType"] = examType
    if year is not None:
        query["years"] = year  # Mongo matches if array contains value

    total = count_jobs(db, query)
    skip = (page - 1) * pageSize
    cursor = (
        db["jobs"]
        .find(query)
        .sort([("createdAt", -1)])
        .skip(skip)
        .limit(pageSize)
    )
    items = [_to_job_response(doc) for doc in cursor]
    meta = pagination_meta(page=page, page_size=pageSize, total_items=total)
    return success_response(items, meta=meta).model_dump()


@router.post("/jobs/{job_id}/cancel")
def cancel_job_endpoint(job_id: str) -> dict:
    """Best-effort cancel – only works while the job is still queued."""
    db = get_db()
    try:
        oid = ObjectId(job_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid job ID")

    doc = cancel_job(db, oid)
    if not doc:
        existing = db["jobs"].find_one({"_id": oid})
        if not existing:
            raise HTTPException(status_code=404, detail="Job not found")
        raise HTTPException(
            status_code=409,
            detail=f"Job cannot be cancelled – current status is '{existing.get('status')}'",
        )
    return success_response(_to_job_response(doc)).model_dump()
