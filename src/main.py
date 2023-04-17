# TODO: inline keyboard

import random
import datetime
import os
import asyncio
from aiogram import executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import (
    sessionmaker,
    relationship,
    Mapped,
    mapped_column,
    declarative_base,
)

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import create_engine

import logging
import pandas as pd
import numpy as np

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler


# region utils
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


# endregion utils


# region init

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
GOOGLE_URL = os.getenv("GOOGLE_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Configure logging
logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
google_table_data = pd.read_csv(GOOGLE_URL)
print(google_table_data.columns)
homeworks = [
    i for i in google_table_data.columns if "Домашние задание №" in i
]  # выбрали оценки по формату "Домашние задание №{number}"
colloquiums = [i for i in google_table_data.columns if "Оценка коллоквиум" in i]
teachers = ["Егоров", "Хасанова"]


class StudentForm(StatesGroup):
    github = State()
    teacher = State()
    queue = State()


# endregion

# region models


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_bot: Mapped[bool] = mapped_column(Boolean)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True)
    added_to_attachment_menu: Mapped[bool] = mapped_column(Boolean, nullable=True)
    language_code: Mapped[str] = mapped_column(String, nullable=True)

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    github: Mapped[str] = mapped_column(String, nullable=True)
    fio: Mapped[str] = mapped_column(String, nullable=True)

    defense_records: Mapped[list] = relationship(
        "DefenseRecord", back_populates="student"
    )

    def __repr__(self):
        return f"User(id='{self.id}', is_bot='{self.is_bot}', first_name='{self.first_name}', last_name='{self.last_name}', username='{self.username}', is_premium='{self.is_premium}', added_to_attachment_menu='{self.added_to_attachment_menu}', is_admin='{self.is_admin}', github='{self.github}', fio='{self.fio}')"


class DefenseRecord(Base):
    __tablename__ = "defense_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    student: Mapped[User] = relationship("User", back_populates="defense_records")
    teacher: Mapped[str] = mapped_column(String)
    task: Mapped[str] = mapped_column(String)
    status: Mapped[bool] = mapped_column(Boolean)
    additional_data: Mapped[str] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"DefenseRecord(id='{self.id}', student_id='{self.student_id}', teacher='{self.teacher}', task='{self.task}', status='{self.status}', additional_data='{self.additional_data}')"


# endregion models

# region db


class DBmanager:
    def __init__(self) -> None:

        self.engine = create_engine(
            f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

        self.Base = Base
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()
        self.Base.metadata.create_all(self.engine)

    # создай очередь для студента
    def get_queue(self, student_id):
        return (
            self.session.query(DefenseRecord).filter_by(student_id=student_id).first()
        )


db = DBmanager()
# endregion db


# region handlers


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):

    userdata = dict(message.from_user)
    db_user = User(**userdata)
    db.session.merge(db_user)
    db.session.commit()

    await StudentForm.github.set()
    await message.reply(
        "Привет!\nДля записи на сдачу работы надо указать ник в github, как в таблице:\n https://docs.google.com/spreadsheets/d/1jIxeW8BcbeZcGmNm47tXzpGPVULhMvnOUYpNX3J2OF4/edit#gid=0"
    )


@dp.message_handler(state=StudentForm.github)
async def process_github(message: types.Message, state: FSMContext):
    if not message.text in google_table_data["Ник на git"].values:
        await message.answer("Такого ника нет в таблице")
    else:
        async with state.proxy() as data:
            # get user data from db by id from message
            db_user = db.session.query(User).filter_by(id=message.from_user.id).first()
            db_user.github = message.text
            db_user.fio = google_table_data[
                google_table_data["Ник на git"] == message.text
            ]["ФИО"].values[0]

            db.session.add(db_user)
            db.session.commit()
            data["github"] = message.text
        await StudentForm.next()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        reply_keyboard.add(*teachers)
        await message.answer(
            "Какому преподавателю ты хочешь сдать домашку?", reply_markup=reply_keyboard
        )


@dp.message_handler(state=StudentForm.teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    if not message.text in teachers:
        await message.answer("Такого преподавателя нет в клавиатуре")
    else:
        row = None
        async with state.proxy() as data:
            data["teacher"] = message.text
            row = google_table_data[google_table_data["Ник на git"] == data["github"]]
            homeworks_status = row[homeworks].values[0]
            response = "None"
            last_task = None
            for name, value in zip(homeworks, homeworks_status):
                print(name, value)
                if pd.isnull(value):
                    last_task = name

                    break
                else:
                    response += f"{name}: {value}\n"
            db_record = (
                db.session.query(DefenseRecord)
                .filter_by(student_id=message.from_user.id)
                .first()
            )
            if db_record:
                db_record.teacher = data["teacher"]
                db_record.task = last_task
                db_record.status = False
            else:
                db_record = DefenseRecord(
                    student=db.session.query(User)
                    .filter_by(id=message.from_user.id)
                    .first(),
                    teacher=data["teacher"],
                    task=last_task,
                    status=False,
                )
                # check if user already has a defense record
            db.session.add(db_record)
            db.session.commit()

        await StudentForm.next()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer(response)

        await message.answer(f"Github: {data['github']}\nTeacher: {data['teacher']}")

        if last_task:
            response = (
                f"Ты можешь сдать {last_task} на следующем занятии\nЗаписываемся?"
            )
            reply_keyboard.add("Да", "Нет")
            await StudentForm.next()
        else:
            response = "Ты сделал все задания! Можешь чилить)"
        await message.answer(response)
        await state.finish()


# endregion handlers

# region appscheduler
async def send_queue(bot: Bot):
    users = db.session.query(User).all()
    print("send_message_time")
    # get all DefenseRecords from db
    records = db.session.query(DefenseRecord).all()
    tasks = {}
    for r in records:
        if r.task in tasks:
            tasks[r.task].append(r.student.fio)
        else:
            tasks[r.task] = [r.student.fio]
    print(tasks)
    for user in users:
        await bot.send_message(chat_id=user.id, text=f"{tasks}")


async def add_shuffle_job(bot: Bot, scheduler: AsyncIOScheduler):
    next_sunday = next_weekday(datetime.datetime.now(), 6)
    next_sunday.time = datetime.time(18, 0, 0)
    scheduler.add_job(
        send_queue,
        trigger="date",
        run_date=next_sunday,
        kwargs={"bot": bot},
    )


scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
scheduler.add_job(
    add_shuffle_job,
    trigger="date",
    run_date=datetime.datetime.now() + datetime.timedelta(seconds=1),
    kwargs={"bot": bot, "scheduler": scheduler},
)


# endregion


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_queue(bot))
    # scheduler.start()

    executor.start_polling(dp, skip_updates=True)
