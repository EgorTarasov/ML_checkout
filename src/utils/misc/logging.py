import logging  # Logging important events
from data import config

# Create a logger instance
def create_logger():
    log = logging.getLogger("backend")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    logfile_path = r"backend.log"

    fh = logging.FileHandler(logfile_path)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # Set logging level
    logging_level_lower = config.LOGGING_LEVEL.lower()
    if logging_level_lower == "debug":
        log.setLevel(logging.DEBUG)
        log.critical("Log level set to debug")
    elif logging_level_lower == "info":
        log.setLevel(logging.INFO)
        log.critical("Log level set to info")
    elif logging_level_lower == "warning":
        log.setLevel(logging.WARNING)
        log.critical("Log level set to warning")
    elif logging_level_lower == "error":
        log.setLevel(logging.ERROR)
        log.critical("Log level set to error")
    elif logging_level_lower == "critical":
        log.setLevel(logging.CRITICAL)
        log.critical("Log level set to critical")
    return log
