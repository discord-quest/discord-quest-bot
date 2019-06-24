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

    # Get the state of this entity
    # This is used to get the appropriate image to draw
    def get_state(self):
        raise NotImplementedError("base Entity.get_state called")


# The player
class PlayerEntity(Entity):
    def get_state(self):
        return "NORMAL"
