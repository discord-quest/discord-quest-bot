from discord.ext import commands
from DQBot.action import Action, Direction
from DQBot.models import ActiveWorld, Player
from DQBot.models.entities import ENTITY_RELATIONSHIPS
from DQBot.tick import TickResultType
import discord

# TODO
NUMBER_EMOJIS = {
    1: u"\U00000031\U000020E3",
    2: u"\U00000032\U000020E3",
    3: "\U00000033\U000020E3",
    4: "\U00000034\U000020E3",
    5: "\U00000035\U000020E3",
}


class Play(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.app = client.app
        self.awaiting_response = {}
        self.new_world_awaiting_response = {}

    @commands.command()
    async def play(self, ctx):
        user_id = ctx.author.id

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
            player = await Player.filter(discord_id=user_id).first()

            if player == None:
                player = Player(discord_id=user_id)
                await player.save()
                # TODO: Onboarding?

            if player != None:
                await self.do_choose_dungeon(ctx)

            else:
                await ctx.send("Couldn't register you as a player.")
        else:
            await self.do_render(ctx.channel, user_id, active_world)

    async def do_choose_dungeon(self, ctx):
        available_worlds = self.app.store.bundled_worlds
        embed = discord.Embed(title="Choose a dungeon:")

        number = 1
        for world in list(available_worlds.values())[:5]:
            embed.add_field(
                name=("%s %s" % (NUMBER_EMOJIS[number], world.friendly_name)),
                value=("%s (%s)" % (world.description, world.difficulty)),
            )
            number += 1

        msg = await ctx.send(embed=embed)

        self.new_world_awaiting_response[msg.id] = ctx.author.id
        for i in range(1, number):
            await msg.add_reaction(NUMBER_EMOJIS[i])

    async def do_render(self, channel, user_id, active_world):
        # Add to render queue & send embed
        url = self.app.server.add_to_queue(active_world)

        # It seems like embeds require a domain name and so dont work with localhost images
        embed = discord.Embed(content="Your world:")
        embed.set_image(url=url)

        msg = await channel.send(embed=embed)

        self.awaiting_response[msg.id] = user_id

        # Add reactions for actions
        world = self.app.store.bundled_worlds[active_world.world_name].world
        for action in await active_world.possible_actions(world, self.app.item_store):
            await msg.add_reaction(action.to_reaction())

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # if this is a message we care about
        message_id = reaction.message.id
        if message_id in self.awaiting_response:
            users = await reaction.users().flatten()

            if (
                reaction.count >= 2
                and self.client.user in users
                and self.awaiting_response[reaction.message.id] in [u.id for u in users]
            ):
                await self.handle_action(reaction, user)
                del self.awaiting_response[message_id]
        elif message_id in self.new_world_awaiting_response:
            users = await reaction.users().flatten()
            if (
                reaction.count >= 2
                and self.client.user in users
                and self.new_world_awaiting_response[reaction.message.id]
                in [u.id for u in users]
            ):
                await self.handle_action_new_world(reaction, user)

                del self.new_world_awaiting_response[message_id]

    async def handle_action_new_world(self, reaction, user):
        if not isinstance(reaction.emoji, str):
            return

        # get the targeted world
        index = (
            next(key for key, value in NUMBER_EMOJIS.items() if value == reaction.emoji)
            - 1
        )
        bundled_world = list(self.app.store.bundled_worlds.values())[index]

        # get the db player
        player = await Player.filter(discord_id=user.id).first()

        # make a new active world for them
        active_world = await bundled_world.create_for(player)

        # render
        await self.do_render(reaction.message.channel, user.id, active_world)

    async def handle_action(self, reaction, user):
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
            did_conclude = False
            for result in tick_results:
                if result.type == TickResultType.CONCLUDE:
                    did_conclude = True

                embed = result.mutate_embed(embed)

            if len(embed.fields) > 0:
                await reaction.message.channel.send(embed=embed)

            if did_conclude:
                # Default delete isn't recursive for some reason
                await active_world.player_entity.delete()
                for entity in await active_world.all_entities_with():
                    await entity.delete()
                await active_world.delete()
            else:
                # Re-render
                await self.do_render(reaction.message.channel, user.id, active_world)


def setup(client):
    client.add_cog(Play(client))
