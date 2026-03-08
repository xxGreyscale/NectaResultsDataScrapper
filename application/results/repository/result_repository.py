from typing import Optional

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

    # ------------------------------------------------------------------
    # Write helpers (unchanged)
    # ------------------------------------------------------------------

    def save_acsee_results(self, results: list[ResultDocument]) -> bool:
        try:
            self.acsee_collection.insert_many([result.to_dict() for result in results])
        except Exception as e:
            print(f"Error saving results: {e}")
            return False

    def save_csee_results(self, results: list[ResultDocument]) -> bool:
        try:
            self.csee_collection.insert_many([result.to_dict() for result in results])
        except Exception as e:
            print(f"Error saving results: {e}")
            return False

    # ------------------------------------------------------------------
    # Single-document lookups
    # ------------------------------------------------------------------

    def get_acsee_results_by_index_number(self, index: str) -> ResultDocument:
        try:
            return self.acsee_collection.find_one({"identifiers.index_number": index})
        except Exception as e:
            print(f"Error getting result by index number: {e}")
            raise RuntimeError(f"Error getting result by index number: {e}")

    def get_csee_results_by_index_number(self, index: str) -> ResultDocument:
        try:
            return self.csee_collection.find_one({"identifiers.index_number": index})
        except Exception as e:
            print(f"Error getting result by index number: {e}")
            raise RuntimeError(f"Error getting result by index number: {e}")

    # ------------------------------------------------------------------
    # Legacy bulk reads
    # ------------------------------------------------------------------

    def get_all_acsee_results(self) -> list[ResultDocument]:
        try:
            return self.acsee_collection.find().collection
        except Exception as e:
            print(f"Error getting all acsee results with error: {e}")

    def get_all_csee_results(self) -> list[ResultDocument]:
        try:
            return self.csee_collection.find().collection
        except Exception as e:
            print(f"Error getting all csee results with error: {e}")

    # ------------------------------------------------------------------
    # Distinct years
    # ------------------------------------------------------------------

    def get_distinct_years(self, exam_type: str) -> list[int]:
        """Return sorted distinct years stored in the results collection."""
        collection = self.acsee_collection if exam_type.upper() == "ACSEE" else self.csee_collection
        years = collection.distinct("current.year")
        return sorted([int(y) for y in years if y is not None])

    # ------------------------------------------------------------------
    # Aggregated results with filters
    # ------------------------------------------------------------------

    def _build_aggregation_pipeline(
        self,
        year: Optional[int] = None,
        center: Optional[str] = None,
        subject: Optional[str] = None,
        sex: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[dict]:
        """Build a reusable MongoDB aggregation pipeline with optional match filters."""
        pipeline: list[dict] = []

        # Pre-match on the results collection before the $lookup
        pre_match: dict = {}
        if year is not None:
            pre_match["current.year"] = year
        if sex:
            pre_match["current.sex"] = sex
        if center:
            pre_match["identifiers.index_number"] = {"$regex": f"^{center}/", "$options": "i"}
        if pre_match:
            pipeline.append({"$match": pre_match})

        # Extract the center portion of the index_number for lookup
        pipeline.append({
            "$addFields": {
                "nectaRegistrationNoToMatch": {
                    "$arrayElemAt": [
                        {"$split": ["$identifiers.index_number", "/"]},
                        0,
                    ]
                }
            }
        })

        # Join with centres collection
        pipeline.append({
            "$lookup": {
                "from": "necta_centers",
                "localField": "nectaRegistrationNoToMatch",
                "foreignField": "identifiers.nectaRegistrationNo",
                "as": "centerDetails",
            }
        })
        pipeline.append({
            "$unwind": {
                "path": "$centerDetails",
                "preserveNullAndEmptyArrays": True,
            }
        })

        # Post-match on subject if requested (array element match)
        if subject:
            pipeline.append({
                "$match": {
                    "current.subjects": {
                        "$elemMatch": {"subject": {"$regex": subject, "$options": "i"}}
                    }
                }
            })

        # Project
        pipeline.append({
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
        })

        # Pagination
        skip = (page - 1) * page_size
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": page_size})

        return pipeline

    def _count_with_filters(
        self,
        collection,
        year: Optional[int] = None,
        center: Optional[str] = None,
        sex: Optional[str] = None,
    ) -> int:
        """Quick count matching the pre-match portion of the pipeline."""
        query: dict = {}
        if year is not None:
            query["current.year"] = year
        if sex:
            query["current.sex"] = sex
        if center:
            query["identifiers.index_number"] = {"$regex": f"^{center}/", "$options": "i"}
        return collection.count_documents(query)

    def get_aggregated_acsee_results(
        self,
        year: Optional[int] = None,
        center: Optional[str] = None,
        subject: Optional[str] = None,
        sex: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            pipeline = self._build_aggregation_pipeline(year, center, subject, sex, page, page_size)
            results = self.acsee_collection.aggregate(pipeline)
            total = self._count_with_filters(self.acsee_collection, year, center, sex)
            return results, total
        except Exception as e:
            print(f"Error got: {e}")
            return None, 0

    def get_aggregated_csee_results(
        self,
        year: Optional[int] = None,
        center: Optional[str] = None,
        subject: Optional[str] = None,
        sex: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            pipeline = self._build_aggregation_pipeline(year, center, subject, sex, page, page_size)
            results = self.csee_collection.aggregate(pipeline)
            total = self._count_with_filters(self.csee_collection, year, center, sex)
            return results, total
        except Exception as e:
            print(f"Error got: {e}")
            return None, 0

    # ------------------------------------------------------------------
    # Center-scoped results (for performance endpoint)
    # ------------------------------------------------------------------

    def get_results_for_center(
        self,
        collection_name: str,
        center_reg_no: str,
        year: Optional[int] = None,
    ) -> list[dict]:
        """Return raw result documents for a specific center, optionally filtered by year."""
        collection = self.acsee_collection if collection_name == "acsee" else self.csee_collection
        query: dict = {
            "identifiers.index_number": {"$regex": f"^{center_reg_no}/", "$options": "i"}
        }
        if year is not None:
            query["current.year"] = year
        return list(collection.find(query))
