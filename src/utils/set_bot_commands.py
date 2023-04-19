from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Записаться на сдачу дз"),
            types.BotCommand("help", "Вывести справку"),
            types.BotCommand("cancel", "Отменить запись"),
            types.BotCommand("status", "Проверить статус записи"),
        ]
    )
