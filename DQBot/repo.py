from enum import Enum
from os import path, listdir
from PIL import Image
import logging

TILE_SIZE = 32

logger = logging.getLogger("repo")

# Represents non-dynamic blocks that can be in the grid of a world
class BlockType(Enum):
    FLOOR = 1
    WALL = 2
    ERROR = -1  # special error type


# Stores the tile images represented by each block and images for
# each possible state of an entity as pillow images
# Example structure:
# base_dir/
#    FLOOR.png
#    WALL.png
#    CHEST/
#        OPEN.png
#        CLOSED.png
class TileRepo:
    # Will scan base_dir immediately
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.blocks = {}
        self.reload()

    # Import all blocktype images and all entity images
    def reload(self):
        # TODO: Async this. Since it's done at startup it might not be too bad though
        # for each block type
        for block_type in BlockType:
            # try to import image
            img_path = path.join(self.base_dir, block_type.name + ".png")
            try:
                img = Image.open(img_path)
                self.blocks[block_type] = img

                logger.debug("imported %s" % block_type)
            except:
                # warn if error
                logger.error("error importing block type %s" % block_type)

        # TODO
        self.entities = {}

        # for each entitytype
        subdirectories = [
            path.join(self.base_dir, x)
            for x in listdir(self.base_dir)
            if path.isdir(path.join(self.base_dir, x))
        ]

        # try to import all states
        for subdir in subdirectories:
            entity_images = {}
            for filename in listdir(subdir):
                state_name = filename.split(".")[0]
                img_path = path.join(subdir, filename)
                try:
                    img = Image.open(img_path)
                    entity_images[state_name] = img
                except:
                    # warn if error
                    logger.error(
                        "error importing state %s for entity %s " % (subdir, state_name)
                    )

            # save that entity
            entity_name = subdir.split("/")[-1]
            self.entities[entity_name] = entity_images

    # Gets the Image for a given block type
    def block(self, block_type):
        if block_type in self.blocks:
            return self.blocks[block_type]
        else:
            return self.blocks[BlockType.ERROR]

    # Gets the Image for a given entity's given state
    def entity(self, entity_type, state):
        if entity_type in self.entities and state in self.entities[entity_type]:
            return self.entities[entity_type][state]
        else:
            return self.blocks[BlockType.ERROR]
