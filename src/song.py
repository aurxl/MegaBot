#!/usr/bin/env python
import yt_dlp
import os
from contextlib import chdir


class song:
    def __init__(self, content: str = None):
        if not content:
            raise Exception('title or link required')

        self.infos = {}
        self.title = ""
        self.url = ""
        self.channel = ""
        self.duration = ""
        self.stream_url = ""
        self.channel_url = ""
        self.thumbnail_url = ""
        self.filename = ""
        self.downlaod_path = "tmp_media"
        self.valid = False
        self.status = "nothing"
        self.ytdl_options_info = {
            "format": "bestaudio/best",
            "default_search": "auto",
            "noplaylist": True,
            "title": True,
        }
        self.ytdl_options_download = {
            "format": "bestaudio/best",
            'restrictfilenames': True,
            "noplaylist": True,
            "progress_hooks": [self.progress_hook],
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }
        self.get_infos(content)

    def get_infos(self, content: str):
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
            raise Exception(f"couldnt find {content}") from exc

        self.infos = ydl.sanitize_info(infos)
        if is_url:
            self.title = self.infos["fulltitle"]
            self.url = self.infos["original_url"]
            self.channel = self.infos['channel']
            self.duration = self.infos['duration']
            self.stream_url = self.infos['url']
            self.channel_url = self.infos['channel_url']
            self.thumbnail_url = self.infos['thumbnail']
        else:
            self.title = self.infos["entries"][0]["fulltitle"]
            self.url = self.infos["entries"][0]["original_url"]
            self.channel = self.infos['entries'][0]['channel']
            self.duration = self.infos['entries'][0]['duration']
            self.stream_url = self.infos['entries'][0]['url']
            self.channel_url = self.infos['entries'][0]['channel_url']
            self.thumbnail_url = self.infos['entries'][0]['thumbnail']

    def check_url(self, probe: str):
        if probe.startswith(("https://", "http://")) and ("www.youtube.com/watch?" in probe or "youtu.be/" in probe):
            return probe
        elif probe.startswith("www.youtube.com/watch?"):
            return "https://" + probe
        return False

    def download(self, directory: str = None):
        if directory:
            self.downlaod_path = directory

        if not os.path.exists(self.downlaod_path):
            try:
                os.mkdir(self.downlaod_path)
            except FileExistsError:
                pass
            except FileNotFoundError as err:
                raise Exception(f"cant create dir {self.downlaod_path}") from err
            except Exception as err:
                raise Exception(f"cant create dir {self.downlaod_path}") from err

        try:
            with chdir(self.downlaod_path):
                try:
                    with yt_dlp.YoutubeDL(self.ytdl_options_download) as ydl:
                        result = ydl.extract_info(self.url, download=True)
                    self.filename = ydl.prepare_filename(result)
                except Exception as exc:
                    raise Exception(f"failed downloading {self.url}") from exc
        except Exception as exc:
            raise Exception(f"cant go to dir {self.downlaod_path}") from exc

        return self.filename

    def progress_hook(self, d):
        if d['status'] == "downloading":
            self.status = f"Downloading {self.title}"
        elif d['status'] == "finished":
            self.status = "finished downlaod"
