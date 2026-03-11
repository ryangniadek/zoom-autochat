#!/bin/bash
# Zoom Auto-Chat Installer
# Run this once to set up the background monitor.

set -euo pipefail

SUPPORT_DIR="$HOME/Library/Application Support/ZoomAutoChat"
PLIST_LABEL="com.$(whoami).zoom-autochat"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_LABEL.plist"
INSTALLED_SCRIPT="$SUPPORT_DIR/zoom-autochat.py"
SOURCE_SCRIPT="$(cd "$(dirname "$0")" && pwd)/zoom-autochat.py"

echo "=== Zoom Auto-Chat Installer ==="
echo

# Check python3 is available
if ! command -v python3 &>/dev/null; then
    echo "✗ python3 not found. Install it via: xcode-select --install"
    exit 1
fi
PYTHON3="$(command -v python3)"

# Copy script
mkdir -p "$SUPPORT_DIR"
cp "$SOURCE_SCRIPT" "$INSTALLED_SCRIPT"
echo "✓ Script installed to: $INSTALLED_SCRIPT"

# Write LaunchAgent plist
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>             <string>$PLIST_LABEL</string>
  <key>ProgramArguments</key>  <array>
    <string>$PYTHON3</string>
    <string>$INSTALLED_SCRIPT</string>
  </array>
  <key>RunAtLoad</key>         <true/>
  <key>KeepAlive</key>         <true/>
  <key>StandardOutPath</key>   <string>/tmp/zoom-autochat.log</string>
  <key>StandardErrorPath</key> <string>/tmp/zoom-autochat-error.log</string>
</dict>
</plist>
PLIST
echo "✓ LaunchAgent created"

# Load (or reload) the agent
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load -w "$PLIST_PATH"
echo "✓ Background monitor is running"

echo
echo "=== Action required: grant Accessibility access ==="
echo
echo "The monitor uses keyboard automation to type in Zoom chat."
echo "macOS requires you to approve this once:"
echo
echo "  1. The System Settings window will open automatically."
echo "  2. Go to Privacy & Security → Accessibility."
echo "  3. Click the lock to make changes."
echo "  4. Click '+' and add:  $PYTHON3"
echo "     (If Terminal appears in the list, enable it too.)"
echo
echo "Opening Privacy & Security now…"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"

echo
echo "All done! The monitor will run automatically every time you log in."
echo "Logs: /tmp/zoom-autochat.log"
