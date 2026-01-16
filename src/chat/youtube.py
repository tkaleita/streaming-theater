import asyncio
import time
import requests
import aiohttp

from chat import router
from core.config import *

access_token = ""
access_token_expires_at = 0

access_token_bot = ""
access_token_bot_expires_at = 0

chat_id = ""

async def youtube_listener():
    global chat_id

    url = "https://youtube.googleapis.com/youtube/v3/liveChat/messages"
    next_page_token = None
    first_run = True  # Flag to skip the backlog

    print("YouTube listener running")

    async with aiohttp.ClientSession() as session:
        while True:
            if not chat_id:
                get_chat_id()
                if chat_id == None:
                    print("YouTube Chat ID not found. Retrying in 5s...")
                    await asyncio.sleep(5)
                    continue
                print(f"YouTube Chat ID found: {chat_id}")

            params = {
                "liveChatId": chat_id,
                "part": "id,snippet,authorDetails",
                "maxResults": 200,
            }
            if next_page_token:
                params["pageToken"] = next_page_token

            headers = get_youtube_headers()

            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status != 200:
                    print("YouTube API error:", await resp.text())
                    await asyncio.sleep(5)
                    continue

                r = await resp.json()
            next_page_token = r.get("nextPageToken")
            poll_ms = r.get("pollingIntervalMillis", 1200)

            if first_run:
                print("Skipping chat backlog...")
                first_run = False
                await asyncio.sleep(poll_ms / 1000)
                continue

            # Process chat messages
            for item in r.get("items", []):
                msg = item["snippet"]["displayMessage"]
                user = item["authorDetails"]["displayName"]
                await router.handle_message(user, msg, "youtube")

            await asyncio.sleep(poll_ms / 1000)#

def send_message(message):
    global chat_id

    url = "https://www.googleapis.com/youtube/v3/liveChat/messages"

    headers = {
        "Authorization": f"Bearer {get_access_token(for_bot=True)}",
        "Content-Type": "application/json",
    }

    params = {
        "part": "snippet"
    }

    payload = {
        "snippet": {
            "liveChatId": get_chat_id(),
            "type": "textMessageEvent",
            "textMessageDetails": {
                "messageText": message
            }
        }
    }

    r = requests.post(
        url,
        params=params,
        headers=headers,
        json=payload,
        timeout=10,
    )

    if r.status_code != 200:
        raise RuntimeError(
            f"YouTube chat send failed: {r.status_code} {r.text}"
        )
    return r.json()

def get_youtube_headers():
    token = get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

def get_chat_id(force_refresh = False):
    global chat_id
    
    if not force_refresh and chat_id != "":
        return chat_id

    url = "https://www.googleapis.com/youtube/v3/liveBroadcasts"

    params = {
        "part": "snippet,status",
        "mine": "true",
        "maxResults": 5,
    }

    headers = get_youtube_headers()
    r = requests.get(url, params=params, headers=headers, timeout=10)

    if r.status_code != 200:
        print("Failed to fetch live broadcasts:", r.text)
        return None

    data = r.json()

    for item in data.get("items", []):
        status = item["status"]["lifeCycleStatus"]
        local_chat_id = item["snippet"].get("liveChatId")

        # This is the ONLY valid state for chat polling
        if status == "live" and local_chat_id:
            chat_id = local_chat_id
            print(f"stream found with title: {item["snippet"].get("title")}")
            return chat_id

    return None

def get_access_token(force_refresh = False, for_bot = False):
    global access_token, access_token_expires_at, access_token_bot, access_token_bot_expires_at

    # check if expired
    now = time.time()
    if for_bot:
        if (not force_refresh and access_token_bot and now < access_token_bot_expires_at - 30):
            return access_token_bot
    else:
        if (not force_refresh and access_token and now < access_token_expires_at - 30):
            return access_token

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": YT_CLIENT_ID,
        "client_secret": YT_CLIENT_SECRET,
        "refresh_token": YT_REFRESH_TOKEN_BOT if for_bot else YT_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }
    
    response = requests.post(token_url, data=data, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to refresh access token: "
            f"{response.status_code} {response.text}"
        )

    token_data = response.json()
    new_token = token_data["access_token"]
    expires_at = time.time() + token_data.get("expires_in", 3600)

    if for_bot:
        access_token_bot = new_token
        access_token_bot_expires_at = expires_at
    else:
        access_token = new_token
        access_token_expires_at = expires_at
    return new_token