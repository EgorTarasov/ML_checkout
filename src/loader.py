from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from data import config
from data import models
from utils.table import update_table
from utils.misc.logging import create_logger

import locale

# set locate to Russian
locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

bot = Bot(token=config.API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

log = create_logger()
engine = create_engine(
    f"postgresql+psycopg2://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

google_table_data = update_table(config.GOOGLE_URL)
homeworks = [
    i for i in google_table_data.columns if "Домашние задание №" in i
]  # выбрали оценки по формату "Домашние задание №{number}"
colloquiums = [i for i in google_table_data.columns if "Оценка коллоквиум" in i]
teachers = ["Егоров", "Хасанова"]


scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
