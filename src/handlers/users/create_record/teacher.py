import logging
from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, google_table_data, homeworks, teachers, Session
import pandas as pd
from data.models import User, DefenseRecord


@dp.message_handler(state=StudentForm.teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    if not message.text in teachers:
        await message.answer("Такого преподавателя нет в клавиатуре")
    else:
        row = None
        async with state.proxy() as data:
            data["teacher"] = message.text
            try:
                github = data["github"]
            except KeyError:
                session = Session()
                db_user = (
                    session.query(User).filter_by(id=message.from_user.id).one_or_none()
                )
                if db_user is None:
                    await message.answer("Что-то пошло не так")
                    return
                github = db_user.github
            row = google_table_data[google_table_data["Ник на git"] == github]
            homeworks_status = row[homeworks].values[0]
            response = ""
            last_task = None
            for name, value in zip(homeworks, homeworks_status):
                if pd.isnull(value):
                    last_task = name
                    break
                else:
                    response += f"{name}: {value}\n"
            data["last_task"] = last_task

        if last_task:
            response = (
                f"Ты можешь сдать {last_task} на следующем занятии\nЗаписываемся?"
            )
            reply_keyboard = types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True
            )
            reply_keyboard.add("Да", "Нет")

            await message.answer(response, reply_markup=reply_keyboard)
            await StudentForm.next()
        else:
            await state.finish()
