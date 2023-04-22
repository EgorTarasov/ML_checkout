import datetime
from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, Session
from data.models import User, DefenseRecord

import utils.scheduler


@dp.message_handler(state=StudentForm.queue)
async def process_queue(message: types.Message, state: FSMContext):
    session = Session()
    db_user = session.query(User).filter_by(id=message.from_user.id).one_or_none()
    if not db_user:
        await message.answer("Что-то пошло не так")
        await state.finish()
        return

    async with state.proxy() as data:
        if message.text == "У меня не получится в эти даты":
            await message.answer(
                "К сожалению, мы пока не можем записать позже, ты можешь записаться после слеующей пары.\n\n /start - для записи на защиту ",
                reply_markup=types.ReplyKeyboardRemove(),
            )
            await state.finish()
            return
        if message.text in [i.strftime("%d.%m") for i in data["next_dates"]]:
            db_record = (
                session.query(DefenseRecord)
                .filter_by(student_id=message.from_user.id)
                .one_or_none()
            )
            if db_record:
                db_record.teacher = data["teacher"]
                db_record.task = data["last_task"]
                db_record.status = False
                db_record.date = datetime.datetime(
                    year=datetime.datetime.now().year,
                    month=int(message.text.split(".")[1]),
                    day=int(message.text.split(".")[0]),
                )
            else:
                db_record = DefenseRecord(
                    teacher=data["teacher"],
                    task=data["last_task"],
                    status=False,
                    date=datetime.datetime(
                        year=datetime.datetime.now().year,
                        month=int(message.text.split(".")[1]),
                        day=int(message.text.split(".")[0]),
                    ),
                )
            db_record.student = db_user
            session.add(db_record)
            session.commit()
        else:
            await message.answer(
                "К сожалению, мы пока не можем записать позже, ты можешь выбрать даты из клавиатуры"
            )
            return
    await message.answer(
        "Красава, в воскресение перед занятием пришлем очередь",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.finish()
    # if not (message.text in ["Да", "Нет"]):
    #     await message.answer("Ошибочка)")
    # else:
    #     session = Session()
    #     if message.text == "Да":
    #         async with state.proxy() as data:
    #             db_record = (
    #                 session.query(DefenseRecord)
    #                 .filter_by(student_id=message.from_user.id)
    #                 .first()
    #             )
    #             next_date = utils.scheduler.next_weekday(datetime.datetime.now(), 0)
    #             if db_record:
    #                 db_record.teacher = data["teacher"]
    #                 db_record.task = data["last_task"]
    #                 db_record.status = False
    #                 db_record.date = next_date
    #             else:
    #                 db_record = DefenseRecord(
    #                     student=session.query(User)
    #                     .filter_by(id=message.from_user.id)
    #                     .first(),
    #                     teacher=data["teacher"],
    #                     task=data["last_task"],
    #                     status=False,
    #                     date=next_date,
    #                 )

    #             session.add(db_record)
    #             session.commit()
    #         await message.answer(
    #             "Красава, в воскресение пришлем очередь",
    #             reply_markup=types.ReplyKeyboardRemove(),
    #         )
    #         await state.finish()
    #     else:
    #         await message.answer(
    #             "Better luck next time!",
    #             reply_markup=types.ReplyKeyboardRemove(),
    #         )
    #         await state.finish()
