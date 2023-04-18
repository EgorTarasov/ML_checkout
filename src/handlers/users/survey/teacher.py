from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, google_table_data, homeworks, teachers, Session, pd
from data.models import User, DefenseRecord


@dp.message_handler(state=StudentForm.teacher)
async def process_teacher(message: types.Message, state: FSMContext):

    if not message.text in teachers:
        await message.answer("Такого преподавателя нет в клавиатуре")
    else:
        session = Session()
        row = None
        async with state.proxy() as data:
            data["teacher"] = message.text
            row = google_table_data[google_table_data["Ник на git"] == data["github"]]
            homeworks_status = row[homeworks].values[0]
            response = "None"
            last_task = None
            for name, value in zip(homeworks, homeworks_status):
                print(name, value)
                if pd.isnull(value):
                    last_task = name

                    break
                else:
                    response += f"{name}: {value}\n"
            db_record = (
                session.query(DefenseRecord)
                .filter_by(student_id=message.from_user.id)
                .first()
            )
            if db_record:
                db_record.teacher = data["teacher"]
                db_record.task = last_task
                db_record.status = False
            else:
                db_record = DefenseRecord(
                    student=session.query(User)
                    .filter_by(id=message.from_user.id)
                    .first(),
                    teacher=data["teacher"],
                    task=last_task,
                    status=False,
                )
                # check if user already has a defense record
            session.add(db_record)
            session.commit()

        await StudentForm.next()
        reply_keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer(response)

        await message.answer(f"Github: {data['github']}\nTeacher: {data['teacher']}")

        if last_task:
            response = (
                f"Ты можешь сдать {last_task} на следующем занятии\nЗаписываемся?"
            )
            reply_keyboard.add("Да", "Нет")
            await StudentForm.next()
        else:
            response = "Ты сделал все задания! Можешь чилить)"
        await message.answer(response)
        await state.finish()
