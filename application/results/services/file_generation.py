import csv
import os

from common.helpers.flatten_dict import flatten_dict


class FileGeneration:
    @staticmethod
    def generate_csv(data: list[dict], file_path: str) -> bool:
        """
        Generate a CSV file from the provided data.
        @TODO("Refactor", "Make this more general for more data, or seprate the functions")
        :param directory:
        :param data: List of dictionaries containing the data to be written to the CSV file.
        :param file_path: The path where the CSV file will be saved.
        :return: True if the file was generated successfully, False otherwise.
        """
        try:
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("Created directory:", directory)
            with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                flat_dict = [flatten_dict(item) for item in data if isinstance(item, dict)]
                for item in flat_dict:
                    if not isinstance(item, dict):
                        raise TypeError("Expected a dictionary item in the data list.")

                    keys_to_rename = []
                    # First pass: Identify keys that need to be renamed
                    for k in item.keys():  # Iterate over a view of keys, not the dict itself
                        if k.startswith("candidatesResultSummary_"):
                            keys_to_rename.append(k)

                    # Second pass: Perform the renaming
                    for old_key in keys_to_rename:
                        new_key = old_key.replace("candidatesResultSummary_", "")
                        new_key = standardize_division_key(new_key)

                        # We use .pop() here to remove the old key and get its value in one go
                        # Then assign it to the new key
                        item[new_key] = item.pop(old_key)

                    if "postedFate" in item:
                        item["posted_date"] = item.pop("postedFate")

                fieldnames = [key for key in flat_dict[0].keys()] if flat_dict else []
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in flat_dict:
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