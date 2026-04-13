# TranscriptVoice — Design Spec

**Date:** 2026-04-13
**Version:** MVP1

---

## Overview

A minimal macOS desktop app. The user pastes text into a window, clicks Play, and the app reads it aloud. Supports Chinese and English. A progress bar shows reading position. Stop kills playback immediately.

---

## Architecture

Three files, each with one responsibility:

| File | Responsibility |
|------|---------------|
| `main.py` | Entry point — launches the AppKit application |
| `app.py` | AppKit window, text area, progress bar, buttons |
| `speaker.py` | Wraps macOS `say` command — play, stop, progress tracking |

### Data Flow

```
User pastes text → clicks Play
→ speaker.py splits text into sentences
→ reads each sentence via `say` one by one (subprocess)
→ progress bar updates after each sentence completes
→ Stop button kills the current `say` process immediately
→ status label shows Idle / Reading... / Done
```

Sentence-by-sentence execution (rather than passing all text at once to `say`) is what makes progress tracking possible.

---

## TTS Engine

**macOS `say` command** via `subprocess`.

- Zero dependencies, fully offline
- Auto-selects Chinese voice when Chinese characters are detected, English voice otherwise
- Stop is instant: `process.kill()`
- Voice used: system default (Tingting for Chinese, Samantha for English)

Language detection: if the sentence contains any CJK Unicode characters (`\u4e00–\u9fff`), use `-v Tingting`; otherwise use `-v Samantha`.

---

## UI

- **Window size:** 420 × 380px, resizable
- **Always on top:** `NSWindowLevel` set to floating so it stays above other apps
- **Text area:** 210px tall, white background, placeholder `"Paste your text here...\n\n支持中英文，自动识别语言。"`
- **Progress bar:** 4px tall, blue fill, sits between text area and buttons
- **Buttons:**
  - Play (blue `#0071e3`) — disabled while reading
  - Stop (gray) — disabled while idle
- **Status label:** right-aligned, small gray text — `Idle` / `Reading...` / `Done`
- **Signature:** `Nuke.Yu` bottom-right, tertiary gray

---

## Module Details

### `speaker.py`

```
class Speaker:
    start(text)      # splits into sentences, reads one by one in background thread
    stop()           # kills current subprocess, clears queue
    on_progress      # callback(current_sentence, total_sentences)
    on_done          # callback() — called when all sentences finish
```

Sentence splitting: split on `。`, `.`, `！`, `!`, `？`, `?`, `\n`. Strip empty strings.

### `app.py`

- `AppDelegate` — `applicationDidFinishLaunching_` builds the window
- `onPlay_` — calls `speaker.start(text)`
- `onStop_` — calls `speaker.stop()`
- `updateProgress_` — called from main thread via `performSelectorOnMainThread`, updates bar and status

---

## File Structure

```
TranscriptVoice/
├── main.py
├── app.py
├── speaker.py
├── requirements.txt       # pyobjc-framework-Cocoa only
└── docs/
    └── superpowers/specs/
        └── 2026-04-13-transcript-voice-design.md
```

---

## Out of Scope (MVP1)

- Speed control
- Voice selection UI
- Pause / resume
- Menu bar mode
- Export to audio file
