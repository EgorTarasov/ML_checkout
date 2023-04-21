import datetime
from aiogram import types
from .states import StudentForm
from aiogram.dispatcher import FSMContext
from loader import dp, Session
from data.models import User, DefenseRecord

import utils.scheduler


@dp.message_handler(state=StudentForm.queue)
async def process_queue(message: types.Message, state: FSMContext):
    if not (message.text in ["Да", "Нет"]):
        await message.answer("Ошибочка)")
    else:
        session = Session()
        if message.text == "Да":
            async with state.proxy() as data:
                db_record = (
                    session.query(DefenseRecord)
                    .filter_by(student_id=message.from_user.id)
                    .first()
                )
                next_date = utils.scheduler.next_weekday(datetime.datetime.now(), 0)
                if db_record:
                    db_record.teacher = data["teacher"]
                    db_record.task = data["last_task"]
                    db_record.status = False
                    db_record.date = next_date
                else:
                    db_record = DefenseRecord(
                        student=session.query(User)
                        .filter_by(id=message.from_user.id)
                        .first(),
                        teacher=data["teacher"],
                        task=data["last_task"],
                        status=False,
                        date=next_date,
                    )

                session.add(db_record)
                session.commit()
            await message.answer("Красава, в воскресение пришлем очередь")
            await state.finish()
        else:
            await message.answer("Better luck next time!")
            await state.finish()
