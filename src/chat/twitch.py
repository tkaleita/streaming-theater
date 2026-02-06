import re
import requests
import websockets
from chat import router
from core.config import *

async def twitch_listener():
    uri = "wss://irc-ws.chat.twitch.tv:443"

    async with websockets.connect(uri) as ws:
        print("Connected to Twitch IRC")

        await ws.send("CAP REQ :twitch.tv/tags")
        await ws.send(f"PASS {TW_OAUTH}")
        await ws.send(f"NICK {TW_DISPLAY_NAME}")
        await ws.send(f"JOIN #{TW_CHANNEL_NAME}")

        async for raw in ws:
            raw = raw.strip()

            # no idea lol, acks i guess?
            if raw.startswith("PING"):
                await ws.send("PONG :tmi.twitch.tv")
                continue

            # only actual chat messages
            if "PRIVMSG" not in raw:
                continue
            
            # message normalization
            try:
                _, rest = raw.split(" ", 1)
                prefix, message = rest.split("PRIVMSG", 1)
                user = prefix.split("!", 1)[0][1:]
                msg = message.split(":", 1)[1].strip()
            except Exception:
                continue
            
            await router.handle_message(user, msg)
    
def refresh_token():
    global TW_TOKEN, TW_REFRESH
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": TW_REFRESH,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(url, data=data).json()
    TW_TOKEN = r['access_token']
    TW_REFRESH = r['refresh_token'] # Refresh tokens can change too!
    print("Token refreshed successfully!")

def send_message(message):
    url = "https://api.twitch.tv/helix/chat/messages"
    headers = {
        "Client-ID": TW_CLIENT_ID,
        "Authorization": f"Bearer {TW_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "sender_id": TW_MODERATOR_ID,
        "broadcaster_id": TW_BROADCASTER_ID,
        "moderator_id": TW_MODERATOR_ID,
        "message": message
    }

    r = requests.post(url, headers=headers, json=data).json()
    print(r)
    return r["data"][0]["message_id"]

def delete_message(message_id):
    url = (
        "https://api.twitch.tv/helix/moderation/chat"
        f"?broadcaster_id={TW_BROADCASTER_ID}"
        f"&moderator_id={TW_MODERATOR_ID}"
        f"&message_id={message_id}"
    )
    headers = {
        "Client-ID": TW_CLIENT_ID,
        "Authorization": f"Bearer {TW_TOKEN}"
    }

    r = requests.delete(url, headers=headers)

    if r.status_code == 204:
        print(f"🗑️ Deleted message {message_id}")
    else:
        print("❌ Delete failed:", r.text)

def normalize(msg: str) -> str:
    msg = msg.lower().strip()
    msg = re.sub(r"\s+", " ", msg)
    msg = re.sub(r"[^\w\s]", "", msg)
    return msg

def deduct_points(user, cost, command):
    remove_cmd = f"!removepoints {user} {cost}"
    msg_id = send_message(remove_cmd)
    delete_message(msg_id)
    print(f"Charged {cost} points from {user}")