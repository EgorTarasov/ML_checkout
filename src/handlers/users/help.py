from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink
from loader import dp, log


@dp.message_handler(commands=["help"], state="*")
async def send_help(message: types.Message, state: FSMContext):
    log.info(
        f"func: send_help: {message.from_user.first_name}, {message.from_user.id}: {message.text}"
    )
    table = hlink(
        "таблице",
        "https://docs.google.com/spreadsheets/d/1jIxeW8BcbeZcGmNm47tXzpGPVULhMvnOUYpNX3J2OF4/edit#gid=0",
    )
    await message.answer(
        f"Для записи на сдачу работы надо указать фамилию или ник в github, как в {table}.\n<b>ФИО (или ник) можно указать только один раз при запуске бота, после авторизации его нельзя будет поменять!</b>\n\n Справка:\n - Кнопка <b>'Отмена'</b> прерывает процесс записи, чтобы начать заного воспользуйтесь командой /start",
        disable_web_page_preview=True,
        reply_markup=types.ReplyKeyboardRemove(),
    )
