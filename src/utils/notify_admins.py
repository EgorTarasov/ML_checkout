import logging

from aiogram import Dispatcher
from loader import Session
from data.models import User


async def on_startup_notify(dp: Dispatcher):
    session = Session()
    admins = session.query(User).filter_by(is_admin=True).all()
    for admin in admins:
        try:
            await dp.bot.send_message(admin.id, "Бот Запущен")

        except Exception as err:
            logging.exception(err)
