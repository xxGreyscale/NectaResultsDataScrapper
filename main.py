from infastructure.database_config import close_db_client
from usecases.get_necta_results import get_and_save_acsee_results


def get_table():
    url = "https://maktaba.tetea.org/exam-results/"
    years = [year for year in range(2023, 2024)]
    get_and_save_acsee_results(url, "ACSEE", years)
    close_db_client()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Make sure db is available
    get_table()
    # get_excel('resource/2004/enrolment/Secondary_by_Age_and_Sex.xlsx')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
