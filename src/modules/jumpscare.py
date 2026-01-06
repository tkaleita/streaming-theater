import random
import time
from core.config import *

# change to your own folder containing mp4s
video_folder = "F:/VideoMaking/Stream Plugins/jumpscare/Videos"
valid_extensions = ('.mp4', '.mov', '.mkv', '.avi', '.ts')
current_video = ""

def play_jumpscare():
    global current_video

    # get jumpscare media source
    item_id = req.get_scene_item_id(SCENE, "Jumpscare").scene_item_id

    # choose random video
    files = [
        os.path.join(video_folder, f) 
        for f in os.listdir(video_folder) 
        if f.lower().endswith(valid_extensions) and f.lower() is not current_video.lower
    ]
    if not files:
        print("No video files found in the directory!")
        exit()
        
    random_video = random.choice(files)
    current_video = random_video
    print(f"Selected video: {random_video}")

    # set to chosen video
    req.set_input_settings("Jumpscare", {'local_file': random_video}, True)
    time.sleep(0.5)
    
    # adjust width and height
    video_settings = req.get_video_settings()
    canvas_w = video_settings.base_width
    canvas_h = video_settings.base_height
    req.set_scene_item_transform(SCENE, item_id, {
        'boundsType': 'OBS_BOUNDS_SCALE_INNER',
        'boundsWidth': canvas_w,
        'boundsHeight': canvas_h,
        'alignment': 5
    })

    # play video
    # this is not needed because changing the linked video (see above) automatically starts playback (for some reason)
    #req.trigger_media_input_action("Jumpscare", "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")
    print("starting chosen video!")
    return