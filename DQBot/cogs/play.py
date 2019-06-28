from discord.ext import commands
from DQBot.action import Action, Direction
from DQBot.models import ActiveWorld, Player
from DQBot.models.entities import ENTITY_RELATIONSHIPS
import discord


class Play(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.app = client.app
        self.awaiting_response = {}

    @commands.command()
    async def play(self, ctx):
        await self.do_render(ctx.channel, ctx.author.id)

    async def do_render(self, channel, user_id):
        # Get active world and everything else needed to render
        active_world = (
            await ActiveWorld.filter(player__discord_id=user_id)
            .prefetch_related(
                "player_entity", "player_entity__inventory", *ENTITY_RELATIONSHIPS
            )
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

                await active_world.fetch_related(
                    "player_entity", "player_entity__inventory", *ENTITY_RELATIONSHIPS
                )
            else:
                await channel.send("Couldn't register you as a player.")

        # Add to render queue & send embed
        url = self.app.server.add_to_queue(active_world)

        # It seems like embeds require a domain name and so dont work with localhost images
        embed = discord.Embed(url=url, content="Your world:")

        msg = await channel.send(embed=embed)

        self.awaiting_response[msg.id] = user_id

        # Add reactions for actions
        world = self.app.store.bundled_worlds[active_world.world_name].world
        for action in await active_world.possible_actions(world):
            await msg.add_reaction(action.to_reaction())

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # if this is a message we care about
        if reaction.message.id not in self.awaiting_response:
            return

        # we added reactions for all valid actions, so it must have at least 2
        users = await reaction.users().flatten()
        if (
            reaction.count >= 2
            and self.client.user in users
            and self.awaiting_response[reaction.message.id] in [u.id for u in users]
        ):
            # get the world and stuff
            active_world = (
                await ActiveWorld.filter(
                    player__discord_id=self.awaiting_response[reaction.message.id]
                )
                .prefetch_related(
                    "player_entity", "player_entity__inventory", *ENTITY_RELATIONSHIPS
                )
                .first()
            )

            # construct the action
            action = await Action.from_emoji(reaction.emoji, active_world)

            if action != None:
                # Perform the action
                item_store = self.app.item_store
                world = self.app.store.bundled_worlds[active_world.world_name].world
                result = await active_world.take_action(action, world, item_store)

                # Do a tick of the world
                # This is when enemies move, etc
                tick_results = await active_world.do_tick(world, item_store)

                embed = discord.Embed()

                # Tell the user what they did
                embed = result.mutate_embed(embed, item_store)

                # Tell the user what happened during the tick
                for result in tick_results:
                    embed = result.mutate_embed(embed)

                if len(embed.fields) > 0:
                    await reaction.message.channel.send(embed=embed)

                # Re-render
                await self.do_render(reaction.message.channel, user.id)


def setup(client):
    client.add_cog(Play(client))
