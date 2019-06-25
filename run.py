from DQBot import App
from os import path, getenv

import logging
import logging.config

import asyncio
from dotenv import load_dotenv

# TODO: Proper settings setup
# Includes environment variables from .env at root
load_dotenv(path.join(path.dirname(__file__), ".env"))

HANDLERS = {
    "console": {
        "class": "logging.StreamHandler",
        "level": getenv("LOG_LEVEL"),
        "formatter": "default",
    },
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "level": getenv("LOG_LEVEL"),
        "filename": path.join(path.dirname(path.realpath(__file__)), "debug.log"),
        "maxBytes": 1024 * 1024,
        "backupCount": 3,
        "formatter": "default",
    },
}

CONFIG_FOR_LOGGERS = {"level": getenv("LOG_LEVEL"), "handlers": ["console", "file"]}

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {"default": {"format": "%(asctime)s - %(levelname)s - %(message)s"}},
    "handlers": HANDLERS,
    # "root": CONFIG_FOR_LOGGERS,
    "loggers": {
        "app": CONFIG_FOR_LOGGERS,
        "repo": CONFIG_FOR_LOGGERS,
        "server": CONFIG_FOR_LOGGERS,
        "world": CONFIG_FOR_LOGGERS,
    },
}

# Setup logging
logging.config.dictConfig(LOGGING_CONFIG)

# Start main event loop
loop = asyncio.get_event_loop()

app = App()
try:
    loop.run_until_complete(app.run())
except KeyboardInterrupt:
    pass
except Exception as e:
    logging.error(e)
    pass
finally:
    loop.run_until_complete(app.teardown())

loop.close()
