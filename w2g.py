import requests
import json

def room_create(api_key:str) -> str:
    header1= {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    r = requests.post("https://w2g.tv/rooms/create.json",
                        headers = header1,
                        data =json.dumps(
                                {"w2g_api_key": api_key,
                                "share": "https://youtu.be/0fAQhSRLQnM",}
                                        )
                      )

    x = json.loads(r.text)
    return f'https://w2g.tv/rooms/{x["streamkey"]}'
