from flask import Flask, request, render_template, make_response
from flask_caching import Cache
from flask_restful import Resource, Api

from loguru import logger

import os
import requests

from collections import deque

from dotenv import load_dotenv


app = Flask(__name__)
api = Api(app)


load_dotenv()


DEBUG = True if os.getenv("DEBUG") == "True" else False


config = {
    "DEBUG": DEBUG,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 10
}
app.config.from_mapping(config)
cache = Cache(app)


class Weather(Resource):

    def get_weather_data(self, city_name):
        response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={os.getenv('API_Key')}")
        return response

    def get(self, city_name: str):

        data = request.view_args["city_name"]

        error_message = None

        cached_data = deque([cached for cached in cache.cache._cache])

        if city_name not in cached_data:

            response = self.get_weather_data(city_name)

            if response.status_code == 200:

                if len(cached_data) > 5:
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
                response = self.get_weather_data(city_name)
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

        if cached_data is not None:
            for cont, city in enumerate(cached_data):
                if city != city_name:
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
        content["other_cities"] = reversed(content["other_cities"])
        return make_response(render_template('index.html', **content))


api.add_resource(Weather, "/<city_name>")

if __name__ == "__main__":
    app.run(debug=DEBUG)
