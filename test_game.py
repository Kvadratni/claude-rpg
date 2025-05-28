#!/usr/bin/env python3
"""
Simple test script to verify game components work
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all modules can be imported"""
    try:
        from src.game import Game
        from src.player import Player
        from src.level import Level
        from src.entity import Entity, NPC, Enemy, Item
        from src.isometric import IsometricRenderer
        from src.inventory import Inventory
        from src.save_system import SaveSystem
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic game functionality"""
    try:
        from src.player import Player
        from src.entity import Item
        from src.isometric import IsometricRenderer
        from src.inventory import Inventory
        from src.save_system import SaveSystem
        
        # Test player creation
        player = Player(10, 10)
        assert player.x == 10
        assert player.y == 10
        assert player.health == 100
        print("✓ Player creation works")
        
        # Test isometric renderer
        iso = IsometricRenderer()
        iso_x, iso_y = iso.cart_to_iso(10, 10)
        cart_x, cart_y = iso.iso_to_cart(iso_x, iso_y)
        assert abs(cart_x - 10) < 0.1
        assert abs(cart_y - 10) < 0.1
        print("✓ Isometric coordinate conversion works")
        
        # Test inventory
        inventory = Inventory()
        item = Item(0, 0, "Test Item")
        assert inventory.add_item(item)
        assert len(inventory.items) == 1
        print("✓ Inventory system works")
        
        # Test save system
        save_system = SaveSystem()
        test_data = {"test": "data"}
        assert save_system.save_game("test_save", test_data)
        loaded_data = save_system.load_game("test_save")
        assert loaded_data["test"] == "data"
        print("✓ Save system works")
        
        return True
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Claude RPG tests...")
    
    tests_passed = 0
    total_tests = 2
    
    if test_imports():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Game is ready to run.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())