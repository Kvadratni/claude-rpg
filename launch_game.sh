#!/bin/bash
# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Auto-install MCP server if needed
echo "🔧 Ensuring MCP server is installed..."
python3 install_mcp.py

# Launch the game
echo "🚀 Launching RPG game..."
uv run goose-rpg &

# Wait a moment for the game to start
sleep 1

# Bring the game window to front (macOS)
osascript -e 'tell application "Python" to activate' 2>/dev/null || true
