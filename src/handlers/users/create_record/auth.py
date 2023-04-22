from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, google_table_data, Session, teachers, log
from data.models import User


@dp.message_handler(state=StudentForm.auth)
async def process_auth(message: types.Message, state: FSMContext):
    log.info(
        f"func: process_auth: {message.from_user.first_name}, {message.from_user.id}: {message.text}"
    )
    session = Session()
    db_user = session.query(User).filter_by(id=message.from_user.id).one_or_none()

    async with state.proxy() as data:
        if db_user.github is None and db_user.fio is None:
            if message.text.lower() in google_table_data["Фамилия"].values:
                userdata = google_table_data[
                    google_table_data["Фамилия"] == message.text.lower()
                ]
                # TODO state should be saved in data['last_name']
                data["github"] = userdata["Фамилия"].values[0]
                db_user.fio = userdata["Фамилия"].values[0]
            elif message.text in google_table_data["Ник на git"].values:
                userdata = google_table_data[
                    google_table_data["Ник на git"] == message.text
                ]
                data["github"] = userdata["Ник на git"].values[0]
                db_user.github = userdata["Ник на git"].values[0]
            else:
                await message.answer(
                    "Я не смог найти тебя в таблице.\nПопробуй еще раз или напиши 'Отмена'"
                )
                return

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
