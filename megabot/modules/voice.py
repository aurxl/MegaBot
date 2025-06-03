import logging
from typing import Optional
import discord

from discord.ext import commands
from megabot.discord import Bot

logger = logging.getLogger(__package__)

class Voice(commands.Cog):
    def __init__(self, bot:Bot ) -> None:
        self.bot = bot
        self.song_queue = []

        logger.info("Voice module enabled")

    @commands.command(name="join")
    async def join(self, ctx, *, channel: str = ""):
        """Joins a voice channel"""

        if not ctx.message.author.voice and not channel:
            logger.debug("No channel available to join")
            return await ctx.send("There is no Channel to join to")

        if not channel:
            channel = ctx.message.author.voice.channel
        else:
            for c in ctx.guild.voice_channels:
                if channel.lower() == c.name.lower():
                    channel = c
                    break
            else:
                logger.debug(f"Requested channel {channel} not found")
                return await ctx.send(f"There is no channel {channel}")

        logger.debug(f"{ctx.author.name} requested to join into channel {channel.name}")
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command(name="leave")
    async def leave(self, ctx):
        """Leaves current voice channel"""

        logger.debug(f"{ctx.author.name} requested to leave channel {ctx.voice_client.channel.name}")

        if ctx.voice_client is not None:
            return await ctx.voice_client.disconnect()
        await ctx.send("There is no channel to leave")

async def setup(bot):
   await bot.add_cog(Voice(bot))
