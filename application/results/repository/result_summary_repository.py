from application.results.repository.entities.result_summary_document import ResultSummaryDocument
from infastructure.database_config import get_database


class ResultSummaryRepository:
    def __init__(self):
        try:
            self.db = get_database("mongodb://root:admin@localhost:27018/", "necta")
        except Exception as e:
            RuntimeWarning(f"Error connecting to database: {e}")

    def get_acsee_summary(self, year) -> ResultSummaryDocument:
        """
        Get a summary of ACSEE results for a specific year.
        :param year: The year for which to retrieve the summary.
        :return: A dictionary containing the summary data.
        """
        try:
            result = self.db["acsee_result_summary"].find_one({"year": year})
            return result
        except Exception as e:
            RuntimeWarning(f"Error getting ACSEE summary: {e}")

    def get_result_summary_by_year(self, year, collection_name: str) -> ResultSummaryDocument:
        """
        Get a summary of results for a specific year.
        :param year: The year for which to retrieve the summary.
        :return: A dictionary containing the summary data.
        """
        try:
            result = self.db[collection_name].find_one({"year": year})
            return result
        except Exception as e:
            RuntimeWarning(f"Error getting ACSEE summary by year: {e}")

    def get_result_summary_by_center(self, year, center_id, collection_name: str) -> ResultSummaryDocument:
        """
        Get a summary of results for a specific year and center.
        :param year: The year for which to retrieve the summary.
        :param center_id: The ID of the center for which to retrieve the summary.
        :return: A dictionary containing the summary data.
        """
        try:
            result = self.db[collection_name].find_one({"year": year, "center_id": center_id})
            return result
        except Exception as e:
            RuntimeWarning(f"Error getting ACSEE summary by center: {e}")

    def create_result_summary(self, result_summary: ResultSummaryDocument, collection_name: str) -> bool:
        """
        Create a new result summary.
        :param result_summary: The result summary to create.
        :return: True if the creation was successful, False otherwise.
        """
        try:
            self.db[collection_name].insert_one(result_summary.to_dict())
            return True
        except Exception as e:
            RuntimeWarning(f"Error creating result summary: {e}")
            return False

    def bulk_create_result_summary(self, result_summaries: list[ResultSummaryDocument], collection_name: str) -> bool:
        """
        Create multiple result summaries.
        :param result_summaries: The result summaries to create.
        :return: True if the creation was successful, False otherwise.
        """
        try:
            self.db[collection_name].insert_many([result_summary.to_dict() for result_summary in result_summaries])
            return True
        except Exception as e:
            RuntimeWarning(f"Error creating result summaries: {e}")
            return False
