# TranscriptVoice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal macOS desktop app that reads pasted text aloud using the built-in `say` command, with a progress bar and Chinese/English auto-detection.

**Architecture:** Three files — `speaker.py` handles TTS logic (sentence splitting, subprocess management, progress callbacks), `app.py` builds the AppKit window and wires UI to speaker, `main.py` is the entry point. The speaker reads sentences one by one so progress can be tracked.

**Tech Stack:** Python 3.11+, pyobjc-framework-Cocoa (AppKit), macOS `say` command (subprocess), pytest

---

### Task 1: Project scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create venv and install dependencies**

```bash
cd /Users/Nuke/claudeFolder/TranscriptVoice
python3 -m venv venv
venv/bin/pip install pyobjc-framework-Cocoa pytest
```

Expected: installs without errors.

- [ ] **Step 2: Create `requirements.txt`**

```
pyobjc-framework-Cocoa>=12.0
pytest>=7.0
```

- [ ] **Step 3: Create `.gitignore`**

```
venv/
__pycache__/
*.pyc
.DS_Store
.superpowers/
```

- [ ] **Step 4: Create `tests/__init__.py`**

Empty file — just `touch tests/__init__.py`.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore tests/__init__.py
git commit -m "feat: project scaffold"
```

---

### Task 2: Sentence splitter (TDD)

**Files:**
- Create: `speaker.py` (sentence splitting only)
- Create: `tests/test_speaker.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_speaker.py`:

```python
from speaker import split_sentences


def test_splits_on_chinese_period():
    assert split_sentences("你好。世界。") == ["你好", "世界"]


def test_splits_on_english_period():
    assert split_sentences("Hello. World.") == ["Hello", "World"]


def test_splits_on_exclamation():
    assert split_sentences("Good！Great!") == ["Good", "Great"]


def test_splits_on_question():
    assert split_sentences("Why？Really?") == ["Why", "Really"]


def test_splits_on_newline():
    assert split_sentences("Line one\nLine two") == ["Line one", "Line two"]


def test_strips_empty_strings():
    assert split_sentences("Hello.\n\nWorld.") == ["Hello", "World"]


def test_mixed_language():
    result = split_sentences("Hello. 你好。")
    assert result == ["Hello", "你好"]


def test_empty_string():
    assert split_sentences("") == []


def test_no_delimiters():
    assert split_sentences("Hello world") == ["Hello world"]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
venv/bin/pytest tests/test_speaker.py -v
```

Expected: `ModuleNotFoundError: No module named 'speaker'`

- [ ] **Step 3: Implement `split_sentences` in `speaker.py`**

Create `speaker.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
venv/bin/pytest tests/test_speaker.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add speaker.py tests/test_speaker.py
git commit -m "feat: sentence splitter with tests"
```

---

### Task 3: Language detection (TDD)

**Files:**
- Modify: `speaker.py` (add `detect_voice`)
- Modify: `tests/test_speaker.py` (add tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_speaker.py`:

```python
from speaker import detect_voice


def test_chinese_text_uses_tingting():
    assert detect_voice("你好世界") == "Tingting"


def test_english_text_uses_samantha():
    assert detect_voice("Hello world") == "Samantha"


def test_mixed_text_uses_tingting():
    # If any CJK chars present, use Chinese voice
    assert detect_voice("Hello 你好") == "Tingting"


def test_numbers_and_symbols_use_samantha():
    assert detect_voice("123 !@#") == "Samantha"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
venv/bin/pytest tests/test_speaker.py::test_chinese_text_uses_tingting -v
```

Expected: `ImportError: cannot import name 'detect_voice'`

- [ ] **Step 3: Add `detect_voice` to `speaker.py`**

Add after `split_sentences`:

```python
def detect_voice(text: str) -> str:
    """Return 'Tingting' if text contains CJK characters, else 'Samantha'."""
    if re.search(r'[\u4e00-\u9fff]', text):
        return "Tingting"
    return "Samantha"
```

- [ ] **Step 4: Run all tests**

```bash
venv/bin/pytest tests/test_speaker.py -v
```

Expected: all 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add speaker.py tests/test_speaker.py
git commit -m "feat: language detection for Chinese/English voice selection"
```

---

### Task 4: Speaker class — play and stop

**Files:**
- Modify: `speaker.py` (add `Speaker` class)
- Modify: `tests/test_speaker.py` (add integration tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_speaker.py`:

```python
import time
from speaker import Speaker


def test_speaker_calls_on_done():
    done = []
    s = Speaker(on_done=lambda: done.append(True))
    s.start("Hi.")
    time.sleep(3)
    assert done == [True]


def test_speaker_calls_on_progress():
    progress = []
    s = Speaker(on_progress=lambda cur, tot: progress.append((cur, tot)))
    s.start("Hi. Bye.")
    time.sleep(5)
    assert len(progress) == 2
    assert progress[-1] == (2, 2)


def test_speaker_stop_before_done():
    done = []
    s = Speaker(on_done=lambda: done.append(True))
    s.start("Hello. World. Goodbye. See you.")
    time.sleep(1)
    s.stop()
    time.sleep(1)
    assert done == []  # on_done not called when stopped early
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
venv/bin/pytest tests/test_speaker.py::test_speaker_calls_on_done -v
```

Expected: `ImportError: cannot import name 'Speaker'`

- [ ] **Step 3: Add `Speaker` class to `speaker.py`**

Append to `speaker.py`:

```python
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
```

- [ ] **Step 4: Run all tests**

```bash
venv/bin/pytest tests/test_speaker.py -v
```

Expected: all 16 tests PASS. (The integration tests take ~5-8s to run.)

- [ ] **Step 5: Commit**

```bash
git add speaker.py tests/test_speaker.py
git commit -m "feat: Speaker class with play/stop/progress callbacks"
```

---

### Task 5: AppKit window

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create `app.py`**

```python
"""
app.py
Native macOS window: text area, progress bar, Play/Stop buttons.
"""

import objc
from AppKit import (
    NSObject, NSApplication, NSApp,
    NSWindow, NSButton, NSTextField, NSScrollView, NSTextView, NSView,
    NSColor, NSFont, NSMakeRect,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable,
    NSBackingStoreBuffered, NSBezelStyleRounded, NSTextAlignmentRight,
    NSWindowLevel,
)
from Foundation import NSMakeRange

from speaker import Speaker


def _btn(title, target, selector, color=None, enabled=True):
    b = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 100, 32))
    b.setTitle_(title)
    b.setBezelStyle_(NSBezelStyleRounded)
    b.setTarget_(target)
    b.setAction_(selector)
    b.setEnabled_(enabled)
    if color:
        b.setContentTintColor_(color)
    return b


def _label(text, size=11, color=None):
    f = NSTextField.labelWithString_(text)
    f.setFont_(NSFont.systemFontOfSize_(size))
    if color:
        f.setTextColor_(color)
    f.setSelectable_(False)
    return f


class AppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, notif):
        self._speaker = Speaker(
            on_progress=self._on_progress,
            on_done=self._on_done,
        )
        self._total_sentences = 0
        self._build_window()
        self._window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def _build_window(self):
        style = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                 NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, 420, 380), style, NSBackingStoreBuffered, False
        )
        self._window.setTitle_("🔊 TranscriptVoice")
        self._window.center()
        self._window.setLevel_(NSWindowLevel.floating)

        root = self._window.contentView()

        # Text area
        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(14, 88, 392, 240))
        scroll.setHasVerticalScroller_(True)
        scroll.setBorderType_(1)
        self._text_view = NSTextView.alloc().initWithFrame_(NSMakeRect(0, 0, 392, 240))
        self._text_view.setFont_(NSFont.systemFontOfSize_(14))
        self._text_view.textContainer().setWidthTracksTextView_(True)
        scroll.setDocumentView_(self._text_view)
        root.addSubview_(scroll)

        # Placeholder label (shown when text view is empty)
        self._placeholder = _label(
            "Paste your text here...\n\n支持中英文，自动识别语言。",
            size=14, color=NSColor.placeholderTextColor()
        )
        self._placeholder.setFrame_(NSMakeRect(20, 200, 360, 120))
        root.addSubview_(self._placeholder)

        # Progress track (background)
        track = NSView.alloc().initWithFrame_(NSMakeRect(14, 78, 392, 4))
        track.setWantsLayer_(True)
        track.layer().setBackgroundColor_(NSColor.separatorColor().CGColor())
        track.layer().setCornerRadius_(2)
        root.addSubview_(track)

        # Progress fill
        self._progress = NSView.alloc().initWithFrame_(NSMakeRect(14, 78, 0, 4))
        self._progress.setWantsLayer_(True)
        self._progress.layer().setBackgroundColor_(NSColor.systemBlueColor().CGColor())
        self._progress.layer().setCornerRadius_(2)
        root.addSubview_(self._progress)

        # Buttons
        self._play_btn = _btn("▶ Play", self, "onPlay:",
                               color=NSColor.systemBlueColor(), enabled=True)
        self._play_btn.setFrame_(NSMakeRect(14, 34, 100, 32))
        root.addSubview_(self._play_btn)

        self._stop_btn = _btn("■ Stop", self, "onStop:", enabled=False)
        self._stop_btn.setFrame_(NSMakeRect(122, 34, 100, 32))
        root.addSubview_(self._stop_btn)

        # Status label
        self._status = _label("Idle", color=NSColor.secondaryLabelColor())
        self._status.setFrame_(NSMakeRect(230, 40, 180, 18))
        self._status.setAlignment_(NSTextAlignmentRight)
        root.addSubview_(self._status)

        # Signature
        sig = _label("Nuke.Yu", color=NSColor.tertiaryLabelColor())
        sig.setFrame_(NSMakeRect(330, 10, 80, 16))
        sig.setAlignment_(NSTextAlignmentRight)
        root.addSubview_(sig)

    # ── Actions ──────────────────────────────────────────────────────────

    def onPlay_(self, sender):
        text = self._text_view.textStorage().string()
        if not text.strip():
            return
        from speaker import split_sentences
        self._total_sentences = len(split_sentences(text))
        self._set_state("reading")
        self._speaker.start(text)

    def onStop_(self, sender):
        self._speaker.stop()
        self._set_state("idle")

    # ── Callbacks (from background thread) ───────────────────────────────

    @objc.python_method
    def _on_progress(self, current: int, total: int):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "applyProgress:", (current, total), False
        )

    @objc.python_method
    def _on_done(self):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "applyDone:", None, False
        )

    def applyProgress_(self, args):
        current, total = args
        frac = current / total if total > 0 else 0
        self._progress.setFrame_(NSMakeRect(14, 78, int(392 * frac), 4))

    def applyDone_(self, _):
        self._set_state("done")

    # ── State helper ─────────────────────────────────────────────────────

    @objc.python_method
    def _set_state(self, state: str):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "applyState:", state, False
        )

    def applyState_(self, state):
        if state == "reading":
            self._play_btn.setEnabled_(False)
            self._stop_btn.setEnabled_(True)
            self._status.setStringValue_("Reading...")
            self._progress.setFrame_(NSMakeRect(14, 78, 0, 4))
        elif state == "idle":
            self._play_btn.setEnabled_(True)
            self._stop_btn.setEnabled_(False)
            self._status.setStringValue_("Idle")
            self._progress.setFrame_(NSMakeRect(14, 78, 0, 4))
        elif state == "done":
            self._play_btn.setEnabled_(True)
            self._stop_btn.setEnabled_(False)
            self._status.setStringValue_("Done")
            self._progress.setFrame_(NSMakeRect(14, 78, 392, 4))
```

- [ ] **Step 2: Syntax check**

```bash
venv/bin/python -c "import ast; ast.parse(open('app.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: AppKit window with text area, progress bar, and buttons"
```

---

### Task 6: Entry point and first run

**Files:**
- Create: `main.py`

- [ ] **Step 1: Create `main.py`**

```python
"""
main.py
Entry point: launch TranscriptVoice.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from AppKit import NSApplication, NSApp
from Foundation import NSAutoreleasePool
from app import AppDelegate


def main():
    pool = NSAutoreleasePool.alloc().init()
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(0)   # NSApplicationActivationPolicyRegular
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    app.run()
    del pool


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the app**

```bash
venv/bin/python main.py
```

Expected: window opens. Paste some text and click Play. Verify:
- Chinese text → spoken in Chinese (Tingting voice)
- English text → spoken in English (Samantha voice)
- Progress bar fills sentence by sentence
- Stop button kills playback immediately
- Status shows `Reading...` → `Done`
- `Nuke.Yu` visible bottom-right

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: entry point, TranscriptVoice MVP1 complete"
```

---

### Task 7: Final checks and push

- [ ] **Step 1: Run full test suite**

```bash
venv/bin/pytest tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Create GitHub repo and push**

```bash
gh repo create TranscriptVoice --public --source=. --remote=origin --push
```

If `gh` is not available:
```bash
git remote add origin https://github.com/nuke-yu/TranscriptVoice.git
git push -u origin main
```
