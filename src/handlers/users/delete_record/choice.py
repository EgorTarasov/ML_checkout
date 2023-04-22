import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from .states import DeleteForm
from data.models import DefenseRecord
from loader import dp, Session


@dp.message_handler(state=DeleteForm.choice)
async def process_delete_choice(message: types.Message, state: FSMContext):
    """Получение статуса о записи"""
    session = Session()
    if not message.text in ["Да", "Нет"]:
        await message.answer("Напиши Да или Нет")
        return
    elif message.text == "Нет":
        await message.answer("Оставил запись")
        await state.finish()
        return
    else:
        record = (
            session.query(DefenseRecord)
            .where(DefenseRecord.student_id == message.from_user.id)
            .filter(DefenseRecord.date > datetime.datetime.now())
            .first()
        )
        if record:
            session.delete(record)
            session.commit()
            session.close()
        await message.answer("Запись отменена")
        await state.finish()
