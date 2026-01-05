import asyncio
import base64
import cv2

from chat import router
from core.state import chat_state
from core.config import openai_client, CHAT_HISTORY_LIMIT, Character

async def get_ai_reply(char: Character, msg, take_screenshot = True, chat_history = []):
    chat_history_str = "".join(f"[{line}]" for line in chat_state.history)
    if (len(chat_history) <= 0):
        chat_history_str = "".join(f"[{line}]" for line in chat_history)

    image_base64 = []
    if (take_screenshot):
        image_base64 = capture_webcam_image()

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: openai_client.chat.completions.create(
        model=char.model,
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text",
                    "text": f"{char.system_prompt}"
                            "MAXIMUM STRICT REPLY LIMIT: NEVER EXCEED 10 WORDS. KEEP YOUR ANSWERS SHORT. ALWAYS!"
                            "never use emojis."
                            "react to the screenshot as if you see it live."
                            "be unpredictable."
                            f"you only know what {char.name} would know."
                            "ALWAYS be in character and write things like you would say them naturally."
                            "you are on a livestream and viewers MIGHT say things to you."
                            "you HAVE to say something related to it. do not ignore any viewer-added messages."
                            "treat it like a viewer speaking TO or AT you."
                            "viewer names are viewable in chat history."
                            "the streamers name is tobi aka tobi_focuss."
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text":    f"Viewer-added message: '{msg}'"
                                f"included are also the last {CHAT_HISTORY_LIMIT} messages of the twitch chat."
                                "these act as extra context for you."
                                f"chat history: {chat_history_str}" 
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

    router.add_to_history(f"{char.name}(You)", ai_reply)
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