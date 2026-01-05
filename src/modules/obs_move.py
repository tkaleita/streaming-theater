from math import log
import time

import numpy as np
from core.config import *
from core.state import tts_state
from core.characters import Character

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

def move_source(char: Character, offset_y):
    try:
        item_id = req.get_scene_item_id(SCENE, char.img_source).scene_item_id
        subtitle_item_id = req.get_scene_item_id(SCENE, char.subtitle_source).scene_item_id

        if offset_y <= 1 and tts_state.hold_time <= 0:
            req.set_scene_item_enabled(SCENE, item_id, False)
            req.set_scene_item_enabled(SCENE, subtitle_item_id, False)
        else:
            req.set_scene_item_enabled(SCENE, item_id, True)
            req.set_scene_item_enabled(SCENE, subtitle_item_id, True)

        new_y = char.original_y - offset_y
        tts_state.hold_time -= 1

        pos_x = req.get_scene_item_transform(SCENE,item_id).scene_item_transform["positionX"]

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
    def fget(x):
        return round(20 * log(x, 10), 1) if x > 0 else -200.0

    for device in data.inputs:
        if device["inputName"] == DEVICE and device["inputLevelsMul"]:
            left, right = device["inputLevelsMul"]
            offset = calculate_offset(
                fget(left[LEVELTYPE.POSTFADER]),
                fget(right[LEVELTYPE.POSTFADER])
            )
            move_source(tts_state.current_char, offset)

def on_input_mute_state_changed(data):
    if data.input_name == DEVICE:
        print(f"{DEVICE} mute toggled")