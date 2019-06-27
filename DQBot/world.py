import numpy as np
from PIL import Image
from .repo import TILE_SIZE, BlockType
import logging
import json
import DQBot.models.entities as entities

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

    def from_text(text):
        lines = [x.strip() for x in text.split("\n")]
        height = len(lines)
        width = max([len(line) for line in lines])
        grid = np.ones(shape=(width, height), dtype=np.int8)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                grid[x, y] = int(char)

        return grid

ENTITY_CLASS = {
    'Chest': entities.ChestEntity
}

class BundledWorld:
    def __init__(self, world, entities):
        self.world = world
        self.entities = entities

    def parse_entities(text):
        arr = []
        for obj in json.loads(text):
            inst = ENTITY_CLASS[obj['type']].from_dict(obj)
            arr.append(inst)
        return arr

    async def from_file(file, repo):
        contents = await file.read()

        (grid_chunk, entities_chunk) = contents.split("---")
        
        grid = World.from_text(grid_chunk)
        world = World(grid, repo)

        entities = BundledWorld.parse_entities(entities_chunk)

        return BundledWorld(world, entities)
