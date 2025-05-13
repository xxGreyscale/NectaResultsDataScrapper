from datetime import date

from common.Domain.centersummary import CenterSummary
from common.Domain.result_summary import CandidatesResultSummary
from common.Enumerations.exam_type import ExamTypeEnum


class NectaYearCenterSummary:
    def __init__(self,
                 center: CenterSummary,
                 result_summary: CandidatesResultSummary,
                 ):
        self.center = center
        self.result_summary = result_summary

    def to_dict(self):
        return {
            "center": self.center.to_dict(),
            "result_summary": self.result_summary.to_dict()
        }


class NectaYear:
    def __init__(self,
                 year: int,
                 centers: [NectaYearCenterSummary] = None,
                 exam_type: ExamTypeEnum = None,  # currently we have only CSEE and ACSEE
                 posted_date: date = None,
                 total_centers: int = None):
        self.year = year
        self.exam_type = exam_type
        self.centers = centers
        self.total_centers = total_centers
        self.updated_at = date.today()
        self.posted_date = posted_date

    def to_dict(self):
        return {
            "year": self.year,
            "result_type": self.exam_type,
            "centers": [center.to_dict() for center in self.centers],
            "total_centers": self.total_centers,
            "posted_date": self.posted_date,
            "updated_at": self.updated_at
        }

    def __str__(self):
        return (f"NectaYear: {self.year},"
                f"Result Type: {self.exam_type},"
                f"Total Centers: {self.total_centers},"
                f"Posted Date: {self.posted_date},"
                f"Updated At: {self.updated_at}")
