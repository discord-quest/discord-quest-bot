from enum import Enum

class Item:
	id = -1
	friendly_name = "missingno"
	capabilities = []
	tier = 9999

class ItemCapability(Enum):
	MELEE_ATTACK = 1

class MeleeWeapon:
	capabilities = [ItemCapability.MELEE_ATTACK]
	damage = 0

class BasicSword(MeleeWeapon):
	id = 1
	friendly_name = "Basic Sword"
	damage = 2
	tier = 1

class ItemStore:
	def __init__(self):
		# TODO: Load item data from somewhere
		self.items = [ 
			# Note: This needs to always be sorted by tier
			BasicSword()
		]

	def roll_loot(self, tier, number):
		# TODO
		return [self.items[0]]