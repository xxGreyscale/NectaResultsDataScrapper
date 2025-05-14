import re

from application.scrapper.service import fetcher


class HtmlExtract:
    def __init__(self):
        self.fetcher = fetcher.Fetcher()

    def get_all_links(self, url: str):
        # Get all the links from the page
        soup = self.fetcher.from_website(url)
        links = []
        for link in soup.find_all("a"):
            links.append(link.get('href'))
        return links

    def get_tables(self, url):
        """"
        Get all the tables from the page
        :param url: The url to fetch
        :return: The tables from the page
        """""
        soup = self.fetcher.from_website(url)
        tables = []
        for table in soup.find_all('table'):
            tables.append(table)
            # There are only two tables in the nectar page
        return tables

    def get_indexed_urls(self, url: str, index_annotator: str) -> list:
        """"
        Get the links in a given page of of given index,
        These links often include an index at the very end of the url. 
        Example: https://www.example.com/page/index_b.html
        :param index_annotator: 
        :param url: The url to fetch
        """""
        soup = self.fetcher.from_website(url)
        links = []

        for link in soup.find_all(href=re.compile("index_annotator")):
            links.append(link.get('href'))
        return links

    def get_indexed_url(self, url: str, index_annotator: str, index: str):
        """""
        Get specified index url
        """""
        soup = self.fetcher.from_website(url)
        link = soup.find(href=re.compile(index_annotator + index))
        return link.get('href')

    def get_result_links_from_url(self, url: str, reg_filter: re):
        """""
        Get results links, in this context. All centre
        """""
        soup = self.fetcher.from_website(url) # Get the soup object, Can come back as an empty soup object
        links = []
        for link in soup.find_all(href=reg_filter):
            links.append(link)
        return links
