from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, google_table_data, Session, teachers
from data.models import User


@dp.message_handler(state=StudentForm.auth)
async def process_auth(message: types.Message, state: FSMContext):

    session = Session()
    db_user = session.query(User).filter_by(id=message.from_user.id).one_or_none()

    if db_user.github is None:

        if message.text.lower() in google_table_data["Фамилия"].values:
            userdata = google_table_data[
                google_table_data["Фамилия"] == message.text.lower()
            ]
        elif message.text in google_table_data["Ник на git"].values:
            userdata = google_table_data[
                google_table_data["Ник на git"] == message.text
            ]
        else:
            await message.answer("Я не смог найти тебя в таблице. Попробуй еще раз")
            return
        async with state.proxy() as data:
            data["github"] = userdata["Ник на git"].values[0]
        db_user.fio = userdata["ФИО"].values[0]
        db_user.github = userdata["Ник на git"].values[0]
        session.add(db_user)
        session.commit()
        session.close()
        await StudentForm.next()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        reply_keyboard.add(*teachers)
        await message.answer(
            "Какому преподавателю ты хочешь сдать домашку?",
            reply_markup=reply_keyboard,
        )
