#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
uv run goose-rpg &
# Wait a moment for the game to start
sleep 1
# Bring the game window to front (macOS)
osascript -e 'tell application "Python" to activate' 2>/dev/null || true
