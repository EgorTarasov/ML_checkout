from aiogram import executor, Bot
import datetime
import handlers, middlewares
from loader import dp, scheduler, Session

from data.models import User, DefenseRecord
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


async def send_queue(bot: Bot):
    session = Session()
    users = session.query(User).all()
    print("send_message_time")
    # get all DefenseRecords from db
    records = session.query(DefenseRecord).all()
    tasks = {}
    for r in records:
        if r.task in tasks:
            tasks[r.task].append(r.student.fio)
        else:
            tasks[r.task] = [r.student.fio]
    print(tasks)
    for user in users:
        await bot.send_message(chat_id=user.id, text=f"{tasks}")


async def add_shuffle_job(bot: Bot, scheduler: AsyncIOScheduler):
    next_sunday = next_weekday(datetime.datetime.now(), 6)
    next_sunday.time = datetime.time(18, 0, 0)
    scheduler.add_job(
        send_queue,
        trigger="date",
        run_date=next_sunday,
        kwargs={"bot": bot},
    )


async def on_startup(dispatcher):

    await set_default_commands(dispatcher)

    await on_startup_notify(dispatcher)

    scheduler.add_job(
        add_shuffle_job,
        trigger="date",
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=1),
        kwargs={"bot": dispatcher.bot, "scheduler": scheduler},
    )


if __name__ == "__main__":

    executor.start_polling(dp, on_startup=on_startup)
