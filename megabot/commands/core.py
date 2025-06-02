import logging
import discord

from discord.ext import commands
from megabot.discord import Bot

logger = logging.getLogger(__package__)


class Core(commands.Cog):
    def __init__(self, bot:Bot ) -> None:
        self.bot = bot
        logger.info("Core module enabled")

    @commands.command(name="hello")
    async def hello(self, ctx, *, member:discord.Member = None):
        member = member or ctx.author
        msg = f"Hello, {member.name}"

        await ctx.send(msg)
        logger.debug(f"Send: {msg}")

    @commands.command(name="id")
    async def id(self, ctx, *, member:discord.Member = None):
        member = member or ctx.author
        msg = f"{member.id}"

        await ctx.send(msg)
        logger.debug(f"Send: {msg}")

async def setup(bot:Bot):
   await bot.add_cog(Core(bot))
