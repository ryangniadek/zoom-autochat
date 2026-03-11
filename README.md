# Zoom Auto-Chat
Vibe-Coded Ryan Gniadek

Automatically sends a message in the Zoom chat every time you join a meeting.

**Default message:**
> I'm using Notion AI to transcribe this meeting and generate notes.

---

## Setup (one-time)

### Step 1 — Open Terminal
Press **Cmd + Space**, type `Terminal`, press Enter.

### Step 2 — Clone the repo and run the installer
In Terminal, run:

```bash
git clone https://github.com/ryangniadek/zoom-autochat.git
cd zoom-autochat
./install.sh
```

### Step 3 — Grant Accessibility access
The installer will open **System Settings → Privacy & Security → Accessibility** automatically, and print the exact Python path you need to add.

1. Click the lock icon and enter your password.
2. Click **+** and add the Python binary printed by the installer (e.g. `/usr/bin/python3` or `/opt/homebrew/bin/python3`).
   *(If you see `Terminal` already listed, make sure its toggle is ON.)*

That's it. The monitor runs silently in the background and restarts automatically every time you log in.

---

## How it works

### Process detection
Every 3 seconds, a Python script polls for Zoom's `CptHost` process using `pgrep`. `CptHost` is the subprocess Zoom spawns only while you are inside an active meeting — it is not present when Zoom is idle in the menu bar. This makes it a reliable signal for "meeting started" without requiring any Zoom API or integration.

### Meeting join detection
The script tracks a `was_in_meeting` boolean across poll cycles. A rising edge (`False → True`) triggers the send flow. It then waits 5 seconds before acting, giving the Zoom UI time to fully render the chat panel.

### Sending the message
The send flow runs entirely through macOS automation:

1. **Clipboard** — The message is written to the system clipboard via `pbcopy`.
2. **AppleScript + Accessibility** — An AppleScript activates `zoom.us`, then uses `System Events` to:
   - Open the chat panel via **View → Chat** in Zoom's menu bar (with a keyboard-shortcut fallback).
   - Paste the clipboard contents (`⌘V`).
   - Press Return to send.

This approach requires macOS **Accessibility permission** for the Python binary because `System Events` is driving another application's UI. The permission is granted once in System Settings and persists.

### Background execution — LaunchAgent
The installer registers the script as a **launchd LaunchAgent** (`~/Library/LaunchAgents/com.<username>.zoom-autochat.plist`) with two flags:

| Flag | Effect |
|------|--------|
| `RunAtLoad: true` | Starts automatically on login |
| `KeepAlive: true` | launchd restarts the process if it ever crashes |

The process runs under your user session (not root), so it has access to the GUI and the clipboard.

### Log files
| Path | Contents |
|------|----------|
| `/tmp/zoom-autochat.log` | Info and error messages from the Python script |
| `/tmp/zoom-autochat-error.log` | stderr captured by launchd |

---

## Customise the message

Open `~/Library/Application Support/ZoomAutoChat/zoom-autochat.py` in any text editor and change the `MESSAGE` line near the top:

```python
MESSAGE = "Your custom message here."
```

Save the file, then restart the monitor:
```bash
launchctl stop com.$(whoami).zoom-autochat
launchctl start com.$(whoami).zoom-autochat
```

---

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.$(whoami).zoom-autochat.plist
rm ~/Library/LaunchAgents/com.$(whoami).zoom-autochat.plist
rm -rf ~/Library/Application\ Support/ZoomAutoChat
```

---

## Troubleshoot

- **Message not sending?** Check Accessibility permissions (Step 3 above). The Python binary in the list must match the one printed by the installer.
- **View logs:** `tail -f /tmp/zoom-autochat.log`
- **Check it's running:** `launchctl list | grep zoom-autochat`
- **Restart the monitor:** `launchctl stop com.$(whoami).zoom-autochat && launchctl start com.$(whoami).zoom-autochat`
