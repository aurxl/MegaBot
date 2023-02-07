import requests
import json

def room_create(api_key: str = "", url: str = ""):
    header1= {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    r = requests.post("https://api.w2g.tv/rooms/create.json",
                        headers = header1,
                        data =json.dumps(
                                {"w2g_api_key": api_key,
                                "share": "{}".format(url),}
                                        )
                      )

    x = json.loads(r.text)
    return f'https://w2g.tv/rooms/{x["streamkey"]}'
