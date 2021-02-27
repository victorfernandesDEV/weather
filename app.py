from flask import Flask, request
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
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app)


class Weather(Resource):

    def get(self, city_name: str):

        data = request.view_args["city_name"]

        cached_data = deque([cached for cached in cache.cache._cache])

        if city_name not in cached_data:

            response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={os.getenv('API_Key')}")

            if response.status_code == 200:

                logger.info("Foi cacheado")

                if len(cached_data) >= 5:
                    logger.info(f"Removido do cache {cached_data.popleft()}")

                payload = {
                    f"{city_name}": response.json()
                }

                cache.set(key=city_name, value=payload)

                return {
                    "data": cache.get(city_name)
                }
        else:
            return {
                "data": cache.get(city_name)
            }
        return {
            "message": "Sorry We coudn't find the specified city."
        }


api.add_resource(Weather, "/<city_name>")

if __name__ == "__main__":
    app.run(debug=DEBUG)
