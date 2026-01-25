import time
from dataclasses import dataclass, field
from typing import Callable, Awaitable

import modules.ai as ai
from core.config import *
from core.state import chat_state, tts_state
import modules.tts as tts
import modules.jumpscare as js
from chat import shared, twitch, router
import modules.idle as idle

#region HELPERS
@dataclass
class Command:
    name: str
    args: list[str]
    cooldown: int # currently always PER-USER
    func: Callable
    enabled: bool = True

COMMANDS: dict[str, Command] = {}

def command(name: str, args: list[str], cooldown: int = 0, enabled: bool = True):
    def decorator(func):
        spec = Command(
            name=name,
            args=args,
            cooldown=cooldown,
            func=func,
            enabled=enabled
        )
        COMMANDS[name] = spec
        return func
    return decorator

def build_usage(spec: Command) -> str:
    parts = []
    for arg in spec.args:
        if arg == "character":
            chars = "|".join(CHARACTERS.keys())
            parts.append(f"<{chars}>")
        else:
            parts.append(f"<{arg}>")
    return f"Usage: !{spec.name} " + " ".join(parts)

async def call_command(origin: str, cmd: Command, user: str, raw_args: str):
    if not cmd.enabled:
        return

    # --- cooldown ---
    if not DEBUG_COOLDOWN:
        now = time.time()
        last = chat_state.last_used[user][cmd.name]

        if now - last < cmd.cooldown:
            remaining = round(cmd.cooldown - (now - last))
            await shared.send_message(origin, f"@{user} -> {cmd.name} cooldown {remaining}s!")
            return

        chat_state.last_used[user][cmd.name] = now

    parts = raw_args.split()
    parsed: dict[str, str | None] = {}
    arg_specs = cmd.args
    i = 0  # index into parts

    # no arguments declared → ignore user args and just call
    if not arg_specs:
        await shared.send_message(origin, f"@{user} -> invokes {cmd.name}!")
        return await cmd.func(origin=origin, user=user)

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
                    await shared.send_message(origin, build_usage(cmd))
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
                await shared.send_message(origin, build_usage(cmd))
                return

    queue_size = tts_state.queue.qsize() + 1 + tts_state.busy
    pos_msg = "" if queue_size == 1 else f" (queue pos {queue_size})"
    await shared.send_message(origin, f"@{user} -> invokes {cmd.name}!{pos_msg}")
    return await cmd.func(origin=origin, user=user, **parsed)
#endregion

#region COMMANDS
@command(
    name="say",
    args=["text"],
    cooldown=SAY_COOLDOWN,
    enabled=SAY_ENABLE
)
async def say(origin, user, text):
    char = SAY_CHARACTER
    router.add_to_history(char.name, text)
    print(f"!say from {user}: {text}")
    tts.say_as(char, text)

@command(
    name="react",
    args=["character", "text?"],
    cooldown=REACT_COOLDOWN,
    enabled=REACT_ENABLE
)
async def react(origin, user, character, text):
    key = character.lower()
    char = CHARACTERS.get(key)
    if char is None:
        available = ", ".join(CHARACTERS.keys())
        await shared.send_message(origin, f"@{user} -> unknown character '{character}'. available: {available}")
        return
    ai_reply = await ai.get_ai_reply(char, f"from {user}: {text}")
    tts.say_as(char, ai_reply)

@command(
    name="jumpscare",
    args=[],
    cooldown=JUMPSCARE_COOLDOWN,
    enabled=JUMPSCARE_ENABLE
)
async def jumpscare(origin, user):
    js.play_jumpscare()
    return
#endregion