#!/usr/bin/env python3
"""
Zoom Auto-Chat
Automatically sends a message in the Zoom chat when you join a meeting.
"""

import subprocess
import time
import sys
import logging
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────
MESSAGE = "I'm using Notion AI to transcribe this meeting and generate notes."
CHECK_INTERVAL = 3   # seconds between checks
JOIN_DELAY = 5       # seconds to wait after detecting a new meeting before sending
# ──────────────────────────────────────────────────────────────────────────────

log_path = Path("/tmp/zoom-autochat.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger()


def is_in_meeting() -> bool:
    """Return True if Zoom's CptHost process is running (only active during meetings)."""
    result = subprocess.run(["pgrep", "-x", "CptHost"], capture_output=True)
    return result.returncode == 0


def send_chat_message(message: str) -> bool:
    """Copy message to clipboard, then paste it into Zoom chat and send."""

    # 1. Put the message on the macOS clipboard
    proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    proc.communicate(message.encode("utf-8"))

    # 2. Bring Zoom to front, open chat, paste, and press Return
    applescript = """\
tell application "zoom.us"
    activate
end tell
delay 0.5
tell application "System Events"
    tell process "zoom.us"
        -- Open chat via the View menu (stable across Zoom versions)
        try
            click menu item "Chat" of menu "View" of menu bar 1
        on error
            -- Fallback: keyboard shortcut
            keystroke "h" using {command down, shift down}
        end try
        delay 1.0
        -- Paste the clipboard content
        keystroke "v" using {command down}
        delay 0.3
        -- Return sends the message
        key code 36
    end tell
end tell
"""
    result = subprocess.run(
        ["osascript", "-e", applescript],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("AppleScript error: %s", result.stderr.strip())
        return False
    return True


def main():
    log.info("Zoom Auto-Chat monitor started (checking every %ds)", CHECK_INTERVAL)
    was_in_meeting = False

    while True:
        try:
            in_meeting = is_in_meeting()

            if in_meeting and not was_in_meeting:
                log.info("Meeting detected — waiting %ds before sending…", JOIN_DELAY)
                time.sleep(JOIN_DELAY)

                if send_chat_message(MESSAGE):
                    log.info("✓ Message sent.")
                else:
                    log.warning("✗ Could not send message. Check Accessibility permissions.")

            was_in_meeting = in_meeting
            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log.info("Stopped.")
            sys.exit(0)
        except Exception as exc:
            log.exception("Unexpected error: %s", exc)
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
