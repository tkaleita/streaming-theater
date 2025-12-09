import time

import modules.ai as ai
from core.config import *
from core.state import chat_state, tts_state
import modules.tts as tts
from chat import twitch, router

def check_cooldown(user, command, cooldown):
    if DEBUG_COOLDOWN: return True

    now = time.time()
    user_last = chat_state.last_used[user][command]

    if now - user_last < cooldown:
        remaining = cooldown - (now - user_last)
        twitch.helix_send_message(f"@{user} -> {command} is on cooldown for another {round(remaining)} seconds.")
        return False

    chat_state.last_used[user][command] = now
    twitch.helix_send_message(f"@{user} -> invokes {command}!{'' if tts_state.queue.qsize()==0 else f' (queue pos {tts_state.queue.qsize()+1})'}")
    return True

async def say_command(user, msg, char: Character):
    if not check_cooldown(user, "say", SAY_COOLDOWN): return
    say_text = msg[5:].strip()
    if say_text:
        router.add_to_history(char.name, say_text)
        print(f"🗣️ !say from {user}: {say_text}")
        tts.enqueue_tts(char, say_text)
        return True

async def react_command(user, msg, char: Character):
    if not check_cooldown(user, "react", REACT_COOLDOWN): return
    react_text = msg[6:].strip()

    # get screenshot of obs output
    screenshot = ai.capture_webcam_image()
    ai_reply = await ai.get_ai_reply(char, f"{user}: {react_text}", screenshot)
    tts.enqueue_tts(char, ai_reply)
    return True