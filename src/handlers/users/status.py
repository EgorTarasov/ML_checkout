import datetime
from aiogram import types

from data.models import DefenseRecord
from loader import dp, Session


@dp.message_handler(commands=["status"])
async def process_status(message: types.Message):
    """Получение статуса о записи"""
    session = Session()
    record = (
        session.query(DefenseRecord)
        .where(DefenseRecord.student_id == message.from_user.id)
        .filter(DefenseRecord.date > datetime.datetime.now())
        .first()
    )
    response = (
        f"Ты уже записался на защиту {record.date.strftime('%d-%m')} \nзадание:{record.task} "
        if record
        else "Ты еще не записался на защиту"
    )
    await message.answer(response)
