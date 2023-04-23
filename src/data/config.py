import os
from dotenv import load_dotenv
from enum import Enum


load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
GOOGLE_URL = os.getenv("GOOGLE_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
BOT_MODE = False if os.getenv("BOT_MODE").lower() == "debug" else True
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")
DOCKER_MODE = True if os.getenv("DOCKER_MODE").lower() == "true" else False
