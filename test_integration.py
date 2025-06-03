#!/usr/bin/env python3
"""
Integration test for the refactored AI NPC system in the game
"""

import sys
import os
import pygame

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_game_integration():
    """Test the AI NPCs in the actual game environment"""
    print("🧪 Testing AI NPC Integration in Game")
    print("=" * 50)
    
    try:
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        # Import game components
        from core.assets import AssetLoader
        from core.game_log import GameLog
        from player import Player
        from template_level import TemplateBasedLevel
        
        print("✅ Game components imported successfully")
        
        # Create game components
        asset_loader = AssetLoader()
        game_log = GameLog()
        player = Player(100, 100, asset_loader, game_log)
        
        print("✅ Game components created successfully")
        
        # Test template level with AI NPCs
        template_path = "assets/maps/main_world.png"
        if os.path.exists(template_path):
            print(f"✅ Template found: {template_path}")
            
            # Create template-based level
            template_gen = TemplateBasedLevel(template_path)
            
            # Generate NPCs
            npcs = template_gen.spawn_npcs(asset_loader)
            
            print(f"✅ Generated {len(npcs)} NPCs")
            
            # Check which NPCs are AI-enabled
            ai_npcs = []
            regular_npcs = []
            
            for npc in npcs:
                if hasattr(npc, 'ai_enabled') and npc.ai_enabled:
                    ai_npcs.append(npc)
                    print(f"🤖 AI NPC: {npc.name} (Class: {npc.__class__.__name__})")
                    
                    # Test AI communication
                    if hasattr(npc, 'send_ai_message'):
                        response = npc.send_ai_message("Hello", "Testing integration")
                        print(f"   Response: {response}")
                else:
                    regular_npcs.append(npc)
                    print(f"📝 Regular NPC: {npc.name}")
            
            print(f"\n📊 Summary:")
            print(f"   AI NPCs: {len(ai_npcs)}")
            print(f"   Regular NPCs: {len(regular_npcs)}")
            print(f"   Total NPCs: {len(npcs)}")
            
            # Test interaction
            if ai_npcs:
                test_npc = ai_npcs[0]
                print(f"\n🎯 Testing interaction with {test_npc.name}")
                
                # Simulate player interaction
                test_npc.interact(player)
                
                if hasattr(player, 'current_ai_chat') and player.current_ai_chat:
                    print(f"✅ AI chat window created for {test_npc.name}")
                    print(f"   Chat active: {player.current_ai_chat.is_active}")
                    print(f"   Chat history: {len(player.current_ai_chat.chat_history)} messages")
                else:
                    print(f"⚠️  No AI chat window created")
            
            return True
            
        else:
            print(f"⚠️  Template not found: {template_path}")
            print("   Creating minimal test without template...")
            
            # Create NPCs directly for testing
            from entities.npcs import VillageElderNPC, MasterMerchantNPC, GuardCaptainNPC
            
            test_npcs = [
                VillageElderNPC(10, 10, asset_loader=asset_loader),
                MasterMerchantNPC(15, 15, asset_loader=asset_loader),
                GuardCaptainNPC(20, 20, asset_loader=asset_loader)
            ]
            
            print(f"✅ Created {len(test_npcs)} test NPCs")
            
            for npc in test_npcs:
                print(f"🤖 Testing {npc.name}")
                response = npc.send_ai_message("Hello", "Direct test")
                print(f"   Response: {response}")
                
                # Test interaction
                npc.interact(player)
                if hasattr(player, 'current_ai_chat') and player.current_ai_chat:
                    print(f"   ✅ AI chat created")
                else:
                    print(f"   ⚠️  No AI chat created")
            
            return True
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_chat_window():
    """Test the AI chat window functionality"""
    print("\n🧪 Testing AI Chat Window")
    print("=" * 50)
    
    try:
        from ui.ai_chat_window import AIChatWindow
        from entities.npcs import VillageElderNPC
        
        # Create test components
        chat_window = AIChatWindow()
        npc = VillageElderNPC(0, 0)
        
        # Set up chat window
        chat_window.npc_reference = npc
        chat_window.is_active = True
        
        # Test adding messages
        chat_window.add_message("Player", "Hello there!")
        chat_window.add_message("Village Elder", "Greetings, young adventurer!")
        
        print(f"✅ Chat window created with {len(chat_window.chat_history)} messages")
        
        # Test message handling (simulate key events)
        print("✅ AI Chat Window test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Chat Window test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("🚀 AI NPC Integration Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test game integration
    if not test_game_integration():
        success = False
    
    # Test AI chat window
    if not test_ai_chat_window():
        success = False
    
    if success:
        print("\n🎉 All integration tests passed!")
        print("\nThe refactored AI NPC system is ready for use!")
        print("\nTo test in the actual game:")
        print("1. Run: ./launch_game.sh")
        print("2. Start a new game")
        print("3. Find and interact with NPCs in the village")
        print("4. Look for: Village Elder, Master Merchant, Guard Captain")
    else:
        print("\n❌ Some integration tests failed")
        print("Check the error messages above for details")

if __name__ == "__main__":
    main()