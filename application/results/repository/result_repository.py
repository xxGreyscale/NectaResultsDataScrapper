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

    def get_all_acsee_results(self) -> list[ResultDocument]:
        """
        Get all acsee results
        :return:
        """
        try:
            return self.acsee_collection.find().collection
        except Exception as e:
            print(f"Error getting all acsee results with error: {e}")

    def get_aggregated_acsee_results(self) -> any:
        try:
            pipeline = [
                {
                    "$addFields": {
                        "nectaRegistrationNoToMatch": {
                            "$arrayElemAt": [
                                {"$split": ["$identifiers.index_number", "/"]},
                                0  # Get the second element (index 1) which is the ObjectId string
                            ]
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "necta_centers",
                        "localField": "nectaRegistrationNoToMatch",
                        "foreignField": "identifiers.nectaRegistrationNo",
                        "as": "centerDetails"
                    }
                },
                {
                    "$unwind": {
                        "path": "$centerDetails",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "year": "$current.year",
                        "sex": "$current.sex",
                        "aggregate": "$current.aggregate",
                        "division": "$current.division",
                        "subjects": "$current.subjects",
                        "indexNumber": "$identifiers.index_number",
                        "schoolRegistration": "$centerDetails.identifier.schoolRegistrationNo",
                        "nectaRegistration": "$centerDetails.identifier.nectaRegistrationNo",
                        "schoolName": "$centerDetails.current.name",
                        "region": "$centerDetails.current.region",
                        "council": "$centerDetails.current.council",
                        "ward": "$centerDetails.current.ward",
                        "ownership": "$centerDetails.current.ownership",
                        "institutionType": "$centerDetails.current.institutionType",
                        "metadata": "$centerDetails.current.metadata",
                    }
                },
            ]
            results = self.acsee_collection.aggregate(pipeline)
            return results
        except Exception as e:
            print(f"Error got: {e}")
            RuntimeWarning(f"Error getting ACSEE summary: {e}")
