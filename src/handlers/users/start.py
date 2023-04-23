from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp, Session, log
from data.models import User, DefenseRecord
from aiogram.dispatcher.filters import Text
from .create_record import StudentForm
from loader import dp, Session, teachers, google_table_data
import datetime
from aiogram.utils.markdown import hlink


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    log.info(f"User {message.from_user.id} {message.from_user.first_name} started bot")
    session = Session()
    userdata = dict(message.from_user)
    db_user = session.query(User).filter_by(id=message.from_user.id).one_or_none()
    if db_user is None or db_user.github is None:
        db_user = User(**userdata)
        session.merge(db_user)
        session.commit()

        await StudentForm.auth.set()
        table = hlink(
            "таблице",
            "https://docs.google.com/spreadsheets/d/1jIxeW8BcbeZcGmNm47tXzpGPVULhMvnOUYpNX3J2OF4/edit#gid=0",
        )
        await message.answer(
            f"Привет!\nДля записи на сдачу работы надо указать фамилию или ник в github, как в {table}.\n<b>ФИО (или ник) можно указать только один раз при запуске бота, после авторизации его нельзя будет поменять!</b>\n\n Справка:\n - Кнопка <b>'Отмена'</b> прерывает процесс записи, чтобы начать заного воспользуйтесь командой /start",
            disable_web_page_preview=True,
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        db_user = User(**userdata)
        session.merge(db_user)
        session.commit()

        await StudentForm.teacher.set()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        buttons = teachers
        reply_keyboard.add(*buttons)
        reply_keyboard.add("Отмена")
        await message.answer(
            "Ты уже авторизован.\nКакому преподавателю ты хочешь сдать домашку?",
            reply_markup=reply_keyboard,
        )


@dp.message_handler(Text(startswith="/shuffle_"))
async def send_shuffle_to_admin(message: types.Message):
    session = Session()
    teacher = (
        "Егоров" if message.text.split()[0].split("_")[1] == "egorov" else "Хасанова"
    )
    today = datetime.datetime.today().date().strftime("%Y-%m-%d")

    last_names = message.text.split()[1:]
    final_records = []
    for last_name in last_names:
        students_from_db = google_table_data[
            google_table_data["Фамилия"] == last_name
        ].values
        # понять, как по этим фамилиями выбирать записи из бд
        for student in students_from_db:
            record_for_student = (
                session.query(DefenseRecord)
                .where(
                    (DefenseRecord.teacher == teacher)
                    & (DefenseRecord.date == today)
                    & (DefenseRecord.student == student)  # вот тут выбираем <-
                )
                .first()
            )
            final_records.append(record_for_student)

    log.debug(final_records)

    next_monday = datetime.datetime.today() + datetime.timedelta(days=1)
    # next_monday = next_monday.strftime("%Y-%m-%d")

    response = f"Очередь на следующий понедельник ({next_monday.strftime('%d.%m')}:\n{teacher}\n"
    # index = 1
    # for student in students_from_db:
    #     response += f"{index}) {str(student.fio).title()}\n"
    #     index += 1

    log.debug(teacher)
    log.debug(last_names)

    await message.answer(response)
