import asyncio
import logging

from discord.ext import commands, tasks
from discord import Activity, ActivityType
from megabot.settings import settings
from megabot.megabot import MegaBot
from megabot.modules.adapters.song import Song
from textwrap import dedent

logger = logging.getLogger(__package__)

class Music(commands.Cog):
    """

    """
    def __init__(self, bot:MegaBot ) -> None:
        self.bot = bot
        self.song_queue = []
        self.current_song = None
        self.is_pause = False

        self.default_status_str = settings.megabot.default_status
        self._update_activity.start()

        logger.info("Music module enabled")

    @staticmethod
    async def send_playing_message(ctx, song:Song, stream:bool=False) -> None:
        h = int(song.duration) // 3600
        m = (int(song.duration) % 3600) // 60
        s = (int(song.duration) % 3600) % 60

        message = f"""\
        **{"Playing" if not stream else "Streaming"}**: `{song.title}`

        Channel: {song.channel}
        Duration: {str(h)+':' if h>0 else ""}{m:02}:{s:02}

        ```
        {song.url}
        ```
        """

        await ctx.send(dedent(message))

    async def unload(self):
        self._update_activity.cancel()

    @tasks.loop(seconds=10)
    async def _update_activity(self):
        if self.current_song and not self.is_pause:
            return await self.__set_listening_activity(title=self.current_song.title)
        await MegaBot.set_default_activity(self.bot)

    async def __housekeeping(self, ctx, song):
        if self.song_queue and self.song_queue[0] == song:
            del self.song_queue[0]

        await asyncio.sleep(song.duration)

        if self.song_queue:
            await self.play(ctx, self.song_queue[0])

    async def __set_listening_activity(self, title):
        status = Activity(type=ActivityType.listening, name=title)
        await self.bot.change_presence(activity=status)

    async def play(self, ctx, song: Song|str = "", stream=False):
        """Playing music from YT"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to play {song}")

        if voice_client is None:
            join_command = self.bot.get_command("join")
            voice_client = await ctx.invoke(join_command)

        if not song:
            if not self.song_queue:
                return await ctx.send("Nothing to play, queue is empty")
            song = self.song_queue[0]

        if not isinstance(song, Song):
            song = Song(content=song, loop=self.bot.loop, stream=stream)

        # Call stop after song object created, so music is still played, while new sing infos are fetched
        if voice_client.is_playing():
            stop_command = self.bot.get_command("stop")
            await ctx.invoke(stop_command)

        self.is_pause = False
        self.current_song = song

        async with ctx.typing():
            player = await song.player()
            voice_client.play(player)

        await self._update_activity()
        await self.send_playing_message(ctx, song=song, stream=stream)
        logger.info(f"{"Playing" if not stream else "Streaming"}: {song.title}")

        await self.__housekeeping(ctx, song)

    @commands.command(name="cacheplay", aliases=["cplay"])
    async def cacheplay(self, ctx, *, request: str = "") -> None:
        """{song} Plays song from YT (will be downloaded) OR Skips to next song if no song given"""
        await self.play(ctx=ctx, song=request)

    @commands.command(name="streamplay", aliases=["stream", "splay", "play"])
    async def streamplay(self, ctx, *, request: str = ""):
        """{song} Streams song from YT OR Skips to next song if no song given"""
        await self.play(ctx=ctx, song=request, stream=True)

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx, *, request: str = ""):
        """{song} Adding song to queue OR Shows current queue if no song given"""
        if not request:
            songs = [song.title for song in self.song_queue]
            return await ctx.send(f"Current queue:\n - {"\n - ".join(songs) if songs else "{empty}"}")
        self.song_queue.append(Song(content=request, loop=self.bot.loop, stream=True))
        logger.debug(f"Added a request to queue {request}")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Skips current played song from queue"""
        if not self.song_queue:
            return await ctx.send("Queue is empty")

        ctx.voice_client.stop()
        await self.play(ctx=ctx)

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stops current played audio"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to stop playing")

        if voice_client is None or not voice_client.is_playing():
            return await ctx.send("Nothing to stop from playing")

        self.current_song = None
        await self._update_activity()
        voice_client.stop()

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pauses current played audio"""
        voice_client = ctx.voice_client

        logger.debug(f"{ctx.author.name} requested to pause playing")

        if voice_client is None or not voice_client.is_playing():
            return await ctx.send(f"Nothing to pause from playing")

        self.is_pause = True
        await self._update_activity()
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

        self.is_pause = False
        await self._update_activity()
        voice_client.resume()

async def setup(bot:MegaBot):
   await bot.add_cog(Music(bot))
