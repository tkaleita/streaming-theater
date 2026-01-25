import asyncio
import random

import modules.ai as ai
import modules.tts as tts
import modules.voice_recog as voice_recog

from core.config import *

idle_reset_event = asyncio.Event()

async def idle_chatter():
    while True:
        delay = random.randint(MIN_IDLE_TIME, MAX_IDLE_TIME)

        try:
            # wait for either timeout OR reset
            idle_reset_event.clear()
            await asyncio.wait_for(idle_reset_event.wait(), timeout=delay)

            # If we get here, reset_timer() was called
            print("Idle timer reset.")
            continue

        except asyncio.TimeoutError:
            # Normal idle trigger
            pass

        try:
            print("Idle chatter triggered.")

            background = random.choice(IDLE_MESSAGES)
            print(background)

            if IDLE_RECORD_TIME != 0:
                background = await asyncio.to_thread(voice_recog.record_fixed_audio, IDLE_RECORD_TIME)

            char = random.choice(list(CHARACTERS.values()))
            ai_reply = await ai.get_ai_reply(char, f"(this is self-initiated speech!) {background}")
            tts.say_as(char, ai_reply)

        except Exception as e:
            print("Idle chatter failed:", e)
            continue


def reset_timer():
    idle_reset_event.set()