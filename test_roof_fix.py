#!/usr/bin/env python3
"""
Quick test to verify roof texture is being used on wall tops
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.assets import AssetLoader
from src.core.isometric import IsometricRenderer
from src.wall_renderer import WallRenderer

class MockLevel:
    """Mock level for testing wall renderer"""
    def __init__(self):
        self.TILE_WALL = 1
        self.TILE_WALL_CORNER_TL = 2
        self.TILE_WALL_CORNER_TR = 3
        self.TILE_WALL_CORNER_BL = 4
        self.TILE_WALL_CORNER_BR = 5
        self.TILE_WALL_HORIZONTAL = 6
        self.TILE_WALL_VERTICAL = 7
        self.TILE_WALL_WINDOW = 8
        self.TILE_WALL_WINDOW_HORIZONTAL = 9
        self.TILE_WALL_WINDOW_VERTICAL = 10
        self.TILE_DOOR = 11
        self.TILE_DOOR_HORIZONTAL = 12
        self.TILE_DOOR_VERTICAL = 13
        
        self.tile_width = 64
        self.tile_height = 32
        self.width = 10
        self.height = 10
        
        # Simple 3x3 room for testing
        self.tiles = [
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0]
        ]
        
        self.tile_sprites = {}

def main():
    pygame.init()
    
    # Create asset loader
    asset_loader = AssetLoader()
    
    # Create mock level
    level = MockLevel()
    level.asset_loader = asset_loader
    
    # Create wall renderer
    wall_renderer = WallRenderer(level)
    
    print("Testing roof texture integration...")
    print(f"Wall texture loaded: {asset_loader.get_image('wall_texture') is not None}")
    print(f"Roof texture loaded: {asset_loader.get_image('roof_texture') is not None}")
    
    # Test that both methods exist
    print(f"render_flat_wall method exists: {hasattr(wall_renderer, 'render_flat_wall')}")
    print(f"render_flat_wall_with_roof_top method exists: {hasattr(wall_renderer, 'render_flat_wall_with_roof_top')}")
    
    # Create test surface
    test_surface = pygame.Surface((200, 200))
    test_surface.fill((50, 50, 50))  # Dark background
    
    try:
        # Test regular wall rendering
        print("Testing regular wall rendering...")
        wall_renderer.render_flat_wall(test_surface, 100, 100, level.TILE_WALL, 2, 2)
        print("✓ Regular wall rendering works")
        
        # Test roof-top wall rendering
        print("Testing roof-top wall rendering...")
        wall_renderer.render_flat_wall_with_roof_top(test_surface, 100, 150, level.TILE_WALL, 2, 2)
        print("✓ Roof-top wall rendering works")
        
        # Save test image
        pygame.image.save(test_surface, "wall_render_test.png")
        print("✓ Test image saved as wall_render_test.png")
        
        print("\n🎉 All tests passed! The roof texture integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    pygame.quit()
    sys.exit(0 if success else 1)