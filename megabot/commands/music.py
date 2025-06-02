import logging

from discord.ext import commands
from megabot.discord import Bot

logger = logging.getLogger(__package__)

class Music(commands.Cog):
    def __init__(self, bot:Bot ) -> None:
        self.bot = bot
        logger.info("music enabled")


async def setup(bot):
   await bot.add_cog(Music(bot))
