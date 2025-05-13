from application.results.repository.entities.candidate_results_summary_document import CandidatesResultSummaryDocument
from common.Domain.change_logs import ChangeLog
from common.Enumerations.exam_type import ExamTypeEnum
from datetime import date

from common.Primitives.result_summary_id import ResultSummaryId


class ResultSummaryDocument:
    """
    This class represents the summary of a result document.
    It contains the following attributes:
    - id: The unique identifier for the result document.
    - year: The year of the result.
    - center_id: The unique identifier for the center.
    - candidates_result_summary: The summary of candidates' results.
    """

    def __init__(
            self,
            _id: ResultSummaryId,
            year: int,
            posted_date: date,
            center_id: str,
            exam_type: ExamTypeEnum,
            candidates_result_summary: CandidatesResultSummaryDocument,
            change_logs: list = None,
    ):
        self.id = ResultSummaryIdentifiers(_id)
        self.year = year
        self.center_id = center_id
        self.posted_date = posted_date
        self.exam_type = exam_type
        self.candidates_result_summary = candidates_result_summary
        self.change_logs = change_logs if change_logs else []

    def to_dict(self):
        """
        Convert the ResultSummaryDocument object to a dictionary.
        :return: A dictionary representation of the ResultSummaryDocument object.
        """
        return {
            "identifiers": self.id.to_dict(),
            "year": self.year,
            "centerId": self.center_id,
            "postedFate": self.posted_date,
            "examType": self.exam_type,
            "candidatesResultSummary": self.candidates_result_summary.to_dict(),
            "changeLogs": [log.to_dict() for log in self.change_logs]
        }

    @staticmethod
    def from_dict(data: dict) -> 'ResultSummaryDocument':
        """
        Create a ResultSummaryDocument object from a dictionary.
        :param data: A dictionary containing the data to create the object.
        :return: A ResultSummaryDocument object.
        """
        return ResultSummaryDocument(
            _id=ResultSummaryId(data["identifiers"]["resultSummaryId"]),
            year=data["year"],
            center_id=data["centerId"],
            posted_date=data["postedFate"],
            exam_type=ExamTypeEnum(data["examType"]),
            candidates_result_summary=CandidatesResultSummaryDocument.from_dict(data["candidatesResultSummary"]),
            change_logs=[ChangeLog.from_dict(log) for log in data.get("changeLogs", [])]
        )


class ResultSummaryIdentifiers:
    """
    This class represents the identifiers for a result summary.
    It contains the following attributes:
    - year: The year of the result summary.
    - center_id: The unique identifier for the center.
    """

    def __init__(self, id: ResultSummaryId):
        self.result_summary_id = id

    def to_dict(self):
        """
        Convert the ResultSummaryIdentifiers object to a dictionary.
        :return: A dictionary representation of the ResultSummaryIdentifiers object.
        """
        return {
            "resultSummaryId": self.result_summary_id.value(),
        }

    def __eq__(self, other):
        if not isinstance(other, ResultSummaryIdentifiers):
            return False
        return self.result_summary_id == other.result_summary_id
