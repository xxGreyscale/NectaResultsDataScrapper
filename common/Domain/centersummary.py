from datetime import datetime

from common.Enumerations.small_enumarations import InstitutionTypeEnum
from common.Primitives.center_id import CenterId


class CenterSummary:
    def __init__(
            self,
            name: str,
            id: CenterId,
            region: str = None,
            council: str = None,
            ward: str = None,
            ownership: str = None,
            institution_type: InstitutionTypeEnum = None,
            necta_reg_no: str = None,
            school_registration_number: str = None,
            created_at: datetime = None,
            updated_at: datetime = None,
    ):
        self.name: str = name
        self.id = id
        self.necta_reg_no = necta_reg_no
        self.school_registration_number: str = school_registration_number
        self.region: str = region
        self.council: str = council
        self.ward: str = ward
        self.ownership = ownership
        if institution_type is None:
            self.institution_type: InstitutionTypeEnum = CenterSummary.institution_type(name, necta_reg_no)
        else:
            self.institution_type: InstitutionTypeEnum = institution_type
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()

    def __str__(self):
        return (f"CenterSummary: {self.name}, "
                f"Center ID: {self.id}, "
                f"NECTA Reg No: {self.necta_reg_no}, "
                f"School Registration No: {self.school_registration_number}, "
                f"Region: {self.region}, "
                f"Council: {self.council}, "
                f"Ward: {self.ward}, "
                f"Institution Type: {self.institution_type.value}, "
                f"Ownership: {self.ownership}"
                f"Created At: {self.created_at}, "
                f"Updated At: {self.updated_at}"
                )

    def to_dict(self):
        return {
            "id": self.id.value(),
            "name": self.name,
            "nectaRegNo": self.necta_reg_no,
            "schoolRegistrationNumber": self.school_registration_number,
            "region": self.region,
            "council": self.council,
            "ward": self.ward,
            "ownership": self.ownership,
            "institution_type": self.institution_type.value,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __eq__(self, other):
        if not isinstance(other, CenterSummary):
            return NotImplemented
        return self.name == other.name and self.necta_reg_no == other.necta_reg_no

    @staticmethod
    def institution_type(name: str = None, necta_reg_no: str = None) -> InstitutionTypeEnum:
        if name and "CENTER" in name.upper() and not necta_reg_no.startswith("S"):
            return InstitutionTypeEnum.CENTER
        else:
            return InstitutionTypeEnum.SCHOOL
