from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, log
from aiogram.dispatcher.filters import Text
import pandas as pd


@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    log.info(
        f"func: отмена: {message.from_user.first_name}, {message.from_user.id}: {message.text}"
    )
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer("Хорошо, отеняем", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=["help"], state="*")
async def help_in_create_record(message: types.Message, state: FSMContext):
    log.info(
        f"func: help_in_create_record: {message.from_user.first_name}, {message.from_user.id}: {message.text}"
    )
    await message.answer(
        "Бот поможет организовать очередь сдачи домашки.\nПросто введи свой github и выбери преподавателя.\n<b>Ник можно указать только один раз, после авторизации его нельзя будет поменять!</b>"
    )
