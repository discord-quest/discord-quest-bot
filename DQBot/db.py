from tortoise import Tortoise
from os import getenv
import tortoise
import asyncio


async def setup():
    await Tortoise.init(
        db_url=getenv("DB_URL"), modules={"models": ["DQBot.models"]}  # TODO
    )

    await Tortoise.generate_schemas()


async def teardown():
    await Tortoise.close_connections()
