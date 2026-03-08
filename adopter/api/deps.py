from __future__ import annotations

from functools import lru_cache

from pymongo.database import Database

from application.center.services.query_service import CenterQueryService
from application.results.services.query_service import ResultsQueryService
from infastructure import settings
from infastructure.database_config import get_database


def get_db() -> Database:
    return get_database(settings.MONGO_URI, settings.DB_NAME)


@lru_cache(maxsize=1)
def get_center_query_service() -> CenterQueryService:
    return CenterQueryService()


@lru_cache(maxsize=1)
def get_results_query_service() -> ResultsQueryService:
    return ResultsQueryService()

