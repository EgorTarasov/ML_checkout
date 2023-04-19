import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, Session, log
from data.models import User, DefenseRecord
from .delete_record.states import DeleteForm
from loader import dp, Session, teachers


from aiogram.utils.markdown import hlink


@dp.message_handler(commands=["cancel"])
async def send_welcome(message: types.Message):

    session = Session()
    record = (
        session.query(DefenseRecord)
        .where(DefenseRecord.student_id == message.from_user.id)
        .filter(DefenseRecord.date > datetime.datetime.now())
        .one_or_none()
    )
    response = (
        f"Ты уже записался на защиту {record.date.strftime('%d-%m')} \nзадание:{record.task}\n Точно хочешь отменить запись? "
        if record
        else "Ты еще не записался на защиту"
    )
    reply_keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    reply_keyboard.add("Да", "Нет")
    await message.answer(response, reply_markup=reply_keyboard)
    await DeleteForm.choice.set()
