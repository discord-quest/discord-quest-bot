from . import dcord, db
import asyncio
from dotenv import load_dotenv
from os import path
import logging

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {"default": {"format": "%(asctime)s - %(levelname)s - %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": path.join(path.dirname(path.realpath(__file__)), "..", "debug.log"),
            "maxBytes": 1024 * 1024,
            "backupCount": 3,
            "formatter": "default",
        },
    },
    "loggers": {"__main__": {"level": "DEBUG", "handlers": ["console", "file"]}},
}

# TODO: Proper settings setup

logging.config.dictConfig()
logger = logging.getLogger("__main__")

# Includes environment variables from .env at root
load_dotenv(path.join(path.dirname(__file__), "..", ".env"))

# Start main event loop
loop = asyncio.get_event_loop()

loop.run_until_complete(db.setup())

loop.run_until_complete(dcord.run())

loop.run_until_complete(db.teardown())

loop.close()
