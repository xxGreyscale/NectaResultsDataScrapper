from datetime import datetime

from common.Domain.result import SubjectAndGrade
from common.Enumerations.sex import SexEnum
from common.Enumerations.small_enumarations import DivisionEnum


class ResultDocumentIdentifiers:
    def __init__(self, index_number: str = None):
        self.index_number = index_number

    def __str__(self):
        return f"ResultDocumentIdentifiers(index_number={self.index_number})"

    def __eq__(self, other):
        if not isinstance(other, ResultDocumentIdentifiers):
            return NotImplemented
        return self.index_number == other.index_number

    def __hash__(self):
        return hash(self.index_number)

    def to_dict(self):
        return {
            "index_number": self.index_number,
        }

    @staticmethod
    def from_dict(data: dict) -> 'ResultDocumentIdentifiers':
        return ResultDocumentIdentifiers(
            index_number=data["index_number"],
        )


class CurrentResultDocument:
    def __init__(
            self,
            year: int,
            sex: SexEnum,
            aggregate: int,
            division: DivisionEnum = None,
            subjects: list[SubjectAndGrade] = None,
    ):
        self.year = year
        self.sex = sex
        self.aggregate = aggregate
        self.division = division
        self.subjects = subjects if subjects else []

    def to_dict(self):
        return {
            "year": self.year,
            "sex": self.sex,
            "aggregate": self.aggregate,
            "division": self.division,
            "subjects": [subject.to_dict() for subject in self.subjects] if self.subjects else None,
        }

    @staticmethod
    def from_dict(data: dict) -> 'CurrentResultDocument':
        return CurrentResultDocument(
            year=data["year"],
            subjects=SubjectAndGrade.from_dict(data["subjects"]) if data.get("subjects") else None,
            sex=data["sex"],
            aggregate=data["aggregate"],
            division=data["division"],
        )


class ResultDocument:
    def __init__(
            self,
            identifiers: ResultDocumentIdentifiers,
            current: CurrentResultDocument,
            data_version: float,
            snapshots: list[CurrentResultDocument] = None,
            created_at: datetime = None,
            updated_at: datetime = None,
    ):
        self.identifiers = identifiers
        self.current = current
        self.snapshots = snapshots if snapshots is not None else []
        self.data_version = data_version
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()

    def to_dict(self):
        return {
            "identifiers": self.identifiers.to_dict(),
            "current": self.current.to_dict(),
            "snapshots": [result.to_dict() for result in self.snapshots] if self.snapshots else None,
            "dataVersion": self.data_version,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict) -> 'ResultDocument':
        identifiers = ResultDocumentIdentifiers.from_dict(data["identifiers"])
        current = CurrentResultDocument.from_dict(data["current"])
        snapshots = [CurrentResultDocument.from_dict(item) for item in data["snapshots"]] if data["snapshots"] else None
        return ResultDocument(
            identifiers=identifiers,
            current=current,
            data_version=data["dataVersion"],
            snapshots=snapshots,
            created_at=datetime.fromisoformat(data["createdAt"]),
            updated_at=datetime.fromisoformat(data["updatedAt"]),
        )
