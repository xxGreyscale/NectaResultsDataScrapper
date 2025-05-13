from datetime import date

from application.results.repository.entities.candidate_results_summary_document import CandidatesResultSummaryDocument
from application.results.repository.entities.result_summary_document import ResultSummaryDocument
from common.Domain.change_logs import ChangeLog
from common.Domain.necta_year import NectaYearCenterSummary
from common.Domain.result_summary import CandidatesResultSummary, PerDivisionSummary
from common.Enumerations.exam_type import ExamTypeEnum
from common.Primitives.result_summary_id import ResultSummaryId


class ResultSummaryMapper:

    @staticmethod
    def from_raw_parsed_table_data(necta_summary_raw_results: list, ) -> CandidatesResultSummary:
        try:
            extract = list(map(lambda result: {
                "sex": result.get("SEX"),
                "divisionOne": result.get("I"),
                "divisionTwo": result.get("II"),
                "divisionThree": result.get("III"),
                "divisionFour": result.get("IV"),
                "divisionZero": result.get("0")
            }, necta_summary_raw_results))
            division_summary = {
                "divisionOne": PerDivisionSummary(),
                "divisionTwo": PerDivisionSummary(),
                "divisionThree": PerDivisionSummary(),
                "divisionFour": PerDivisionSummary(),
                "divisionZero": PerDivisionSummary()
            }
            for row in extract:
                sex = row.get("sex")
                for division, value in row.items():
                    if value == "F" or value == "T" or value == "M":
                        continue
                    try:
                        count = int(value)
                        if sex == "F":
                            division_summary[division].females += count
                        elif sex == "M":
                            division_summary[division].males += count
                        elif sex == "T":
                            division_summary[division].total += count
                    except ValueError:
                        print(f"Warning: Could not convert value '{value}' for {division} to integer.")
            id = ResultSummaryId().generate()
            return CandidatesResultSummary(
                id=id,
                division_one=division_summary["divisionOne"],
                division_two=division_summary["divisionTwo"],
                division_three=division_summary["divisionThree"],
                division_four=division_summary["divisionFour"],
                division_zero=division_summary["divisionZero"]
            )
        except Exception as e:
            raise ValueError(f"Error mapping NECTA summary results: {e}")

    @staticmethod
    def to_document(
        year: int,
        exam_type: ExamTypeEnum,
        posted_date: date,
        center_summary: NectaYearCenterSummary,
        change_log: list[ChangeLog] = None
    ) -> ResultSummaryDocument:
        id: ResultSummaryId = ResultSummaryId().generate()
        return ResultSummaryDocument(
            _id=id,
            year=year,
            posted_date=posted_date,
            center_id=center_summary.center.id.value(),
            exam_type=exam_type,
            candidates_result_summary=CandidatesResultSummaryDocument(
                division_one=center_summary.result_summary.division_one,
                division_two=center_summary.result_summary.division_two,
                division_three=center_summary.result_summary.division_three,
                division_four=center_summary.result_summary.division_four,
                division_zero=center_summary.result_summary.division_zero
            ),
            change_logs=change_log
        )
