import logging

from discord.ext import commands
from discord import Member
from megabot.megabot import MegaBot

logger = logging.getLogger(__package__)


class Core(commands.Cog):
    def __init__(self, bot:MegaBot ) -> None:
        self.bot = bot

        logger.info("Core module enabled")

    @commands.command(name="hello")
    async def hello(self, ctx, *, member:Member = None):
        """Says Hello {member}"""
        member = member or ctx.author
        msg = f"Hello, {member.global_name}"

        await ctx.send(msg)
        logger.debug(f"Send: {msg} to {ctx.author.global_name}")

    @commands.command(name="id")
    async def id(self, ctx, *, member:Member = None):
        """Shows your/others ID """
        member = member or ctx.author
        msg = f"{member.id}"

        await ctx.send(msg)
        logger.debug(f"Send: {msg} to {ctx.author.global_name}")

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Shows Bot latency"""
        msg = f"My latency: {round(self.bot.latency * 1000)}ms"

        await ctx.send(msg)
        logger.debug(f"Send: {msg} to {ctx.author.global_name}")


async def setup(bot:MegaBot):
   await bot.add_cog(Core(bot))
