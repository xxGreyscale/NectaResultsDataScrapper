
from application.center.repository.center_repository import CenterRepository
from application.center.repository.entities.center import ChangeLog
from application.center.services.center_mappers import CenterMapper
from common.Domain.centersummary import CenterSummary
from common.Enumerations.log_action_enum import ActionToChangeEnum


class CenterStorageClient:
    def __init__(self):
        self.center_repository = CenterRepository()
        self.center_mapper = CenterMapper()

    def save_centers(self, centers: list[CenterSummary]) -> bool:
        """
        Create centers, insert more than one center
        :param centers:
        :return:
        """
        try:
            for center in centers:
                if not isinstance(center, CenterSummary):
                    raise TypeError("Expected CenterSummary instance")
                saved_center = self.center_repository.get_center_by_necta_reg_no(center.necta_reg_no)
                if saved_center:
                    # center already exists, skip saving
                    continue
                change_logs = [ChangeLog(ActionToChangeEnum.CREATE)]
                self.center_repository.create_center(self.center_mapper.to_document_object(center, change_logs))
            return True
        except Exception as e:
            print(f"Error saving centers: {e}")
            raise RuntimeError(f"Error saving centers: {e}")

    def get_centers(self):
        """
        Get all centers
        :return:
        """
        try:
            centers = self.center_repository.get_all_centers()
            if not centers:
                return []
            # Convert to domain objects
            centers = [self.center_mapper.to_domain(center) for center in centers]
            # Filter out None values
            centers = [center for center in centers if center is not None]
            # Sort centers by name
            centers.sort(key=lambda x: x.name)
            return centers
        except Exception as e:
            print(f"Error getting centers: {e}")
            raise RuntimeError(f"Error getting centers: {e}")

    def get_by_necta_reg_no(self, necta_reg_no):
        """
        Get center by necta registration number
        :param necta_reg_no:
        :return:
        """
        try:
            center = self.center_repository.get_center_by_necta_reg_no(necta_reg_no)
            return center
        except Exception as e:
            print(f"Error getting center by necta registration number: {e}")
            raise RuntimeError(f"Error getting center by necta registration number: {e}")
