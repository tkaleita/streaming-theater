import asyncio
from math import log
import threading
import time

import numpy as np
from core.config import *
from core.sound_player import Sounds, play_sound
from core.state import tts_state
from core.characters import Character

is_active = False
original_y = None

def run_obs_listener():
    with obs.EventClient(
        subs=(obs.Subs.LOW_VOLUME | obs.Subs.INPUTVOLUMEMETERS)
    ) as client:
        client.callback.register([
            on_input_volume_meters,
            on_input_mute_state_changed
        ])

        print("OBS audio listener running")

        while True:
            time.sleep(1)

def calculate_offset(dbL, dbR):
    db = (dbL + dbR) / 2
    if db <= -175:
        return 0

    tts_state.hold_time = HOLD_TIME # db > 0

    db = max(min(db, 0), -100)
    return np.interp(db, [-75, 0], [0, MOVEMENT_STRENGTH])

def slide_animation(char: Character, start_y, end_y, duration=0.35, reset_on_end=False):
    tts_state.sliding = True
    steps = 30
    step_time = duration / steps

    for i in range(steps + 1):
        t = i / steps
        eased = 1 - (1 - t) ** 3  # ease-out
        current_y = start_y + (end_y - start_y) * eased

        try:
            item_id = req.get_scene_item_id(
                SCENE, char.img_source
            ).scene_item_id

            subtitle_item_id = req.get_scene_item_id(
                SCENE, char.subtitle_source
            ).scene_item_id

            req.set_scene_item_enabled(SCENE, item_id, True)

            req.set_scene_item_transform(
                SCENE,
                item_id,
                {"positionY": current_y}
            )
            req.set_scene_item_transform(
                SCENE,
                subtitle_item_id,
                {"positionY": current_y - char.subtitle_y_offset}
            )
        except Exception:
            pass

        time.sleep(step_time)

    if reset_on_end:
        req.set_scene_item_enabled(SCENE, item_id, False)
        req.set_scene_item_transform(SCENE,item_id,{"positionY": start_y})

    tts_state.sliding = False

def move_source(char: Character, original_y, offset_y):
    try:
        item_id = req.get_scene_item_id(SCENE, char.img_source).scene_item_id
        subtitle_item_id = req.get_scene_item_id(SCENE, char.subtitle_source).scene_item_id

        if offset_y <= 1 and tts_state.hold_time <= 0:
            req.set_scene_item_enabled(SCENE, subtitle_item_id, False)
        else:
            req.set_scene_item_enabled(SCENE, subtitle_item_id, True)

        pos_x = req.get_scene_item_transform(SCENE,item_id).scene_item_transform["positionX"]

        new_y = original_y - offset_y
        tts_state.hold_time -= 1

        req.set_scene_item_transform(
            SCENE,
            item_id,
            {
                "positionY": new_y,
                "rotation": offset_y * 0.05
            }
        )
        req.set_scene_item_transform(
            SCENE,
            subtitle_item_id,
            {
                "positionY": new_y - char.subtitle_y_offset,
                "rotation": offset_y * 0.05,
                "positionX": pos_x
            }
        )

    except Exception as e:
        print("ERR moving source:", e)

def on_input_volume_meters(data):
    global is_active, original_y

    if tts_state.tts_start_flag:
        print("TTS START")
        play_sound(Sounds.MESSAGE, 0.25)
        # get position once when we start
        item_id = req.get_scene_item_id(SCENE, tts_state.current_char.img_source).scene_item_id
        original_y = req.get_scene_item_transform(SCENE, item_id).scene_item_transform["positionY"]
        is_active = True
        tts_state.tts_start_flag = False
        threading.Thread(target=slide_animation,args=(tts_state.current_char, original_y + 750, original_y),daemon=True).start()

    if not is_active:
        return
    
    def fget(x):
        return round(20 * log(x, 10), 1) if x > 0 else -200.0

    for device in data.inputs:
        if device["inputName"] == DEVICE and device["inputLevelsMul"]:
            left, right = device["inputLevelsMul"]
            offset_y = calculate_offset(
                fget(left[LEVELTYPE.POSTFADER]),
                fget(right[LEVELTYPE.POSTFADER])
            )
            if original_y != None and tts_state.sliding is False:
                move_source(tts_state.current_char, original_y, offset_y)

    # doing this back here so the last run can hide the image/subtitle source
    if tts_state.tts_end_flag:
        print("TTS END")
        threading.Thread(target=slide_animation,args=(tts_state.current_char, original_y, original_y + 750, 0.35, True),daemon=True).start()
        original_y = None
        is_active = False
        tts_state.tts_end_flag = False

def on_input_mute_state_changed(data):
    if data.input_name == DEVICE:
        print(f"{DEVICE} mute toggled")