"""
app.py
Native macOS window: text area, progress bar, Play/Stop buttons.
"""

import objc
from AppKit import (
    NSObject, NSApplication, NSApp,
    NSWindow, NSButton, NSTextField, NSScrollView, NSTextView,
    NSProgressIndicator,
    NSColor, NSFont, NSMakeRect,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable,
    NSBackingStoreBuffered, NSBezelStyleRounded, NSTextAlignmentRight,
    NSFloatingWindowLevel,
)

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
        self._build_window()
        self._window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def _build_window(self):
        style = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                 NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(100, 100, 420, 380), style, NSBackingStoreBuffered, False
        )
        self._window.setTitle_("🔊 TranscriptVoice")
        self._window.center()
        self._window.setLevel_(NSFloatingWindowLevel)

        root = self._window.contentView()

        # Text area
        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(14, 88, 392, 240))
        scroll.setHasVerticalScroller_(True)
        scroll.setBorderType_(1)
        self._text_view = NSTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, 392, 240))
        self._text_view.setFont_(NSFont.systemFontOfSize_(14))
        scroll.setDocumentView_(self._text_view)
        root.addSubview_(scroll)

        # Progress bar (system built-in)
        self._progress = NSProgressIndicator.alloc().initWithFrame_(
            NSMakeRect(14, 78, 392, 8))
        self._progress.setStyle_(1)           # bar style
        self._progress.setIndeterminate_(False)
        self._progress.setMinValue_(0.0)
        self._progress.setMaxValue_(1.0)
        self._progress.setDoubleValue_(0.0)
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

    def applicationShouldHandleReopen_hasVisibleWindows_(self, app, hasVisibleWindows):
        if not hasVisibleWindows:
            self._window.makeKeyAndOrderFront_(None)
        return True

    def onPlay_(self, sender):
        text = self._text_view.textStorage().string()
        if not text.strip():
            return
        self.applyState_("reading")
        self._speaker.start(text)

    def onStop_(self, sender):
        self._speaker.stop()
        self.applyState_("idle")

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
        self._progress.setDoubleValue_(frac)

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
            self._progress.setDoubleValue_(0.0)
        elif state == "idle":
            self._play_btn.setEnabled_(True)
            self._stop_btn.setEnabled_(False)
            self._status.setStringValue_("Idle")
            self._progress.setDoubleValue_(0.0)
        elif state == "done":
            self._play_btn.setEnabled_(True)
            self._stop_btn.setEnabled_(False)
            self._status.setStringValue_("Done")
            self._progress.setDoubleValue_(1.0)
