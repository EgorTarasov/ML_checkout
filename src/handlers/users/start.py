from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, Session
from data.models import User
from .survey import StudentForm
from loader import dp, Session, teachers

from aiogram.utils.markdown import hlink


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    session = Session()
    userdata = dict(message.from_user)
    db_user = session.query(User).filter_by(id=message.from_user.id).one_or_none()
    if db_user is None or db_user.github is None:
        db_user = User(**userdata)
        session.merge(db_user)
        session.commit()

        await StudentForm.auth.set()
        table = hlink(
            "таблице",
            "https://docs.google.com/spreadsheets/d/1jIxeW8BcbeZcGmNm47tXzpGPVULhMvnOUYpNX3J2OF4/edit#gid=0",
        )
        await message.answer(
            f"Привет!\nДля записи на сдачу работы надо указать ник в github, как в {table}.",
            disable_web_page_preview=True,
        )
    else:
        db_user = User(**userdata)
        session.merge(db_user)
        session.commit()

        await StudentForm.teacher.set()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        reply_keyboard.add(*teachers)
        await message.answer(
            "Ты уже авторизован.\nКакому преподавателю ты хочешь сдать домашку?",
            reply_markup=reply_keyboard,
        )
