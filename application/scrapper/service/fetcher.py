import warnings

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import DataFrame

from application.scrapper.exceptions.website_fetch_error import WebsiteFetchError


class Fetcher:
    def __init__(self):
        pass

    @staticmethod
    def _fetch_html(url: str) -> BeautifulSoup:
        """Internal helper to fetch and parse HTML from a URL."""
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')

    def from_website(self, url):
        """"
        Fetches the html content of a given url
        :param url: The url to fetch
        :return: The html content of the url
        """""
        try:
            return self._fetch_html(url)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # warnings.warn(f"Error fetching initial URL '{url}': {e}", RuntimeWarning)
                print(f"Error fetching initial URL '{url}': {e}")
                return BeautifulSoup("", 'html.parser')
            elif e.response.status_code == 500:
                warnings.warn(f"Error fetching initial URL '{url}': {e}", RuntimeWarning)
                return BeautifulSoup("", 'html.parser')
            else:
                raise WebsiteFetchError(f"HTTP error: {e}")
        except Exception as e:
            raise WebsiteFetchError(f"HTTP error: {e}")

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
