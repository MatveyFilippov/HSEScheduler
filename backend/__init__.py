from typing import Final
import logging
import os
import pytz
from datetime import datetime


TEMPLATES_FOLDER_PATH: Final = os.path.join(os.getcwd(), "templates")
STATIC_FOLDER_PATH: Final = os.path.join(TEMPLATES_FOLDER_PATH, "static")
PATH_TO_DATA_FOLDER: Final = "HSESchedulerData"
os.makedirs(PATH_TO_DATA_FOLDER, exist_ok=True)

PROJECT_HOST: Final = "localhost"  # "85.193.90.158"
PROJECT_PORT: Final = "1212"

LOGGER_NAME: Final = "HSESchedulerLogs"
PATH_TO_LOGFILE: Final = os.path.join(PATH_TO_DATA_FOLDER, f"{LOGGER_NAME}.log")
PATH_TO_DBFILE: Final = os.path.join(PATH_TO_DATA_FOLDER, f"HSESchedulerUsers.db")

EMAIL_LOGIN: Final = "hse.scheduler@yandex.ru"
EMAIL_PASSWORD: Final = "xfzqexwmsfvfhnqh"
EMAIL_HOST: Final = "smtp.yandex.ru"
EMAIL_PORT: Final = 587

moscow_timezone = pytz.timezone('Europe/Moscow')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO, filename=PATH_TO_LOGFILE, encoding="UTF-8", datefmt=DATETIME_FORMAT,
    format="%(levelname)s %(asctime)s --> %(message)s"
)


def get_msk_time(timestamp=False):
    if timestamp:
        return datetime.now(moscow_timezone).timestamp()
    return datetime.now(moscow_timezone).strftime(DATETIME_FORMAT)
