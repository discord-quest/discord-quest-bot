import numpy as np
from PIL import Image
from .repo import TILE_SIZE, BlockType
import logging

logger = logging.getLogger("world")

# A world that is played by many players through ActiveWorld
# The grid of each World is the same, but the Entities within it vary for each ActiveWorld
# Each player has their own ActiveWorld, meaning everyone plays their own copy of the same "base" World.
class World:
    def __init__(self, grid, tile_repo):
        self.dimensions = grid.shape

        # Non-dynamic blocks (walls, etc)
        self.grid = grid

        self.prerender_world(tile_repo)

    # Cache the 'grid' (non-dynamic blocks) as an image
    # This renders the *entire* world into a single image and keeps it for later use.
    def prerender_world(self, tile_repo):
        logger.debug("Caching image for world...")

        size = (self.dimensions[0] * TILE_SIZE, self.dimensions[1] * TILE_SIZE)
        image = Image.new("RGB", size)

        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                # get the block type and image for that block type
                block_type = BlockType(self.grid[x, y])
                block_img = tile_repo.block(block_type)

                # paste onto the image
                coords = (x * TILE_SIZE, y * TILE_SIZE)
                image.paste(block_img, coords)

        self.image = image

    # Helper function
    def block_at(self, x, y):
        return BlockType(self.grid[x, y])

    # This is a test function, so it's not async or optimised at all
    def from_file(file, repo):
        lines = file.read().split("\n")
        height = len(lines)
        width = max([len(line) for line in lines])
        grid = np.ones(shape=(width, height), dtype=np.int8)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                grid[x, y] = int(char)

        return World(grid, repo)
