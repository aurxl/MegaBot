import logging

from discord.ext import commands
from megabot.discord import Bot
from megabot.modules.adapters.song import Song

logger = logging.getLogger(__package__)

class Music(commands.Cog):
    def __init__(self, bot:Bot ) -> None:
        self.bot = bot
        self.song_queue = []

        logger.info("Music module enabled")

    @commands.command(name="play")
    async def play(self, ctx, *, request:str):
        """Plays music"""

        song = Song(content=request)
        song_queue = [song]
        song_queue.extend(self.song_queue)
        self.song_queue = song_queue

async def setup(bot):
   await bot.add_cog(Music(bot))
