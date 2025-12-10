from enum import IntEnum
import os
from elevenlabs import ElevenLabs
from openai import OpenAI
import obsws_python as obs
from dotenv import load_dotenv

from core.characters import *

#region SECRETS
load_dotenv()
TW_OAUTH = os.getenv("TW_OAUTH")
TW_DISPLAY_NAME = os.getenv("TW_DISPLAY_NAME")
TW_CHANNEL_NAME = os.getenv("TW_CHANNEL_NAME")
TW_CLIENT_ID = os.getenv("TW_CLIENT_ID")
TW_CLIENT_SECRET = os.getenv("TW_CLIENT_SECRET")
TW_TOKEN = os.getenv("TW_TOKEN")
TW_BROADCASTER_ID = os.getenv("TW_BROADCASTER_ID")
TW_MODERATOR_ID = os.getenv("TW_MODERATOR_ID")

YT_CLIENT_ID = os.getenv("YT_CLIENT_ID")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")
YT_TOKEN = os.getenv("YT_TOKEN")
YT_LIVE_CHAT_ID = os.getenv("YT_LIVE_CHAT_ID")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
#endregion

#region REGULAR
# clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
req = obs.ReqClient(host="localhost", port=4455)

# obs general audio movement
LEVELTYPE = IntEnum("LEVELTYPE", "VU POSTFADER PREFADER", start=0)
DEVICE = "TTS Output"
HOLD_TIME = 20 # max amount of ticks to keep image and text visible after db reaches 0
MOVEMENT_STRENGTH = 50

ENABLE_COMBO = False
COMBO_TRIGGER_COUNT = 2
COMBO_WINDOW_SECONDS = 10

# commands
DEBUG_COOLDOWN = True
SAY_CHARACTER = CHAT
DEFAULT_REACT_CHARACTER = SKELETON

# elevenlabs
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# obs sources
SCENE = "Overlay"

# chat history
CHAT_HISTORY_LIMIT = 20

# idle chatter
ENABLE_IDLE_CHATTER = True
#IDLE_CHARACTER = 
#IDLE_RESET_BY_REACT = 
MIN_IDLE_TIME = 300
MAX_IDLE_TIME = 600
IDLE_RECORD_TIME = 15
IDLE_MESSAGES = [
    "ramble about what you see.",
    "scream loudly.",
    "drop unhinged lore.",
    "comment on current chat conversation.",
    "talk about your current emotional state."
]
#endregion