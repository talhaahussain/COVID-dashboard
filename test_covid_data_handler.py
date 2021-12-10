import pytest
import datetime
import time

from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import local_covid_data
from covid_data_handler import national_covid_data
from covid_data_handler import covid_scheduler


def test_parse_csv_data():
    """This test ensures that the 'parse_csv_data' function correctly parses the exemplar CSV file."""
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639


def test_process_covid_csv_data():
    """This test ensures that the 'process_covid_csv_data' function correctly processes the data from the exemplar CSV file."""
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544


def test_covid_API_request():
    """This test ensures that the 'covid_API_request' function returns a dictionary."""
    data = covid_API_request()
    assert isinstance(data, dict)


def test_schedule_covid_updates():
    """This test ensures that the 'schedule_covid_updates' function works correctly,
    by ensuring that it updates the data according to the specified time.
    """
    now = datetime.datetime.now()
    update_interval = now + datetime.timedelta(seconds=1)  # Prepares an update one second away from the current time
    schedule_covid_updates(update_interval, covid_API_request) 
    covid_scheduler.run(blocking=True)
    assert local_covid_data["last_update"].timestamp() - update_interval.timestamp() < 0.5  # Checks that the time between the specified update time and the actual update time is less than half a second 
    assert national_covid_data["last_update"].timestamp() - update_interval.timestamp() < 0.5
