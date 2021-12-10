"""main - This module is the main Flask app."""

import json
import logging
import datetime
import time
import sched
from flask import Flask, render_template, request

import covid_data_handler
import covid_news_handling 

FORMAT = "%(levelname)s: %(asctime)s %(message)s"
logging.basicConfig(filename="system_log.log", level=logging.DEBUG, format=FORMAT)
app = Flask(__name__)
logging.info("Program has been launched.")
covid_scheduler = covid_data_handler.covid_scheduler
news_scheduler = covid_news_handling.news_scheduler
updates = []

try:
    covid_data_handler.covid_API_request(location = covid_data_handler.config_data["local_location"],
                                         location_type = covid_data_handler.config_data["local_type"])
    covid_data_handler.covid_API_request(location = covid_data_handler.config_data["national_location"],
                                         location_type = "nation")
except:
    # If unable to connect with the API, log the issue and terminate the program.
    logging.critical("Connection to Coronavirus API has failed. Terminating the program.")
    exit()

try:
    covid_news_handling.news_API_request()
except:
    logging.critical("Connection to News API has failed. Terminating the program.")
    exit()


@app.route("/")
def index() -> render_template:
    """This is the index page for the website."""
    logging.info("The user has navigated to index.")
    
    for item in updates:
        """ EXPIRY CHECK """
        if (item["time"] < (datetime.datetime.now())) and (item["repeat"] == False):
            item["complete"] = True

        """ CANCELLING UPDATES """
        if item ["cancelled"] == True:
            if item["covid-data"] == True:
                # Remove the item from the covid scheduler queue
                covid_scheduler.cancel(item["covid_event_ids"][0])
                covid_scheduler.cancel(item["covid_event_ids"][1])
            if item["news"] == True:
                # Remove the item from the news scheduler queue
                news_scheduler.cancel(item["news_event_id"])
            logging.info("The user has cancelled update '" + str(item["title"]) + "' for " + str(item["time"]) + ".")
            updates.remove(item)

        """ CARRYING OUT OPERATION """       
        if (item["complete"] == False) and (item["cancelled"] == False):        
            if (item["covid-data"] == True) and (item["news"] == True) and (item["repeat"] == True):
                item["covid_event_ids"] = covid_data_handler.schedule_covid_updates(item["time"], covid_data_handler.covid_API_request)
                item["news_event_id"] = covid_news_handling.update_news(item["time"], covid_news_handling.news_API_request)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the COVID scheduler.")
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the news scheduler.")
                item["time"] += datetime.timedelta(days=1)  # Increment time by 1 day, so that the update can be repeated again tomorrow at the same time
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " is now scheduled to repeat tomorrow.")
                
            elif (item["covid-data"] == True) and (item["news"] == True) and (item["repeat"] == False):
                item["covid_event_ids"] = covid_data_handler.schedule_covid_updates(item["time"], covid_data_handler.covid_API_request)
                item["news_event_id"] = covid_news_handling.update_news(item["time"], covid_news_handling.news_API_request)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the COVID scheduler.")
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the news scheduler.")
                
            elif (item["covid-data"] == True) and (item["news"] == False) and (item["repeat"] == True):
                item["covid_event_ids"] = covid_data_handler.schedule_covid_updates(item["time"], covid_data_handler.covid_API_request)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the COVID scheduler.")
                item["time"] += datetime.timedelta(days=1)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " is now scheduled to repeat tomorrow.")
                
            elif (item["covid-data"] == False) and (item["news"] == True) and (item["repeat"] == True):
                item["news_event_id"] = covid_news_handling.update_news(item["time"], covid_news_handling.news_API_request)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the news scheduler.")
                item["time"] += datetime.timedelta(days=1)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " is now scheduled to repeat tomorrow.")
                
            elif (item["covid-data"] == True) and (item["news"] == False) and (item["repeat"] == False):
                item["covid_event_ids"] = covid_data_handler.schedule_covid_updates(item["time"], covid_data_handler.covid_API_request)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the COVID scheduler.")
                
            elif (item["covid-data"] == False) and (item["news"] == True) and (item["repeat"] == False):
                item["news_event_id"] = covid_news_handling.update_news(item["time"], covid_news_handling.news_API_request)
                logging.info("'" + str(item["title"]) + "' for " + str(item["time"]) + " has been added to the news scheduler.")
                
            else:
                logging.warning("'" + str(item["title"]) + "' for " + str(item["time"]) + "is an invalid item in updates list. Item has been ignored.")

        """ REMOVING IF COMPLETE """
        if item["complete"] == True:
            updates.remove(item)
            logging.info("Update '" + str(item["title"]) + "' for " + str(item["time"]) + " has been completed.")

    covid_scheduler.run(blocking=False)
    news_scheduler.run(blocking=False)

    return render_template("index.html",
                           title="SARS-CoV-2 (Coronavirus) dashboard",
                           location=covid_data_handler.local_covid_data["location"],
                           nation_location=covid_data_handler.national_covid_data["nation_location"],
                           local_7day_infections=covid_data_handler.local_covid_data["local_7day_infections"],
                           national_7day_infections=covid_data_handler.national_covid_data["national_7day_infections"],
                           hospital_cases=covid_data_handler.national_covid_data["hospital_cases"],
                           deaths_total=covid_data_handler.national_covid_data["deaths_total"],
                           news_articles=covid_news_handling.news_data[-1]["articles"],
                           updates=updates,
                           image="favicon.png") 
                        

@app.route("/index")
def update() -> index:
    """This function will be called every time the user sends a request to the server."""
    if "update" in request.args:
        content = request.args.to_dict()

        if content["update"] == "":
            return index()


        now = datetime.datetime.now()
        spec_time = now.replace(hour = int((str(content["update"]))[0:2]), minute = int((str(content["update"]))[3:5]), second = 0, microsecond = 0)  # Replace  

        if now >= spec_time:
            spec_time += datetime.timedelta(days=1)  # If the chosen time has already passed today, schedule the update for tomorrow instead.

        if now < spec_time:
            pass

        if ("covid-data" in request.args) and ("news" in request.args) and ("repeat" in request.args):
            item = {
                "title": str(content["two"]),
                "content": "Next update is at " + str(content["update"]) + ". COVID data updates set. News updates also set. Updates will repeat.",
                "time": spec_time,
                "covid-data": True,
                "news": True,
                "repeat": True,
                "complete": False,
                "news_event_id" : None,
                "covid_event_ids": None,
                "cancelled": False
                }                
            logging.info("The user has scheduled update '" + str(content["two"]) + "' for " + str(spec_time) + ". COVID updates set. News updates set. Updates will repeat.")
            
        elif ("covid-data" in request.args) and ("news" in request.args) and ("repeat" not in request.args):
            item = {
                "title": str(content["two"]),   
                "content": "Next update is at " + str(content["update"]) + ". COVID data updates set. News updates also set.",
                "time": spec_time,
                "covid-data": True,
                "news": True,
                "repeat": False,
                "complete": False,
                "news_event_id" : None,
                "covid_event_ids": None,
                "cancelled": False
                }
            logging.info("The user has scheduled update '" + str(content["two"]) + "' for " + str(spec_time) + ". COVID updates set. News updates set.")

        elif ("covid-data" in request.args) and ("news" not in request.args) and ("repeat" in request.args):
            item = {
                "title": str(content["two"]),
                "content": "Next update is at " + str(content["update"]) + ". COVID data updates set. Updates will repeat.",
                "time": spec_time,
                "covid-data": True,
                "news": False,
                "repeat": True,
                "complete": False,
                "news_event_id" : None,
                "covid_event_ids": None,
                "cancelled": False
                }
            logging.info("The user has scheduled update '" + str(content["two"]) + "' for " + str(spec_time) + ". COVID updates set. Updates will repeat.")

        elif ("covid-data" not in request.args) and ("news" in request.args) and ("repeat" in request.args):
            item = {
                "title": str(content["two"]),
                "content": "Next update is at " + str(content["update"]) + ". News updates set. Updates will repeat.",
                "time": spec_time,
                "covid-data": False,
                "news": True,
                "repeat": True,
                "complete": False,
                "news_event_id" : None,
                "covid_event_ids": None,
                "cancelled": False
                }
            logging.info("The user has scheduled update '" + str(content["two"]) + "' for " + str(spec_time) + ". News updates set. Updates will repeat.")
            
        elif ("covid-data" in request.args) and ("news" not in request.args) and ("repeat" not in request.args):
            item = {
                "title": str(content["two"]),
                "content": "Next update is at " + str(content["update"]) + ". COVID data updates set.",
                "time": spec_time,
                "covid-data": True,
                "news": False,
                "repeat": False,
                "complete": False,
                "news_event_id" : None,
                "covid_event_ids": None,
                "cancelled": False
                }
            logging.info("The user has scheduled update '" + str(content["two"]) + "' for " + str(spec_time) + ". COVID updates set.")

        elif ("covid-data" not in request.args) and ("news" in request.args) and ("repeat" not in request.args):
            item = {
                "title": str(content["two"]),
                "content": "Next update is at " + str(content["update"]) + ". News updates set.",
                "time": spec_time,
                "covid-data": False,
                "news": True,
                "repeat": False,
                "complete": False,
                "news_event_id" : None,
                "covid_event_ids": None,
                "cancelled": False
                }
            logging.info("The user has scheduled update '" + str(content["two"]) + "' for " + str(spec_time) + ". News updates set.")

        else:
            logging.warning("The user has attempted to schedule an invalid update. Their input has been ignored.")
            return index()
    
        updates.append(item)
    
    elif 'notif' in request.args:
        content = request.args.to_dict()
        
        for article in covid_news_handling.news_data[-1]["articles"]:
            if article["title"] == content["notif"]:
                covid_news_handling.news_data[-1]["articles"].remove(article)
                logging.info("The user has removed article titled '" + str(article["title"]) + "'.")
                return index()

                
    elif 'update_item' in request.args:
        content = request.args.to_dict()

        for item in updates:
            if item["title"] == content["update_item"]:
                item["cancelled"] = True
                return index()

    else:
        return index()
    
    return index()

    
if __name__ == "__main__":
    app.run(debug=True)

