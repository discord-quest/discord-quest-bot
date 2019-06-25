from tortoise.models import Model
from tortoise import fields

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
# Because this is references by ActiveWorld, inheriting from Entity would cause a catch-22
class PlayerEntity(Model):
    x = fields.IntField()
    y = fields.IntField()

    def get_name(self):
        return "PLAYER"
    
    def get_state(self):
        return "NORMAL"

# A chest
# Higher level = better loot
class ChestEntity(Entity, Model):
    # TODO: Inheritance isn't working properly for some reason
    active_world = fields.ForeignKeyField("models.ActiveWorld", related_name="entities")
    x = fields.IntField()
    y = fields.IntField()
    level = fields.IntField()
    opened = fields.BooleanField()

    class Meta:
        unique_together = [("active_world", "x", "y")]

    def get_name(self):
        return "CHEST"

    def get_state(self):
        return "OPENED" if self.opened else "CLOSED"