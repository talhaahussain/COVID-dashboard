"""
covid_data_handler - This module is the COVID data handler module.
This module is responsible for handling all COVID-19 related data.
This includes...
    - Parsing data from a CSV file into a list of strings to allow processing.
    - Processing a list (read from a CSV file) and returning the relevant interpreted data.
    - Sending a request to Coronavirus API to fetch the relevant COVID-19 data.
    - Parsing the API data into a usable format for the Flask app, via dictionaries.
    - Enabling the user to schedule updates to the COVID-19 data at their chosen interval.
"""
import csv
import json
import sched
import time
import datetime
from uk_covid19 import Cov19API


config_file = open("config.json")
config_data = json.load(config_file)
covid_scheduler = sched.scheduler(time.time, time.sleep)

local_covid_data = {
    "data": None,
    "location": None,
    "local_7day_infections": None,
    "last_update": None
    }
national_covid_data = {
    "data": None,
    "nation_location": None,
    "national_7day_infections": None,
    "hospital_cases": None,
    "deaths_total": None,
    "last_update": None
    }


def parse_csv_data(csv_filename : str) -> list:
    """Returns a list of strings for all lines in a CSV file.

        Parameters:
            csv_filename (str): The name of some CSV file to be parsed.

        Returns:
            data (list): A list of strings for all lines of the CSV file.
    """        
    file_1 = open(csv_filename, "r")
    csvreader = csv.reader(file_1) # Read csv to variable 'csvreader'
    data = []
    for row in csvreader:
        data.append(row) # Append all data read from csv to list, row by row

    return data


def process_covid_csv_data(covid_csv_data: list) -> int:
    """Processes a list and returns data interpreted from the list.

        Parameters:
            covid_csv_data (list): A list of strings for all lines of a CSV file (passed from 'parse_csv_data').

        Returns:
            last7days_cases (int): The sum of all COVID-19 cases in the last 7 days, as interpreted from the list.
            current_hospital_cases (int): The current number of COVID-19-related hospital cases, as interpreted from the list.
            total_deaths (int): The total number of COVID-19-related deaths, as interpreted from the list.
    """    
    days = []
    last7days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0
    for i in range(3,10):
        last7days_cases += int(covid_csv_data[i][-1])
    current_hospital_cases = int(covid_csv_data[1][-2])
    total_deaths = int(covid_csv_data[14][-3])
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> dict:
    """Returns a JSON object containing data on the COVID-19 pandemic from Public Health England.

        Parameters:
            location (str): Specifies the location for which the data is to be fetched.
            location_type (str): Specifies the type of the location.

        Returns:
            data (dict): A dictionary containing the COVID API data as fetched from Public Health England.
    """    
    last_update = datetime.datetime.now()
    location_spec = ["areaType="+str(location_type), "areaName="+str(location)]
    data_spec = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
        }
    api = Cov19API(filters = location_spec, structure = data_spec)
    data = api.get_json()
    process_covid_API_data(data, location_type, location, last_update)
    return data


def process_covid_API_data(data: dict, location_type: str, location: str, last_update: datetime.datetime) -> None:
    """Processes COVID API data according to the required fields and updates two dictionaries to contain this data.

        Parameters:
            data (dict): A dictionary with all fetched data, passed from the 'covid_API_request' function.
            location (str): Specifies the location for which the data is to be fetched.
            location_type (str): Specifies the type of the location.
            last_update (datetime.datetime): Specifies the time at which the 'covid_API_request' function was called.

        Returns:
            None
    """
    _7day_infections = 0
    for i in range(1,8):
        _7day_infections += data["data"][i]["newCasesBySpecimenDate"]
    if location_type == "nation":
        national_covid_data.update({"nation_location": data["data"][1]["areaName"]})
        national_covid_data.update({"national_7day_infections": _7day_infections})
        national_covid_data.update({"hospital_cases": "Current hospital cases: " + str(data["data"][0]["hospitalCases"])})
        national_covid_data.update({"deaths_total": "Deaths as of " +  str(data["data"][17]["date"]) + ": " + str(data["data"][17]["cumDailyNsoDeathsByDeathDate"])})
        national_covid_data.update({"last_update": last_update})
    else:
        local_covid_data.update({"location": data["data"][1]["areaName"]})
        local_covid_data.update({"local_7day_infections": _7day_infections})
        local_covid_data.update({"last_update": last_update})


def schedule_covid_updates(update_interval: datetime.datetime, update_name: str) -> sched.Event:
    """Calls the given function at the given interval.

        Parameters:
            update_interval (datetime.datetime): Specifies when the function will be called using date and time.
            update_name (str): Specifies the name of the function to be called.

        Returns:
            event_id (sched.Event): Specifies a unique ID for the event, which can be used to cancel the update.      
    """
    update_interval = update_interval.timestamp()  # Converts datetime object to UTC
    local_event_id = covid_scheduler.enterabs(update_interval, 1, update_name,(config_data["local_location"], config_data["local_type"]))
    national_event_id = covid_scheduler.enterabs(update_interval, 1, update_name, (config_data["national_location"], "nation"))
    return local_event_id, national_event_id  # Returns two sched.Event objects, which can be used to cancel the update if need be
