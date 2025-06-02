#!/usr/bin/env python3
"""
Test script for AI integration
"""

import sys
import os
sys.path.append('src')

from ai_integration import GooseRecipeIntegration

def test_ai_integration():
    print("🧪 Testing AI Integration...")
    
    # Create AI integration for a test NPC
    ai = GooseRecipeIntegration("Village Elder")
    
    # Test sending a message
    print("📤 Sending test message...")
    response = ai.send_message("Hello, who are you?", "Player is in the village center")
    
    print(f"🤖 AI Response: {response}")
    
    # Test another message
    response2 = ai.send_message("What can you tell me about this place?", "Player is exploring")
    print(f"🤖 AI Response 2: {response2}")
    
    print("✅ AI Integration test completed!")

if __name__ == "__main__":
    test_ai_integration()
