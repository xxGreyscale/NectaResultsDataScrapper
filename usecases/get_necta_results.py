import datetime
import re
import application.extraction.htmlextract as html_e
import application.parser.content_parser_mapper as m
from application.center.services.storage_client import CenterStorageClient
from application.extraction.xlsx_extractor import XlsxExtractor
from application.results.services.data_aggregation import DataAggregation
from application.results.services.mappers.result_mapper import ResultMapper
from application.results.services.storage_client import ResultStorageClient
from common.Domain.centersummary import CenterSummary
from common.Domain.necta_year import NectaYear, NectaYearCenterSummary
from common.Domain.result import NectaACSEEResult
from common.Enumerations.exam_type import ExamTypeEnum
from common.Primitives.center_id import CenterId
from tqdm import tqdm

PATH_TO_SECONDARY_SCHOOL_ENROLMENT = 'resource/2004/enrolment/Secondary_by_Age_and_Sex.xlsx'


def get_and_save_acsee_results(url: str, level: str, years: [int]) -> [NectaYear, list]:
    """"
    This function retrieves the results from the NECTA (or alike) website for a given level and year.
    It uses the extract module to fetch the data and the content_parser_mapper module to parse the tables.
    :param years: 
    :param url: The base URL of the NECTA website
    :param level: The level of the results to retrieve (e.g., CSEE, ACSEE)
    :return: A list of NectaYear objects and a list of centers with their results
    """""
    extractor = html_e.HtmlExtract()
    content_mapper = m.ContentParserMapper()
    xlsx_extractor = XlsxExtractor()
    secondary_enrollment_df = xlsx_extractor.extract(PATH_TO_SECONDARY_SCHOOL_ENROLMENT)
    # minimize columns to School name, Reg. no, Ownership, Ward, Region and Council
    secondary_enrollment_df = (
        secondary_enrollment_df)[['School Name', 'Reg. No', 'Ownership', 'Ward', 'Region', 'Council']]

    ranged_years_results = [] # Does not necessarily need it but we want to return something
    for year in years:
        # Let's skip year 2015 and 2008.
        # Year 2015 they used a Distinction Merit system
        # Yeah 2008 is not available
        if year == 2015 or year == 2008:
            continue
        posted_date = datetime.datetime(year, 7, 14)
        centers_with_results: [CenterSummary, list[NectaACSEEResult]] = []
        yearly_records = NectaYear(year=year, exam_type=ExamTypeEnum[level], centers=[], posted_date=posted_date)
        constructed_url = url + level + str(year) + "/"
        reg_filter = re.compile(r"^s[0-9]{4}\.htm$")
        links = extractor.get_result_links_from_url(constructed_url, reg_filter)
        if len(links) < 1:
            RuntimeWarning(f"No links found for {year} {level} at {constructed_url}")
            continue
        for link in tqdm(links[100:120], desc=f"Taking results from year {year}:", colour="green", total=len(links)):
            link_url = constructed_url + link.get("href")
            center_name = " ".join(link.text.strip().split(" ")[1:])
            center_internal_id = CenterId().generate()
            exam_center = CenterSummary(name=center_name, id=center_internal_id)
            # search for the name in the secondary enrollment df and get the row
            # if not found, then set the ownership to None
            # and the region, council and ward to None
            # else set the ownership to the value in the df
            # and the region, council and ward to the values in the df
            # get the row in the df
            row = (secondary_enrollment_df["School Name"].
                   str.
                   contains(flexible_search_patterns(exam_center.name), case=False, regex=True))
            if row.any():
                row = secondary_enrollment_df[row]
                exam_center.ownership = row.iloc[0]["Ownership"]
                exam_center.region = row.iloc[0]["Region"]
                exam_center.council = row.iloc[0]["Council"]
                exam_center.ward = row.iloc[0]["Ward"]
                exam_center.school_registration_number = row.iloc[0]["Reg. No"]
            # else:
            # No else since they are defaulted to None
            exam_center.necta_reg_no = link.text.strip().split(" ")[0]
            tables = extractor.get_tables(url=link_url)

            # Some websites have different table structures
            #  For websites from 2005 -> 2018, the results are in the first table
            #  For websites from 2020 -> 2024, the results are in the third table
            # And some websites have more than 3 tables
            if len(tables) == 0:
                RuntimeWarning(f"No tables found for {year} {level} at {link_url}")
                continue
            if year < 2020:
                center_results = ResultMapper().acsee_result_mapping(content_mapper.parse_table(tables[0]), year)
            else:
                center_results = ResultMapper().acsee_result_mapping(content_mapper.parse_table(tables[2]), year)

            # Get the aggregated result as a summary for each center
            center_result_summary = DataAggregation().aggregate_result_summary_by_gender(center_results)

            centers_with_results.append([exam_center, center_results])
            yearly_records.centers.append(NectaYearCenterSummary(center=exam_center,
                                                                 result_summary=center_result_summary))
        yearly_records.total_centers = len(yearly_records.centers)

        # Save the centers to db
        CenterStorageClient().save_centers([center for center, _ in centers_with_results])
        # Save the results to db
        ResultStorageClient().save_acsee_results([results for _, results in centers_with_results])
        # Save the results summary to db
        ResultStorageClient().save_acsee_year_result_summary(yearly_records)
        ranged_years_results.append([yearly_records, centers_with_results])

    return ranged_years_results


def flexible_search_patterns(name):
    """
    Creates a regex pattern to match a school name, handling optional apostrophes at the end of the word
    and "seminary"/"seminari" variations, and only applies the seminary variation
    if "seminary" is present in the original name.
    """
    name = name.lower()
    # Split the name into words
    words = name.split()
    # Create a regex pattern for each word
    patterns = []
    for word in words:
        # Handle optional apostrophes at the end of the word
        if word.endswith("'"):
            word = word[:-1]
        # Handle "seminary" and "seminari" variations
        if "seminary" in word:
            patterns.append(f"{word}|'?{word[:-2]}ri")
        else:
            patterns.append(word)
    # Join the patterns with optional spaces in between
    return r"\s*".join(patterns)
