from tortoise import Tortoise
from os import getenv
import tortoise
import asyncio

async def setup():
    await Tortoise.init(
        db_url=getenv('DB_URL'), # TODO
        modules={'models': ['DQBot.models']}
    )

    await Tortoise.generate_schemas()

async def teardown():
    await Tortoise.close_connections()
