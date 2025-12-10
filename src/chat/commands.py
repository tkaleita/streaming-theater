import time
from dataclasses import dataclass, field
from typing import Callable, Awaitable

import modules.ai as ai
from core.config import *
from core.state import chat_state, tts_state
import modules.tts as tts
from chat import twitch, router

#region DEFINE COMMANDS
@dataclass
class Command:
    name: str
    args: list[str]
    cooldown: int
    func: Callable

COMMANDS: dict[str, Command] = {}

def command(name: str, args: list[str], cooldown: int = 0):
    def decorator(func):
        spec = Command(
            name=name,
            args=args,
            cooldown=cooldown,
            func=func
        )
        COMMANDS[name] = spec
        return func
    return decorator
#endregion

def build_usage(spec: Command) -> str:
    parts = []
    for arg in spec.args:
        if arg == "character":
            chars = "|".join(CHARACTERS.keys())
            parts.append(f"<{chars}>")
        else:
            parts.append(f"<{arg}>")
    return f"Usage: !{spec.name} " + " ".join(parts)

async def call_command(cmd: Command, user: str, raw_args: str):
    # --- cooldown ---
    if not DEBUG_COOLDOWN:
        now = time.time()
        last = chat_state.last_used[user][cmd.name]

        if now - last < cmd.cooldown:
            remaining = round(cmd.cooldown - (now - last))
            twitch.helix_send_message(f"@{user} -> {cmd.name} cooldown {remaining}s!")
            return

        chat_state.last_used[user][cmd.name] = now

    parts = raw_args.split()
    parsed: dict[str, str | None] = {}
    arg_specs = cmd.args
    i = 0  # index into parts

    # no arguments declared → ignore user args and just call
    if not arg_specs:
        return await cmd.func(user=user)

    REST_NAMES = {"rest", "text", "message"}

    for idx, spec in enumerate(arg_specs):
        optional = spec.endswith("?")
        name = spec[:-1] if optional else spec
        is_last = (idx == len(arg_specs) - 1)
        is_rest_like = name in REST_NAMES

        # last arg and rest-like: absorb remaining text
        if is_last and is_rest_like:
            if i >= len(parts):
                if optional:
                    parsed[name] = ""
                    break
                else:
                    # missing required rest-like argument
                    twitch.helix_send_message(build_usage(cmd))
                    return
            parsed[name] = " ".join(parts[i:])
            break

        # normal positional arg
        if i < len(parts):
            parsed[name] = parts[i]
            i += 1
        else:
            if optional:
                parsed[name] = None
                continue
            else:
                # missing required arg
                twitch.helix_send_message(build_usage(cmd))
                return

    queue_size = tts_state.queue.qsize()
    pos_msg = "" if queue_size == 0 else f" (queue pos {queue_size + 1})"
    twitch.helix_send_message(f"@{user} -> invokes {cmd.name}!{pos_msg}")
    return await cmd.func(user=user, **parsed)

@command(
    name="say",
    args=["text"],
    cooldown=30
)
async def say(user, text):
    char = SAY_CHARACTER
    router.add_to_history(char.name, text)
    print(f"!say from {user}: {text}")
    tts.enqueue_tts(char, text)

@command(
    name="react",
    args=["character", "text?"],
    cooldown=30
)
async def react(user, character, text):
    key = character.lower()
    char = CHARACTERS.get(key)
    if char is None:
        available = ", ".join(CHARACTERS.keys())
        twitch.helix_send_message(
            f"unknown character '{character}'. available: {available}"
        )
        return
    screenshot = ai.capture_webcam_image()
    ai_reply = await ai.get_ai_reply(char, f"{user}: {text}", screenshot)
    tts.enqueue_tts(char, ai_reply)