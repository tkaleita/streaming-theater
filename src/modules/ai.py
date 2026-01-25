import asyncio
import base64
import cv2

from chat import router
from core.state import chat_state
from core.config import *
import modules.idle as idle

async def get_ai_reply(char: Character, msg, take_screenshot = True, chat_history = chat_state.chat_history):
    if IDLE_RESET_ON_REACT:
        idle.reset_timer()

    chat_history_str = "".join(f"[{line}]" for line in chat_state.chat_history)
    if (len(chat_history) <= 0):
        chat_history_str = "".join(f"[{line}]" for line in chat_history)
    print(f"CHAT HISTORY STR: {chat_history_str}")

    convo_history_str = "".join(f"[{line}]" for line in chat_state.history)
    if (len(chat_state.history) <= 0):
        convo_history_str = "".join(f"[{line}]" for line in chat_state.history)
    print(f"CONVO HISTORY STR: {convo_history_str}")

    image_base64 = []
    if (take_screenshot):
        image_base64 = capture_webcam_image()

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: openai_client.chat.completions.create(
        model=char.model,
        max_tokens=100,
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text",
                    "text": 
                            "MAX 5–35 WORDS. DO NOT END A REPLY WITH A QUESTION."
                            f"You are {char.name} (just a title), the streamer’s improv partner. Stay in character and react dynamically."
                            "The streamer's name is 'Tobi' aka 'tobi_focuss'."
                            "Always “yes, and” the viewer message; add creative details or lore for your character."
                            f"Dont include your own name at the beginning, i.e. '{char.name}: <message>'. Dont do this."
                            "NEVER be stingy when it comes to information. Simply make something up."
                            "Attached below is also a history of the current conversation. Treat it as extra context and do NOT ignore it."
                            "It allows you to keep track of who said what."
                            "Attached below everything else is the current Twitch chat. Respond to something if you like."
                            "Your priority context goes like this: 1. Message, 2. Convo History, 3. Twitch History"
                            "Subvert expectations and dont simply go for the obvious jokes."
                            "Do not break the 4th wall unless really funny. Swear if appropriate."
                            "The stream is for mature audiences."
                            "React to the screenshot as if live. Use your imagination, be unpredictable."
                            "- CHARACTER PROMPT START -"
                            f"{char.system_prompt}"

                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text":    f"Message (directed at you): '{msg}' | "
                                f"Convo History: {convo_history_str} | "
                                f"Twitch Chat History: {chat_history_str} | "
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ],
            }
        ]
    ))

    ai_reply = response.choices[0].message.content
    print("Response:", ai_reply)

    router.add_to_history(char.name, ai_reply)
    return ai_reply

def capture_webcam_image(output_file="screenshot.jpg"):
    cap = cv2.VideoCapture(1)

    # Set 16:9 resolution
    width  = 1280
    height = 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise IOError("Failed to capture image")

    cv2.imwrite(output_file, frame)
    cap.release()

    print(f"Saved {output_file} at {width}×{height}")

    with open("screenshot.jpg", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        return b64