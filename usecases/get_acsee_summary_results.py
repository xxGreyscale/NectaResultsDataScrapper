from application.results.services.file_generation import FileGeneration
from application.results.services.storage_client import ResultStorageClient


def results_summary_csv():
    results_storage_client = ResultStorageClient()
    summary_cursor = results_storage_client.get_all_acsee_centers_results_summary()
    if not summary_cursor:
        print("No results found")
        return
    try:
        summary = [_summary for _summary in summary_cursor]
        FileGeneration.generate_csv(summary, "/Users/salinastic/PycharmProjects/necta/resource/csv/acsee_results_summary.csv")
        print("CSV file generated successfully at ../resource/csv/acsee_results_summary.csv")
    except Exception as e:
        print(f"Error generating CSV file: {e}")
        return
