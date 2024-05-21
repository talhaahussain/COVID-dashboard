# COVID-dashboard

Continuous Assessment for ECM1400 - Programming, set by Dr. Matt Collison (Year 1, Semester 1). The COVID dashboard is a tool that allows a user to stay up-to-date with the ongoing SARS-CoV-2 global pandemic. The dashboard serves a number of functions, including:
  - Providing the user with the latest news on the pandemic
  - Providing the user the latest statistics on the pandemic, according to their location (this can be adjusted in the configuration file)
  - Allowing the user to schedule updates to the data at their desired time intervals

This work received a final mark of 68/100.

Please see `specification.pdf` for specification.

## Installation
To install the COVID dashboard, the user will need to have Python 3 installed. They will then need to install the following libraries:
  - "uk-covid19"
  - "newsapi"
  - "flask"

Installing these libraries can be done using the pip installer via the command line.

All modules and files in this repository are required in order to allow the COVID dashboard to function correctly, except for the modules with the 'test' prefix. These are recommended in order to ensure that all functions in the system are performing as expected. Should you choose to make use of the testing modules, the following additional library will need to be installed.
  - "pytest"

More information on testing will be given in subsequent sections.

## Configuration
The dashboard can be configured to suit your needs using the 'config.json' file. The local location and national location can be changed from here. This is done by replacing the values matching the keys under the headings "local_location" and "national_location". By default, these are set to "Exeter" and "England" respectively. Ensure that 'location_type' is also adjusted to match the local location selected. This information can be found on UK government websites. Please note that the COVID-19 API may not have data for all areas and nations. Please ensure that your locations are valid by referring to the relevant tests. These will be specified and explained in a later section.

## How to use
Once installation and configuration are complete, the dashboard is ready to use. Launch the module named 'main.py', and wait for the following response from the terminal:
 * Serving Flask app 'main' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on

If the program immediately closes itself, please check your connection; it may be that the program is unable to connect to Public Health England and/or News API, and hence is immediately terminating itself, as instructed. Once this response has been recieved from the terminal, navigate to 'localhost:5000' or '127.0.0.1:5000' in your web browser. You should see a screen with statistics down the middle and a column of news articles on the right. If so, congratulations! You have successfully initialised the application, and it is ready for use.

Updates to the COVID data and the news articles can be scheduled by entering a label in the field and selecting a time at which the updates should take place. You can specify if you only want updates to the COVID data or the news articles, or both simultaneously. You can also enable repeating updates - with this, the updates will repeat every 24 hours at the specified time. These updates will continue to occur indefinitely, until they are cancelled. Scheduled updates will appear on the left hand column, with information about the update. Updates can be cancelled simply by clicking on the [X] button on their box. News articles that you do not wish to see anymore can also be removed in the same fashion.

## Testing
Developers and users alike may carry out testing, using the aforementioned testing modules. In order to run these tests, you must open your command line and change your directory to match this repository. Then, type "pytest" followed by the test module you wish to use. There are two modules: "test_covid_data_handler.py" and "test_news_data_handling.py", each of which test the module implied by their names. Pytest will then carry out all the tests and provide feedback on their success. Please note that if the program fails a test after the configuration file has been modified, this may be a result of an invalid location for the COVID API. In this case, please try another location or revert the configuration file back to its original state. Always check the local area type with a UK government website for any area. The individual unit tests are briefly explained in the source code, which can be viewed using the Python IDLE. A more in-depth explanation is given here.

### test_covid_data_handler.py
This series of unit tests goes hand in hand with "covid_data_handler.py".
  - 'test_parse_csv_data' - This tests the 'parse_csv_data' function. This test checks that the function correctly parses the rows of the exemplar CSV file into a list, by checking the length of the list is correct.
  - 'test_process_covid_csv_data' - This tests the 'process_covid_csv_data' function. This test checks that the function correctly processes the data extracted from the CSV file, by checking the values outputted by the function are correct.
  - 'test_covid_API_request' - This tests the 'covid_API_request' function. This test checks that the function returns a dictionary after being called, a dictionary which is supposed to contain the COVID data as fetched from the API.
  - 'test_schedule_covid_updates' - This tests the 'schedule_covid_updates' function. This test checks that the function updates the data at the expected time. It does this by scheduling an update one second away from the current time, and then executing this update. Since the dictionary for the COVID data contains a field which specifies when the last update took place, this is compared with the time the update was scheduled, and ensures that they are within half a second of eachother (thus proving the update took place as scheduled.)

### test_news_data_handling.py
This series of unit tests goes hand in hand with "covid_news_handling.py".
  - 'test_news_API_request' - This tests the 'news_API_request' function. This test ensures that the correct arguments are being used, meaning the correct keywords are being passed to the news API, and hence the correct articles are being returned to the user.
  - 'test_update_news' - This tests the 'update_news' function. This test verifies that the data update for the news articles has taken place at the expected time, by scheduling an update one second away from the current time, and then executing this update. It then checks that the length of the list of the data from the news API has been incremented by one, indicating that the update has taken place.

Please note that there are no tests for the main Flask application, because no advanced data processing takes place within the module.

## Design choices
I have made some unique design choices for the system that are designed to help both users and developers. They are explained here.
  - Use of datetime objects/conversion to UTC - This is done to allow easy manipulation of the data (for example, incrementing the 'days' field by 1 for repeating updates), as well as eliminating the need to calculate the exact delay in seconds between the current time and the scheduled time. This makes the code much more readable, and allows use of the 'enterabs' method of the sched library to much greater effect. The 'timestamp' method from the datetime library is used to quickly and accurately convert the datetime object into a UTC object for scheduling.
  - Use of dictionaries - By encoding information, such as information on scheduled updates, into dictionaries, code is much more concise and easy to read and modify. This also allows metadata to be stored alongside data for debugging and improving code, without interfering with the user experience.
  - Use of conditional branching - Organising the program into branches for different situations and purposes allows the program to be much easier to follow and debug. This is used alongside the dictionaries to quickly retrieve information and ensure a reasonably fast turnaround time.
  - Smarter time scheduling - Relating to all of the above, the program also has a feature where it will detect if the user is scheduling an update for a time prior to the current time of the day. If so, the program will set the update for tomorrow, ensuring that the user doesn't accidentally 'lose' any of their updates.

## Logging
The application comes with a log file that automatically updates to record all events that take place while the dashboard is running. This log file is viewable using any basic text editor, and has different levels to denote different severities of events. For instance, taking the previously mentioned situation where the program is unable to connect with the APIs, checking the log file will show a 'CRITICAL' event has been recorded, followed by immediate shutdown of the program. The logger can be used for debugging and diagnostics for developers and users alike. Developers are welcome to add their own events to the log via the main Flask application, to help improve and further logging accuracy.

## Footnotes
This program is available to any developers who wish to modify or improve the code. Docstrings, type-hinting and comments are featured in the source code to allow easy access and readability. This project is hosted on GitHub here: https://github.com/monky-kong/COVID-Dashboard.git
