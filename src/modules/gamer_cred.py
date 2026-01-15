from core import file_updater, sound_player
from core.config import *

def handle_message(msg): # only gets called if active
    match(msg):
        case "-5":
            file_updater.change_field("gamer_cred", -5)
            sound_player.play_sound(sound_player.Sounds.XP_ERROR, 0.2, 0.9, 0.95)
        case "+5":
            file_updater.change_field("gamer_cred", +5)
            sound_player.play_sound(sound_player.Sounds.DING, 0.2, 1.05, 1.1)
            
    gamer_cred = file_updater.read_field("gamer_cred")
    req.set_input_settings(
        name="Gamer Cred",
        settings={"text": f"Gamer Cred: {gamer_cred}"},
        overlay=True
    )