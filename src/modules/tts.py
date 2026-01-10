import asyncio
import os
import time
import sounddevice as sd
import soundfile as sf
from queue import Queue
import ctypes

from core.state import tts_state
from core.config import *
from core.sound_player import *

# background threads
audio_queue = Queue()
def audio_worker():
    ctypes.windll.ole32.CoInitialize(None)

    # wait until audio is supposed to play, then play it
    while True:
        path = audio_queue.get()
        print(path)
        try:
            play_sound(Sounds.MESSAGE, 0.25)
            play_file_to_virtual_cable(path)
        except Exception as e:
            print("Audio error:", e)
        audio_queue.task_done()

async def tts_queue_processor():
    while True:
        await asyncio.sleep(0.05)

        if tts_state.queue.empty():
            continue

        if tts_state.busy:
            continue

        char, text = await tts_state.queue.get()
        print(f"[QUEUE] popped: {char.name}: {text!r}")
        tts_state.busy = True

        await fire_tts(char, text)

        start_timeout = time.time() + 5  # to avoid instantly popping queue again (theres a delay on the TTS)
        while tts_state.hold_time <= 0 and time.time() < start_timeout:
            await asyncio.sleep(0.05)

        while tts_state.hold_time > 0:
            await asyncio.sleep(0.05)

        tts_state.busy = False

def eleven_generate(char: Character, text):
    # Request TTS generation
    audio = eleven_client.text_to_speech.convert(
        voice_id=char.voice_id,
        model_id="eleven_turbo_v2",   # or any model you prefer
        text=text,
        output_format="mp3_44100_128"
    )
    
    filename = f"tts_output\\tts_output_{int(time.time()*1000)}.mp3"
    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    abs_path = os.path.abspath(filename)
    return abs_path

def get_virtual_cable_device():
    devices = sd.query_devices()

    for idx, dev in enumerate(devices):
        name = dev["name"]
        hostapi = sd.query_hostapis()[dev["hostapi"]]["name"]

        if "CABLE Input" in name and "WASAPI" in hostapi:
            return idx

    raise RuntimeError("VB-Cable WASAPI device not found")

def play_file_to_virtual_cable(path):
    data, samplerate = sf.read(path, dtype="float32")

    device_index = get_virtual_cable_device()
    sd.default.device = device_index
    print(f"playing through VB-Cable (device {device_index})")

    sd.play(data, samplerate)
    sd.wait()

def say_as(char: Character, text):
    tts_state.queue.put_nowait((char, text))

async def fire_tts(char: Character, text):
    tts_state.current_char = char
    print(tts_state.current_char.name)

    audio_file = eleven_generate(char, text)
    
    # update OBS subtitle and current source
    req.set_input_settings(
        name=char.subtitle_source,
        settings={"text": text},
        overlay=True
    )
    audio_queue.put(audio_file)