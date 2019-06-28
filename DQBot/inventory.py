from enum import Enum
import random


class Item:
    id = -1
    friendly_name = "missingno"
    description = "???"
    capabilities = []
    tier = 9999


class ItemCapability(Enum):
    MELEE_ATTACK = 1


class MeleeWeapon:
    capabilities = [ItemCapability.MELEE_ATTACK]
    damage = 0


class BasicSword(MeleeWeapon):
    id = 0
    friendly_name = "Basic Sword"
    description = "a normal sword"
    damage = 2
    tier = 1


class ItemStore:
    def __init__(self):
        # TODO: This is stored really inefficiently
        self.items = [
            # Note: This needs to always be sorted by tier
            BasicSword()  # Index 0 = ID 0
        ]

        # tiers[tier-1] is the range (last exclusive) of indexes of items that are in that tier
        self.tiers = [(0, 0)]

    def roll_loot(self, tier):
        # Amount of items = tier, starting at tier 1
        return [self.roll_item(tier) for i in range(tier)]

    def roll_item(self, tier):
        possible = self.tiers[tier - 1]
        selected = random.randint(possible[0], possible[1])
        return self.items[selected]
