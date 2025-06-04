#!/usr/bin/env python3
"""
Window wall rendering test
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
    """Mock level class for testing"""
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.tile_width = 64
        self.tile_height = 32
        self.width = 20
        self.height = 20
        self.tile_sprites = {}
        
        # Define tile constants
        self.TILE_WALL = 5
        self.TILE_WALL_CORNER_TL = 6
        self.TILE_WALL_CORNER_TR = 7
        self.TILE_WALL_CORNER_BL = 8
        self.TILE_WALL_CORNER_BR = 9
        self.TILE_WALL_HORIZONTAL = 10
        self.TILE_WALL_VERTICAL = 11
        self.TILE_WALL_WINDOW = 12
        self.TILE_WALL_WINDOW_HORIZONTAL = 14
        self.TILE_WALL_WINDOW_VERTICAL = 15
        self.TILE_DOOR = 16

def main():
    pygame.init()
    
    # Set up display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Window Wall Rendering Test")
    
    # Load assets
    asset_loader = AssetLoader()
    iso_renderer = IsometricRenderer()
    
    # Create mock level
    level = MockLevel()
    level.asset_loader = asset_loader
    
    # Create wall renderer
    wall_renderer = WallRenderer(level)
    
    print("Starting window wall rendering test...")
    print(f"Wall texture loaded: {asset_loader.get_image('wall_texture') is not None}")
    print(f"Window wall texture loaded: {asset_loader.get_image('wall_texture_window') is not None}")
    
    # Test different wall types
    wall_configs = [
        ('Regular Wall', level.TILE_WALL, 200, 150),
        ('Window Wall Generic', level.TILE_WALL_WINDOW, 400, 150),
        ('Window Wall Horizontal', level.TILE_WALL_WINDOW_HORIZONTAL, 600, 150),
        ('Window Wall Vertical', level.TILE_WALL_WINDOW_VERTICAL, 200, 350),
    ]
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear screen
        screen.fill((50, 50, 50))  # Dark gray background
        
        # Render each wall configuration
        for config_name, tile_type, x, y in wall_configs:
            # Create a surface for this wall
            wall_surface = pygame.Surface((150, 100), pygame.SRCALPHA)
            
            # Render the wall
            wall_renderer.render_flat_wall(
                wall_surface, 
                75,   # center of the 150px wide surface
                50,   # center of the 100px tall surface
                tile_type,
                10,   # world_x
                10    # world_y
            )
            
            # Blit to main screen
            screen.blit(wall_surface, (x - 75, y - 50))
            
            # Add label
            font = pygame.font.Font(None, 24)
            label = font.render(config_name, True, (255, 255, 255))
            screen.blit(label, (x - label.get_width() // 2, y + 60))
        
        # Add instructions
        font = pygame.font.Font(None, 36)
        title = font.render("Window Wall Rendering Test", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 20))
        
        instructions_font = pygame.font.Font(None, 20)
        instructions = [
            "Testing different wall types:",
            "- Regular walls should show normal stone texture",
            "- Window walls should show window texture with glass/frames",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instructions_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (20, screen_height - 100 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()