import asyncio
import requests

from chat import router
from core.config import *

async def youtube_listener():
    url = "https://youtube.googleapis.com/youtube/v3/liveChat/messages"
    next_page_token = None

    print("📺 YouTube listener running")

    while True:
        params = {
            "liveChatId": YT_LIVE_CHAT_ID,
            "part": "id,snippet,authorDetails",
        }
        if next_page_token:
            params["pageToken"] = next_page_token

        r = requests.get(url, params=params, headers=get_youtube_headers()).json()

        # How long YouTube tells us to wait
        poll_ms = r.get("pollingIntervalMillis", 1200)

        next_page_token = r.get("nextPageToken")

        # Process chat messages
        for item in r.get("items", []):
            msg = item["snippet"]["displayMessage"]
            user = item["authorDetails"]["displayName"]

            await router.handle_message(user, msg)

        await asyncio.sleep(poll_ms / 1000)#

def get_youtube_headers():
    token = YT_TOKEN
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

def get_live_chat_id():
    url = "https://www.googleapis.com/youtube/v3/liveBroadcasts"
    params = {
        "part": "snippet",
        "mine": True
    }

    headers = get_youtube_headers()
    r = requests.get(url, params=params, headers=headers).json()

    items = r.get("items", [])
    if not items:
        print("❌ No active YouTube livestream found!")
        return None

    # Extract liveChatId
    return items[0]["snippet"]["liveChatId"]