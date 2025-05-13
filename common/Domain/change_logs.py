from _datetime import datetime

from common.Enumerations.log_action_enum import ActionToChangeEnum


class ChangeLog:
    def __init__(
            self,
            action: ActionToChangeEnum,
            created_at: str = None,
            updated_at: str = None
    ):
        self.action = action
        self.created_at = datetime.now() if created_at is None else created_at
        self.updated_at = datetime.now() if updated_at is None else created_at

    def to_dict(self):
        return {
            "action": self.action,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }

    @staticmethod
    def from_dict(data: dict) -> 'ChangeLog':
        return ChangeLog(
            action=ActionToChangeEnum[data["action"]],
            created_at=data["createdAt"],
            updated_at=data["createdAt"]
        )
