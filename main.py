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
