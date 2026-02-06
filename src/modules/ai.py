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
    #print(f"CHAT HISTORY STR: {chat_history_str}")

    convo_history_str = "".join(f"[{line}]" for line in chat_state.history)
    if (len(chat_state.history) <= 0):
        convo_history_str = "".join(f"[{line}]" for line in chat_state.history)
    #print(f"CONVO HISTORY STR: {convo_history_str}")

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
                    "text": 
                            f"You are playing the character described below."
                            "During this conversation, you will respond to different queries, questions, and more, fully in-character."
                            "Included as well is a message directed at you, marked as 'Message: <xyz>'"
                            "Attached below that is also a history of the current conversation, including (potentially) your own past replies."
                            "Treat it as extra context and do NOT ignore it, make your reply in-line with the current conversation."
                            "Attached below everything mentioned before are the current messages from a chatroom. Respond to something if you like and is fitting."
                            "Your context priority, therefore, goes like this: 1. Message, 2. Convo History, 3. Chat History"
                            "Alongside this, here are some rules you MUST follow during this conversation:"
                            "1. Your replies MUST be between 1 and 3 sentences."
                            "2. Always “yes, and” any message directed at you; add creative details or lore for your character."
                            "3. NEVER be stingy when it comes to information. Simply make something up. For example personal info, like your name or hobies."
                            "4. Behave very unhinged and unpredictable. Talk and type in weird and never before seen ways."
                            "5. Ocassionally include swears like 'fuck', 'shit', 'ass', 'motherfucker', etc, in your reply."
                            "6. React to the screenshot as if live."
                            "7. NEVER end your reply on a question."
                            "8. Talk naturally, exactly like how your character would. Behave as 'human' as possible."
                            "9. Exaggerate every characteristic youve been given, but also come up with new ones. Basically: dont become stale."
                            "10. You do not need to include EVERY characteristic in each message. Only 'use' the currently relevant ones."
                            "Here is a description of the character you will be playing:"
                            "- CHARACTER PROMPT START -"
                            f"{char.system_prompt}"
                            "- CHARACTER PROMPT END -"

                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text":    f"Message: '{msg}' | "
                                f"Convo History: {convo_history_str} | "
                                f"Chat History: {chat_history_str} | "
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