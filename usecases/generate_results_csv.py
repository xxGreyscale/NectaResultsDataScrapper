from application.results.services.file_generation import FileGeneration, standardize_division_key
from application.results.services.storage_client import ResultStorageClient
from common.Enumerations.subject import ACSEESubjectEnum, CSEESubjectEnum
from common.helpers.flatten_dict import flatten_dict
from infastructure import settings


def generate_acsee_results_csv(output_dir: str | None = None) -> str | None:
    results_storage_client = ResultStorageClient()
    results_cursor = results_storage_client.aggregated_acsee_results()
    if not results_cursor:
        print("No results found")
        return None
    try:
        acsee_results = [_summary for _summary in results_cursor]
        flat_dict = [flatten_dict(item) for item in acsee_results if isinstance(item, dict)]
        for item in flat_dict:
            if not isinstance(item, dict):
                raise TypeError("Expected a dictionary item in the data list.")
        initial_fieldnames = [key for key in flat_dict[0].keys()] if flat_dict else []
        initial_fieldnames_set = set(initial_fieldnames)
        subjects_to_add_set = set(subject.value for subject in ACSEESubjectEnum)
        final_fieldnames = list(initial_fieldnames_set.union(subjects_to_add_set))
        final_fieldnames.append("subjects")
        output_dir = output_dir or settings.EXPORT_DIR
        file_path = f"{output_dir}/students_aggregated_acsee_results.csv"
        FileGeneration.generate_csv(flat_dict, final_fieldnames, file_path)
        print(f"CSV file generated successfully at {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating CSV file: {e}")
        return None


def generate_csee_results_csv(output_dir: str | None = None) -> str | None:
    results_storage_client = ResultStorageClient()
    results_cursor = results_storage_client.aggregated_csee_results()
    if not results_cursor:
        print("No results found")
        return None
    try:
        csee_results = [_summary for _summary in results_cursor]
        flat_dict = [flatten_dict(item) for item in csee_results if isinstance(item, dict)]
        for item in flat_dict:
            if not isinstance(item, dict):
                raise TypeError("Expected a dictionary item in the data list.")
        initial_fieldnames = [key for key in flat_dict[0].keys()] if flat_dict else []
        initial_fieldnames_set = set(initial_fieldnames)
        subjects_to_add_set = set(subject.value for subject in CSEESubjectEnum)
        final_fieldnames = list(initial_fieldnames_set.union(subjects_to_add_set))
        final_fieldnames.append("subjects")
        output_dir = output_dir or settings.EXPORT_DIR
        file_path = f"{output_dir}/students_aggregated_csee_results.csv"
        FileGeneration.generate_csv(flat_dict, final_fieldnames, file_path)
        print(f"CSV file generated successfully at {file_path}")
        return file_path
    except Exception as e:
        print(f"Error generating CSV file: {e}")
        return None
