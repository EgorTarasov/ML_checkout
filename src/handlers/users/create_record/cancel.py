from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, log, config
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink
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


@dp.message_handler(Text(equals="/cancel", ignore_case=True), state="*")
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

    table = hlink("таблице", config.GOOGLE_URL)
    await message.answer(
        f"Для записи на сдачу работы надо указать фамилию или ник в github, как в {table}.\n<b>ФИО (или ник) можно указать только один раз при запуске бота, после авторизации его нельзя будет поменять!</b>\n\n Справка:\n - Кнопка <b>'Отмена'</b> прерывает процесс записи, чтобы начать заного воспользуйтесь командой /start",
        disable_web_page_preview=True,
        reply_markup=types.ReplyKeyboardRemove(),
    )
