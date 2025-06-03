#!/usr/bin/env python
import os
import re
import pathlib
import yt_dlp
import asyncio
import discord

from contextlib import chdir
from discord import PCMVolumeTransformer, FFmpegPCMAudio
from megabot.settings import settings


class Song:
    """ song class can hold one song at a time.

    The song or better the audio will be downloaded from YouTube
    using yt-dlp.

    The song object MUST be initialized with a str containing a video
    title or valid YoutTube url. If not given a valid url, the given
    str will be searched on YouTube and an url will be gathered.

    Useful gathered informations are accessible by the class attributes.
    Those informations will be gathered on object initialization.

    Params:
    content: str -- str containing wether valid YT url, or buzzwords
                    that will link to song

    Attributes:
    infos        -- ytdl extract_info json, a LOT of useful infos
    title        -- YT title of found video
    url          -- YT url
    channel      -- channel name
    duration     -- video duration
    stream_url   -- url for googlevideo stream -- COULD be used for
                    playing in channel. Not working now
    channel_url  -- YT channel link
    thumbnail_url -- where to find the thumbnail
    filename     -- the real file name -- will be gathered ON download
    valid        -- if the object is holding a valid song that can be played
    status       -- current status -- useful when downloading the audio
    ytdl_options_info     -- ytdl options for gathering all the infos
    ytdl_options_format -- ytdl options for downloading the audio
    """

    def __init__(self, content: str, stream=False, loop=None):
        """ initialize object attributes."""

        self.stream = stream
        self.infos = dict()
        self.title = ""
        self.url = ""
        self.channel = ""
        self.duration = ""
        self.stream_url = ""
        self.channel_url = ""
        self.thumbnail_url = ""
        self.filename = ""
        self.codec = "m4a"
        self.download_path = pathlib.Path(settings.player.mediapath).resolve()
        self.valid = False
        self.status = "nothing"
        self.ytdl_options_info = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        }
        self.ytdl_format_options_download = {
            "format": "bestaudio/best",
            'restrictfilenames': True,
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.codec,
            }]
        }
        self.ytdl_format_options_stream = {
            "format": "bestaudio/best",
            'restrictfilenames': True,
            "noplaylist": True,
        }
        self.ffmpeg_options = {
            "options": "-vn  -acodec copy",
            "before_options": "-allowed_extensions ALL"
        }
        self.get_infos(content)

    async def play(self):
        source = self.stream_url
        if not self.stream:
            source = str(pathlib.Path(f"{self.download_path}/{self.download()}").resolve())
        return discord.FFmpegPCMAudio(source, **self.ffmpeg_options)

    def get_infos(self, content: str) -> None:
        """ gathering song/ audio file infos

        Always be called on object initialization to set object atributes.

        Params:
        content: str -- passed from class param
        """

        is_url = True
        if not self.check_url(content):
            is_url = False
        else:
            content = self.check_url(content)

        try:
            with yt_dlp.YoutubeDL(self.ytdl_options_info) as ydl:
                infos = ydl.extract_info(content, download=False)
            self.valid = True
        except Exception as exc:
            raise Exception(f"Couldn't find {content}") from exc

        self.infos = ydl.sanitize_info(infos)
        if not is_url:
            self.infos = self.infos["entries"][0]

        self.title = self.infos["fulltitle"]
        self.url = self.infos["original_url"]
        self.channel = self.infos["channel"]
        self.duration = self.infos["duration"]
        self.stream_url = self.infos["url"]
        self.channel_url = self.infos["channel_url"]
        self.thumbnail_url = self.infos["thumbnail"]

    def reload_infos(self) -> bool:
        """regather infos

        Return:
        True if successful
        """

        try:
            self.get_infos(self.url)
            return True
        except Exception as exc:
            raise Exception(f"cant reload infos ({self.url})") from exc

    @staticmethod
    def check_url(probe: str) -> str:
        """ checking if given str is YT link

        Params:
        probe: str -- str to check

        Return:
        str       -- if valid
        empty str -- if not valid
        """

        if probe.startswith(("https://", "http://")) and ("www.youtube.com/watch?" in probe or "youtu.be/" in probe):
            return probe
        if probe.startswith("www.youtube.com/watch?"):
            return "https://" + probe
        return ""

    def download(self, directory: str = None) -> str:
        """ downloading audio file

        When given dir is present, chdir to it and download it there.
        If not present, it will be created.

        Params:
        directory: str -- optional download path

        Return:
        str: -- real filename if download successful
        """

        if directory:
            self.download_path = directory

        if not os.path.exists(self.download_path):
            try:
                os.mkdir(self.download_path)
            except FileExistsError:
                pass
            except FileNotFoundError as err:
                raise Exception(f"cant create dir {self.download_path}") from err
            except Exception as err:
                raise Exception(f"cant create dir {self.download_path}") from err

        try:
            with chdir(self.download_path):
                try:
                    with yt_dlp.YoutubeDL(self.ytdl_format_options_download) as ydl:
                        result = ydl.extract_info(self.url, download=True)
                    self.filename = self.__prepare_filename(ydl.prepare_filename(result))
                except Exception as exc:
                    raise Exception(f"failed downloading {self.url}") from exc
        except Exception as exc:
            raise Exception(f"cant go to dir {self.download_path}") from exc

        return self.filename

    def __prepare_filename(self, file_name) -> str:
        base_name = re.match(r'(.*)\.[^.]+$', file_name).group(1)
        return f"{base_name}.{self.codec}"

    def progress_hook(self, d) -> None:
        """ ytdl download progress

        provided by yt_dlp. Current status will be stored in self.status.

        Params:
        progress hook object
        """

        if d['status'] == "downloading":
            self.status = f"Downloading {self.title}"
        elif d['status'] == "finished":
            self.status = "finished downlaod"
