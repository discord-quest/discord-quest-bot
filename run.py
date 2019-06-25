from DQBot import App
from os import path

import logging
import logging.config

import asyncio
from dotenv import load_dotenv


LOGGING_CONFIG = {
    "version": 1,
    "formatters": {"default": {"format": "%(asctime)s - %(levelname)s - %(message)s"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": path.join(
                path.dirname(path.realpath(__file__)), "..", "debug.log"
            ),
            "maxBytes": 1024 * 1024,
            "backupCount": 3,
            "formatter": "default",
        },
    },
    "loggers": {"__main__": {"level": "DEBUG", "handlers": ["console", "file"]}},
}


# TODO: Proper settings setup
# Includes environment variables from .env at root
load_dotenv(path.join(path.dirname(__file__), '.env'))

# Setup logging
logging.config.dictConfig(LOGGING_CONFIG)


# Start main event loop
loop = asyncio.get_event_loop()

app = App()
try:
	loop.run_until_complete(app.run())
except Exception as e:
	print(e)
	pass
finally:
	loop.run_until_complete(app.teardown())

loop.close()
