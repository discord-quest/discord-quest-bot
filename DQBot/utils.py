from os import getenv

def get_dev_IDs():
    return [int(f) for f in getenv("DEV_IDS").split(";")]
