import time
from cv2 import normalize

from chat import commands
from core.config import *
from core.state import chat_state
from modules import director
from modules import gamer_cred
import modules.tts as tts

async def handle_message(user, msg, origin = "twitch"):
    # filter specific users
    if user == "tobi_focuss_bot":
        return

    # normal message
    if not msg.startswith("!"):
        add_to_history(user, msg)
        if DIRECTOR_ENABLE:
            director.handle_message(msg)
        if GAMER_CRED_ENABLE:
             gamer_cred.handle_message(msg)
        return

    # commands
    parts = msg[1:].split(" ", 1)
    name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if name in commands.COMMANDS:
        spec = commands.COMMANDS[name]
        await commands.call_command(origin, spec, user, args)

    # combo system (bugged rn i guess?)
    if not COMBO_ENABLE:
        return

    msg_norm = normalize(msg)
    now = time.time()

    user_map = chat_state.spam_map[msg_norm]
    user_map[user] = now

    expired = [u for u, t in user_map.items() if now - t > COMBO_WINDOW_SECONDS]
    for u in expired:
        del user_map[u]

    unique_count = len(user_map)

    print(f"{user}: {msg} (unique users: {unique_count})")

    if unique_count >= COMBO_TRIGGER_COUNT:
        chat_state.spam_map[msg_norm].clear()
        await tts.say_as(SAY_CHARACTER, msg)

def add_to_history(user, msg):
    chat_state.history.append(f"{user}: {msg}")
    if len(chat_state.history) > CHAT_HISTORY_LIMIT:
        chat_state.history.pop(0)