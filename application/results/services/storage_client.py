from typing import Optional

from application.results.repository.result_repository import ResultRepository
from application.results.repository.result_summary_repository import ResultSummaryRepository
from application.results.services.mappers.result_mapper import ResultMapper
from application.results.services.mappers.result_summary_mapper import ResultSummaryMapper
from common.Domain.change_logs import ChangeLog
from common.Domain.necta_year import NectaYearCenterSummary, NectaYear
from common.Domain.result import NectaACSEEResult, NectaCSEEResult
from common.Enumerations.log_action_enum import ActionToChangeEnum


class ResultStorageClient:
    def __init__(self):
        self.result_summary_repo = ResultSummaryRepository()
        self.result_repository = ResultRepository()  # Fine-grained repository
        self.result_mapper = ResultMapper()
        self.result_summary_mapper = ResultSummaryMapper()

    # ------------------------------------------------------------------
    # Write helpers (unchanged)
    # ------------------------------------------------------------------

    def save_acsee_results(self, resultsCollection: list[list[NectaACSEEResult]]):
        try:
            multi_docs = []
            for center_results in resultsCollection:
                for result in center_results:
                    if not isinstance(result, NectaACSEEResult):
                        raise TypeError("Expected NectaACSEEResult instance. but got: " + str(type(result)))
                    if not result.index_number and not result.exam_center:
                        continue
                    saved_result = self.result_repository.get_acsee_results_by_index_number(
                        result.exam_center + "/" + result.index_number)
                    if saved_result:
                        continue
                    doc = self.result_mapper.acsee_to_document(result)
                    multi_docs.append(doc)
            if not multi_docs:
                print("No new results to save")
                return False
            return self.result_repository.save_acsee_results(multi_docs)
        except Exception as e:
            print(f"Error saving results: {e}")
            raise RuntimeError(f"Error saving results: {e}")

    def save_csee_results(self, resultsCollection: list[list[NectaCSEEResult]]):
        try:
            multi_docs = []
            for center_results in resultsCollection:
                for result in center_results:
                    if not isinstance(result, NectaCSEEResult):
                        raise TypeError("Expected NectaCSEEResult instance. but got: " + str(type(result)))
                    if not result.index_number and not result.exam_center:
                        continue
                    saved_result = self.result_repository.get_csee_results_by_index_number(
                        result.exam_center + "/" + result.index_number)
                    if saved_result:
                        continue
                    doc = self.result_mapper.csee_to_document(result)
                    multi_docs.append(doc)
            if not multi_docs:
                print("No new results to save")
                return False
            return self.result_repository.save_csee_results(multi_docs)
        except Exception as e:
            print(f"Error saving results: {e}")
            raise RuntimeError(f"Error saving results: {e}")

    def save_acsee_year_result_summary(self, necta_year: NectaYear) -> bool:
        try:
            print(f"Saving results for year: {necta_year.year}, exam type: {necta_year.exam_type}")
            multiple_summary_doc = []
            for result in necta_year.centers:
                if not isinstance(result, NectaYearCenterSummary):
                    raise TypeError("Expected NectaYearCenterSummary instance")
                saved_result = self.result_summary_repo.get_result_summary_by_year(necta_year.year, "acsee_result_summary")
                if saved_result:
                    continue
                change_logs = [ChangeLog(ActionToChangeEnum.CREATE)]
                doc = self.result_summary_mapper.to_document(
                    necta_year.year,
                    necta_year.exam_type,
                    necta_year.posted_date,
                    result,
                    change_logs
                )
                multiple_summary_doc.append(doc)
            if multiple_summary_doc:
                return self.result_summary_repo.bulk_create_result_summary(multiple_summary_doc, "acsee_result_summary")
            else:
                print("No new results to save")
                return False
        except Exception as e:
            print(f"Error saving results: {e}")
            raise RuntimeError(f"Error saving results: {e}")

    def save_csee_year_result_summary(self, necta_year: NectaYear) -> bool:
        try:
            print(f"Saving results for year: {necta_year.year}, exam type: {necta_year.exam_type}")
            multiple_summary_doc = []
            for result in necta_year.centers:
                if not isinstance(result, NectaYearCenterSummary):
                    raise TypeError("Expected NectaYearCenterSummary instance")
                saved_result = self.result_summary_repo.get_result_summary_by_year(necta_year.year, "csee_result_summary")
                if saved_result:
                    continue
                change_logs = [ChangeLog(ActionToChangeEnum.CREATE)]
                doc = self.result_summary_mapper.to_document(
                    necta_year.year,
                    necta_year.exam_type,
                    necta_year.posted_date,
                    result,
                    change_logs
                )
                multiple_summary_doc.append(doc)
            if multiple_summary_doc:
                return self.result_summary_repo.bulk_create_result_summary(multiple_summary_doc, "csee_result_summary")
            else:
                print("No new results to save")
                return False
        except Exception as e:
            print(f"Error saving results: {e}")
            raise RuntimeError(f"Error saving results: {e}")

    # ------------------------------------------------------------------
    # Summary reads (with filters)
    # ------------------------------------------------------------------

    def get_all_acsee_centers_results_summary(
        self,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            return self.result_summary_repo.get_acsee_summary_results(
                year=year, center_id=center_id, region=region,
                sort_by=sort_by, page=page, page_size=page_size,
            )
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, 0

    def get_all_csee_centers_results_summary(
        self,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            return self.result_summary_repo.get_csee_summary_results(
                year=year, center_id=center_id, region=region,
                sort_by=sort_by, page=page, page_size=page_size,
            )
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, 0

    # ------------------------------------------------------------------
    # All-years aggregated summaries
    # ------------------------------------------------------------------

    def get_all_years_summary(
        self,
        exam_type: str,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            if exam_type.upper() == "ACSEE":
                return self.result_summary_repo.get_acsee_all_years_summary(
                    region=region, sort_by=sort_by, page=page, page_size=page_size,
                )
            else:
                return self.result_summary_repo.get_csee_all_years_summary(
                    region=region, sort_by=sort_by, page=page, page_size=page_size,
                )
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, 0

    # ------------------------------------------------------------------
    # Aggregated individual results (with filters)
    # ------------------------------------------------------------------

    def aggregated_acsee_results(
        self,
        year: Optional[int] = None,
        center: Optional[str] = None,
        subject: Optional[str] = None,
        sex: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            return self.result_repository.get_aggregated_acsee_results(
                year=year, center=center, subject=subject, sex=sex, page=page, page_size=page_size,
            )
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, 0

    def aggregated_csee_results(
        self,
        year: Optional[int] = None,
        center: Optional[str] = None,
        subject: Optional[str] = None,
        sex: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            return self.result_repository.get_aggregated_csee_results(
                year=year, center=center, subject=subject, sex=sex, page=page, page_size=page_size,
            )
        except Exception as e:
            print(f"Error occurred: {e}")
            return None, 0

    # ------------------------------------------------------------------
    # Distinct years
    # ------------------------------------------------------------------

    def get_distinct_result_years(self, exam_type: str) -> list[int]:
        return self.result_repository.get_distinct_years(exam_type)

    def get_distinct_summary_years(self, exam_type: str) -> list[int]:
        collection_name = "acsee_result_summary" if exam_type.upper() == "ACSEE" else "csee_result_summary"
        return self.result_summary_repo.get_distinct_years(collection_name)

    # ------------------------------------------------------------------
    # Center-scoped results (for performance endpoint)
    # ------------------------------------------------------------------

    def get_results_for_center(
        self,
        exam_type: str,
        center_reg_no: str,
        year: Optional[int] = None,
    ) -> list[dict]:
        collection_name = "acsee" if exam_type.upper() == "ACSEE" else "csee"
        return self.result_repository.get_results_for_center(collection_name, center_reg_no, year)

    def get_summaries_for_center(self, exam_type: str, center_id: str) -> list[dict]:
        collection_name = "acsee_result_summary" if exam_type.upper() == "ACSEE" else "csee_result_summary"
        return self.result_summary_repo.get_summaries_for_center(collection_name, center_id)
