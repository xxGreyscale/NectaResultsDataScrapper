from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from application.center.services.query_service import CenterQueryService
from adopter.api.deps import get_center_query_service
from adopter.api.models import (
    ErrorResponse,
    SuccessResponse,
)
from adopter.api.response_utils import pagination_meta, success_response
from adopter.api.serialization import to_jsonable

router = APIRouter()


# -----------------------------------------------------------------------
# GET /centers  –  paginated, filterable list
# -----------------------------------------------------------------------
@router.get(
    "/centers",
    response_model=SuccessResponse[list[dict]],
    responses={500: {"model": ErrorResponse}},
    summary="List / search centers",
    tags=["centers"],
)
def list_centers(
    search: Optional[str] = Query(None, description="Free-text search on name or NECTA reg no"),
    region: Optional[str] = Query(None, description="Filter by region"),
    council: Optional[str] = Query(None, description="Filter by council"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(50, ge=1, le=500, alias="pageSize", description="Items per page"),
    svc: CenterQueryService = Depends(get_center_query_service),
) -> SuccessResponse[list[dict]]:
    centers, total = svc.list_centers(
        search=search,
        region=region,
        council=council,
        page=page,
        page_size=page_size,
    )
    return success_response(
        to_jsonable(centers),
        meta=pagination_meta(page=page, page_size=page_size, total_items=total),
    )


# -----------------------------------------------------------------------
# GET /centers/{necta_reg_no}  –  single center detail
# -----------------------------------------------------------------------
@router.get(
    "/centers/{necta_reg_no}",
    response_model=SuccessResponse[dict],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Get center details",
    tags=["centers"],
)
def get_center(
    necta_reg_no: str,
    svc: CenterQueryService = Depends(get_center_query_service),
) -> SuccessResponse[dict]:
    center = svc.get_center(necta_reg_no)
    if not center:
        raise HTTPException(status_code=404, detail="Center not found")
    return success_response(to_jsonable(center))


# -----------------------------------------------------------------------
# GET /centers/{necta_reg_no}/performance  –  KPIs for a year
# -----------------------------------------------------------------------
@router.get(
    "/centers/{necta_reg_no}/performance",
    response_model=SuccessResponse[dict],
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Center performance KPIs for a given year and exam type",
    tags=["centers"],
)
def get_center_performance(
    necta_reg_no: str,
    exam_type: str = Query(..., alias="examType", description="ACSEE or CSEE"),
    year: int = Query(..., description="Examination year"),
    svc: CenterQueryService = Depends(get_center_query_service),
) -> SuccessResponse[dict]:
    performance = svc.get_center_performance(
        necta_reg_no=necta_reg_no,
        exam_type=exam_type,
        year=year,
    )
    if not performance:
        raise HTTPException(status_code=404, detail="Center not found or no data for the given year")
    return success_response(to_jsonable(performance))
