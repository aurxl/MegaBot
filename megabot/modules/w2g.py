import logging
from typing import Optional

from discord.ext import commands
from discord import Member
from megabot.megabot import MegaBot
from megabot.settings import settings
from megabot.modules.adapters.w2g import WatchToGether

logger = logging.getLogger(__package__)


class W2G(commands.Cog):
    def __init__(self, bot:MegaBot ) -> None:
        self.bot: MegaBot = bot
        self.api_token: str = settings.modules.w2g.token

        logger.info("W2G module enabled")

    @commands.command(name="w2g")
    async def w2g(self, ctx, *, init_url:str = ""):
        """{url} Creats a w2g room from given url OR empty room if no url given"""
        room: WatchToGether = WatchToGether(self.api_token)
        url: str = room.create_room(url=init_url)
        await ctx.send(url)


async def setup(bot:MegaBot) -> None:
   await bot.add_cog(W2G(bot))
