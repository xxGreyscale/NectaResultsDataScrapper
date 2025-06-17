from pymongo.synchronous.database import Database

from application.results.repository.result_repository import ResultRepository
from application.results.repository.result_summary_repository import ResultSummaryRepository
from application.results.services.mappers.result_mapper import ResultMapper
from application.results.services.mappers.result_summary_mapper import ResultSummaryMapper
from common.Domain.change_logs import ChangeLog
from common.Domain.necta_year import NectaYearCenterSummary, NectaYear
from common.Domain.result import NectaACSEEResult
from common.Enumerations.log_action_enum import ActionToChangeEnum


class ResultStorageClient:
    def __init__(self):
        self.result_summary_repo = ResultSummaryRepository()
        self.result_repository = ResultRepository()  # Fine-grained repository
        self.result_mapper = ResultMapper()
        self.result_summary_mapper = ResultSummaryMapper()

    # def save_detailed_results(self, necta_year: NectaYear) -> bool:
    #

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
                        # result already exists, skip saving
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

    def save_acsee_year_result_summary(self, necta_year: NectaYear) -> bool:
        """
        Create results, insert more than one result
        :param necta_year: NectaYear object
        """
        try:
            print(f"Saving results for year: {necta_year.year}, exam type: {necta_year.exam_type}")
            multiple_summary_doc = []
            for result in necta_year.centers:
                if not isinstance(result, NectaYearCenterSummary):
                    raise TypeError("Expected NectaYearCenterSummary instance")
                saved_result = self.result_summary_repo.get_result_summary_by_year(necta_year.year, "acsee_result_summary")
                if saved_result:
                    # result already exists, skip saving
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

    def get_all_acsee_centers_results_summary(self) -> any:
        """
        :return:
        """
        try:
            print("Getting all centers results summary..")
            # @TODO(refactor): Use a more specific return type instead of any
            # @TODO(refactor): Do proper mapping of the results to a specific type
            return self.result_summary_repo.get_acsee_summary_results()
        except Exception as e:
            print(f"Error occurred: {e}")
