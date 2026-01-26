import asyncio
from collections import defaultdict
from dataclasses import dataclass, field

from core.characters import *
from core.config import *

@dataclass
class TtsState:
    queue: asyncio.Queue[tuple[Character, str]] = field(default_factory=asyncio.Queue)
    busy: bool = False
    current_char: Character = field(default_factory=lambda: DEFAULT_REACT_CHARACTER)
    hold_time: float = 0.0
    tts_start_flag: bool = False
    tts_end_flag: bool = False

@dataclass
class ChatState:
    chat_history: list[str] = field(default_factory=list) # generel chat history
    history: list[str] = field(default_factory=list) # convo history for characters
    last_used: dict = field(default_factory=lambda: defaultdict(lambda: defaultdict(float)))
    spam_map: dict = field(default_factory=lambda: defaultdict(dict))

@dataclass
class RecordingState:
    recording: bool = False
    audio_buffer: list = field(default_factory=list)
    stream: any = None

tts_state = TtsState()
chat_state = ChatState()
record_state = RecordingState()