#!/usr/bin/env python3
"""
Test the new AI integration
"""

import subprocess
import os
import tempfile

def test_instructions_file():
    print("🧪 Testing Goose with instructions file...")
    
    # Create test prompt
    prompt = """You are Village Elder, an NPC in a fantasy RPG world.

ROLE GUIDELINES:
- You are Village Elder
- Stay in character at all times
- Respond naturally and helpfully
- Keep responses concise (1-2 sentences)
- Use medieval fantasy language appropriate for your role

- You are a wise village elder with knowledge of local history
- You give quests and advice to adventurers
- You speak with wisdom and authority

CURRENT CONTEXT: Player is in the village

PLAYER SAYS: "Hello, who are you?"

Respond as Village Elder in character:"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(prompt)
        temp_file = f.name
    
    try:
        # Set up environment
        env = os.environ.copy()
        env["GOOSE_MODEL"] = "goose-gpt-4o-mini"
        
        # Run goose with instructions file
        cmd = ["goose", "run", "--instructions", temp_file, "--no-session"]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Success!")
            print(f"📤 Output:\n{result.stdout}")
        else:
            print(f"❌ Failed: {result.stderr}")
            
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    test_instructions_file()
