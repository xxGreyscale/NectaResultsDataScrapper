from infastructure.database_config import close_db_client
from infastructure.setup_database import DbSetup
from usecases.generate_results_csv import generate_acsee_results_csv
from usecases.get_necta_results import get_and_save_acsee_results
import argparse


def get_necta_acsee_results(start_year: int = 2022, end_year: int = 2024):
    url = "https://maktaba.tetea.org/exam-results/"
    years = [year for year in range(start_year, end_year)]
    DbSetup().setup_indices()
    get_and_save_acsee_results(url, "ACSEE", years)
    close_db_client()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Make sure db is available
    # results_summary_csv() # Remove after debugging
    generate_acsee_results_csv()
    # parser = argparse.ArgumentParser(
    #     description="A script to process NECTA data, generate CSVs, or extract Excel data."
    # )
    # # Optional argument to run results_summary_csv
    # parser.add_argument(
    #     '--results-summary-csv',
    #     action='store_true',
    #     help='Generate the results summary CSV file.'
    # )
    #
    # parser.add_argument(
    #     '--get-acsee-results',
    #     action='store_true',
    #     help='Run the function to fetch and save ACSEE exam results.'
    # )
    #
    # parser.add_argument(
    #     '--get-table',
    #     action='store_true',  # If this flag is present, its value will be True
    #     help='Run the get_necta_acsee_results() and get then save '
    #          'Necta acsee results in the database. For specified years'
    # )
    #
    # # Arguments for start_year and end_year, dependent on --get-acsee-results
    # parser.add_argument(
    #     '--start-year',
    #     type=int,
    #     default=2022,  # Default value if not provided
    #     help='Specify the start year for fetching ACSEE results (e.g., 2022). Only applicable with --get-acsee-results.'
    # )
    # parser.add_argument(
    #     '--end-year',
    #     type=int,
    #     default=2024,  # Default value if not provided
    #     help='Specify the end year for fetching ACSEE results (inclusive, e.g., 2024). Only applicable with '
    #          '--get-acsee-results.'
    # )
    #
    # args = parser.parse_args()
    #
    # if args.results_summary_csv:
    #     results_summary_csv()
    # if args.get_acsee_results:
    #     if args.start_year is None or args.end_year is None:
    #         print("Error: start_year and end_year must be specified with --get-acsee-results.")
    #     if args.start_year >= args.end_year:
    #         print("Error: start_year must be less than end_year.")
    #     get_necta_acsee_results(args.start_year, args.end_year)
    #
    # if not any(vars(args).values()):  # Check if any argument was provided
    #     print("No specific action requested. Please use --help for options.")
