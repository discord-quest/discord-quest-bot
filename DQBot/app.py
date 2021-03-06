from .server import DataStore, RenderServer
from .inventory import ItemStore
from .utils import get_dev_IDs
from os import getenv, listdir, path
import logging
import asyncio
from tortoise import Tortoise

import discord
from discord.ext import commands

logger = logging.getLogger("app")


class App:
    async def run(self):
        logger.info("Initialising...")

        # database init
        await self.db_start()

        # rendering
        self.store = DataStore()
        await self.store.ready()

        self.item_store = ItemStore()
        self.server = RenderServer(self.store)

        await self.server.setup()

        class DQBot(commands.Bot):
            # Overwrites default owner check to allow for multiple owners as defined in .env
            async def is_owner(self, user: discord.User):
                if user.id in get_dev_IDs():
                    return True

                # Else fall back to the original
                return await super().is_owner(user)

        self.bot = DQBot(command_prefix=";")
        self.bot.app = self

        self.bot.load_extension(
            "jishaku"
        )  # Load jishaku (dev tools) https://github.com/Gorialis/jishaku
        for filename in listdir(
            path.join(path.dirname(path.realpath(__file__)), "cogs")
        ):
            if filename.endswith(".py"):
                try:
                    self.bot.load_extension(f"DQBot.cogs.{filename[0:-3]}")
                except commands.ExtensionError as e:
                    logger.error(e)

        await self.bot.start(getenv("BOT_TOKEN"))

        logger.debug("Active")
        # keep everything alive by sleeping forever
        while True:
            await asyncio.sleep(3600)

    async def db_start(self):
        logger.debug("Trying to connect to database...")
        await Tortoise.init(
            db_url=getenv("DB_URL"), modules={"models": ["DQBot.models"]}
        )
        # todo: slows stuff down, but should work for now
        await Tortoise.generate_schemas(safe=True)
        logger.info("Successfullly connected to database")

    async def teardown(self):
        logger.info("Tearing down app")

        await Tortoise.close_connections()
        await self.server.teardown()
