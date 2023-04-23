from aiogram import executor, Bot
import datetime
import handlers, middlewares
from loader import dp, scheduler, Session, log, config

from data.models import User, DefenseRecord
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.scheduler import add_shuffle_job


async def on_startup(dispatcher):

    await set_default_commands(dispatcher)

    log.info("Starting scheduler")
    scheduler.add_job(
        add_shuffle_job,
        trigger="date",
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=5),
        kwargs={"bot": dispatcher.bot, "scheduler": scheduler},
    )
    scheduler.start()
    log.info("Scheduler started")
    await on_startup_notify(dispatcher)


if __name__ == "__main__":
    if config.DOCKER_MODE:
        executor.start_polling(dp, on_startup=on_startup)
    else:
        ans = input("Ты уверен что хочешь запустить бота? (y/n)")
        if ans.lower() == "y":
            executor.start_polling(dp, on_startup=on_startup)
        else:
            exit(0)
