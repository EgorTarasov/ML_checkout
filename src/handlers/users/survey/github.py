from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, google_table_data, Session, teachers
from data.models import User


@dp.message_handler(state=StudentForm.github)
async def process_github(message: types.Message, state: FSMContext):
    session = Session()
    if not message.text in google_table_data["Ник на git"].values:
        await message.answer("Такого ника нет в таблице")
    else:
        async with state.proxy() as data:
            # TODO: skip state if db_user.github != None
            # TODO: find by fio
            db_user = session.query(User).filter_by(id=message.from_user.id).first()
            db_user.github = message.text
            db_user.fio = google_table_data[
                google_table_data["Ник на git"] == message.text
            ]["ФИО"].values[0]

            session.add(db_user)
            session.commit()
            data["github"] = message.text
        await StudentForm.next()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        reply_keyboard.add(*teachers)
        await message.answer(
            "Какому преподавателю ты хочешь сдать домашку?", reply_markup=reply_keyboard
        )
