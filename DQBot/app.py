from . import dcord, db
import asyncio
from dotenv import load_dotenv
from os import path

# TODO: Proper settings setup
# Includes environment variables from .env at root
load_dotenv(path.join(path.dirname(__file__), '..', '.env'))

# Start main event loop
loop = asyncio.get_event_loop()

loop.run_until_complete(db.setup())

loop.run_until_complete(dcord.run())

loop.run_until_complete(db.teardown())

loop.close()