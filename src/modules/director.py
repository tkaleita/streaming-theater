import asyncio
import time
from core.state import chat_state
import modules.tts as tts
import modules.ai as ai
import core.characters as characters
from core.config import DIRECTOR_COOLDOWN, DIRECTOR_CHAT_TIME

chat_history = []
active = False

def handle_message(msg):
    global chat_history, active

    if not active:
        return
    
    chat_history.append(msg)
    print("appended message to director chat history!")

async def run_director_loop():
    global chat_history, active

    while True:
        active = False
        chat_history = []
        await asyncio.sleep(DIRECTOR_COOLDOWN) # 5 minutes

        active = True
        delay = DIRECTOR_CHAT_TIME

        ai_reply = await ai.get_ai_reply(characters.DIRECTOR,
                                         f"tell the viewers to send suggestions in the chat and that they have {delay} seconds!")
        tts.say_as(characters.DIRECTOR, ai_reply)
        print("Director window open!")

        await asyncio.sleep(delay) # wait n seconds. getting chat messages is not dependent on this! so its okay.

        print(f"Director window closed! Collected {len(chat_history)} messages.")
        ai_reply = await ai.get_ai_reply(characters.DIRECTOR, '', chat_history=chat_history)
        tts.say_as(characters.DIRECTOR, ai_reply)