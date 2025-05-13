from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import DataFrame


class Fetcher:
    def __init__(self):
        pass

    @staticmethod
    def from_website(url):
        """"
        Fetches the html content of a given url
        :param url: The url to fetch
        :return: The html content of the url
        """""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes (e.g., 404)
            soup = BeautifulSoup(response.content, 'html.parser')  # Use response.content for bytes
            return soup
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error fetching URL: {e}")

    @staticmethod
    def from_xlsx(file_path) -> DataFrame:
        """"
        Fetches the xlsx content of a given file path
        :param file_path: The url to fetch
        :return: Dataframe
        """""
        try:
            excel_file = pd.read_excel(file_path, sheet_name=0)
            return excel_file
        except Exception as e:
            raise RuntimeError(f"Error fetching or reading given file path to the excel sheet: {e}")
