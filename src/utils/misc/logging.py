import logging

logging.basicConfig(
    filename="bot.log",
    encoding="utf-8",
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO,
    # level=logging.DEBUG,  # Можно заменить на другой уровень логгирования.
)