from enum import Enum

class ActionType(Enum):
	MOVE = 1

# co-ord system is 0 is upper-left
class MoveDirection(Enum):
	UP = 1    # -y
	DOWN = 2  # +y
	LEFT = 3  # -x
	RIGHT = 4 # +x

class Action:
	# Don't use this directly, instead use the helper functions to ensure consistency
	def __init__(self, type, args):
		self.type = type
		if self.type == ActionType.MOVE:
			self.direction = args[0]
	
	def move(direction):
		return Action(ActionType.MOVE, (direction,))
