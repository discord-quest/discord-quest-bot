from enum import Enum


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
            self.loot = args

    def success():
        return ActionResult(ActionResultType.SUCCESS, ())

    def error():
        return ActionResult(ActionResultType.ERROR, ())

    def got_loot(loot):
        return ActionResult(ActionResultType.GOT_LOOT, (loot,))


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
            return Direction.UP
        elif new[1] < base[1]:
            return Direction.DOWN
        return Direction.NONE


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

    def __str__(self):
        if self.type == ActionType.MOVE:
            return "MOVE %s" % self.direction
        elif self.type == ActionType.OPEN_CHEST:
            return "OPEN_CHEST %s" % self.direction
        else:
            return "%s" % self.type

    __repr__ = __str__
