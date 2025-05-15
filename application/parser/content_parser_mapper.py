import html
import re


class ContentParserMapper:
    @staticmethod
    def parse_table(table: html) -> list:
        # Get headers first, the first row is the headers
        headers = []
        table_object = []
        for index, row in enumerate(table.find_all('tr')):
            if index == 0:
                for header in row.find_all('td'):
                    headers.append(header.text.strip())
            else:
                row_data = {}
                for row_index, data_cell in enumerate(row.find_all('td')):
                    # Extract text, discarding HTML tags using a loop for robustness
                    cell_text = ""
                    for content in data_cell.contents:  # Iterate through cell's children
                        if isinstance(content, str):  # If it's a string, add it
                            cell_text += content
                        else:
                            cell_text += content.get_text(separator=" ")
                    cell_text = cell_text.strip()

                    if cell_text:
                        if headers[row_index] == 'DETAILED SUBJECTS':
                            row_data[headers[row_index]] = ContentParserMapper.detailed_subjects_mapper(cell_text)
                        else:
                            row_data[headers[row_index]] = cell_text
                if row_data:
                    table_object.append(row_data)
        return table_object

    @staticmethod
    def detailed_subjects_mapper(detailed_subjects: str) -> dict:
        """"
        This is specific for the NECTA result page table
        :param detailed_subjects: The detailed subjects string
        :return: A dictionary with subject names as keys and grades as values
        """""
        # Regular expression pattern to find subject and grade
        pattern = r"([a-zA-Z0-9\s/-]+) - '([A-Z/]+)'"
        # Find all matches of the pattern in the string
        matches = re.findall(pattern, detailed_subjects)
        # Convert the list of tuples (subject, grade) to a dictionary
        result_dict = dict(matches)
        # Strip spaces from both keys and values
        stripped_dict = {key.strip(): value.strip() for key, value in result_dict.items()}
        return stripped_dict
