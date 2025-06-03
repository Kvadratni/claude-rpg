#!/usr/bin/env python3
"""
Test script for the refactored AI NPC system
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_npc_creation():
    """Test creating NPCs with embedded recipes"""
    print("🧪 Testing NPC Creation with Embedded Recipes")
    print("=" * 50)
    
    try:
        from entities.npcs import VillageElderNPC, MasterMerchantNPC, GuardCaptainNPC
        
        # Create NPCs
        village_elder = VillageElderNPC(x=10, y=15)
        master_merchant = MasterMerchantNPC(x=20, y=25)
        guard_captain = GuardCaptainNPC(x=30, y=35)
        
        npcs = [village_elder, master_merchant, guard_captain]
        
        for npc in npcs:
            print(f"\n✅ Created {npc.name}")
            print(f"   - AI Enabled: {npc.ai_enabled}")
            print(f"   - Has Recipe: {npc.recipe is not None}")
            print(f"   - Session Name: {npc.session_name}")
            
            if npc.recipe:
                print(f"   - Recipe Title: {npc.recipe.get('title', 'N/A')}")
                print(f"   - Recipe Version: {npc.recipe.get('version', 'N/A')}")
        
        print(f"\n🎉 Successfully created {len(npcs)} AI NPCs!")
        return npcs
        
    except Exception as e:
        print(f"❌ Error creating NPCs: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_ai_communication():
    """Test AI communication with NPCs"""
    print("\n🧪 Testing AI Communication")
    print("=" * 50)
    
    npcs = test_npc_creation()
    if not npcs:
        print("❌ Cannot test AI communication - NPC creation failed")
        return
    
    # Test messages
    test_messages = [
        "Hello, who are you?",
        "Can you help me?",
        "What do you know about this place?"
    ]
    
    for npc in npcs:
        print(f"\n🗣️  Testing {npc.name}:")
        
        for message in test_messages:
            print(f"   Player: {message}")
            try:
                response = npc.send_ai_message(message, "Player is testing the system")
                print(f"   {npc.name}: {response}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"   💬 Conversation history: {len(npc.conversation_history)} messages")

def test_fallback_responses():
    """Test fallback response system"""
    print("\n🧪 Testing Fallback Response System")
    print("=" * 50)
    
    try:
        from entities.npcs import VillageElderNPC
        
        # Create NPC and force fallback mode
        npc = VillageElderNPC(x=0, y=0)
        npc.use_fallback = True
        
        test_messages = ["hello", "who", "help", "quest", "bye", "random message"]
        
        print(f"Testing fallback responses for {npc.name}:")
        for message in test_messages:
            response = npc.send_ai_message(message)
            print(f"   '{message}' → '{response}'")
            
    except Exception as e:
        print(f"❌ Error testing fallback: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("🚀 Refactored AI NPC System Test")
    print("=" * 50)
    
    test_npc_creation()
    test_ai_communication()
    test_fallback_responses()
    
    print("\n✅ All tests completed!")
    print("\nTo integrate with the game:")
    print("1. Update level generation to use new NPC classes")
    print("2. Update game.py to handle AI chat events")
    print("3. Test in-game interactions")

if __name__ == "__main__":
    main()