import asyncio
import logging
from typing import Dict, List, Union, Optional

from discord.ext import commands, tasks
from discord import Activity, ActivityType, Guild, VoiceClient
from megabot.settings import settings
from megabot.megabot import MegaBot
from megabot.modules.adapters.song import Song
from textwrap import dedent

logger = logging.getLogger(__package__)


class GuildMusicContext:
    """ Isolating Guilds

    Holding music player states for each guild the bot is connected to.
    This allows isolated Guild states.
    """
    def __init__(self, guild) -> None:
        self.guild:Guild = guild
        self.song_queue:list[Song] = []
        self.current_song:Song = None
        self.is_pause:bool = False


class Music(commands.Cog):
    """
    Handling the music associated commands. Music is actually everything that
    is available on YouTube.
    """
    def __init__(self, bot:MegaBot ) -> None:
        self.bot: MegaBot = bot
        self.default_status_str: str = settings.megabot.default_status

        self.guild_states: Dict[int, GuildMusicContext] = dict()
        for guild in self.bot.guilds:
            self.guild_states[guild.id] = GuildMusicContext(guild)

        logger.info("Music module enabled")

    @staticmethod
    async def send_playing_message(ctx, song:Song, stream:bool=False) -> None:
        """Preparing and sending the now playing message to the chat."""
        h: int = int(song.duration) // 3600
        m: int = (int(song.duration) % 3600) // 60
        s: int = (int(song.duration) % 3600) % 60

        message: str = f"""\
        **{"Playing" if not stream else "Streaming"}**: `{song.title}`

        Channel: {song.channel}
        Duration: {str(h)+':' if h>0 else ""}{m:02}:{s:02}

        ```
        {song.url}
        ```
        """

        await ctx.send(dedent(message))

    async def __housekeeping(self, ctx, song:Song):
        """Keeping everything tidy after playing.

        Assumed to be running after a play was called to remove the song from first queue and
        also start next queue items if there are any.
        """
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]

        if mctx.song_queue and mctx.song_queue[0] == song:
            del mctx.song_queue[0]

        sleep_interval: float = 0.1
        sleeped: float = 0
        to_sleep: float = song.duration
        while sleeped < to_sleep:
            await asyncio.sleep(sleep_interval)
            sleeped += sleep_interval

            if mctx.is_pause:
                to_sleep += sleep_interval

        if mctx.current_song == song:
            mctx.current_song = None

        if mctx.song_queue:
            await self.play(ctx, mctx.song_queue[0])

    async def __set_listening_activity(self, title: str) -> None:
        status: Activity = Activity(type=ActivityType.listening, name=title)
        await self.bot.change_presence(activity=status)

    async def play(self, ctx, song: Union[Song, str] = "", stream: bool = False) -> None:
        """Playing music from YT"""
        voice_client: Optional[VoiceClient] = ctx.voice_client
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]

        logger.debug(f"{ctx.author.name} requested to play {song}")

        if voice_client is None:
            join_command = self.bot.get_command("join")
            voice_client = await ctx.invoke(join_command)

        if not song:
            if not mctx.song_queue:
                return await ctx.send("Nothing to play, queue is empty")
            song = mctx.song_queue[0]

        if not isinstance(song, Song):
            song = Song(content=song, loop=self.bot.loop, stream=stream)

        # Call stop after song object created, so music is still played, while new sing infos are fetched
        if voice_client.is_playing():
            stop_command = self.bot.get_command("stop")
            await ctx.invoke(stop_command)

        mctx.is_pause = False
        mctx.current_song = song

        async with ctx.typing():
            player = await song.player()
            voice_client.play(player)

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
    async def queue(self, ctx, *, request: str = "") -> None:
        """{song} Adding song to queue OR Shows current queue if no song given"""
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]
        if not request:
            songs: List[str] = [song.title for song in mctx.song_queue]
            return await ctx.send(f"Current queue:\n - {"\n - ".join(songs) if songs else "{empty}"}")
        mctx.song_queue.append(Song(content=request, loop=self.bot.loop, stream=True))
        logger.debug(f"Added a request to queue {request}")

    @commands.command(name="skip")
    async def skip(self, ctx) -> None:
        """Skips current played song from queue"""
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]
        if not mctx.song_queue:
            return await ctx.send("Queue is empty")

        ctx.voice_client.stop()
        await self.play(ctx=ctx)

    @commands.command(name="stop")
    async def stop(self, ctx) -> None:
        """Stops current played audio"""
        voice_client: Optional[VoiceClient] = ctx.voice_client
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]

        logger.debug(f"{ctx.author.name} requested to stop playing")

        if voice_client is None or not voice_client.is_playing():
            return await ctx.send("Nothing to stop from playing")

        mctx.current_song = None
        voice_client.stop()

    @commands.command(name="pause")
    async def pause(self, ctx) -> None:
        """Pauses current played audio"""
        voice_client: Optional[VoiceClient] = ctx.voice_client
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]

        logger.debug(f"{ctx.author.name} requested to pause playing")

        if voice_client is None or not voice_client.is_playing():
            return await ctx.send(f"Nothing to pause from playing")

        mctx.is_pause = True
        voice_client.pause()

    @commands.command(name="resume")
    async def resume(self, ctx) -> None:
        """Resumes current played audio"""
        voice_client: Optional[VoiceClient] = ctx.voice_client
        mctx: GuildMusicContext = self.guild_states[ctx.guild.id]

        logger.debug(f"{ctx.author.name} requested to resume playing")

        if voice_client is None:
            return await ctx.send(f"Nothing to resume to play")

        if voice_client.is_playing():
            return await ctx.send(f"Already playing, can't resume")

        mctx.is_pause = False
        voice_client.resume()

async def setup(bot:MegaBot) -> None:
   await bot.add_cog(Music(bot))
