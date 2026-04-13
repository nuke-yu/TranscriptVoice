"""
speaker.py
TTS engine: splits text into sentences and reads each via macOS `say`.
"""

import re


def split_sentences(text: str) -> list[str]:
    """Split text on sentence-ending punctuation and newlines."""
    parts = re.split(r'[。.！!？?\n]+', text)
    return [p.strip() for p in parts if p.strip()]
