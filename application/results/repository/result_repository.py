from application.results.repository.entities.results_document import ResultDocument
from infastructure.database_config import get_database


class ResultRepository:
    def __init__(self):
        try:
            db = get_database("mongodb://root:admin@localhost:27018/", "necta")
            self.acsee_collection = db["necta_acsee_results"]
            self.csee_collection = db["necta_csee_results"]
        except Exception as e:
            RuntimeWarning(f"Error connecting to database: {e}")

    def save_acsee_results(self, results: list[ResultDocument]) -> bool:
        """
        Save a list of results to the database.
        :param results: The list of results to save.
        :return: True if the save was successful, False otherwise.
        """
        try:
            self.acsee_collection.insert_many([result.to_dict() for result in results])
        except Exception as e:
            print(f"Error saving results: {e}")
            return False

    def get_acsee_results_by_index_number(self, index: str) -> ResultDocument:
        """
        Get a result by index number.
        :param index: The index number to search for.
        :return: The result document if found, None otherwise.
        """
        try:
            return self.acsee_collection.find_one({"identifiers.index_number": index})
        except Exception as e:
            print(f"Error getting result by index number: {e}")
            raise RuntimeError(f"Error getting result by index number: {e}")
