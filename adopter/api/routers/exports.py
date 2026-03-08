from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter
from pymongo import ReturnDocument

from adopter.api.deps import get_db
from adopter.api.serialization import to_jsonable

router = APIRouter()


@router.post("/exports/{export_type}", status_code=201)
def create_export(export_type: str) -> dict:
    db = get_db()
    now = datetime.now(timezone.utc)
    doc = db["exports"].find_one_and_update(
        {"type": export_type, "status": "queued"},
        {"$setOnInsert": {"type": export_type, "status": "queued", "createdAt": now, "updatedAt": now}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return to_jsonable(doc)


@router.get("/exports/{export_id}")
def get_export(export_id: str) -> dict | None:
    db = get_db()
    doc = None
    try:
        doc = db["exports"].find_one({"_id": ObjectId(export_id)})
    except InvalidId:
        doc = None
    return to_jsonable(doc) if doc else None

