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
GAMER_CRED_ENABLE = False

# progress
PROGRESS_ENABLE = False

# commands
DEBUG_COOLDOWN = True  # remove all command cooldown if true

SAY_ENABLE = True
SAY_COOLDOWN = 90
SAY_CHARACTER = CHEF

ASK_ENABLE = True
ASK_COOLDOWN = 60
ASK_DEFAULT_CHAR = ANGRY_CHEF

JUMPSCARE_ENABLE = False
JUMPSCARE_COOLDOWN = 120

# elevenlabs
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# obs sources
SCENE = "Overlay"

# chat history
CHAT_HISTORY_LIMIT = 20

# idle chatter
IDLE_CHATTER_ENABLE = True
#IDLE_CHARACTER = 
IDLE_RESET_ON_REACT = False
MIN_IDLE_TIME = 300
MAX_IDLE_TIME = 1200
IDLE_RECORD_TIME = 0 # keep at 0 for now. recording causes problems
IDLE_MESSAGES = [
    "(this is automatic idle chatter) be helpful!",
    "(this is automatic idle chatter) make an observation!",
    "(this is automatic idle chatter) go absolutely crazy",
    "(this is automatic idle chatter) share something about yourself",
    "(this is automatic idle chatter) whats going on?"
    #"ramble about what you see.",
    #"scream loudly.",
    #"drop random lore.",
    #"comment on current chat conversation.",
    #"talk about your current emotional state."
]
#endregion