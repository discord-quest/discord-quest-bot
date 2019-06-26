from .server import DataStore, RenderServer
from .inventory import ItemStore
from os import getenv
import logging
import asyncio
import tortoise
from tortoise import Tortoise
import random

logger = logging.getLogger("app")

# For testing stuff
# async def test_chest(store, item_store):
    # from .models import Player, ActiveWorld, PlayerEntity, ChestEntity
    # from .action import Action, Direction

    # player = Player(discord_id=str(random.random() * 100))
    # await player.save()
    # player_entity = PlayerEntity(x=4, y=4)
    # await player_entity.save()
    # activeworld = ActiveWorld(world_name="test", player=player, player_entity=player_entity)
    # await activeworld.save()

    # chest = ChestEntity(x=5, y=4, level=1, active_world=activeworld)
    # await chest.save()

    # print(await player_entity.inventory.all())
    # await activeworld.take_action(Action.open_chest(Direction.RIGHT), store.worlds[activeworld.world_name], item_store)
    # print(await player_entity.inventory.all())

    # print(self.server.add_to_queue(activeworld))


class App:
    async def run(self):
        logger.info("Initialising...")

        # database init
        await self.db_start()

        # rendering
        self.store = DataStore()
        self.item_store = ItemStore()
        self.server = RenderServer(self.store)

        await self.server.setup()

        # await test_chest(self.store, self.item_store)
        # TODO: Discord.py setup

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
