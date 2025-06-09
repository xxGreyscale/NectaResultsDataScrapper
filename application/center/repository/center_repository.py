from http.client import HTTPException
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
