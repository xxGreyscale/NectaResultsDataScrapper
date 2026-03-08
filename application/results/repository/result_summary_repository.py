from typing import Optional

from application.results.repository.entities.result_summary_document import ResultSummaryDocument
from infastructure.database_config import get_database
from infastructure import settings


class ResultSummaryRepository:
    def __init__(self):
        try:
            self.db = get_database("mongodb://root:admin@localhost:27018/", "necta")
        except Exception as e:
            RuntimeWarning(f"Error connecting to database: {e}")

    # ------------------------------------------------------------------
    # Distinct years available in summaries
    # ------------------------------------------------------------------

    def get_distinct_years(self, collection_name: str) -> list[int]:
        """Return sorted list of distinct years in the given summary collection."""
        try:
            years = self.db[collection_name].distinct("year")
            return sorted([int(y) for y in years if y is not None])
        except Exception as e:
            print(f"Error getting distinct years: {e}")
            return []

    # ------------------------------------------------------------------
    # Aggregated summary queries with filters
    # ------------------------------------------------------------------

    def _summary_pipeline(
        self,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[dict]:
        """Build an aggregation pipeline for summary results with optional filters."""
        pipeline: list[dict] = []

        # Pre-match
        pre_match: dict = {}
        if year is not None:
            pre_match["year"] = year
        if center_id:
            pre_match["centerId"] = center_id
        if pre_match:
            pipeline.append({"$match": pre_match})

        # Lookup center details
        pipeline.append({
            "$lookup": {
                "from": "necta_centers",
                "localField": "centerId",
                "foreignField": "identifiers.centerId",
                "as": "centerDetails",
            }
        })
        pipeline.append({"$unwind": "$centerDetails"})

        # Post-match on region (lives on the center)
        if region:
            pipeline.append({
                "$match": {"centerDetails.current.region": {"$regex": region, "$options": "i"}}
            })

        # ------------------------------------------------------------------
        # Always compute passRate as a weighted score inside Mongo.
        # Coefficients come from env-backed settings so they are tuneable.
        # passRate = (w1×divI + w2×divII + w3×divIII + w4×divIV) / (w1 × total)
        # Div 0 and every other non-pass category contribute 0 (failure).
        # ------------------------------------------------------------------
        w1 = settings.DIVISION_WEIGHT_I
        w2 = settings.DIVISION_WEIGHT_II
        w3 = settings.DIVISION_WEIGHT_III
        w4 = settings.DIVISION_WEIGHT_IV

        _crs = "$candidatesResultSummary"
        pipeline.append({
            "$addFields": {
                "_d1": {"$ifNull": [f"{_crs}.divisionOne.total", 0]},
                "_d2": {"$ifNull": [f"{_crs}.divisionTwo.total", 0]},
                "_d3": {"$ifNull": [f"{_crs}.divisionThree.total", 0]},
                "_d4": {"$ifNull": [f"{_crs}.divisionFour.total", 0]},
                "_d0": {"$ifNull": [f"{_crs}.divisionZero.total", 0]},
            }
        })
        pipeline.append({
            "$addFields": {
                "_totalCandidates": {"$add": ["$_d1", "$_d2", "$_d3", "$_d4", "$_d0"]},
                "_weightedSum": {"$add": [
                    {"$multiply": [w1, "$_d1"]},
                    {"$multiply": [w2, "$_d2"]},
                    {"$multiply": [w3, "$_d3"]},
                    {"$multiply": [w4, "$_d4"]},
                ]},
            }
        })
        pipeline.append({
            "$addFields": {
                "passRate": {
                    "$cond": {
                        "if": {"$gt": ["$_totalCandidates", 0]},
                        "then": {"$round": [
                            {"$divide": ["$_weightedSum", {"$multiply": [w1, "$_totalCandidates"]}]},
                            4,
                        ]},
                        "else": 0.0,
                    }
                }
            }
        })

        # Only sort by passRate when explicitly requested
        if sort_by and sort_by.lower() == "passrate":
            pipeline.append({"$sort": {"passRate": -1}})

        # Project
        pipeline.append({
            "$project": {
                "year": 1,
                "postedFate": 1,
                "examType": 1,
                "candidatesResultSummary": 1,
                "passRate": 1,
                "totalCandidates": "$_totalCandidates",
                "schoolRegistration": "$centerDetails.identifier.schoolRegistrationNo",
                "nectaRegistration": "$centerDetails.identifier.nectaRegistrationNo",
                "name": "$centerDetails.current.name",
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

    def _count_summaries(
        self,
        collection_name: str,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
    ) -> int:
        query: dict = {}
        if year is not None:
            query["year"] = year
        if center_id:
            query["centerId"] = center_id
        return self.db[collection_name].count_documents(query)

    def get_acsee_summary_results(
        self,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            pipeline = self._summary_pipeline(year, center_id, region, sort_by, page, page_size)
            results = self.db["acsee_result_summary"].aggregate(pipeline)
            total = self._count_summaries("acsee_result_summary", year, center_id)
            return results, total
        except Exception as e:
            print(f"Error getting ACSEE summary: {e}")
            return None, 0

    def get_csee_summary_results(
        self,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            pipeline = self._summary_pipeline(year, center_id, region, sort_by, page, page_size)
            results = self.db["csee_result_summary"].aggregate(pipeline)
            total = self._count_summaries("csee_result_summary", year, center_id)
            return results, total
        except Exception as e:
            print(f"Error getting CSEE summary: {e}")
            return None, 0

    # ------------------------------------------------------------------
    # All-years aggregated summaries (one record per center)
    # Computes passRate per year first, then averages across years.
    # ------------------------------------------------------------------

    def _all_years_summary_pipeline(
        self,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[dict]:
        """Aggregate all years into one record per center.
        Computes passRate for each year individually, then averages them."""
        pipeline: list[dict] = []

        w1 = settings.DIVISION_WEIGHT_I
        w2 = settings.DIVISION_WEIGHT_II
        w3 = settings.DIVISION_WEIGHT_III
        w4 = settings.DIVISION_WEIGHT_IV

        _crs = "$candidatesResultSummary"

        # --- Step 1: compute per-year passRate on each document ---
        pipeline.append({
            "$addFields": {
                "_d1": {"$ifNull": [f"{_crs}.divisionOne.total", 0]},
                "_d2": {"$ifNull": [f"{_crs}.divisionTwo.total", 0]},
                "_d3": {"$ifNull": [f"{_crs}.divisionThree.total", 0]},
                "_d4": {"$ifNull": [f"{_crs}.divisionFour.total", 0]},
                "_d0": {"$ifNull": [f"{_crs}.divisionZero.total", 0]},
            }
        })
        pipeline.append({
            "$addFields": {
                "_totalCandidates": {"$add": ["$_d1", "$_d2", "$_d3", "$_d4", "$_d0"]},
                "_weightedSum": {"$add": [
                    {"$multiply": [w1, "$_d1"]},
                    {"$multiply": [w2, "$_d2"]},
                    {"$multiply": [w3, "$_d3"]},
                    {"$multiply": [w4, "$_d4"]},
                ]},
            }
        })
        pipeline.append({
            "$addFields": {
                "_yearPassRate": {
                    "$cond": {
                        "if": {"$gt": ["$_totalCandidates", 0]},
                        "then": {"$round": [
                            {"$divide": ["$_weightedSum", {"$multiply": [w1, "$_totalCandidates"]}]},
                            4,
                        ]},
                        "else": 0.0,
                    }
                }
            }
        })

        # --- Step 2: group by center, collect per-year breakdowns ---
        pipeline.append({
            "$group": {
                "_id": "$centerId",
                "yearlyBreakdown": {
                    "$push": {
                        "year": "$year",
                        "passRate": "$_yearPassRate",
                        "totalCandidates": "$_totalCandidates",
                        "candidatesResultSummary": "$candidatesResultSummary",
                    }
                },
                "divisionOneTotal": {"$sum": "$_d1"},
                "divisionTwoTotal": {"$sum": "$_d2"},
                "divisionThreeTotal": {"$sum": "$_d3"},
                "divisionFourTotal": {"$sum": "$_d4"},
                "divisionZeroTotal": {"$sum": "$_d0"},
                "divisionOneMales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionOne.males", 0]}},
                "divisionOneFemales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionOne.females", 0]}},
                "divisionTwoMales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionTwo.males", 0]}},
                "divisionTwoFemales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionTwo.females", 0]}},
                "divisionThreeMales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionThree.males", 0]}},
                "divisionThreeFemales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionThree.females", 0]}},
                "divisionFourMales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionFour.males", 0]}},
                "divisionFourFemales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionFour.females", 0]}},
                "divisionZeroMales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionZero.males", 0]}},
                "divisionZeroFemales": {"$sum": {"$ifNull": ["$candidatesResultSummary.divisionZero.females", 0]}},
                "totalCandidatesAllYears": {"$sum": "$_totalCandidates"},
                "yearsCount": {"$sum": 1},
                "years": {"$push": "$year"},
                # Average of per-year passRates (each year weighted equally)
                "_avgPassRate": {"$avg": "$_yearPassRate"},
            }
        })

        # Lookup center details
        pipeline.append({
            "$lookup": {
                "from": "necta_centers",
                "localField": "_id",
                "foreignField": "identifiers.centerId",
                "as": "centerDetails",
            }
        })
        pipeline.append({"$unwind": "$centerDetails"})

        # Post-match on region
        if region:
            pipeline.append({
                "$match": {"centerDetails.current.region": {"$regex": region, "$options": "i"}}
            })

        # Overall passRate = average of per-year passRates
        pipeline.append({
            "$addFields": {
                "passRate": {"$round": [{"$ifNull": ["$_avgPassRate", 0.0]}, 4]},
            }
        })

        # Sort by passRate when requested
        if sort_by and sort_by.lower() == "passrate":
            pipeline.append({"$sort": {"passRate": -1}})

        # Project
        pipeline.append({
            "$project": {
                "centerId": "$_id",
                "passRate": 1,
                "totalCandidates": "$totalCandidatesAllYears",
                "yearsCount": 1,
                "years": 1,
                "yearlyBreakdown": 1,
                "candidatesResultSummary": {
                    "divisionOne": {"males": "$divisionOneMales", "females": "$divisionOneFemales", "total": "$divisionOneTotal"},
                    "divisionTwo": {"males": "$divisionTwoMales", "females": "$divisionTwoFemales", "total": "$divisionTwoTotal"},
                    "divisionThree": {"males": "$divisionThreeMales", "females": "$divisionThreeFemales", "total": "$divisionThreeTotal"},
                    "divisionFour": {"males": "$divisionFourMales", "females": "$divisionFourFemales", "total": "$divisionFourTotal"},
                    "divisionZero": {"males": "$divisionZeroMales", "females": "$divisionZeroFemales", "total": "$divisionZeroTotal"},
                },
                "name": "$centerDetails.current.name",
                "region": "$centerDetails.current.region",
                "council": "$centerDetails.current.council",
                "ward": "$centerDetails.current.ward",
                "ownership": "$centerDetails.current.ownership",
                "institutionType": "$centerDetails.current.institutionType",
                "schoolRegistration": "$centerDetails.identifier.schoolRegistrationNo",
                "nectaRegistration": "$centerDetails.identifier.nectaRegistrationNo",
            }
        })

        # Pagination
        skip = (page - 1) * page_size
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": page_size})

        return pipeline

    def _count_all_years_centers(self, collection_name: str, region: Optional[str] = None) -> int:
        """Count distinct centers in the collection."""
        try:
            pipeline: list[dict] = [{"$group": {"_id": "$centerId"}}]
            if region:
                pipeline.append({
                    "$lookup": {
                        "from": "necta_centers",
                        "localField": "_id",
                        "foreignField": "identifiers.centerId",
                        "as": "cd",
                    }
                })
                pipeline.append({"$unwind": "$cd"})
                pipeline.append({
                    "$match": {"cd.current.region": {"$regex": region, "$options": "i"}}
                })
            pipeline.append({"$count": "total"})
            result = list(self.db[collection_name].aggregate(pipeline))
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Error counting all-years centers: {e}")
            return 0

    def get_acsee_all_years_summary(
        self,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            pipeline = self._all_years_summary_pipeline(region, sort_by, page, page_size)
            results = self.db["acsee_result_summary"].aggregate(pipeline)
            total = self._count_all_years_centers("acsee_result_summary", region)
            return results, total
        except Exception as e:
            print(f"Error getting ACSEE all-years summary: {e}")
            return None, 0

    def get_csee_all_years_summary(
        self,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ):
        try:
            pipeline = self._all_years_summary_pipeline(region, sort_by, page, page_size)
            results = self.db["csee_result_summary"].aggregate(pipeline)
            total = self._count_all_years_centers("csee_result_summary", region)
            return results, total
        except Exception as e:
            print(f"Error getting CSEE all-years summary: {e}")
            return None, 0

    # ------------------------------------------------------------------
    # Summaries for a specific center (all years)
    # ------------------------------------------------------------------

    def get_summaries_for_center(
        self,
        collection_name: str,
        center_id: str,
    ) -> list[dict]:
        """Return all summary documents for a given center across years."""
        try:
            return list(
                self.db[collection_name].find({"centerId": center_id}).sort("year", 1)
            )
        except Exception as e:
            print(f"Error getting summaries for center: {e}")
            return []

    # ------------------------------------------------------------------
    # Legacy single-document queries (kept for backwards compatibility)
    # ------------------------------------------------------------------

    def get_result_summary_by_year(self, year, collection_name: str) -> ResultSummaryDocument:
        try:
            result = self.db[collection_name].find_one({"year": year})
            return result
        except Exception as e:
            RuntimeWarning(f"Error getting ACSEE summary by year: {e}")

    def get_result_summary_by_center(self, year, center_id, collection_name: str) -> ResultSummaryDocument:
        try:
            result = self.db[collection_name].find_one({"year": year, "centerId": center_id})
            return result
        except Exception as e:
            RuntimeWarning(f"Error getting ACSEE summary by center: {e}")

    def create_result_summary(self, result_summary: ResultSummaryDocument, collection_name: str) -> bool:
        try:
            self.db[collection_name].insert_one(result_summary.to_dict())
            return True
        except Exception as e:
            RuntimeWarning(f"Error creating result summary: {e}")
            return False

    def bulk_create_result_summary(self, result_summaries: list[ResultSummaryDocument], collection_name: str) -> bool:
        try:
            self.db[collection_name].insert_many([result_summary.to_dict() for result_summary in result_summaries])
            return True
        except Exception as e:
            RuntimeWarning(f"Error creating result summaries: {e}")
            return False
