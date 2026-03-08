from __future__ import annotations

from infastructure.database_config import get_database
from infastructure import settings


def _safe_create_index(collection, keys, **kwargs) -> None:
    """Create an index, logging but not failing on errors."""
    name = kwargs.get("name", str(keys))
    try:
        collection.create_index(keys, **kwargs)
    except Exception as e:
        print(f"Index creation note for {collection.name}.{name}: {type(e).__name__}: {e}")


def setup_api_indexes() -> None:
    db = get_database(settings.MONGO_URI, settings.DB_NAME)

    # ------------------------------------------------------------------
    # Job and export queues
    # ------------------------------------------------------------------
    _safe_create_index(db["jobs"], "idempotencyKey", unique=True)
    _safe_create_index(db["jobs"], "status")
    _safe_create_index(db["exports"], "status")

    # ------------------------------------------------------------------
    # Results – individual documents
    # ------------------------------------------------------------------
    # Primary lookup by index_number
    try:
        db["necta_acsee_results"].create_index("identifiers.index_number", unique=True)
    except Exception:
        _safe_create_index(db["necta_acsee_results"], "identifiers.index_number")

    try:
        db["necta_csee_results"].create_index("identifiers.index_number", unique=True)
    except Exception:
        _safe_create_index(db["necta_csee_results"], "identifiers.index_number")

    # Year filter
    _safe_create_index(db["necta_acsee_results"], "current.year")
    _safe_create_index(db["necta_csee_results"], "current.year")

    # Compound: year + sex (results explorer)
    _safe_create_index(db["necta_acsee_results"], [("current.year", 1), ("current.sex", 1)])
    _safe_create_index(db["necta_csee_results"], [("current.year", 1), ("current.sex", 1)])

    # ------------------------------------------------------------------
    # Result summaries
    # ------------------------------------------------------------------
    try:
        db["acsee_result_summary"].create_index([("year", 1), ("centerId", 1)], unique=True)
    except Exception:
        _safe_create_index(db["acsee_result_summary"], [("year", 1), ("centerId", 1)])

    try:
        db["csee_result_summary"].create_index([("year", 1), ("centerId", 1)], unique=True)
    except Exception:
        _safe_create_index(db["csee_result_summary"], [("year", 1), ("centerId", 1)])

    _safe_create_index(db["acsee_result_summary"], "year")
    _safe_create_index(db["csee_result_summary"], "year")
    _safe_create_index(db["acsee_result_summary"], "centerId")
    _safe_create_index(db["csee_result_summary"], "centerId")

    # ------------------------------------------------------------------
    # Centers – support text/regex search and region/council filter
    # ------------------------------------------------------------------
    _safe_create_index(db["necta_centers"], "identifiers.nectaRegistrationNo")
    _safe_create_index(db["necta_centers"], "identifiers.centerId")
    _safe_create_index(db["necta_centers"], "current.name")
    _safe_create_index(db["necta_centers"], "current.region")
    _safe_create_index(db["necta_centers"], "current.council")

