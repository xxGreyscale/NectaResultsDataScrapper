from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import Optional

from application.results.services.query_service import ResultsQueryService
from adopter.api.deps import get_results_query_service
from adopter.api.models import ErrorResponse, SuccessResponse
from adopter.api.response_utils import pagination_meta, success_response
from adopter.api.serialization import to_jsonable

router = APIRouter()


@router.get(
    "/results/{exam_type}",
    response_model=SuccessResponse[list[dict]],
    responses={500: {"model": ErrorResponse}},
    summary="Explore individual results with filters",
    tags=["results"],
)
def list_results(
    exam_type: str,
    year: Optional[int] = Query(None, description="Filter by examination year"),
    center: Optional[str] = Query(None, description="Filter by center NECTA registration number"),
    subject: Optional[str] = Query(None, description="Filter by subject name (partial match)"),
    sex: Optional[str] = Query(None, description="Filter by sex (M or F)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, alias="pageSize", description="Items per page"),
    svc: ResultsQueryService = Depends(get_results_query_service),
) -> SuccessResponse[list[dict]]:
    items, total = svc.list_results(
        exam_type=exam_type,
        year=year,
        center=center,
        subject=subject,
        sex=sex,
        page=page,
        page_size=page_size,
    )
    return success_response(
        to_jsonable(items),
        meta=pagination_meta(page=page, page_size=page_size, total_items=total),
    )

