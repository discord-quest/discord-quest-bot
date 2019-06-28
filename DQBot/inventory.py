from enum import Enum
import random


class Item:
    id = -1
    capabilities = []

    def __init__(self, friendly_name, description, tier):
        global ITEM_ID
        self.id = ITEM_ID
        self.friendly_name = friendly_name
        self.description = description
        self.tier = tier
        ITEM_ID += 1


class ItemCapability(Enum):
    MELEE_ATTACK = (1,)
    HEAL = 2


# This is such a bad way to do this
ITEM_ID = 0


class HealingItem(Item):
    capabilities = [ItemCapability.HEAL]

    def __init__(self, friendly_name, description, amnt, tier):
        global ITEM_ID
        self.id = ITEM_ID
        self.friendly_name = friendly_name
        self.description = "%s (Heals %s)" % (description, amnt)
        self.tier = tier
        self.amnt = amnt

        ITEM_ID += 1


class MeleeWeapon:
    capabilities = [ItemCapability.MELEE_ATTACK]

    def __init__(self, friendly_name, description, damage, tier):
        global ITEM_ID
        self.id = ITEM_ID
        self.friendly_name = friendly_name
        self.description = "%s (%s damage)" % (description, damage)
        self.damage = damage
        self.tier = tier
        ITEM_ID += 1


class ItemStore:
    def __init__(self):
        # TODO: This is stored really inefficiently
        self.items = [
            # Note: This needs to always be sorted by tier
            MeleeWeapon(
                "Wooden Sword", "It's not very strong, but it'll do.", 2, 1
            ),  # Index 0 = ID 0
            Item("Wooden Coin", "Small change.", 1),
            HealingItem("Rum", "Technically a solution.", 2, 1),
            MeleeWeapon(
                "Smuggler's Sword", "Once belonged to a ring of smugglers.", 3, 2
            ),
            Item("Silver Coin", "Worth a bit.", 2),
            HealingItem("Salve", "", 5, 2),
            MeleeWeapon(
                "Boss' Sword",
                "A big hunk of metal with the word 'Mine' engraved on the helm.",
                4,
                3,
            ),
            Item("Gold Coin", "Well worth the trip.", 3),
            MeleeWeapon(
                "Legendary Sword",
                "A giant hunk of metal with the word 'Odgrub' engraved on the helm.",
                2,
                4,
            ),
            Item("Platinum Coin", "Worth as much as this whole place.", 4),
        ]

        # tiers[tier-1] is the range (last exclusive) of indexes of items that are in that tier
        self.tiers = [(0, 2), (0, 4), (2, 6), (4, 8)]

    def roll_loot(self, tier):
        # Amount of items = tier, starting at tier 1
        return [self.roll_item(tier) for i in range(tier)]

    def roll_item(self, tier):
        possible = self.tiers[tier - 1]
        selected = random.randint(possible[0], possible[1])
        return self.items[selected]

    def find_capable(self, items, capability):
        capable = [x for x in items if capability in x.capabilities]

        if capability == ItemCapability.MELEE_ATTACK:
            capable.sort(key=lambda x: x.damage, reverse=True)
        elif capability == ItemCapability.HEAL:
            capable.sort(key=lambda x: x.amnt, reverse=True)

        if len(capable) > 0:
            return capable[0]
