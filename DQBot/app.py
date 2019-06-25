from .server import DataStore, RenderServer
from os import getenv
import logging
import asyncio
import tortoise
from tortoise import Tortoise

logger = logging.getLogger("app")


class App:
    async def run(self):
        logger.info("Initialising...")

        # database init
        await self.db_start()

        # rendering
        self.store = DataStore()
        self.server = RenderServer(self.store)

        await self.server.setup()

        # TODO: Discord.py setup

        # For testing rendering quickly
        # from .models import Player, ActiveWorld, PlayerEntity
        # player = Player(discord_id="99999999")
        # await player.save()
        # player_entity = PlayerEntity(x=4, y=4)
        # await player_entity.save()
        # activeworld = ActiveWorld(world_name="test", player=player, player_entity=player_entity)
        # await activeworld.save()

        ## or:
        # activeworld = await ActiveWorld.first()

        # from .action import Action, MoveDirection
        # await activeworld.take_action(Action.move(MoveDirection.UP), self.store.worlds[activeworld.world_name])

        # print(self.server.add_to_queue(activeworld))

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
