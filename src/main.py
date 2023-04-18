from aiogram import executor, Bot
import datetime
import handlers, middlewares
from loader import dp, scheduler, Session

from data.models import User, DefenseRecord
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.scheduler import add_shuffle_job


async def on_startup(dispatcher):

    await set_default_commands(dispatcher)

    await on_startup_notify(dispatcher)

    scheduler.add_job(
        add_shuffle_job,
        trigger="date",
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=5),
        kwargs={"bot": dispatcher.bot, "scheduler": scheduler},
    )


if __name__ == "__main__":
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)
