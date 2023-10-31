#!/usr/bin/env python
import json
import requests


class w2g:
    """ wg class.

    w2g class is responsible for creating rooms, customize and updating them.
    One created object is responsible for one room. Stream Key and custom
    settings are stored in that object. Therefore multiple objects can be
    created and later be referred for updating them.

    A w2g object MUST be created by providing an API Key. Once the Object is
    created only ONE room can be held. Either create a room at the beginning,
    or create a new room later with the same object. Note that in this case
    you can only refer to the prevoius room if you saved the stream_key.

    By updating a room, the given video will be played immediately.

    Params:
    api_key -- YOUR w2g API Key

    Attributes:
    stream_key  -- set when creating a room, needed to interact later on
    room_link   -- the room link to share
    bg_color    -- optioanl option, sets background color when creating a room
    bg_opacity  -- optional option, sets background opacity when creating a room
    """

    def __init__(self, api_key: str):
        """initialize object attributes"""

        self.api_key = api_key
        self.stream_key = ""
        self.room_link = ""
        self.bg_color = "#232929"
        self.bg_opacity = "90"

    def create_room(self, url: str, bg_color: str = "", bg_opacity: str = "") -> str | str:
        """ creating w2g room

        params:
        url         -- valid youtube url/ share link
        bg_color    -- if not already set, sets background color in room
        bg_opacity  -- if not already set, sets background opacity

        return:
        self.room_link, self.stream_key -- in this func gathered
                                           and set object attributes
                                           (described in class docstring)
        """

        if bg_color != "":
            self.bg_color = bg_color
        if bg_opacity != "":
            self.bg_opacity = bg_opacity

        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.post(
                "https://api.w2g.tv/rooms/create.json",
                headers=header,
                data=json.dumps(
                    {
                        "w2g_api_key": self.api_key,
                        "share": f"{url}",
                        "bg_color": self.bg_color,
                        "bg_opacity": self.bg_opacity
                    }
                ),
                timeout=3
            )
        except Exception as exc:
            raise Exception('failed post request') from exc
        print(req.json())
        response = req.json()

        self.stream_key = response["streamkey"]
        self.room_link = f'https://w2g.tv/rooms/{response["streamkey"]}'
        return self.room_link, self.stream_key

    def update_room(self, url: str) -> bool:
        """ update currently playing video

        params:
        url -- valid youtube url/ share link

        return:
        bool -- True if server response is ok
        """

        header = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.post(
                f'https://api.w2g.tv/rooms/{self.stream_key}/sync_update',
                headers=header,
                data=json.dumps({
                    "w2g_api_key": self.api_key,
                    "item_url": f"{url}"
                }),
                timeout=3
            )
            if req.ok:
                return True
        except Exception as exc:
            raise Exception('failed post request') from exc
