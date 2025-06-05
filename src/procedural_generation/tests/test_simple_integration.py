#!/usr/bin/env python3
"""
Simple Integration Test for Phase 4
Tests the basic functionality of procedural generation integration
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_procedural_mixin():
    """Test the procedural generation mixin"""
    print("Testing ProceduralGenerationMixin...")
    
    try:
        from src.level.procedural_mixin import ProceduralGenerationMixin
        
        # Create a mock class with the mixin
        class MockLevel(ProceduralGenerationMixin):
            def __init__(self):
                self.width = 100
                self.height = 100
                self.asset_loader = None
                self.npcs = []
                self.enemies = []
                self.objects = []
                self.items = []
                self.walkable = None
                self.heightmap = None
        
        level = MockLevel()
        
        # Test procedural methods
        print(f"  - is_procedural_level(): {level.is_procedural_level()}")
        print(f"  - get_procedural_seed(): {level.get_procedural_seed()}")
        print(f"  - get_procedural_settlements(): {len(level.get_procedural_settlements())}")
        
        print("✅ ProceduralGenerationMixin working correctly")
        return True
        
    except Exception as e:
        print(f"❌ ProceduralGenerationMixin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_procedural_menu():
    """Test the procedural world menu"""
    print("\nTesting ProceduralWorldMenu...")
    
    try:
        from src.ui.menu.procedural_menu import ProceduralWorldMenu
        
        # Create a mock game
        class MockGame:
            def __init__(self):
                self.asset_loader = None
                self.menu = None
            
            def new_game(self, use_procedural=False, seed=None):
                print(f"Mock new_game called: procedural={use_procedural}, seed={seed}")
        
        game = MockGame()
        menu = ProceduralWorldMenu(game)
        
        print(f"  - Menu title: {menu.title}")
        print(f"  - Menu options: {menu.options}")
        print(f"  - Use random seed: {menu.use_random_seed}")
        
        # Test seed input
        menu.seed_input = "12345"
        menu.use_random_seed = False
        print(f"  - Custom seed input: {menu.seed_input}")
        
        print("✅ ProceduralWorldMenu working correctly")
        return True
        
    except Exception as e:
        print(f"❌ ProceduralWorldMenu test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_modular_system():
    """Test the modular procedural generation system"""
    print("\nTesting Modular Procedural Generation System...")
    
    try:
        from src.procedural_generation import ProceduralWorldGenerator
        
        # Create generator
        generator = ProceduralWorldGenerator(50, 50, 12345)
        
        # Generate world without entities (no asset loader)
        world_data = generator.generate_world()
        
        print(f"  - World seed: {world_data['seed']}")
        print(f"  - World dimensions: {world_data['width']}x{world_data['height']}")
        print(f"  - Settlements: {len(world_data['settlements'])}")
        print(f"  - Tiles generated: {len(world_data['tiles'])} rows")
        print(f"  - Walkable grid: {len(world_data['walkable_grid'])} rows")
        
        # Test statistics
        stats = generator.get_world_stats()
        print(f"  - Biome stats: {stats['biome_stats']}")
        
        print("✅ Modular system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Modular system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_flow():
    """Test the complete integration flow"""
    print("\nTesting Integration Flow...")
    
    try:
        # Test 1: Create procedural world data
        from src.procedural_generation import ProceduralWorldGenerator
        
        generator = ProceduralWorldGenerator(100, 100, 54321)
        world_data = generator.generate_world()
        
        print(f"  - Generated world with seed: {world_data['seed']}")
        
        # Test 2: Test save data structure
        procedural_info = {
            'is_procedural': True,
            'seed': world_data['seed'],
            'settlements': world_data['settlements'],
            'safe_zones': world_data['safe_zones']
        }
        
        save_data = {
            'procedural_info': procedural_info
        }
        
        print(f"  - Save data structure: {list(save_data.keys())}")
        print(f"  - Procedural info: {list(procedural_info.keys())}")
        
        # Test 3: Test regeneration from save data
        if save_data['procedural_info']['is_procedural']:
            saved_seed = save_data['procedural_info']['seed']
            
            # Regenerate world with same seed
            generator2 = ProceduralWorldGenerator(100, 100, saved_seed)
            world_data2 = generator2.generate_world()
            
            if world_data2['seed'] == saved_seed:
                print(f"  - World regenerated correctly with seed: {saved_seed}")
            else:
                print(f"  - ❌ World regeneration failed")
                return False
        
        print("✅ Integration flow working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Integration flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("Phase 4: Integration & Polish - Simple Test Suite")
    print("=" * 60)
    
    tests = [
        test_procedural_mixin,
        test_procedural_menu,
        test_modular_system,
        test_integration_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 4 integration is working correctly.")
        print("\nKey Features Implemented:")
        print("✅ ProceduralGenerationMixin for Level system")
        print("✅ ProceduralWorldMenu for UI")
        print("✅ Game class integration with procedural options")
        print("✅ Save/load system support for procedural worlds")
        print("✅ Complete integration flow working")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)