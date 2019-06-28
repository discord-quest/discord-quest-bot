# encoding:utf-8

from discord import Emoji, Embed
from enum import Enum
from tortoise.query_utils import Q


class ActionType(Enum):
    MOVE = 1
    OPEN_CHEST = 2


class ActionResultType(Enum):
    SUCCESS = (1,)
    ERROR = (2,)
    GOT_LOOT = 3


class ActionResult:
    def __init__(self, type, args):
        self.type = type
        if self.type == ActionResultType.GOT_LOOT:
            self.loot = args[0]

    def success():
        return ActionResult(ActionResultType.SUCCESS, ())

    def error():
        return ActionResult(ActionResultType.ERROR, ())

    def got_loot(loot):
        return ActionResult(ActionResultType.GOT_LOOT, (loot,))

    def to_embed(self, item_store):
        if self.type == ActionResultType.GOT_LOOT:
            embed = Embed(title="You found:")
            for item in self.loot:
                embed.add_field(
                    name=item.friendly_name, value=item.description, inline=False
                )
            return embed
        else:
            return None


# co-ord system is 0 is upper-left
class Direction(Enum):
    UP = 1  # -y
    DOWN = 2  # +y
    LEFT = 3  # -x
    RIGHT = 4  # +x
    NONE = 5

    # Return pos after moving one unit in this direction
    def mutate(self, pos):
        x, y = pos
        if self == Direction.UP:
            y -= 1
        elif self == Direction.DOWN:
            y += 1
        elif self == Direction.LEFT:
            x -= 1
        elif self == Direction.RIGHT:
            x += 1
        return (x, y)

    def from_delta(base, new):
        if new[0] > base[0]:
            return Direction.RIGHT
        elif new[0] < base[0]:
            return Direction.LEFT
        elif new[1] > base[1]:
            return Direction.DOWN
        elif new[1] < base[1]:
            return Direction.UP
        return Direction.NONE


DIRECTION_TO_ARROWS = {
    Direction.UP: u"\U00002B06",
    Direction.DOWN: u"\U00002B07",
    Direction.LEFT: u"\U00002B05",
    Direction.RIGHT: u"\U000027A1",
}

CHEST_EMOJI = u"\U0001F4BC"  # TODO: Find a better emoji


class Action:
    # Don't use this directly, instead use the helper functions to ensure consistency
    def __init__(self, type, args):
        self.type = type
        if self.type == ActionType.MOVE:
            self.direction = args[0]
        if self.type == ActionType.OPEN_CHEST:
            self.direction = args[0]

    def move(direction):
        return Action(ActionType.MOVE, (direction,))

    def open_chest(direction):
        return Action(ActionType.OPEN_CHEST, (direction,))

    def to_reaction(self):
        if self.type == ActionType.MOVE:
            return DIRECTION_TO_ARROWS[self.direction]
        elif self.type == ActionType.OPEN_CHEST:
            return CHEST_EMOJI

    async def from_emoji(emoji, active_world):
        if isinstance(emoji, str):
            if emoji in DIRECTION_TO_ARROWS.values():
                return Action.move(
                    next(
                        key
                        for key, value in DIRECTION_TO_ARROWS.items()
                        if value == emoji
                    )
                )
            elif emoji == CHEST_EMOJI:
                (x, y) = (active_world.player_entity.x, active_world.player_entity.y)

                unopened_chest = await active_world.chest_entities.filter(
                    Q(x__in=(x + 1, x - 1), y=y)
                    | Q(y__in=(y + 1, y - 1), x=x) & Q(opened=False)
                ).first()

                direction = Direction.from_delta(
                    (x, y), (unopened_chest.x, unopened_chest.y)
                )

                return Action.open_chest(direction)
        return None

    def __str__(self):
        if self.type == ActionType.MOVE:
            return "MOVE %s" % self.direction
        elif self.type == ActionType.OPEN_CHEST:
            return "OPEN_CHEST %s" % self.direction
        else:
            return "%s" % self.type

    __repr__ = __str__
