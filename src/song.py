#!/usr/bin/env python
import yt_dlp


class song:
    def __init__(self, content: str = None):
        if not content:
            raise Exception('title or link required')

        self.infos = {}
        self.url = ""
        self.stream_url = ""
        self.title = ""
        self.duration = ""
        self.thumbnail = ""
        self.valid = False
        self.ytdl_options = {
            "format": "bestaudio/best",
            "default_search": "auto",
            "noplaylist": True,
            "title": True
        }
        self.get_infos(content)

    def get_infos(self, content: str):
        content = self.check_url(content)

        try:
            with yt_dlp.YoutubeDL(self.ytdl_options) as ydl:
                infos = ydl.extract_info(content, download=False)
        except Exception as exc:
            raise Exception(f"couldnt find {content}") from exc

        self.infos = ydl.sanitize_info(infos)
        self.url = self.infos["entries"][0]["original_url"]
        self.stream_url = infos.get('url')
        self.title = infos.get('title')
        self.duration = infos.get('duration')
        self.thumbnail = infos.get('thumbnail')

    def check_url(self, probe: str):
        if probe.startswith(("https://", "http://")) and "www.youtube.com/watch?" in probe:
            return probe
        elif probe.startswith("www.youtube.com/watch?"):
            return "https://" + probe
        return probe
