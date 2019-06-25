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

    async def paste_entity(self, entity, image, repo, lower_bounds, upper_bounds):
        # bounds check
        if False in tuple(a > lower_bounds[i] and a < upper_bounds[i] for i,a in enumerate((entity.x, entity.y))):
            return

        # translate to local world co-ords
        local_world_coords = (entity.x - lower_bounds[0], entity.y - lower_bounds[1])

        # then to local image co-ords
        image_coords = (local_world_coords[0] * TILE_SIZE, local_world_coords[1] * TILE_SIZE)

        # get image to render
        entity_image = repo.entity(entity.get_name(), entity.get_state())

        # paste onto map
        image.paste(entity_image, image_coords)

    # Return an image
    async def render(self, world, repo):
        await self.fetch_related('player_entity')
        await self.fetch_related('entities')
        
        # cut out the view around the player
        # TODO: Probably nicer looking ways to do this
        section_center = tuple((a + 0.5) * TILE_SIZE for a in (self.player_entity.x, self.player_entity.y))
        section_top_left = tuple(a - ((VIEW_SIZE[i] // 2) * TILE_SIZE) for i,a in enumerate(section_center))

        section_size = tuple(VIEW_SIZE[i] * TILE_SIZE for i in (0,1))

        lower_right_point = tuple(section_top_left[i] + section_size[i] for i in (0,1))

        coords = section_top_left + lower_right_point
        image = world.image.crop(coords)

        lower_bounds = tuple(a - (VIEW_SIZE[i] // 2) for i,a in enumerate((self.player_entity.x, self.player_entity.y)))
        upper_bounds = tuple(a + (VIEW_SIZE[i] // 2) for i,a in enumerate((self.player_entity.x, self.player_entity.y)))
        
        async for entity in self.entities:
            await self.paste_entity(entity, image, repo, lower_bounds, upper_bounds)

        await self.paste_entity(self.player_entity, image, repo, lower_bounds, upper_bounds) 
        return image
