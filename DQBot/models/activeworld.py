import numpy as np
from PIL import Image
from DQBot.repo import TILE_SIZE, BlockType

from tortoise.models import Model
from tortoise import fields

# The amount of tiles player around them players can see
VIEW_SIZE = (6, 6)

# A World a player is playing in. This inherits the blocks in it from World,
# but stores its own entities.
# This is what you should actually render for a player
class ActiveWorld(Model):
    world_name = fields.CharField(20)  # Right now maps aren't stored in the database
    player = fields.ForeignKeyField("models.Player", related_name="active_world")

    # Perform the requested action in the world, ie move the player, kill the enemy
    def take_action(self):
        pass

    # Return an image
    def render(self, world):
        # TODO
        # get world & image from world
        # cut out the view around the player
        # render entities onto it
        return world.image
