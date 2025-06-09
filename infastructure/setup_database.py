from infastructure.database_config import get_database
from pymongo.synchronous.collection import Collection
from collections.abc import Mapping


class DbSetup:
    def __init__(self):
        try:
            db = get_database("mongodb://root:admin@localhost:27018/", "necta")
            self.center_collection = db["necta_centers"]
        #     We can add more collections here
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise RuntimeError(f"Error connecting to database: {e}")

    def setup_indices(self):
        print(f"Connecting to DB and setting up indices...")
        self.make_necta_reg_no_unique_key(self.center_collection)
        # self.make_school_reg_no_unique_key(self.collection)
    #     We can add more indices here

    @staticmethod
    def make_school_reg_no_unique_key(_db):
        try:
            _db.create_index("schoolRegistrationNo", unique=True)
            print("Unique index created on schoolRegistrationNo.")
        except Exception as e:
            print(f"Error creating unique index on schoolRegistrationNo: {e}")
            RuntimeWarning("Error creating unique index on nectaRegistrationNo: {e}")

    @staticmethod
    def make_necta_reg_no_unique_key(_db: Collection[Mapping[str, any]]):
        try:
            # Create a unique index on the 'nectaRegistrationNo' field
            _db.create_index("identifiers.nectaRegistrationNo", unique=True)
            print("Unique index created on nectaRegistrationNo.")
        except Exception as e:
            print(f"Error creating unique index on nectaRegistrationNo: {e}")
            RuntimeWarning("Error creating unique index on nectaRegistrationNo: {e}")

