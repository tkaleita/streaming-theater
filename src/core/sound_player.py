from enum import Enum
import random
import pygame
import numpy as np

pygame.mixer.init()

BASE_DIR = "F:/VideoMaking/Editing Library/Sound Effects/"
class Sounds(Enum):
    VINE_BOOM = f"{BASE_DIR}Vine boom sound effect.mp3"
    XP_ERROR = f"{BASE_DIR}Windows XP Error Sound.mp3"
    WIN = f"{BASE_DIR}WIN sound effect no copyright.mp3"
    MESSAGE = f"{BASE_DIR}Half-Life 2/message.wav"
    DING = f"{BASE_DIR}Ding Sound Effect HD.mp3"
    DING2 = f"{BASE_DIR}Half-Life 2/buttonclickrelease.wav"

def play_sound(sound_enum: Sounds, volume: float = 0.5, min_pitch = 0.95, max_pitch = 1.05):
    file_path = sound_enum.value

    try:
        sound = pygame.mixer.Sound(str(file_path))

        sound_array = pygame.sndarray.array(sound)
        factor = random.uniform(min_pitch, max_pitch)
        
        # resample the array
        # we create new indices to "stretch" or "compress" the sound
        indices = np.round(np.arange(0, len(sound_array), factor))
        indices = indices[indices < len(sound_array)].astype(int)
        new_array = sound_array[indices]
        
        sound = pygame.sndarray.make_sound(new_array)

        sound.set_volume(volume)
        sound.play()
        
    except Exception as e:
        print(f"Failed to play sound: {e}")