import logging
from typing import Optional

from discord.ext import commands
from discord import Member
from megabot.megabot import MegaBot

logger = logging.getLogger(__package__)


class Core(commands.Cog):
    def __init__(self, bot:MegaBot ) -> None:
        self.bot: MegaBot = bot

        logger.info("Core module enabled")

    @commands.command(name="hello")
    async def hello(self, ctx, *, member:Optional[Member] = None):
        """Says Hello {member}"""
        member = member or ctx.author
        msg: str = f"Hello, {member.global_name}"

        await ctx.send(msg)

    @commands.command(name="id")
    async def id(self, ctx, *, member:Optional[Member] = None):
        """Shows your/others ID """
        member = member or ctx.author
        msg: str = f"{member.id}"

        await ctx.send(msg)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Shows Bot latency"""
        msg: str = f"My latency: {round(self.bot.latency * 1000)}ms"

        await ctx.send(msg)


async def setup(bot:MegaBot):
   await bot.add_cog(Core(bot))
