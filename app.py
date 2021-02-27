from flask import Flask, request, render_template, make_response
from flask_caching import Cache

from loguru import logger

import os
import requests

from collections import deque

from dotenv import load_dotenv


flask_app = Flask(__name__)


load_dotenv()


DEBUG = True if os.getenv("DEBUG") == "True" else False


API_KEY = os.getenv('API_Key')


config = {
    "DEBUG": DEBUG,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300
}
flask_app.config.from_mapping(config)
cache = Cache(flask_app)


# fetch over the weather api and retrieve the data corresponding to the passed city name.
def get_weather_data(city_name):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}")
    return response

@flask_app.route("/weather", methods=["GET", "POST"])
def weather_index():
    if request.method == "POST":
        city_name = request.form["city_name"]

        error_message = None

        cached_data = deque([cached for cached in cache.cache._cache])

        # if the passed city are not in cache, it will add the city to the cache.
        # if the city are not found in the api, it will be return an error message.
        if city_name not in cached_data:

            response = get_weather_data(city_name)

            if response.status_code == 200:

                if len(cached_data) >= 5:
                    cache.delete(cached_data.popleft())

                payload = {
                    f"{city_name}": response.json()
                }

                cache.set(key=city_name, value=payload)
            else:
                error_message = "Sorry We coudn't find the specified city."

        if error_message is not None:
            content = {
                "error_message": error_message,
                "other_cities": []
            }
        else:
            try:
                # gets the city active in the cache, if the time of cache has been expired, it will bypass over the error
                cached_city = cache.get(city_name)
                content = {
                    "current_city": {
                        "city_name": cached_city[city_name]["name"],
                        "degree": f"{int(cached_city[city_name]['main']['temp']) - 273.15:.2f}",
                        "state": cached_city[city_name]["weather"][0]["description"]
                    },
                    "other_cities": []
                }
            except TypeError as err:
                logger.info("Cache already expired, it has been updated")
                response = get_weather_data(city_name)
                payload = {
                    f"{city_name}": response.json()
                }
                cache.set(key=city_name, value=payload)
                cached_city = cache.get(city_name)
                content = {
                    "current_city": {
                        "city_name": cached_city[city_name]["name"],
                        "degree": f"{int(cached_city[city_name]['main']['temp']) - 273.15:.2f}",
                        "state": cached_city[city_name]["weather"][0]["description"]
                    },
                    "other_cities": []
                }

        cached_data = deque([cached for cached in cache.cache._cache])

        # return the list of other cities in cache if have more than one.
        if cached_data is not None and len(cached_data) > 1:
            for cont, city in enumerate(reversed(cached_data)):
                try:
                    city_data = cache.get(city)
                    payload = {
                        "city_name": city_data[city]["name"],
                        "degree": f"{int(city_data[city]['main']['temp']) - 273.15:.2f}",
                        "state": city_data[city]["weather"][0]["description"]
                    }
                    content["other_cities"].append(payload)
                except TypeError as err:
                    cache.delete(key=city)
        return make_response(render_template('index.html', **content))
    else:
        content = {
            "other_cities": []
        }

        cached_data = deque([cached for cached in cache.cache._cache])

        data = request.args

        max_number = None
        try:
            if "max" in data:
                max_number = int(data["max"])
        except:
            pass

        # return all cities in cache
        if cached_data is not None:
            for cont, city in enumerate(reversed(cached_data)):
                try:
                    # verify if max_number is valid (extracted from querystring), if is tru (more than 0)
                    # it will be used to limit the loop
                    if max_number != None and max_number <= cont:
                        break
                    city_data = cache.get(city)
                    payload = {
                        "city_name": city_data[city]["name"],
                        "degree": f"{int(city_data[city]['main']['temp']) - 273.15:.2f}",
                        "state": city_data[city]["weather"][0]["description"]
                    }
                    content["other_cities"].append(payload)
                except TypeError as err:
                    cache.delete(key=city)

        return make_response(render_template("index.html", **content))


@flask_app.route("/weather/<string:city_name>", methods=["GET"])
def get_data_by_city_name(city_name: str):

    error_message = None

    cached_data = deque([cached for cached in cache.cache._cache])
    if city_name not in cached_data:

        response = get_weather_data(city_name)

        if response.status_code == 200:

            if len(cached_data) >= 5:
                cache.delete(cached_data.popleft())

            payload = {
                f"{city_name}": response.json()
            }

            cache.set(key=city_name, value=payload)
        else:
            error_message = "Sorry We coudn't find the specified city."

    if error_message is not None:
        content = {
            "error_message": error_message,
            "other_cities": []
        }
    else:
        try:
            cached_city = cache.get(city_name)
            content = {
                "current_city": {
                    "city_name": cached_city[city_name]["name"],
                    "degree": f"{int(cached_city[city_name]['main']['temp']) - 273.15:.2f}",
                    "state": cached_city[city_name]["weather"][0]["description"]
                },
                "other_cities": []
            }
        except TypeError as err:
            logger.info("Cache already expired, it has been updated")
            response = get_weather_data(city_name)
            payload = {
                f"{city_name}": response.json()
            }
            cache.set(key=city_name, value=payload)
            cached_city = cache.get(city_name)
            content = {
                "current_city": {
                    "city_name": cached_city[city_name]["name"],
                    "degree": f"{int(cached_city[city_name]['main']['temp']) - 273.15:.2f}",
                    "state": cached_city[city_name]["weather"][0]["description"]
                },
                "other_cities": []
            }

    cached_data = deque([cached for cached in cache.cache._cache])

    # return the list of other cities in cache if have more than one.
    if cached_data is not None and len(cached_data) > 1:
        for cont, city in enumerate(reversed(cached_data)):
            try:
                city_data = cache.get(city)
                payload = {
                    "city_name": city_data[city]["name"],
                    "degree": f"{int(city_data[city]['main']['temp']) - 273.15:.2f}",
                    "state": city_data[city]["weather"][0]["description"]
                }
                content["other_cities"].append(payload)
            except TypeError as err:
                cache.delete(key=city)
    return make_response(render_template('index.html', **content))


if __name__ == "__main__":
    flask_app.run(debug=DEBUG)
