from .repo import TileRepo
from os import getenv, path, listdir
import numpy as np
from aiohttp import web
from .world import World, BundledWorld
from io import BytesIO
import logging
import aiofiles
import asyncio

# TODO: Async this. Since it's done at startup it might not be too bad though

logger = logging.getLogger("server")

# Keeps ownership of the TileRepo and all Worlds
# Deals with tying ActiveWorlds to Worlds
class DataStore:
    def __init__(self):
        self.repo = TileRepo(getenv("TILE_DIR"))
        self.bundled_worlds = {}

    async def ready(self):
        world_dir = getenv("WORLD_DIR")

        # this part cant be done async yet
        worlds = [
            (x.split(".")[0], path.join(world_dir, x))
            for x in listdir(world_dir)
            if path.isfile(path.join(world_dir, x))
        ]

        for (world_name, world_path) in worlds:
            async with aiofiles.open(world_path, "r") as f:
                self.bundled_worlds[world_name] = await BundledWorld.from_file(
                    world_name, f, self.repo
                )


# Deals with rendering worlds and preventing them to the user
# This is done by returning a URL (obtained from here) then doing the actual rendering
# Once a request is made to that URL
class RenderServer:
    def __init__(self, store):
        self.store = store
        self.queue = {}

    # Returns the image URL of the rendered map
    def add_to_queue(self, active_world):
        # TODO: Should this be a properly random thing?
        queue_id = str(active_world.id)

        self.queue[queue_id] = active_world
        return self.address + str(queue_id) + ".png"

    async def remove_from_queue(self, queue_id):
        # give them a minute to request it again
        # apparently discord does some funky stuff with the images
        # so it might be got more than once
        await asyncio.sleep(60)
        del self.queue[queue_id]

    # Actually render the image to an HTTP response
    async def process_render(self, active_world):
        try:
            # get world
            world = self.store.bundled_worlds[active_world.world_name].world

            # get the rendered image
            image = await active_world.render(world, self.store.repo)

            # return it
            buf = (
                BytesIO()
            )  # TODO: Allocate initial bytes? also might be more efficient way to do this
            image.save(buf, format="png")

            return web.Response(body=buf.getvalue(), content_type="image/png")
        except Exception as e:
            logging.error(e)
            return web.Response(text="Something went wrong")

    async def handle(self, req):
        # get the id of what we're supposed to render
        queue_id = req.match_info.get("id")

        if queue_id != None and queue_id in self.queue:
            # render it
            resp = await self.process_render(self.queue[queue_id])

            # schedule delete from queue
            asyncio.create_task(self.remove_from_queue(queue_id))

            return resp
        else:
            return web.Response(text="Something went wrong!")

    async def setup(self):
        logger.debug("Trying to start render server...")

        self.app = web.Application()
        self.app.add_routes([web.get("/{id}.png", self.handle)])

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        host = getenv("HTTP_HOST")
        port = int(getenv("PORT"))

        external_port = port

        if getenv("EXTERNAL_PORT") != None:
            external_port = int(getenv("EXTERNAL_PORT"))

        if external_port != 80:
            self.address = "http://%s:%s/" % (host, port)
        else:
            self.address = "http://%s/" % host

        self.site = web.TCPSite(self.runner, None, port)
        await self.site.start()

        logger.debug("Render server started at %s" % self.address)

    async def teardown(self):
        logger.debug("Tearing down render server..")
        await self.runner.cleanup()
