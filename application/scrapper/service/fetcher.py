import warnings

from bs4 import BeautifulSoup
import requests
import pandas as pd
from pandas import DataFrame

from application.scrapper.exceptions.website_fetch_error import WebsiteFetchError


FALL_BACK_PATH = "/alevel.html"
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
        except requests.exceptions.RequestException as initial_e:
            # Try adding a fallback mechanism, some urls have alevel.html at the end
            # Add the alevel.html and try again
            fallback_url = url.rstrip('/') + FALL_BACK_PATH # Construct fallback URL
            try:
                return self._fetch_html(fallback_url)
            except requests.exceptions.RequestException as fallback_e:
                warnings.warn(f"Error fetching initial URL '{url}': {fallback_e}", RuntimeWarning)
                return BeautifulSoup("", 'html.parser')  # Return empty soup if fallback fails
        except Exception as e:
            warnings.warn(f"Error fetching initial URL '{url}': {e}", RuntimeWarning)
            raise WebsiteFetchError(f"Error fetching URL: {e}")

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
