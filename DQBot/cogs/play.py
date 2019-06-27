from discord.ext import commands
from DQBot.action import Action
from DQBot.models import ActiveWorld, Player
import discord


class Play(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.app = client.app

    @commands.command()
    async def play(self, ctx):
        user_id = ctx.author.id

        # Get active world and everything else needed to render
        active_world = (
            await ActiveWorld.filter(player__discord_id=user_id)
            .prefetch_related("player_entity", "entities", "player_entity__inventory")
            .first()
        )

        # Create the world/player if not found
        if active_world == None:
            # TODO: Proper creation of world
            player = Player(discord_id=user_id)
            try:
                await player.save()
            except:
                # probably already exists, but no world
                player = await Player.filter(discord_id=user_id).first()

            if player != None:
                active_world = await self.app.store.bundled_worlds["test"].create_for(
                    player
                )

                await active_world.prefetch_related(
                    "player_entity", "entities", "player_entity__inventory"
                ).first()
            else:
                await ctx.send("Couldn't register you as a player.")

        # Add to render queue & send embed
        url = self.app.server.add_to_queue(active_world)

        # It seems like embeds require a domain name and so dont work with localhost images
        embed = discord.Embed(url=url, content="Your world:")

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Play(client))
