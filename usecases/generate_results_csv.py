from application.results.services.file_generation import FileGeneration, standardize_division_key
from application.results.services.storage_client import ResultStorageClient
from common.Enumerations.subject import ACSEESubjectEnum
from common.helpers.flatten_dict import flatten_dict


def generate_acsee_results_csv():
    results_storage_client = ResultStorageClient()
    results_cursor = results_storage_client.aggregated_acsee_results()
    if not results_cursor:
        print("No results found")
        return
    try:
        acsee_results = [_summary for _summary in results_cursor]
        flat_dict = [flatten_dict(item) for item in acsee_results if isinstance(item, dict)]
        for item in flat_dict:
            if not isinstance(item, dict):
                raise TypeError("Expected a dictionary item in the data list.")
        initial_fieldnames = [key for key in flat_dict[0].keys()] if flat_dict else []
        # We have subjects for different items
        initial_fieldnames_set = set(initial_fieldnames)
        subjects_to_add_set = set(subject.value for subject in ACSEESubjectEnum)
        final_fieldnames = list(initial_fieldnames_set.union(subjects_to_add_set))
        # Add subjects to the fieldname but remember to remove the column during model creation
        final_fieldnames.append("subjects")
        FileGeneration.generate_csv(flat_dict, final_fieldnames,
                                    "/Users/salinastic/PycharmProjects/necta/resource/csv"
                                    "/students_aggregated_acsee_results.csv")
        print("CSV file generated successfully at students_aggregated_acsee_results.csv")
    except Exception as e:
        print(f"Error generating CSV file: {e}")
        return
