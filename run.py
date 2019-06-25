from DQBot import App
from os import path

import asyncio
from dotenv import load_dotenv

# TODO: Proper settings setup
# Includes environment variables from .env at root
load_dotenv(path.join(path.dirname(__file__), '.env'))

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
