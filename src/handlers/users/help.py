from aiogram import types
from loader import dp


@dp.message_handler(commands=["help"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Бот поможет организовать очередь сдачи домашки.\nПросто введи свой github и выбери преподавателя.\n<b>Ник можно указать только один раз, после авторизации его нельзя будет поменять!</b>"
    )
