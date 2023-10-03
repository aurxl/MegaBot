#!/usr/bin/env python
import json
import requests


class w2g:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.stream_key = ""
        self.room_link = ""
        self.bg_color = "#232929"
        self.bg_opacity = "90"

    def create_room(self, url: str, bg_color: str = "", bg_opacity: str = "") -> str | str:
        if bg_color != "":
            self.bg_color = bg_color
        if bg_opacity != "":
            self.bg_opacity = bg_opacity

        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.post("https://api.w2g.tv/rooms/create.json",
                                headers=header,
                                data=json.dumps({
                                    "w2g_api_key": self.api_key,
                                    "share": f"{url}",
                                    "bg_color": self.bg_color,
                                    "bg_opacity": self.bg_opacity
                                    }
                                )
                                )
        except Exception as exc:
            raise Exception('failed post request') from exc

        response = json.loads(req.text)

        self.stream_key = response["streamkey"]
        self.room_link = f'https://w2g.tv/rooms/{response["streamkey"]}'
        return self.room_link, self.stream_key

    def update_room(self, url: str) -> bool:
        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.post(f'https://api.w2g.tv/rooms/{self.stream_key}/sync_update',
                                headers=header,
                                data=json.dumps({
                                    "w2g_api_key": self.api_key,
                                    "item_url": f"{url}"
                                    }
                                )
                                )
            return req
        except Exception as exc:
            raise Exception('failed post request') from exc
