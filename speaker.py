"""
speaker.py
TTS engine: splits text into sentences and reads each via macOS `say`.
"""

import re
import subprocess
import threading
from typing import Callable


def split_sentences(text: str) -> list[str]:
    """Split text on sentence-ending punctuation and newlines."""
    parts = re.split(r'[。.！!？?\n]+', text)
    return [p.strip() for p in parts if p.strip()]


def detect_voice(text: str) -> str:
    """Return 'Tingting' if text contains CJK characters, else 'Samantha'."""
    if re.search(r'[\u4e00-\u9fff]', text):
        return "Tingting"
    return "Samantha"


class Speaker:
    def __init__(
        self,
        on_progress: Callable[[int, int], None] = None,
        on_done: Callable[[], None] = None,
    ):
        self.on_progress = on_progress
        self.on_done = on_done
        self._process: subprocess.Popen | None = None
        self._stopped = False

    def start(self, text: str):
        """Split text into sentences and read each one via `say`."""
        self._stopped = False
        sentences = split_sentences(text)
        if not sentences:
            if self.on_done:
                self.on_done()
            return
        threading.Thread(
            target=self._run, args=(sentences,), daemon=True
        ).start()

    def _run(self, sentences: list[str]):
        total = len(sentences)
        for i, sentence in enumerate(sentences):
            if self._stopped:
                return
            voice = detect_voice(sentence)
            self._process = subprocess.Popen(
                ["say", "-v", voice, sentence],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._process.wait()
            if self._stopped:
                return
            if self.on_progress:
                self.on_progress(i + 1, total)
        if not self._stopped and self.on_done:
            self.on_done()

    def stop(self):
        """Kill current `say` process and cancel remaining sentences."""
        self._stopped = True
        if self._process and self._process.poll() is None:
            self._process.kill()
            self._process = None
