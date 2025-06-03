import logging

from discord import FFmpegOpusAudio
from discord.ext import commands
from megabot.discord import Bot
from megabot.modules.adapters.song import Song

logger = logging.getLogger(__package__)

class Music(commands.Cog):
    def __init__(self, bot:Bot ) -> None:
        self.bot = bot
        self.song_queue = []

        logger.info("Music module enabled")


    async def __add_to_queue(self, song:Song) -> None:
        self.song_queue.append(song)

    async def __skip_song(self) -> None:
        del self.song_queue[0]

    @commands.command(name="play")
    async def play(self, ctx, *, request:str):
        """Plays music"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to play {request}")

        if voice_client is None:
            join_command = self.bot.get_command("join")
            voice_client = await ctx.invoke(join_command)

        song = Song(content=request)
        song_queue = [song]
        song_queue.extend(self.song_queue)
        self.song_queue = song_queue

        song.download()
        await ctx.send(f"Playing: {song.title}")
        file = f"{song.download_path}/{song.filename}"
        voice_client.play(FFmpegOpusAudio(file))

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stops current played audio"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to stop playing")

        if voice_client is None or not voice_client.is_playing():
            return await ctx.send(f"Nothing to stop from playing")

        voice_client.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pauses current played audio"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to pause playing")

        if voice_client is None or not voice_client.is_playing():
            return await ctx.send(f"Nothing to pause from playing")

        voice_client.pause()

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Resumes current played audio"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to resume playing")

        if voice_client is None:
            return await ctx.send(f"Nothing to resume to play")

        if voice_client.is_playing():
            return await ctx.send(f"Already playing, can't resume")

        voice_client.resume()


async def setup(bot):
   await bot.add_cog(Music(bot))
