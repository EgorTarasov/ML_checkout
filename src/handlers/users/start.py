from aiogram import types
from loader import dp, Session
from data.models import User
from .survey import StudentForm
from loader import dp, Session


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    session = Session()
    userdata = dict(message.from_user)
    db_user = User(**userdata)
    session.merge(db_user)
    session.commit()

    await StudentForm.github.set()
    await message.reply(
        "Привет!\nДля записи на сдачу работы надо указать ник в github, как в таблице:\n https://docs.google.com/spreadsheets/d/1jIxeW8BcbeZcGmNm47tXzpGPVULhMvnOUYpNX3J2OF4/edit#gid=0"
    )
