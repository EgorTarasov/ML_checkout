from aiogram.dispatcher import FSMContext


# async def cancel(message, state: FSMContext):
#     if message.text == "/cancel":
#         current_state = await state.get_state()
#         await state.finish()

#     else:
#         return False


import logging
from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp
from aiogram.dispatcher.filters import Text
import pandas as pd


@dp.message_handler(Text(equals="отмена", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer("Хорошо, отеняем", reply_markup=types.ReplyKeyboardRemove())
