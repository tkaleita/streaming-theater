from enum import IntEnum
import os
from pathlib import Path
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
YT_REFRESH_TOKEN_BOT = os.getenv("YT_REFRESH_TOKEN_BOT")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
#endregion

#region REGULAR
# clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
req = obs.ReqClient(host="localhost", port=4455)

# data file path
DATA_FILE = Path(__file__).resolve().parent.parent / "data.json"

# obs general audio movement
LEVELTYPE = IntEnum("LEVELTYPE", "VU POSTFADER PREFADER", start=0)
DEVICE = "TTS Output"
HOLD_TIME = 20 # max amount of ticks to keep image and text visible after db reaches 0
MOVEMENT_STRENGTH = 50

# chat combo
COMBO_ENABLE = False # currently bugged
COMBO_TRIGGER_COUNT = 2
COMBO_WINDOW_SECONDS = 10

# director
DIRECTOR_ENABLE = False
DIRECTOR_COOLDOWN = 300
DIRECTOR_CHAT_TIME = 30

# gamer cred
GAMER_CRED_ENABLE = True

# progress
PROGRESS_ENABLE = False

# commands
DEBUG_COOLDOWN = True

SAY_ENABLE = True
SAY_COOLDOWN = 90
SAY_CHARACTER = CHAT

REACT_ENABLE = False
REACT_COOLDOWN = 60
DEFAULT_REACT_CHARACTER = SKELETON

JUMPSCARE_ENABLE = True
JUMPSCARE_COOLDOWN = 90

# elevenlabs
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# obs sources
SCENE = "Overlay"

# chat history
CHAT_HISTORY_LIMIT = 20

# idle chatter
IDLE_CHATTER_ENABLE = False
#IDLE_CHARACTER = 
#IDLE_RESET_ON_REACT = False
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