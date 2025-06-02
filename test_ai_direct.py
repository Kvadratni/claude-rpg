#!/usr/bin/env python3
"""
Test the AI integration imports directly
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔧 Testing AI integration imports...")

try:
    from src.ai_integration import EnhancedGooseRecipeIntegration, RECIPES_AVAILABLE
    print(f"✅ Successfully imported AI integration")
    print(f"🔧 RECIPES_AVAILABLE: {RECIPES_AVAILABLE}")
    
    # Test creating an integration
    integration = EnhancedGooseRecipeIntegration("Village Elder")
    print(f"✅ Successfully created integration for Village Elder")
    
    # Test sending a message
    response = integration.send_message("Hello, who are you?", "Player is testing the system")
    print(f"✅ Got response: {response}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()