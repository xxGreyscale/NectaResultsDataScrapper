from http.client import HTTPException

import re
from typing import Optional

from application.center.repository.entities.center import CenterDocument
from infastructure.database_config import get_database


class CenterRepository:
    def __init__(self):
        try:
            db = get_database("mongodb://root:admin@localhost:27018/", "necta")
            self.collection = db["necta_centers"]
        except Exception as e:
            RuntimeWarning(f"Error initializing CenterRepository: {e}")

    def get_all_centers(self):
        return self.collection.find()

    def search_centers(
        self,
        search: Optional[str] = None,
        region: Optional[str] = None,
        council: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list, int]:
        """Return a paginated list of center documents matching the given filters."""
        query: dict = {}
        if search:
            escaped = re.escape(search)
            query["$or"] = [
                {"current.name": {"$regex": escaped, "$options": "i"}},
                {"identifiers.nectaRegistrationNo": {"$regex": escaped, "$options": "i"}},
            ]
        if region:
            query["current.region"] = {"$regex": re.escape(region), "$options": "i"}
        if council:
            query["current.council"] = {"$regex": re.escape(council), "$options": "i"}

        total = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = self.collection.find(query).sort("current.name", 1).skip(skip).limit(page_size)
        return list(cursor), total

    def get_distinct_regions(self) -> list[str]:
        """Return sorted distinct region values."""
        regions = self.collection.distinct("current.region")
        return sorted([r for r in regions if r])

    def get_distinct_councils(self, region: Optional[str] = None) -> list[str]:
        """Return sorted distinct council values, optionally filtered by region."""
        query: dict = {}
        if region:
            query["current.region"] = {"$regex": re.escape(region), "$options": "i"}
        councils = self.collection.distinct("current.council", query)
        return sorted([c for c in councils if c])

    def get_center_by_id(self, center_id):
        return self.collection.find_one({"identifiers.centerId": center_id})

    def get_center_by_school_reg_no(self, school_reg_no):
        return self.collection.find_one({"identifiers.schoolRegistrationNo": school_reg_no})

    def get_center_by_necta_reg_no(self, necta_reg_no):
        # nectaRegistrationNo is now inside identifiers
        return self.collection.find_one({"identifiers.nectaRegistrationNo": necta_reg_no})

    def create_center(self, center_data: CenterDocument):
        self.collection.insert_one(center_data.to_dict())
        return center_data

    def create_centers(self, centers: list[CenterDocument]):
        """"
        Create centers, insert more than one center
        :param centers: list of Center objects
        """""
        centers_to_db = []
        for center in centers:
            center_dict = center.to_dict()
            centers_to_db.append(center_dict)
        self.collection.insert_many(centers_to_db)
        return centers

    def update_center(self, _id, data: CenterDocument):
        center_dict = data.to_dict()
        if len(center_dict) == 0:
            return False
        update_result = self.collection.update_one(
            {"_id": _id},
            {"$set": center_dict}
        )
        if update_result.modified_count == 0:
            raise HTTPException()

    def delete_center(self, _id):
        delete_result = self.collection.delete_one({"_id": _id})
        if delete_result.deleted_count != 1:
            raise HTTPException()
        # Find a better response
        return "deleted"
