from common.Domain.result import NectaACSEEResult
from common.Domain.result_summary import CandidatesResultSummary, PerDivisionSummary
from common.Enumerations.sex import SexEnum
from common.Enumerations.small_enumarations import DivisionEnum
from common.Primitives.result_summary_id import ResultSummaryId


class DataAggregation:
    def __init__(self):
        pass

    def aggregate_result_summary_by_gender(self, center_results: list[NectaACSEEResult]) -> CandidatesResultSummary:
        results_by_division = {}
        for division in DivisionEnum:
            results_by_division[division] = [
                r for r in center_results if r.division == division
            ]
        return CandidatesResultSummary(
            id=ResultSummaryId().generate(),
            division_one=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.I, [])),
            division_two=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.II, [])),
            division_three=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.III, [])),
            division_four=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.IV, [])),
            division_zero=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.ZERO, [])),
            e_star=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.E_STAR, [])),
            absent=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.ABS, [])),
            result_withheld=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.RESULT_WITHHELD, [])),
            withdrawn=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.WITHDRAWN, [])),
            special_pass=self._specific_division_summary_by_gender(results_by_division.get(DivisionEnum.S_STAR, [])),
        )

    @staticmethod
    def _specific_division_summary_by_gender(specific_division_category: list[NectaACSEEResult]) -> PerDivisionSummary:
        return PerDivisionSummary(
            males=sum(1 for candidate_result in specific_division_category if candidate_result.sex == SexEnum.MALE),
            females=sum(1 for candidate_result in specific_division_category if candidate_result.sex == SexEnum.FEMALE),
            total=len(specific_division_category)
        )
