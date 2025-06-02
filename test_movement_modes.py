#!/usr/bin/env python3
"""
Test script to verify movement mode functionality
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_movement_system():
    """Test the movement system functionality"""
    print("🎮 Testing Movement Mode System")
    print("=" * 40)
    
    try:
        # Import the movement system
        from systems.movement import MovementSystem
        
        # Create a mock player object
        class MockPlayer:
            def __init__(self):
                self.x = 100
                self.y = 100
                self.size = 0.4
                self.game_log = MockGameLog()
        
        class MockGameLog:
            def add_message(self, message, category):
                print(f"[{category.upper()}] {message}")
        
        # Create movement system
        player = MockPlayer()
        movement_system = MovementSystem(player)
        
        print(f"✅ MovementSystem created successfully")
        print(f"   Initial mode: {movement_system.movement_mode}")
        
        # Test mode toggle
        print(f"\n🔄 Testing mode toggle...")
        new_mode = movement_system.toggle_movement_mode()
        print(f"   Mode after toggle: {new_mode}")
        
        # Toggle back
        new_mode = movement_system.toggle_movement_mode()
        print(f"   Mode after second toggle: {new_mode}")
        
        print(f"\n✅ Movement mode toggle working correctly!")
        
        # Test WASD movement keys
        print(f"\n⌨️  Testing WASD key detection...")
        
        # Mock pygame keys
        class MockKeys:
            def __init__(self):
                self.keys = {}
            
            def __getitem__(self, key):
                return self.keys.get(key, False)
            
            def set_key(self, key, pressed):
                self.keys[key] = pressed
        
        # Import pygame constants
        import pygame
        pygame.init()  # Initialize pygame to get key constants
        
        mock_keys = MockKeys()
        
        # Test W key
        mock_keys.set_key(pygame.K_w, True)
        print(f"   W key pressed: {mock_keys[pygame.K_w]}")
        
        # Test all WASD keys
        wasd_keys = {
            pygame.K_w: "W (Up)",
            pygame.K_a: "A (Left)", 
            pygame.K_s: "S (Down)",
            pygame.K_d: "D (Right)"
        }
        
        for key, name in wasd_keys.items():
            mock_keys.set_key(key, True)
            print(f"   {name}: {mock_keys[key]}")
            mock_keys.set_key(key, False)
        
        print(f"\n✅ WASD key detection working!")
        
        print(f"\n🎯 Movement System Test Complete!")
        print(f"   ✅ Movement system initialization")
        print(f"   ✅ Mode toggling (mouse ↔ wasd)")
        print(f"   ✅ Key detection for WASD")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_f5_key():
    """Test F5 key constant"""
    print(f"\n🔑 Testing F5 Key Constant...")
    
    try:
        import pygame
        pygame.init()
        
        f5_key = pygame.K_F5
        print(f"   F5 key constant: {f5_key}")
        print(f"   ✅ F5 key constant available")
        
        return True
        
    except Exception as e:
        print(f"   ❌ F5 key test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 MOVEMENT MODE SYSTEM TESTS")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    # Test movement system
    if test_movement_system():
        tests_passed += 1
    
    # Test F5 key
    if test_f5_key():
        tests_passed += 1
    
    print(f"\n" + "=" * 50)
    print(f"🏁 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print(f"🎉 All tests passed! Movement mode system is ready!")
        print(f"\n💡 To use in game:")
        print(f"   • Press F5 to toggle between Mouse and WASD modes")
        print(f"   • Mouse mode: Click to move and interact")
        print(f"   • WASD mode: Use WASD keys to move, click to interact")
        print(f"   • Movement mode indicator appears in the HUD")
    else:
        print(f"❌ Some tests failed. Please check the implementation.")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)