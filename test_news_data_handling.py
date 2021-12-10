import pytest
import datetime

from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import news_data
from covid_news_handling import news_scheduler


def test_news_API_request():
    """Checks that the 'news_API_request' function is using the correct arguments and hence searching for the correct articles."""
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()


def test_update_news():
    """Checks that the 'update_news' function updates the news articles at the specified time,
    by checking if the length of the news data has incremened by 1 after the update has taken place.
    """
    length = len(news_data)
    now = datetime.datetime.now()
    update_interval = now + datetime.timedelta(seconds=1)
    update_news(update_interval, news_API_request)
    news_scheduler.run(blocking=True)
    assert len(news_data) == length + 1
    
