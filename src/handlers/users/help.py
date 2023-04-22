from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, log


@dp.message_handler(commands=["help"], state="*")
async def send_help(message: types.Message, state: FSMContext):
    log.info(
        f"func: send_help: {message.from_user.first_name}, {message.from_user.id}: {message.text}"
    )
    await message.answer(
        "Бот поможет организовать очередь сдачи домашки.\nПросто введи свой github и выбери преподавателя.\n<b>Ник можно указать только один раз, после авторизации его нельзя будет поменять!</b>"
    )
