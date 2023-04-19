from aiogram import Bot
from data.models import *
from loader import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


async def send_queue(bot: Bot):
    next_date = next_weekday(datetime.datetime.now(), 0).strftime("%Y-%m-%d")
    session = Session()
    users = session.query(User).all()
    records = session.query(DefenseRecord).where(DefenseRecord.date == next_date).all()

    tasks = {}
    for r in records:
        if r.task in tasks:
            tasks[r.task].append(r.student.fio)
        else:
            tasks[r.task] = [r.student.fio]
    response_data = {task: len(tasks[task]) for task in tasks.keys()}
    priority = sorted(response_data, key=response_data.get, reverse=True)
    response = "Очередь на следующий понедельник:\n"
    for task in priority:
        response += f"{task}:\n"
        for index, student in enumerate(tasks[task]):
            response += f"   {index + 1} - {student}\n"

        response += "\n\n"

    for user in users:
        await bot.send_message(chat_id=user.id, text=f"{response}")


async def add_shuffle_job(bot: Bot, scheduler: AsyncIOScheduler):
    # TODO: add 15 seconds delay for testing
    next_sunday = next_weekday(datetime.datetime.now(), 6)
    # next_sunday.time = datetime.time(18, 0, 0)
    scheduler.add_job(
        send_queue,
        trigger="date",
        run_date=next_sunday,
        kwargs={"bot": bot},
    )
