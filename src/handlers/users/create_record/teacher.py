from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, google_table_data, homeworks, teachers, Session, log
import pandas as pd
from data.models import User, DefenseRecord


@dp.message_handler(state=StudentForm.teacher)
async def process_teacher(message: types.Message, state: FSMContext):
    log.info(
        f"func: process_teacher: {message.from_user.first_name}, {message.from_user.id}: {message.text}"
    )
    session = Session()
    db_user = session.query(User).filter_by(id=message.from_user.id).one_or_none()
    if db_user is None:
        await message.answer("Что-то пошло не так")
        await state.finish()
        return

    if not message.text in teachers:
        await message.answer("Такого преподавателя нет в клавиатуре")
    else:

        async with state.proxy() as data:
            data["teacher"] = message.text
            try:
                fio = data["fio"]
            except KeyError:
                fio = db_user.fio
            log.info(f"func: process_teacher: fio: {fio}")
            row = google_table_data[google_table_data["ФИО"] == fio]
            homeworks_status = row[homeworks].values[0]
            response = ""
            last_task = None
            for name, value in zip(homeworks, homeworks_status):
                if pd.isnull(value) or type(value) == str:
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
            # добавляем отмена, чтобы руками не писать
            reply_keyboard.add("Отмена")
            await message.answer(response, reply_markup=reply_keyboard)
            await StudentForm.next()
        else:
            response = "Ты уже сдал все домашки 🎉"
            await message.answer(response, reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
