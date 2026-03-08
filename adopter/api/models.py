from __future__ import annotations

from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Job models
# ---------------------------------------------------------------------------

# --- Generic create (kept for backward compat / scheduler) -----------------

class JobCreate(BaseModel):
    type: Literal["results", "full_rebuild", "export_results", "export_summaries"]
    examType: Literal["ACSEE", "CSEE"]
    years: list[int] = Field(default_factory=list)
    sourceUrl: str | None = None
    priority: int | None = None


# --- Task-specific create models (frontend-facing) -------------------------

class ResultsJobCreate(BaseModel):
    """Queue a job that fetches results for the given years."""
    examType: Literal["ACSEE", "CSEE"]
    years: list[int] = Field(..., min_length=1)
    sourceUrl: str | None = None
    priority: int | None = None


class FullRebuildJobCreate(BaseModel):
    """Queue a job that deletes existing results then re-fetches them."""
    examType: Literal["ACSEE", "CSEE"]
    years: list[int] = Field(..., min_length=1)
    sourceUrl: str | None = None
    priority: int | None = None


class ExportJobCreate(BaseModel):
    """Queue a CSV export job."""
    exportType: Literal["results", "summaries"]
    examType: Literal["ACSEE", "CSEE"]
    priority: int | None = None


# --- Response model (matches what the DB stores) ----------------------------

class JobResponse(BaseModel):
    id: str
    type: str
    examType: str
    years: list[int] = Field(default_factory=list)
    sourceUrl: str | None = None
    priority: int | None = None
    status: str
    idempotencyKey: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    lockedBy: str | None = None
    progress: dict | None = None
    error: str | None = None
    deduplicated: bool = False


# Legacy alias ---------------------------------------------------------------
class JobStatus(BaseModel):
    id: str = Field(alias="_id")
    type: str
    status: str
    payload: dict
    createdAt: datetime
    updatedAt: datetime
    progress: dict | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Generic response envelope
# ---------------------------------------------------------------------------

class PaginationMeta(BaseModel):
    page: int = 1
    pageSize: int = 50
    totalItems: int | None = None
    totalPages: int | None = None


class SuccessResponse(GenericModel, Generic[T]):
    data: T
    meta: dict | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    detail: dict | None = None


class ErrorResponse(BaseModel):
    errors: list[ErrorDetail]
    meta: dict | None = None


# ---------------------------------------------------------------------------
# Center models
# ---------------------------------------------------------------------------

class CenterListItem(BaseModel):
    id: str | None = None
    name: str | None = None
    nectaRegNo: str | None = None
    schoolRegistrationNumber: str | None = None
    region: str | None = None
    council: str | None = None
    ward: str | None = None
    ownership: str | None = None
    institutionType: str | None = None


class CenterDetail(CenterListItem):
    createdAt: str | None = None
    updatedAt: str | None = None
    metaData: list[dict] | None = None


class PerDivisionSummaryModel(BaseModel):
    males: int = 0
    females: int = 0
    total: int = 0


class DivisionDistribution(BaseModel):
    divisionOne: PerDivisionSummaryModel = PerDivisionSummaryModel()
    divisionTwo: PerDivisionSummaryModel = PerDivisionSummaryModel()
    divisionThree: PerDivisionSummaryModel = PerDivisionSummaryModel()
    divisionFour: PerDivisionSummaryModel = PerDivisionSummaryModel()
    divisionZero: PerDivisionSummaryModel = PerDivisionSummaryModel()
    absent: PerDivisionSummaryModel = PerDivisionSummaryModel()
    resultWithheld: PerDivisionSummaryModel = PerDivisionSummaryModel()
    eStar: PerDivisionSummaryModel = PerDivisionSummaryModel()
    withdrawn: PerDivisionSummaryModel = PerDivisionSummaryModel()
    specialPass: PerDivisionSummaryModel = PerDivisionSummaryModel()


class CenterPerformance(BaseModel):
    center: CenterDetail
    year: int
    examType: str
    candidatesCount: int = 0
    passRate: float = 0.0
    divisionDistribution: DivisionDistribution = DivisionDistribution()


# ---------------------------------------------------------------------------
# Results explorer models
# ---------------------------------------------------------------------------

class SubjectGradeItem(BaseModel):
    subject: str
    grade: str


class ResultItem(BaseModel):
    year: int | None = None
    sex: str | None = None
    aggregate: int | str | None = None
    division: str | None = None
    indexNumber: str | None = None
    subjects: list[SubjectGradeItem] | None = None
    schoolName: str | None = None
    nectaRegistration: str | None = None
    region: str | None = None
    council: str | None = None


# ---------------------------------------------------------------------------
# Summaries models
# ---------------------------------------------------------------------------

class SummaryItem(BaseModel):
    year: int | None = None
    examType: str | None = None
    name: str | None = None
    nectaRegistration: str | None = None
    region: str | None = None
    council: str | None = None
    ward: str | None = None
    ownership: str | None = None
    candidatesResultSummary: dict | None = None


# ---------------------------------------------------------------------------
# Meta models
# ---------------------------------------------------------------------------

class YearInfo(BaseModel):
    examType: str
    years: list[int]


class SubjectInfo(BaseModel):
    value: str
    abbreviation: str | None = None


