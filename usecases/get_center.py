from application.center.services.storage_client import CenterStorageClient
from application.extraction.xlsx_extractor import XlsxExtractor
from common.Domain.centersummary import CenterSummary
from common.Domain.meta_data import Metadata
from common.Primitives.center_id import CenterId
from common.helpers.matching_names import get_matching_name

PATH_TO_SECONDARY_SCHOOL_ENROLMENT = 'resource/2004/enrolment/Secondary_by_Age_and_Sex.xlsx'
MATCHING_THRESHOLD = 90


def create_exam_center(link, center_storage_client: CenterStorageClient) -> CenterSummary:
    center_name = " ".join(link.text.strip().split(" ")[1:])
    necta_reg_no = link.text.strip().split(" ")[0]

    exam_center = center_storage_client.get_by_necta_reg_no(necta_reg_no)
    if exam_center:
        return exam_center

    xlsx_extractor = XlsxExtractor()
    try:
        secondary_enrollment_df = xlsx_extractor.extract(PATH_TO_SECONDARY_SCHOOL_ENROLMENT)
        # minimize columns to School name, Reg. no, Ownership, Ward, Region and Council
        secondary_enrollment_df = (
            secondary_enrollment_df)[['School Name', 'Reg. No', 'Ownership', 'Ward', 'Region', 'Council']]
    except FileNotFoundError as e:
        print(f"Warning: Enrollment data file not found at {PATH_TO_SECONDARY_SCHOOL_ENROLMENT}. With error {e}")
        return exam_center
    except KeyError as e:
        print(f"Warning: Expected column {e} not found in enrollment data. Proceeding without it.")
        return exam_center

    exam_center = CenterSummary(name=center_name, id=CenterId().generate(), necta_reg_no=necta_reg_no)
    # search for the name in the secondary enrollment df and get the row
    # if not found, then set the ownership to None
    # and the region, council and ward to None
    # else set the ownership to the value in the df
    # and the region, council and ward to the values in the df
    # get the row in the df
    row, confidence_level = get_matching_name(secondary_enrollment_df, exam_center, MATCHING_THRESHOLD)
    if row is not None:
        exam_center.ownership = row["Ownership"]
        exam_center.region = row["Region"]
        exam_center.council = row["Council"]
        exam_center.ward = row["Ward"]
        exam_center.school_registration_number = row["Reg. No"]
        exam_center.meta_data = [
            Metadata(key="confidenceLevel", value=confidence_level),
            Metadata(key="comments",
                     value="Confidence level is desired to be above 90%, anything below that is less reliable"),
        ]
    # Save the exam center_
    return CenterStorageClient().save_center(exam_center)
