
from chat import twitch, youtube

async def send_message(dest, msg: str):
    if dest == "youtube":
        msg = msg.replace("@@", "@") # i dont care anymore
        print(msg)
        youtube.send_message(msg)
    else:
        twitch.send_message(msg)