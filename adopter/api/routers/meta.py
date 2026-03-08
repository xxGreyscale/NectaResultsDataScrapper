from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from typing import Optional

from application.center.services.query_service import CenterQueryService
from application.results.services.query_service import ResultsQueryService
from adopter.api.deps import get_center_query_service, get_results_query_service
from adopter.api.models import SuccessResponse, YearInfo, SubjectInfo
from adopter.api.response_utils import success_response
from common.Enumerations.exam_type import ExamTypeEnum
from common.Enumerations.subject import ACSEESubjectEnum, CSEESubjectEnum
from common.Enumerations.sex import SexEnum

router = APIRouter()


# -----------------------------------------------------------------------
# Exam types
# -----------------------------------------------------------------------
@router.get("/meta/exam-types", tags=["meta"], summary="Available exam types")
def exam_types() -> list[str]:
    return [item.value for item in ExamTypeEnum]


# -----------------------------------------------------------------------
# Subjects
# -----------------------------------------------------------------------
@router.get(
    "/meta/subjects/acsee",
    response_model=list[SubjectInfo],
    tags=["meta"],
    summary="ACSEE subject catalogue",
)
def acsee_subjects() -> list[SubjectInfo]:
    return [
        SubjectInfo(value=item.value, abbreviation=item.abbreviation)
        for item in ACSEESubjectEnum
    ]


@router.get(
    "/meta/subjects/csee",
    response_model=list[SubjectInfo],
    tags=["meta"],
    summary="CSEE subject catalogue",
)
def csee_subjects() -> list[SubjectInfo]:
    return [
        SubjectInfo(value=item.value, abbreviation=item.abbreviation)
        for item in CSEESubjectEnum
    ]


# -----------------------------------------------------------------------
# Sex
# -----------------------------------------------------------------------
@router.get("/meta/sex", tags=["meta"], summary="Sex filter values")
def sexes() -> list[str]:
    return [item.value for item in SexEnum]


# -----------------------------------------------------------------------
# Years (NEW) – available exam years per type
# -----------------------------------------------------------------------
@router.get(
    "/meta/years",
    response_model=SuccessResponse[list[YearInfo]],
    tags=["meta"],
    summary="Available examination years per exam type",
)
def available_years(
    svc: ResultsQueryService = Depends(get_results_query_service),
) -> SuccessResponse[list[YearInfo]]:
    data = []
    for et in ExamTypeEnum:
        years = svc.get_available_years(et.value)
        data.append(YearInfo(examType=et.value, years=years))
    return success_response(data)


# -----------------------------------------------------------------------
# Regions & councils (NEW) – for filter dropdowns
# -----------------------------------------------------------------------
@router.get(
    "/meta/regions",
    response_model=SuccessResponse[list[str]],
    tags=["meta"],
    summary="Distinct regions",
)
def regions(
    svc: CenterQueryService = Depends(get_center_query_service),
) -> SuccessResponse[list[str]]:
    return success_response(svc.get_distinct_regions())


@router.get(
    "/meta/councils",
    response_model=SuccessResponse[list[str]],
    tags=["meta"],
    summary="Distinct councils (optionally filtered by region)",
)
def councils(
    region: Optional[str] = Query(None, description="Filter councils by region"),
    svc: CenterQueryService = Depends(get_center_query_service),
) -> SuccessResponse[list[str]]:
    return success_response(svc.get_distinct_councils(region))


