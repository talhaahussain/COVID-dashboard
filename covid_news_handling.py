"""
covid_news_handling - This module is the COVID news handling module.
This module is responsible for handling all news related data.
This includes...
    - Sending a request to the News API to fetch the relevant news data.
    - Updating a data structure to hold all of the news data.
    - Enabling the user to schedule updates to the news data at their chosen interval.
"""
import json
import sched
import time
import datetime
import requests
from newsapi import NewsApiClient


config_file = open("config.json")
config_data = json.load(config_file)
news_scheduler = sched.scheduler(time.time, time.sleep)
news_data = []
newsapi = NewsApiClient(api_key = config_data["api_key"])


def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus") -> dict:
    """Fetches latest news articles on the COVID-19 pandemic from the News API and appends this data to a list.

        Parameters:
            covid_terms (str): Keywords which specify what terms the News API should search for.

        Returns:
            response (dict): A dictionary containing the News API data as fetched.
    """
    url = ("https://newsapi.org/v2/everything?")
    parameters = {
        "q" : covid_terms,
        "apiKey" : config_data["api_key"]
        }
    
    response = requests.get(url, params = parameters).json()
    news_data.append(response)
    return response


def update_news(update_interval: datetime.datetime, update_name: str) -> sched.Event:
    """Calls the given function at the given interval.

        Parameters:
            update_interval (datetime.datetime): Specifies when the function will be called using date and time.
            update_name (str): Specifies the name of the function to be called.

        Returns:
            event_id (sched.Event): Specifies a unique ID for the event, which can be used to cancel the update.
    """
    update_interval = update_interval.timestamp()  # Parses datetime object to UTC
    event_id = news_scheduler.enterabs(update_interval, 1, update_name,())  # Generates event ID to allow update cancelling
    return event_id


