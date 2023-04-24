from aiogram import Bot
from data.models import *
from loader import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data import config
from loader import teachers, log
from data.models import DefenseRecord
import datetime


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def make_shuffle(
    records: list[DefenseRecord], next_date: str, teacher: str, student_id: int
):
    tasks = {}
    for r in records:
        if r.task in tasks:
            tasks[r.task].append(r.student)
        else:
            tasks[r.task] = [r.student]
    response_data = {task: len(tasks[task]) for task in tasks.keys()}
    priority = sorted(response_data, key=response_data.get, reverse=True)
    response = f"Очередь на следующий понедельник ({next_date.split('-')[2]}.{next_date.split('-')[1]}):\n{teacher}\n"
    index = 1
    for task in priority:
        for student in tasks[task]:
            response += (
                f"{index}) <b>{str(student.fio).title()}</b>⬅️\n"
                if student.id == student_id
                else f"{index}) {str(student.fio).title()}\n"
            )
            index += 1

    return response


async def send_queue(bot: Bot):
    log.debug("Запускаем функцию отправки очереди")
    next_date = next_weekday(datetime.datetime.now(), 0).strftime("%Y-%m-%d")
    session = Session()

    for teacher in teachers:
        records = (
            session.query(DefenseRecord)
            .where(
                (DefenseRecord.date == next_date) & (DefenseRecord.teacher == teacher)
            )
            .all()
        )
        for record in records:
            response = make_shuffle(records, next_date, teacher, record.student_id)
            if not config.BOT_MODE:
                log.debug(
                    f"{record.student.fio} - {record.student.id} - {record.student.is_admin}"
                )
                if record.student.is_admin:
                    await bot.send_message(
                        chat_id=record.student.id,
                        text=response,
                    )
            else:
                await bot.send_message(
                    chat_id=record.student.id,
                    text=response,
                )


async def add_shuffle_job(bot: Bot, scheduler: AsyncIOScheduler):
    day = datetime.datetime.now()
    if not (day.weekday() == 6 and day.hour < 18):
        day = next_weekday(day, 0)

    day = day.replace(hour=18, minute=0, second=0)

    task_date = (
        datetime.datetime.now() + datetime.timedelta(seconds=10)
        if not config.BOT_MODE
        else day
    )
    log.debug(f"режим бота:{config.BOT_MODE}")
    log.info(
        f"Добавляем задачу в планировщик на {task_date.strftime('%d.%m.%Y %H:%M:%S')}')"
    )
    scheduler.add_job(
        send_queue,
        trigger="date",
        run_date=task_date,
        kwargs={"bot": bot},
    )
