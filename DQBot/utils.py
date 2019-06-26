from os import getenv


def get_dev_IDs():
    return [int(f) for f in getenv("DEV_IDS").split(";")]


async def add_reactions(message, *reacs):
    for reac in reacs:
        await message.add_reaction(reac)
