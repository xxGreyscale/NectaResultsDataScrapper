from datetime import datetime

from common.Domain.change_logs import ChangeLog
from common.Enumerations.small_enumarations import InstitutionTypeEnum


class CenterDocument:
    def __init__(
            self,
            identifiers: 'CenterIdentifiers',
            current: 'CurrentCenterData',
            data_version: float,
            snapshot: list['CurrentCenterData'] = None,
            change_logs: list[ChangeLog] = None,
            created_at: datetime = None,
            updated_at: datetime = None,
    ):
        self.identifiers = identifiers
        self.current = current
        self.snapshot = snapshot if snapshot is not None else []
        self.data_version = data_version
        self.change_logs = change_logs if change_logs else []
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()

    def to_dict(self):
        return {
            "identifiers": self.identifiers.to_dict(),
            "current": self.current.to_dict(),
            "dataVersion": self.data_version,
            "snapshot": [snapshot.to_dict() for snapshot in self.snapshot] if self.snapshot else None,
            "changeLogs": self.change_logs,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> 'CenterDocument':
        return CenterDocument(
            identifiers=CenterIdentifiers.from_dict(data["identifiers"]),
            current=CurrentCenterData.from_dict(data["current"]),
            data_version=data["dataVersion"],
            snapshot=[CurrentCenterData.from_dict(item) for item in data["snapshot"]] if data.get("snapshot") else None,
            change_logs=[ChangeLog.from_dict(item) for item in data["changeLogs"]] if data.get("changeLogs") else None,
            created_at=datetime.fromisoformat(data["createdAt"]) if data.get("createdAt") else None,
            updated_at=datetime.fromisoformat(data["updatedAt"]) if data.get("updatedAt") else None,
        )


class CenterIdentifiers:
    def __init__(self, center_id: str, schoolRegistrationNo: str, nectaRegistrationNo: str):
        self.center_id = center_id
        self.schoolRegistrationNo = schoolRegistrationNo
        self.nectaRegistrationNo = nectaRegistrationNo

    def to_dict(self):
        return {
            "centerId": self.center_id,
            "schoolRegistrationNo": self.schoolRegistrationNo,
            "nectaRegistrationNo": self.nectaRegistrationNo
        }

    @staticmethod
    def from_dict(data: dict) -> 'CenterIdentifiers':
        return CenterIdentifiers(
            center_id=data.get("centerId"),
            schoolRegistrationNo=data.get("schoolRegistrationNo"),
            nectaRegistrationNo=data.get("nectaRegistrationNo")
        )


class CurrentCenterData:
    def __init__(
            self,
            name: str,
            region: str,
            council: str,
            ward: str,
            ownership: str,
            institutionType: InstitutionTypeEnum,
    ):
        self.name = name
        self.region = region
        self.council = council
        self.ward = ward
        self.ownership = ownership
        self.institutionType = institutionType

    def to_dict(self):
        return {
            "name": self.name,
            "region": self.region,
            "council": self.council,
            "ward": self.ward,
            "ownership": self.ownership,
            "institutionType": self.institutionType.value
        }

    @staticmethod
    def from_dict(data: dict) -> 'CurrentCenterData':
        return CurrentCenterData(
            name=data.get("name"),
            region=data.get("region"),
            council=data.get("council"),
            ward=data.get("ward"),
            ownership=data.get("ownership"),
            institutionType=InstitutionTypeEnum(data.get("institutionType"))
        )
