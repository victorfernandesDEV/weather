import os
import re
import tempfile

import pytest
from loguru import logger
from requests_html import HTMLSession
from wsgiadapter import WSGIAdapter

from app import flask_app
from app import get_weather_data


API_KEY = os.getenv('API_Key')


valid_cities_list = ["Recife", "Itambé", "João Pessoa", "Pedras de Fogo"]
invalid_Cities_list = ["SDFsdfs", "sadsdasda", "SADSASDA"]


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    client = flask_app.test_client()
    yield client

#def test_weather_endpoint(client):
#    for city in valid_cities_list:
#        response = get_weather_data(city)
#        assert 200 == response.status_code

def test_post_valid_cities(client):
    for city in valid_cities_list:
        response = HTMLSession()
        response.mount("http://test", WSGIAdapter(flask_app))
        payload = {
            "city_name": city
        }
        response = response.post("http://test/weather", data=payload)
        assert 200 == response.status_code
        assert city in response.html.html

def test_post_invalid_cities(client):
    for invalid_city in invalid_Cities_list:
        response = HTMLSession()
        response.mount("http://test", WSGIAdapter(flask_app))
        payload = {
            "city_name": invalid_city
        }
        response = response.post("http://test/weather", data=payload)
        match = re.search(r"Sorry We coudn't find the specified city.", response.html.text).group()
        assert 200 == response.status_code
        assert "Sorry We coudn't find the specified city." == match






