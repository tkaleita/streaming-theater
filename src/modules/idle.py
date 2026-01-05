import asyncio
import random

import modules.ai as ai
import modules.tts as tts
import modules.voice_recog as voice_recog

from core.config import *

async def idle_chatter():
    while True:
        delay = random.randint(MIN_IDLE_TIME, MAX_IDLE_TIME)  # 5 to 10 minutes
        #delay = random.randint(20, 30)
        await asyncio.sleep(delay)

        try:
            print("Idle chatter triggered.")
            
            # Use a special message indicating "no viewer spoke"
            #msg = random.choice(IDLE_MESSAGES)

            background = voice_recog.record_fixed_audio(IDLE_RECORD_TIME)
            char = random.choice(list(CHARACTERS.values()))
            ai_reply = await ai.get_ai_reply(char, f"tobi: {background}")
            tts.say_as(char, ai_reply)

        except Exception as e:
            print("Idle chatter failed:", e)
            continue