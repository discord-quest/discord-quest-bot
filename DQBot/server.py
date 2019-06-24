from .repo import TileRepo
from os import getenv
import numpy as np

# TODO: Async this. Since it's done at startup it might not be too bad though

# Keeps ownership of the TileRepo and all Worlds
# Deals with tying ActiveWorlds to Worlds
class DataStore:
	def __init__(self):
		self.repo = TileRepo(getenv('TILE_DIR'))
		self.worlds = {
			'test': World(np.random.randint(1, size=dimensions, high=3), (25, 25), self.repo) # Random floor/ground
		}
		# TODO: Load worlds properly


# Deals with rendering worlds and preventing them to the user
# This is done by returning a URL (obtained from here) then doing the actual rendering
# Once a request is made to that URL
class RenderServer:
	def __init__(self, store):
		self.store = store
		# TODO: Server setup

	# Returns the image URL of the rendered map
	def add_to_queue(self, active_world)
		# TODO
		return "http://placeholder.com/500/500"

	# Actually render the image to an HTTP response
	def process_render(self, active_world)
		# TODO
		pass