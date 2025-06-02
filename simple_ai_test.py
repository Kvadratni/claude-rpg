#!/usr/bin/env python3
"""
Simple test for AI integration without pygame
"""

import subprocess
import os
import re

def test_goose_command():
    print("🧪 Testing Goose CLI command...")
    
    # Set up environment with GPT-4o-mini
    env = os.environ.copy()
    env["GOOSE_MODEL"] = "goose-gpt-4o-mini"
    
    # Create a simple NPC prompt
    npc_prompt = """You are Village Elder, an NPC in a fantasy RPG. 

Character: Village Elder
Context: Player is in the village center
Player says: "Hello, who are you?"

Respond as Village Elder in 1-2 sentences. Stay in character and be helpful."""
    
    # Use goose run with text input
    cmd = [
        "goose", "run",
        "--text", npc_prompt,
        "--no-session"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Goose command successful!")
            print(f"📤 Raw output:\n{result.stdout}")
            
            # Try to extract clean response
            lines = result.stdout.strip().split('\n')
            clean_lines = []
            for line in lines:
                if line.strip() and not any(skip in line for skip in ['running without session', 'working directory']):
                    # Remove ANSI codes
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
                    if clean_line.strip():
                        clean_lines.append(clean_line.strip())
            
            print(f"🤖 Cleaned response: {' '.join(clean_lines[-3:])}")  # Last few lines
        else:
            print(f"❌ Goose command failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_goose_command()
