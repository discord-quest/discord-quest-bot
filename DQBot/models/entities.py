from tortoise.models import Model
from tortoise import fields

from .inventory import InventoryEntry

# A base class for all entities to inherit from
# An entity is anything that could vary between each player's world.
# For example an enemy which takes damage and eventually dies
# But also a chest that can only be looted once
class Entity(Model):
    active_world = fields.ForeignKeyField(
        "models.ActiveWorld", related_name="entities", on_delete=fields.CASCADE
    )
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

    def from_json(json):
        raise NotImplementedError("base Entity.from_json called")


PLAYER_MAX_HEALTH = 20

# The player
# Because this is referenced by ActiveWorld, inheriting from Entity would cause a catch-22
class PlayerEntity(Model):
    x = fields.IntField()
    y = fields.IntField()
    health = fields.IntField(default=PLAYER_MAX_HEALTH)

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
    active_world = fields.ForeignKeyField(
        "models.ActiveWorld", related_name="chest_entities", on_delete=fields.CASCADE
    )
    x = fields.IntField()
    y = fields.IntField()
    level = fields.IntField()
    opened = fields.BooleanField(default=False)

    class Meta:
        unique_together = [("active_world", "x", "y")]

    def get_name(self):
        return "CHEST"

    def get_state(self):
        return "OPEN" if self.opened else "CLOSED"

    def from_dict(obj):
        entity = ChestEntity()
        entity.x = int(obj["x"])
        entity.y = int(obj["y"])
        entity.level = int(obj["level"])
        entity.opened = False
        return entity

    def __str__(self):
        return "<ChestEntity %s: (%s,%s) in id %s, level %s, opened: %s>" % (
            self.id,
            self.x,
            self.y,
            self.active_world_id,
            self.level,
            self.opened,
        )

    __repr__ = __str__


class EnemyEntity(Model):
    active_world = fields.ForeignKeyField("models.ActiveWorld", related_name="entities")
    x = fields.IntField()
    y = fields.IntField()

    friendly_name = "missingno"
    health = fields.IntField()
    max_health = 0
    speed = 1
    exp_reward = 0
    damage = 0
    vision_distance = 0
    attack_delay = 0

    class Meta:
        abstract = True

    async def take_damage(self, damage):
        self.health = self.health - damage
        if self.health <= 0:
            await self.delete()
        else:
            await self.save()


class BigZombieEntity(EnemyEntity):
    active_world = fields.ForeignKeyField(
        "models.ActiveWorld",
        related_name="bigzombie_entities",
        on_delete=fields.CASCADE,
    )
    x = fields.IntField()
    y = fields.IntField()
    health = fields.IntField()

    ticks_since_move = fields.IntField(default=0)
    ticks_since_attack = fields.IntField(default=0)
    friendly_name = "Giant Zombie"
    max_health = 8
    speed = 0.5
    exp_reward = 10
    damage = 6
    vision_distance = 5
    attack_delay = 1

    def from_dict(obj):
        entity = BigZombieEntity()
        entity.x = int(obj["x"])
        entity.y = int(obj["y"])
        entity.health = entity.max_health
        return entity

    def get_name(self):
        return "GIANT_ZOMBIE"

    def get_state(self):
        return "NORMAL"


class ZombieEntity(EnemyEntity):
    active_world = fields.ForeignKeyField(
        "models.ActiveWorld", related_name="zombie_entities", on_delete=fields.CASCADE
    )
    x = fields.IntField()
    y = fields.IntField()

    health = fields.IntField()
    friendly_name = "Zombie"
    max_health = 4
    speed = 1
    exp_reward = 2
    damage = 1
    vision_distance = 4

    def from_dict(obj):
        entity = ZombieEntity()
        entity.x = int(obj["x"])
        entity.y = int(obj["y"])
        entity.health = entity.max_health
        return entity

    def get_name(self):
        return "ZOMBIE"

    def get_state(self):
        return "NORMAL"


ENTITY_RELATIONSHIPS = ["zombie_entities", "chest_entities", "bigzombie_entities"]
