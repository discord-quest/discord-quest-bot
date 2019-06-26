from DQBot.utils import get_dev_IDs
from traceback import format_exception

from discord.ext import commands


class ErrorHandling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if (
            isinstance(exc, commands.CheckFailure)
            or isinstance(exc, commands.CommandNotFound)
            or isinstance(exc, commands.DisabledCommand)
        ):
            return

        if isinstance(exc, commands.CommandInvokeError):
            if ctx.author.id in get_dev_IDs():
                await ctx.send(
                    "Error raised! Since you're a developer, I'm DMing you the traceback."
                )
                await ctx.author.send(
                    f"```py\n{''.join(format_exception(type(exc), exc, exc.__traceback__))}\n```"
                )

            # TODO: error reporting for non-devs

        await ctx.send(exc)


def setup(client):
    client.add_cog(ErrorHandling(client))
