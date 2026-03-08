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
    "/summaries/{exam_type}/all-years",
    response_model=SuccessResponse[list[dict]],
    responses={500: {"model": ErrorResponse}},
    summary="All-years aggregated summaries — one record per center with per-year breakdown",
    tags=["summaries"],
)
def list_all_years_summaries(
    exam_type: str,
    region: Optional[str] = Query(None, description="Filter by region"),
    sort_by: Optional[str] = Query(None, alias="sortBy", description="Sort field (e.g. 'passRate')"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, alias="pageSize", description="Items per page"),
    svc: ResultsQueryService = Depends(get_results_query_service),
) -> SuccessResponse[list[dict]]:
    items, total = svc.list_all_years_summaries(
        exam_type=exam_type,
        region=region,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return success_response(
        to_jsonable(items),
        meta=pagination_meta(page=page, page_size=page_size, total_items=total),
    )


@router.get(
    "/summaries/{exam_type}",
    response_model=SuccessResponse[list[dict]],
    responses={500: {"model": ErrorResponse}},
    summary="Multi-center result summaries (division distribution per center)",
    tags=["summaries"],
)
def list_summaries(
    exam_type: str,
    year: Optional[int] = Query(None, description="Filter by examination year"),
    center_id: Optional[str] = Query(None, alias="centerId", description="Filter by internal center ID"),
    region: Optional[str] = Query(None, description="Filter by region"),
    sort_by: Optional[str] = Query(None, alias="sortBy", description="Sort field (e.g. 'passRate')"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, alias="pageSize", description="Items per page"),
    svc: ResultsQueryService = Depends(get_results_query_service),
) -> SuccessResponse[list[dict]]:
    items, total = svc.list_summaries(
        exam_type=exam_type,
        year=year,
        center_id=center_id,
        region=region,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    return success_response(
        to_jsonable(items),
        meta=pagination_meta(page=page, page_size=page_size, total_items=total),
    )
