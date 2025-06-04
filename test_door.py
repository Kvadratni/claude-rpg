#!/usr/bin/env python3
"""
Door rendering test - shows multiple door configurations
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.assets import AssetLoader
from src.core.isometric import IsometricRenderer
from src.door_renderer import DoorRenderer

class MockLevel:
    """Mock level class for testing"""
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.wall_renderer = MockWallRenderer()

class MockWallRenderer:
    """Mock wall renderer for testing different door configurations"""
    def __init__(self):
        # Define different wall configurations for testing
        # Each config defines where walls should be around a door at (3, 0) - the actual coordinates from the test
        self.wall_configs = {
            # Isolated door (no adjacent walls)
            'isolated': set(),
            
            # Horizontal door (walls north and south) - door opens east/west
            'horizontal_ns': {(2, 0), (4, 0)},  # walls at north and south of door at (3, 0)
            
            # Vertical door (walls east and west) - door opens north/south
            'vertical_ew': {(3, 1), (3, -1)},  # walls at east and west of door at (3, 0)
            
            # Corner configurations
            'corner_ne': {(2, 0), (3, 1)},  # walls at north and east
            'corner_se': {(4, 0), (3, 1)},  # walls at south and east
            'corner_sw': {(4, 0), (3, -1)},  # walls at south and west
            'corner_nw': {(2, 0), (3, -1)},  # walls at north and west
        }
        self.current_config = 'isolated'
    
    def set_config(self, config_name):
        """Set the wall configuration for testing"""
        self.current_config = config_name
    
    def has_wall_or_door_at(self, x, y):
        """Check if there's a wall at the given coordinates"""
        walls = self.wall_configs.get(self.current_config, set())
        result = (x, y) in walls
        return result

def main():
    pygame.init()
    
    # Set up display
    screen_width = 1200
    screen_height = 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Door Rendering Test - All Configurations")
    
    # Load assets
    asset_loader = AssetLoader()
    iso_renderer = IsometricRenderer()
    door_renderer = DoorRenderer(asset_loader, iso_renderer)
    
    # Create mock level
    level = MockLevel()
    
    print("Starting door rendering test...")
    print(f"Archway texture loaded: {door_renderer.archway_texture is not None}")
    print(f"Wall door texture loaded: {door_renderer.wall_door_texture is not None}")
    
    # Test configurations
    configs = [
        ('Isolated Door', 'isolated', 200, 150),
        ('Horizontal Door (N-S walls)', 'horizontal_ns', 500, 150),
        ('Vertical Door (E-W walls)', 'vertical_ew', 800, 150),
        ('Corner NE', 'corner_ne', 200, 350),
        ('Corner SE', 'corner_se', 500, 350),
        ('Corner SW', 'corner_sw', 800, 350),
        ('Corner NW', 'corner_nw', 200, 550),
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
        
        # Render each door configuration
        for config_name, config_key, x, y in configs:
            # Set the wall configuration
            level.wall_renderer.set_config(config_key)
            
            # Create a surface for this door
            door_surface = pygame.Surface((200, 150), pygame.SRCALPHA)
            
            # Render the door (door position is always at 15, 3 in world coordinates)
            door_renderer.render_door_tile(
                door_surface, 
                100,  # center of the 200px wide surface
                75,   # center of the 150px tall surface
                'door_tile',
                level,
                64,   # tile_width
                32    # tile_height
            )
            
            # Blit to main screen
            screen.blit(door_surface, (x - 100, y - 75))
            
            # Add label
            font = pygame.font.Font(None, 24)
            label = font.render(config_name, True, (255, 255, 255))
            screen.blit(label, (x - label.get_width() // 2, y + 80))
        
        # Add instructions
        font = pygame.font.Font(None, 36)
        title = font.render("Door Rendering Test - All Configurations", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 20))
        
        instructions_font = pygame.font.Font(None, 20)
        instructions = [
            "Each door shows different texture combinations:",
            "- Archway texture on front face (where player approaches)",
            "- Wall_door texture on side/back faces (showing open door)",
            "- Stone texture on top face",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instructions_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (20, screen_height - 120 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()