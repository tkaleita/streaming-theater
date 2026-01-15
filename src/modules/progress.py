import asyncio
import keyboard
import json
import pygame

from core.config import *
import core.file_updater as file_updater
import core.sound_player as sound_player
from core.sound_player import play_sound, Sounds

progress_text = "Day"
current_progress = 0
max_progress = 7

# Define what you want to happen for each key
def plus_progress():
    global current_progress
    current_progress += 1

    print("plus_progress")
    update_progress()

    sound_player.play_sound(Sounds.MESSAGE, 0.4, 1, 1.1)

    if current_progress >= max_progress:
        sound_player.play_sound(Sounds.WIN, 0.5)
    return

def minus_progress():
    global current_progress
    current_progress -= 1

    print("minus_progress")
    update_progress()

    sound_player.play_sound(Sounds.MESSAGE, 0.4, 0.9, 0.95)
    return

def reset_progress():
    global current_progress

    print("reset_progress")
    file_updater.change_field("resets", 1) # add 1 to resets field
    current_progress = 0
    update_progress()

    # update obs text
    resets = file_updater.read_field("resets")
    req.set_input_settings(
        name="Resets",
        settings={"text": f"Resets: {resets}"},
        overlay=True
    )

    # play audio file
    sound_player.play_sound(Sounds.XP_ERROR, 0.3)
    return

def update_progress():
    global current_progress, max_progress, progress_text

    set_progress_bar_text(f"{progress_text} {current_progress}/{max_progress}")
    set_crop(current_progress / max_progress)

def set_progress_bar_text(text):
    req.set_input_settings(
        name="Progress Bar Text",
        settings={"text": text},
        overlay=True
    )

def set_crop(percent=0.5):
    response = req.get_scene_item_id("Progress Bar", "Progress Bar Bar")
    item_id = response.scene_item_id

    transform = {
        'cropRight': max(min(1500*(1-percent), 1499), 0) # 1 less because otherwise it doesnt update for some reason...
    }

    req.set_scene_item_transform("Progress Bar", item_id, transform)

async def run_progress_loop():
    # Register the hotkeys once
    # 'keyboard' handles these in the background automatically
    keyboard.add_hotkey("ctrl+f8", plus_progress)
    keyboard.add_hotkey("ctrl+f9", minus_progress)
    keyboard.add_hotkey("ctrl+f10", reset_progress)

    # Keep the async loop alive
    # does this cause problems? async-wise
    while True:
        # If you want to stop the script when 'esc' is pressed
        if keyboard.is_pressed("esc"):
            break
            
        await asyncio.sleep(1) # Sleep to keep the CPU usage low

if __name__ == "__main__":
    try:
        asyncio.run(run_progress_loop())
    except KeyboardInterrupt:
        pass