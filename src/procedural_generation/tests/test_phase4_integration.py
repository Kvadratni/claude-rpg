#!/usr/bin/env python3
"""
Integration Test for Phase 4: Integration & Polish
Tests the integration of procedural generation with the refactored game architecture
"""

import sys
import os
import time

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pygame for testing without display
class MockPygame:
    KEYDOWN = 1
    K_ESCAPE = 2
    K_i = 3
    K_RETURN = 4
    
    class font:
        @staticmethod
        def Font(name, size):
            return MockFont()
    
    class display:
        @staticmethod
        def set_mode(size, flags=0):
            return MockSurface()
        
        @staticmethod
        def set_caption(caption):
            pass
        
        @staticmethod
        def flip():
            pass
    
    class time:
        @staticmethod
        def Clock():
            return MockClock()
    
    class key:
        @staticmethod
        def get_pressed():
            return {}

class MockFont:
    def render(self, text, antialias, color):
        return MockSurface()

class MockSurface:
    def get_width(self):
        return 800
    
    def get_height(self):
        return 600
    
    def get_rect(self, **kwargs):
        return MockRect()
    
    def fill(self, color):
        pass
    
    def blit(self, surface, rect):
        pass
    
    def set_alpha(self, alpha):
        pass

class MockRect:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 50
        self.left = 0
        self.right = 100
        self.top = 0
        self.bottom = 50
        self.center = (50, 25)
        self.centery = 25

class MockClock:
    def tick(self, fps):
        pass

# Mock pygame
sys.modules['pygame'] = MockPygame()

def test_level_integration():
    """Test Level class integration with procedural generation"""
    print("=" * 60)
    print("Testing Level Integration")
    print("=" * 60)
    
    try:
        # Import after mocking pygame
        from src.level import Level
        from src.core.assets import AssetLoader
        from src.core.game_log import GameLog
        from src.player import Player
        
        # Create mock objects
        asset_loader = AssetLoader()
        game_log = GameLog()
        player = Player(100, 100, asset_loader, game_log)
        
        print("✅ Imports successful")
        
        # Test template level creation (existing system)
        print("\n1. Testing Template Level Creation...")
        try:
            template_level = Level("test_template", player, asset_loader, None, use_procedural=False)
            print("✅ Template level created successfully")
        except Exception as e:
            print(f"❌ Template level creation failed: {e}")
            return False
        
        # Test procedural level creation
        print("\n2. Testing Procedural Level Creation...")
        try:
            procedural_level = Level("test_procedural", player, asset_loader, None, use_procedural=True, seed=12345)
            print("✅ Procedural level created successfully")
            
            # Test procedural methods
            is_procedural = procedural_level.is_procedural_level()
            seed = procedural_level.get_procedural_seed()
            settlements = procedural_level.get_procedural_settlements()
            
            print(f"  - Is procedural: {is_procedural}")
            print(f"  - Seed: {seed}")
            print(f"  - Settlements: {len(settlements)}")
            
            if is_procedural and seed == 12345:
                print("✅ Procedural level methods working correctly")
            else:
                print("❌ Procedural level methods not working correctly")
                return False
                
        except Exception as e:
            print(f"❌ Procedural level creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ Level integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Level integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_game_integration():
    """Test Game class integration with procedural generation"""
    print("\n" + "=" * 60)
    print("Testing Game Integration")
    print("=" * 60)
    
    try:
        from src.game import Game
        
        # Create game instance
        game = Game()
        print("✅ Game instance created")
        
        # Test template game creation
        print("\n1. Testing Template Game Creation...")
        try:
            game.new_game(use_procedural=False)
            print("✅ Template game created successfully")
            
            # Check if level was created
            if game.current_level and not game.current_level.is_procedural_level():
                print("✅ Template level properly initialized")
            else:
                print("❌ Template level not properly initialized")
                return False
                
        except Exception as e:
            print(f"❌ Template game creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test procedural game creation
        print("\n2. Testing Procedural Game Creation...")
        try:
            game.new_game(use_procedural=True, seed=54321)
            print("✅ Procedural game created successfully")
            
            # Check if procedural level was created
            if (game.current_level and 
                game.current_level.is_procedural_level() and 
                game.current_level.get_procedural_seed() == 54321):
                print("✅ Procedural level properly initialized")
            else:
                print("❌ Procedural level not properly initialized")
                return False
                
        except Exception as e:
            print(f"❌ Procedural game creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ Game integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Game integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_integration():
    """Test Menu integration with procedural generation"""
    print("\n" + "=" * 60)
    print("Testing Menu Integration")
    print("=" * 60)
    
    try:
        from src.ui.menu.procedural_menu import ProceduralWorldMenu
        from src.ui.menu.main_menu import MainMenu
        from src.game import Game
        
        # Create game instance
        game = Game()
        
        # Test main menu
        print("\n1. Testing Main Menu...")
        main_menu = MainMenu(game)
        
        # Check if procedural world option is in menu
        if "Procedural World" in main_menu.menu_items:
            print("✅ Procedural World option added to main menu")
        else:
            print("❌ Procedural World option not found in main menu")
            return False
        
        # Test procedural menu
        print("\n2. Testing Procedural World Menu...")
        procedural_menu = ProceduralWorldMenu(game)
        
        # Check menu options
        expected_options = ["Random Seed", "Custom Seed", "Generate World", "Back to Main Menu"]
        if procedural_menu.options == expected_options:
            print("✅ Procedural menu options correct")
        else:
            print(f"❌ Procedural menu options incorrect: {procedural_menu.options}")
            return False
        
        print("\n✅ Menu integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Menu integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_save_load_integration():
    """Test save/load integration with procedural worlds"""
    print("\n" + "=" * 60)
    print("Testing Save/Load Integration")
    print("=" * 60)
    
    try:
        from src.game import Game
        
        # Create game instance
        game = Game()
        
        # Create procedural game
        print("\n1. Creating Procedural Game...")
        game.new_game(use_procedural=True, seed=99999)
        
        if not game.current_level.is_procedural_level():
            print("❌ Failed to create procedural game")
            return False
        
        original_seed = game.current_level.get_procedural_seed()
        print(f"✅ Procedural game created with seed: {original_seed}")
        
        # Test save data generation
        print("\n2. Testing Save Data Generation...")
        try:
            save_data = {
                "player": game.player.get_save_data() if hasattr(game.player, 'get_save_data') else {},
                "level": game.current_level.get_save_data() if hasattr(game.current_level, 'get_save_data') else {}
            }
            
            # Add procedural info
            procedural_data = game.current_level.get_procedural_save_data()
            save_data["level"].update(procedural_data)
            
            print("✅ Save data generated successfully")
            
            # Check if procedural info is in save data
            if 'procedural_info' in save_data["level"]:
                procedural_info = save_data["level"]['procedural_info']
                if procedural_info.get('is_procedural') and procedural_info.get('seed') == original_seed:
                    print("✅ Procedural info correctly saved")
                else:
                    print("❌ Procedural info not correctly saved")
                    return False
            else:
                print("❌ Procedural info not found in save data")
                return False
                
        except Exception as e:
            print(f"❌ Save data generation failed: {e}")
            return False
        
        print("\n✅ Save/Load integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Save/Load integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all integration tests"""
    print("Phase 4: Integration & Polish - Test Suite")
    print("=" * 70)
    
    tests = [
        ("Level Integration", test_level_integration),
        ("Game Integration", test_game_integration),
        ("Menu Integration", test_menu_integration),
        ("Save/Load Integration", test_save_load_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"Integration Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! Phase 4 is working correctly.")
        return True
    else:
        print("❌ Some integration tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)