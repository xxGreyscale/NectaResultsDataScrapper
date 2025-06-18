import csv
import os

from common.helpers.flatten_dict import flatten_dict


class FileGeneration:
    @staticmethod
    def generate_csv(data: list[dict], fieldnames: list[str], file_path: str) -> bool:
        """
        Generate a CSV file from the provided data.
        @TODO("Refactor", "Make this more general for more data, or separate the functions")
        :param fieldnames:
        :param data: Should be a list flat dictionaries without arrays or nested objects
        :param file_path: The path where the CSV file will be saved.
        :return: True if the file was generated successfully, False otherwise.
        """
        try:
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("Created directory:", directory)
            with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error generating CSV file: {e}")
            return False


def standardize_division_key(key):
    """
    Example function for standardizing division keys.
    Replace this with your actual implementation of standardize_division_key.
    """
    import re
    number_word_to_underscore = {
        'One': 'one', 'Two': 'two', 'Three': 'three', 'Four': 'four',
        'Zero': 'zero'
    }
    pattern = r'(division)([A-Z][a-z]*)'

    match = re.search(pattern, key)
    if match:
        prefix = match.group(1) # 'division'
        number_word = match.group(2) # 'One', 'Two', etc.
        if number_word in number_word_to_underscore:
            replacement = f"{prefix}_{number_word_to_underscore[number_word]}"
            return re.sub(pattern, replacement, key)
    return key