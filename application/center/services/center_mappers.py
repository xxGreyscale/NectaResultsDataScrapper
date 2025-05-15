from application.center.repository.entities.center import CenterDocument, ChangeLog, CenterIdentifiers, \
    CurrentCenterData
from common.Domain.centersummary import CenterSummary
from common.Primitives.center_id import CenterId
from common.Domain.meta_data import Metadata

DATA_VERSION = 1.0  # change everytime we update data structure during development


class CenterMapper:
    @staticmethod
    def to_document_object(center_summary: CenterSummary, changeLogs: list[ChangeLog]) -> CenterDocument:
        return CenterDocument(
            identifiers=CenterIdentifiers(
                center_id=center_summary.id.value(),
                schoolRegistrationNo=center_summary.school_registration_number,
                nectaRegistrationNo=center_summary.necta_reg_no
            ),
            current=CurrentCenterData(
                name=center_summary.name,
                region=center_summary.region,
                council=center_summary.council,
                ward=center_summary.ward,
                ownership=center_summary.ownership,
                institutionType=center_summary.institution_type,
                metadata=[meta_data for meta_data in center_summary.meta_data] if center_summary.meta_data else None,
            ),
            created_at=center_summary.created_at,
            updated_at=center_summary.updated_at,
            data_version=DATA_VERSION,
            change_logs=[change_log for change_log in changeLogs],
        )

    @staticmethod
    def to_domain(center_document: CenterDocument) -> CenterSummary:
        return CenterSummary(
            id=CenterId(center_document.identifiers.center_id),
            name=center_document.current.name,
            school_registration_number=center_document.identifiers.schoolRegistrationNo,
            necta_reg_no=center_document.identifiers.nectaRegistrationNo,
            region=center_document.current.region,
            council=center_document.current.council,
            ward=center_document.current.ward,
            ownership=center_document.current.ownership,
            institution_type=center_document.current.institutionType,
            created_at=center_document.created_at,
            updated_at=center_document.updated_at,
            meta_data=[Metadata.from_dict(item) for item in center_document.metadata] if center_document.metadata else None,
        )
