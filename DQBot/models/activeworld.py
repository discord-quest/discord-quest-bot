import numpy as np
from PIL import Image
from DQBot.repo import TILE_SIZE, BlockType

from tortoise.models import Model
from tortoise import fields

# The amount of tiles player around them players can see
VIEW_SIZE = (5, 5)

# A World a player is playing in. This inherits the blocks in it from World,
# but stores its own entities.
# This is what you should actually render for a player
class ActiveWorld(Model):
    world_name = fields.CharField(20) # Right now maps aren't stored in the database
    player = fields.ForeignKeyField('models.Player', related_name='active_world')
    player_entity = fields.ForeignKeyField('models.PlayerEntity', related_name='active_world')

    # Perform the requested action in the world, ie move the player, kill the enemy
    def take_action(self):
        pass

    # Return an image
    async def render(self, world):
        # cut out the view around the player
        await self.fetch_related('player_entity')
        
        center_point = ((self.player_entity.x + 0.5) * TILE_SIZE, (self.player_entity.y + 0.5) * TILE_SIZE)
        top_left_point = (center_point[0] - ((VIEW_SIZE[0] // 2) * TILE_SIZE), center_point[1] - ((VIEW_SIZE[1] // 2) * TILE_SIZE))

        size = (VIEW_SIZE[0] * TILE_SIZE, VIEW_SIZE[1] * TILE_SIZE)
        lower_right_point = (top_left_point[0] + size[0], top_left_point[1] + size[1])

        coords = top_left_point + lower_right_point

        image = world.image.crop(coords)

        # TODO: render entities onto it
        return image
