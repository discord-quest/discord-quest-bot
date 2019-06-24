from .repo import TileRepo
from os import getenv
import numpy as np
from aiohttp import web
from .world import World

# TODO: Async this. Since it's done at startup it might not be too bad though

# Keeps ownership of the TileRepo and all Worlds
# Deals with tying ActiveWorlds to Worlds
class DataStore:
	def __init__(self):
		self.repo = TileRepo(getenv('TILE_DIR'))
		self.worlds = {
			'test': World(np.random.randint(1, size=(25,25), high=3), self.repo) # Random floor/ground
		}
		# TODO: Load worlds properly


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
		queue_id = active_world.id

		self.queue[queue_id] = active_world
		return self.address + queue_id

	# Actually render the image to an HTTP response
	# There's not actually any I/O when rendering, so this isn't async.
	def process_render(self, active_world):
		# TODO
		return web.Response(text="It works!")

	async def handle(self, req):
		# get the id of what we're supposed to render
		queue_id = req.match_info.get('id')

		if queue_id != None and queue_id in self.queue:
			# render it
			resp = self.process_render(self.queue[queue_id])

			# delete from queue
			del self.queue[queue_id]

			return resp
		else:
			return web.Response(text="Something went wrong!")

	async def setup(self):
		self.app = web.Application()
		self.app.add_routes([web.get('/{id}', self.handle)])

		self.runner = web.AppRunner(self.app)
		await self.runner.setup()
		
		host = getenv("HTTP_HOST")
		port = getenv("HTTP_PORT")
		self.address = "http://%s:%s/" % (host, port)

		self.site = web.TCPSite(self.runner, host, port)
		await self.site.start()

	async def teardown(self):
		await self.runner.cleanup()