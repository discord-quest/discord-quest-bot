from .server import DataStore, RenderServer
import asyncio

# TODO: Discord.py setup
async def run():

    # rendering
    store = DataStore()
    server = RenderServer(store)
    await server.setup()

    try:
        # keep everything alive by sleeping forever
        while True:
            await asyncio.sleep(3600)
    except:
        pass
    finally:
        await server.teardown()
