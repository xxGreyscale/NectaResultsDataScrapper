from application.scrapper.service import fetcher


class XlsxExtractor:
    def __init__(self):
        self.fetcher = fetcher.Fetcher()

    def extract(self, data):
        """
        Extracts the data from the xlsx file
        :param data: The xlsx file to extract
        :return: The extracted data
        """
        try:
            df = self.fetcher.from_xlsx(data)
            return df
        except Exception as e:
            raise RuntimeError(f"Error extracting data from xlsx file: {e}")
