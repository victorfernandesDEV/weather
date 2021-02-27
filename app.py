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




if __name__ == "__main__":
    app.run(debug=DEBUG)
