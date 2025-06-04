#!/bin/bash
cd /Users/mnovich/Development/claude-rpg
uv run goose-rpg &
# Wait a moment for the game to start
sleep 1
# Bring the game window to front (macOS)
osascript -e 'tell application "Python" to activate' 2>/dev/null || true
