import datetime
import re
import application.extraction.htmlextract as html_e
import application.parser.content_parser_mapper as m
from application.center.services.storage_client import CenterStorageClient
from application.results.services.data_aggregation import DataAggregation
from application.results.services.mappers.result_mapper import ResultMapper
from application.results.services.storage_client import ResultStorageClient
from common.Domain.centersummary import CenterSummary
from common.Domain.necta_year import NectaYear, NectaYearCenterSummary
from common.Domain.result import NectaACSEEResult
from common.Enumerations.exam_type import ExamTypeEnum
from tqdm import tqdm

from usecases.get_center import get_exam_center


def get_and_save_acsee_results(url: str, level: str, years: [int]) -> [NectaYear, list]:
    """"
    This function retrieves the results from the NECTA (or alike) website for a given level and year.
    It uses the extract module to fetch the data and the content_parser_mapper module to parse the tables.
    :param years: 
    :param url: The base URL of the NECTA website
    :param level: The level of the results to retrieve (e.g., CSEE, ACSEE)
    :return: A list of NectaYear objects and a list of centers with their results
    """""
    # @TODO(make sure the confidence level can be tracked and saved to the database. It should not be vague)
    extractor = html_e.HtmlExtract()
    content_mapper = m.ContentParserMapper()
    center_storage_client = CenterStorageClient()
    result_storage_client = ResultStorageClient()

    ranged_years_results = []  # Does not necessarily need it but we want to return something
    for year in years:
        # Let's skip year 2015 and 2008.
        # Year 2015 they used a Distinction Merit system
        # Yeah 2008 is not available
        if year == 2015 or year == 2008:
            print(f"Skipping year: {year}")
            continue
        posted_date = datetime.datetime(year, 7, 14)
        centers_with_results: [CenterSummary, list[NectaACSEEResult]] = []
        yearly_records = NectaYear(year=year, exam_type=ExamTypeEnum[level], centers=[], posted_date=posted_date)

        constructed_url = url + level + str(year) + "/"
        if year < 2010:
            constructed_url += "alevel.html"
        elif year < 2016:
            constructed_url += "alevel.htm"
        else:
            constructed_url += ""
        regex_expression = re.compile(r"^s[0-9]{4}\.htm$") if year > 2008 else re.compile(r"^\.?/s[0-9]{4}\.htm(l)?$")
        print(f"Fetching results for year {year} and level {level} from {constructed_url}")
        # Get the links to the results
        links = extractor.get_result_links_from_url(constructed_url, regex_expression)
        if len(links) < 1:
            print(f"No links found for year {year} and level {level}")
            continue
        print(f"Found {len(links)} links for year {year} and level {level}")
        for link in tqdm(links, desc=f"Taking results from year {year}:", colour="green", total=len(links)):
            if year < 2010:
                constructed_url = constructed_url.replace("alevel.html", "") if year < 2016 else constructed_url
                link_url = constructed_url + "/" + link.get("href").replace("./", "")
            elif 2016 > year > 2009:
                constructed_url = constructed_url.replace("alevel.htm", "")
                link_url = constructed_url + "/" + link.get("href")
            else:
                constructed_url = constructed_url
                link_url = constructed_url + "/" + link.get("href")

            exam_center = get_exam_center(link, center_storage_client)

            tables = extractor.get_tables(url=link_url)
            # Some websites have different table structures
            #  For websites from 2005 -> 2018, the results are in the first table
            #  For websites from 2020 -> 2024, the results are in the third table
            # And some websites have more than 3 tables
            if len(tables) == 0:
                RuntimeWarning(f"No tables found for {year} {level} at {link_url}")
                continue
            if year < 2020:
                center_results = ResultMapper().acsee_result_mapping(exam_center.necta_reg_no,
                                                                     content_mapper.parse_table(tables[0], year), year)
            else:
                center_results = ResultMapper().acsee_result_mapping(exam_center.necta_reg_no,
                                                                     content_mapper.parse_table(tables[2], year), year)

            # Get the aggregated result as a summary for each center
            centers_with_results.append([exam_center, center_results])
            yearly_records.centers.append(
                NectaYearCenterSummary(
                    center=exam_center,
                    result_summary=DataAggregation().aggregate_result_summary_by_gender(center_results))
            )

        # Set the total number of candidates and centers
        yearly_records.total_centers = len(yearly_records.centers)

        # Save the results to the database
        save_results_to_db(centers_with_results, yearly_records, result_storage_client)
        ranged_years_results.append([yearly_records, centers_with_results])

    return ranged_years_results


def save_results_to_db(centers_with_results, yearly_records, result_storage_client: ResultStorageClient):
    """
    This function saves the results to the database.
    :param result_storage_client:
    :param centers_with_results:
    :param yearly_records:
    :return:
    """
    # Save the results to db
    result_storage_client.save_acsee_results([results for _, results in centers_with_results])
    # Save the results summary to db
    result_storage_client.save_acsee_year_result_summary(yearly_records)
