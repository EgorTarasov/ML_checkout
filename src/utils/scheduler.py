from aiogram import Bot
from data.models import *
from loader import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from data import config
from loader import teachers
import datetime


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def make_shuffle(records: list[DefenseRecord], next_date: str, teacher: str):
    tasks = {}
    for r in records:
        if r.task in tasks:
            tasks[r.task].append(r.student.fio)
        else:
            tasks[r.task] = [r.student.fio]
    response_data = {task: len(tasks[task]) for task in tasks.keys()}
    priority = sorted(response_data, key=response_data.get, reverse=True)
    response = f"Очередь на следующий понедельник ({next_date.split('-')[2]}.{next_date.split('-')[1]}):\n{teacher}\n"
    index = 1
    for task in priority:
        # response += f"{task}:\n"
        for student in tasks[task]:
            # response += f"    {index + 1} - <b>{student}</b>\n"
            response += f"{index}) <b>{student}</b> - {task}"

        response += "\n\n"

    return response


async def send_queue(bot: Bot):
    next_date = next_weekday(datetime.datetime.now(), 0).strftime("%Y-%m-%d")
    session = Session()
    
    for teacher in teachers:
        records = session.query(DefenseRecord).where((DefenseRecord.date == next_date) &
                                                     (DefenseRecord.teacher == teacher)).all()
        
        response = make_shuffle(records, next_date, teacher)
        
        for record in records:
            await bot.send_message(chat_id=record.student_id, text=response)


async def add_shuffle_job(bot: Bot, scheduler: AsyncIOScheduler):
    # TODO: add 15 seconds delay for testing
    next_sunday = next_weekday(datetime.datetime.now(), 6)
    # next_sunday.time = datetime.time(18, 0, 0)
    next_sunday = next_sunday.replace(hour=18, minute=0)
    
    scheduler.add_job(
        send_queue,
        trigger="date",
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=8) if config.BOT_MODE == "debug" else next_sunday.date(),
        kwargs={"bot": bot},
    )
