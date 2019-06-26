from tortoise.models import Model
from tortoise import fields

from .inventory import InventoryEntry

# A base class for all entities to inherit from
# An entity is anything that could vary between each player's world.
# For example an enemy which takes damage and eventually dies
# But also a chest that can only be looted once
class Entity(Model):
    active_world = fields.ForeignKeyField("models.ActiveWorld", related_name="entities")
    x = fields.IntField()
    y = fields.IntField()

    class Meta:
        abstract = True
        unique_together = [("active_world", "x", "y")]

    # Get the name of this entity
    # This is used to get the appropriate image to draw
    def get_name(self):
        raise NotImplementedError("base Entity.get_name called")

    # Get the state of this entity
    # This is used to get the appropriate image to draw
    def get_state(self):
        raise NotImplementedError("base Entity.get_state called")


# The player
# Because this is referenced by ActiveWorld, inheriting from Entity would cause a catch-22
class PlayerEntity(Model):
    x = fields.IntField()
    y = fields.IntField()

    def get_name(self):
        return "PLAYER"

    def get_state(self):
        return "NORMAL"

    # add items to inventory
    async def add_items(self, items):
        for item in items:
            # check for existing one
            entry = await self.inventory.filter(item_id=item.id).first()
            if entry == None:
                entry = InventoryEntry(item_id=item.id, player_entity=self, quantity=0)
            
            entry.quantity += 1

            await entry.save()


# A chest
# Higher level = better loot
class ChestEntity(Entity):
    # TODO: Inheritance isn't working properly for some reason
    active_world = fields.ForeignKeyField("models.ActiveWorld", related_name="entities")
    x = fields.IntField()
    y = fields.IntField()
    level = fields.IntField()
    opened = fields.BooleanField(default=False)

    class Meta:
        unique_together = [("active_world", "x", "y")]

    def get_name(self):
        return "CHEST"

    def get_state(self):
        return "OPENED" if self.opened else "CLOSED"
