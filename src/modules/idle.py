import asyncio
import random

import modules.ai as ai
import modules.tts as tts
import modules.voice_recog as voice_recog

from core.config import *

# TODO make idle chatter cooldown reset if react was used

async def idle_chatter():
    while True:
        delay = random.randint(MIN_IDLE_TIME, MAX_IDLE_TIME)  # 5 to 10 minutes
        #delay = random.randint(20, 30)
        await asyncio.sleep(delay)

        try:
            print("Idle chatter triggered.")

            screenshot = ai.capture_webcam_image()
            
            # Use a special message indicating "no viewer spoke"
            #msg = random.choice(IDLE_MESSAGES)

            background = voice_recog.record_fixed_audio(IDLE_RECORD_TIME)
            ai_reply = await ai.get_ai_reply(REACT_CHARACTER, f"tobi: {background}", screenshot)
            tts.enqueue_tts(REACT_CHARACTER, ai_reply)

        except Exception as e:
            print("Idle chatter failed:", e)
            continue