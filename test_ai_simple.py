#!/usr/bin/env python3
"""
Simple test to verify AI integration works
"""

import sys
import os
sys.path.append('src')

# Test the basic AI integration
def test_basic_ai():
    print("🧪 Testing basic AI integration...")
    
    from ai_integration import GooseRecipeIntegration
    
    ai = GooseRecipeIntegration("Village Elder")
    
    print("📤 Sending test message...")
    response = ai.send_message("Hello, who are you?", "Player is in the village center")
    
    print(f"🤖 Response: {response}")
    
    if "Village Elder" in response or len(response) > 20:
        print("✅ AI integration working!")
    else:
        print("⚠️  AI might be using fallback")

if __name__ == "__main__":
    test_basic_ai()
