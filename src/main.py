import asyncio
import threading

# own files
from chat import twitch, youtube
from core.config import * # so every variable is just plain accessible
from modules import director
import modules.idle as idle
import modules.tts as tts
import modules.obs_move as obs_move
import modules.progress as progress
from modules.tts import audio_worker
import modules.voice_recog as voice_recog

async def run_all_listeners():
    tasks = [
        twitch.twitch_listener(),
        #youtube.youtube_listener()
    ]
    
    if SAY_ENABLE or REACT_ENABLE:
        tasks.append(tts.tts_queue_processor())

    if REACT_ENABLE:
        await voice_recog.setup_vr()
    
    if IDLE_CHATTER_ENABLE:
        tasks.append(idle.idle_chatter())

    if DIRECTOR_ENABLE:
        tasks.append(director.run_director_loop())

    if PROGRESS_ENABLE:
        tasks.append(progress.run_progress_loop())

    await asyncio.gather(*tasks)

def main():
    #YT_LIVE_CHAT_ID = get_live_chat_id()

    obs_thread = threading.Thread(target=obs_move.run_obs_listener, daemon=True)
    obs_thread.start()

    threading.Thread(target=audio_worker, daemon=True).start()

    asyncio.run(run_all_listeners())

if __name__ == "__main__":
    main()