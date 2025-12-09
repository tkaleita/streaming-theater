import time
import keyboard
import numpy as np
from openai import chat
import sounddevice as sd
import soundfile as sf

from chat import router
import modules.ai as ai
from core.config import *
from core.state import record_state
import modules.tts as tts

def run_vr_loop():
    while True:
        keyboard.wait("f7")
        time.sleep(0.1)  # debounce so one press doesn't double-trigger

        if not record_state.recording:
            # START recording
            start_recording()
        else:
            # STOP recording
            text = stop_recording_and_transcribe()
            if not text:
                continue

            screenshot = ai.capture_webcam_image()
            router.add_to_history("tobi_focuss", text)

            ai_reply = ai.get_ai_reply(REACT_CHARACTER, f"tobi_focuss: {text}", screenshot)
            tts.enqueue_tts(REACT_CHARACTER, ai_reply)

def start_recording():
    if record_state.recording:
        return

    print("🎤 Recording started...")
    record_state.recording = True
    record_state.audio_buffer = []

    mic_index = find_hyperx_directsound_mic()
    sd.default.device = (mic_index, None)

    def audio_callback(indata, frames, time_data, status):
        if record_state.recording:
            record_state.audio_buffer.append(indata.copy())

    record_state.stream = sd.InputStream(
        samplerate=44100,
        channels=1,
        callback=audio_callback
    )
    record_state.stream.start()

def stop_recording_and_transcribe():
    if not record_state.recording:
        return ""

    record_state.recording = False

    print("🛑 Recording stopped.")

    if record_state.stream:
        record_state.stream.stop()
        record_state.stream.close()
        record_state.stream = None

    if not record_state.audio_buffer:
        print("⚠️ No audio recorded.")
        return ""

    audio = np.concatenate(record_state.audio_buffer, axis=0)
    temp_file = "mic_input.wav"
    sf.write(temp_file, audio, 44100)

    transcript = openai_client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=open(temp_file, "rb")
    )

    text = transcript.text.strip()
    print("🗣️ Transcript:", text)
    return text

def record_fixed_audio(duration=5):
    fs = 44100
    mic_index = find_hyperx_directsound_mic()
    sd.default.device = (mic_index, None)

    print(f"🎤 Recording {duration}s of idle audio...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    temp_file = "idle_input.wav"
    sf.write(temp_file, audio, fs)

    transcript = openai_client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=open(temp_file, "rb")
    )

    text = transcript.text.strip()
    print("🗣️ Idle background transcription:", text)
    return text


def find_hyperx_directsound_mic():
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()

    for idx, dev in enumerate(devices):
        name = dev["name"].lower()
        if "hyperx" not in name:
            continue

        if dev["max_input_channels"] <= 0:
            continue

        host = hostapis[dev["hostapi"]]["name"].lower()

        if "directsound" in host:  # ✅ Your working API
            print(f"Using HyperX (DirectSound): {dev['name']} at index {idx}")
            return idx

    raise RuntimeError("Could not find HyperX QuadCast (DirectSound) microphone!")