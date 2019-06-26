import discord
import discord.ext.commands as commands

class Quest(commands.Cog):
	def __init__(self, bot, app):
		self.bot = bot
		self.app = app

	@commands.command()
	async def hello(self, ctx, *, member: discord.Member = None):
		await ctx.send("Hello, World!")