from application.results.services.file_generation import FileGeneration, standardize_division_key
from application.results.services.storage_client import ResultStorageClient
from common.helpers.flatten_dict import flatten_dict


def results_summary_csv():
    results_storage_client = ResultStorageClient()
    summary_cursor = results_storage_client.get_all_acsee_centers_results_summary()
    if not summary_cursor:
        print("No results found")
        return
    try:
        summary = [_summary for _summary in summary_cursor]
        flat_dict = [flatten_dict(item) for item in summary if isinstance(item, dict)]
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
        FileGeneration.generate_csv(flat_dict, fieldnames, "/Users/salinastic/PycharmProjects/necta/resource/csv"
                                                           "/acsee_results_summary.csv")
        print("CSV file generated successfully at ../resource/csv/acsee_results_summary.csv")
    except Exception as e:
        print(f"Error generating CSV file: {e}")
        return
