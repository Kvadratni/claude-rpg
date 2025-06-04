#!/usr/bin/env python3
"""
Test different interior roof heights to find the optimal positioning
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.assets import AssetLoader

def main():
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Interior Roof Height Testing")
    
    # Load assets
    asset_loader = AssetLoader()
    
    print("Testing different interior roof heights...")
    
    # Load roof texture
    roof_texture = asset_loader.get_image('roof_texture')
    if not roof_texture:
        print("❌ Failed to load roof texture")
        return False
    
    # Test surface
    surface = pygame.Surface((900, 600), pygame.SRCALPHA)
    surface.fill((50, 100, 50))  # Green background
    
    # Tile dimensions
    tile_width, tile_height = 64, 32
    wall_height = 48
    floor_y = 300  # Reference floor level
    
    # Test different roof heights
    test_positions = [
        ("Current (Wall Height)", floor_y - tile_height // 2 - wall_height),
        ("3/4 Wall Height", floor_y - tile_height // 2 - (wall_height * 3 // 4)),
        ("1/2 Wall Height", floor_y - tile_height // 2 - (wall_height // 2)),
        ("1/4 Wall Height", floor_y - tile_height // 2 - (wall_height // 4)),
        ("Floor + Tile Height", floor_y - tile_height),
        ("Floor + 1/2 Tile", floor_y - tile_height // 2),
        ("Floor + 1/4 Tile", floor_y - tile_height // 4),
    ]
    
    # Prepare roof texture
    rotated_roof = pygame.transform.rotate(roof_texture, 45)
    scaled_roof = pygame.transform.scale(rotated_roof, (tile_width, tile_height))
    
    # Render each test position
    x_positions = [100, 200, 300, 400, 500, 600, 700]
    
    for i, (label, roof_y) in enumerate(test_positions):
        if i < len(x_positions):
            x_pos = x_positions[i]
            
            # Draw floor reference
            pygame.draw.circle(surface, (255, 255, 0), (x_pos, floor_y), 3)
            
            # Draw roof
            roof_rect = scaled_roof.get_rect()
            roof_rect.center = (x_pos, roof_y)
            surface.blit(scaled_roof, roof_rect)
            
            # Add label
            font = pygame.font.Font(None, 16)
            label_lines = label.split()
            for j, line in enumerate(label_lines):
                text = font.render(line, True, (255, 255, 255))
                text_rect = text.get_rect()
                text_rect.center = (x_pos, 50 + j * 20)
                surface.blit(text, text_rect)
            
            # Add height info
            height_diff = floor_y - roof_y
            height_text = font.render(f"{height_diff}px", True, (200, 200, 200))
            height_rect = height_text.get_rect()
            height_rect.center = (x_pos, floor_y + 30)
            surface.blit(height_text, height_rect)
    
    # Draw floor reference line
    pygame.draw.line(surface, (255, 255, 0), (0, floor_y), (900, floor_y), 2)
    floor_label = pygame.font.Font(None, 20).render("Floor Level", True, (255, 255, 0))
    surface.blit(floor_label, (10, floor_y + 5))
    
    # Blit to screen
    screen.fill((0, 0, 0))
    screen.blit(surface, (50, 50))
    
    # Add title and instructions
    title_font = pygame.font.Font(None, 36)
    title = title_font.render("Interior Roof Height Testing", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))
    
    instructions = [
        "Yellow dots = Floor level reference",
        "Different roof heights shown above",
        "Current implementation uses full wall height (leftmost)",
        "Press 1-7 to select preferred height, ESC to exit"
    ]
    
    instruction_font = pygame.font.Font(None, 18)
    for i, instruction in enumerate(instructions):
        text = instruction_font.render(instruction, True, (200, 200, 200))
        screen.blit(text, (50, 650 + i * 20))
    
    pygame.display.flip()
    
    # Wait for user input
    selected_height = None
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                elif pygame.K_1 <= event.key <= pygame.K_7:
                    selected_height = event.key - pygame.K_1
                    waiting = False
    
    if selected_height is not None:
        selected_label, selected_y = test_positions[selected_height]
        height_diff = floor_y - selected_y
        print(f"Selected: {selected_label}")
        print(f"Height above floor: {height_diff}px")
        print(f"Calculation: screen_y - {floor_y - selected_y}")
        
        # Calculate the formula
        if selected_y == floor_y - tile_height // 2 - wall_height:
            formula = "screen_y - tile_height // 2 - wall_height"
        elif selected_y == floor_y - tile_height // 2 - (wall_height * 3 // 4):
            formula = "screen_y - tile_height // 2 - (wall_height * 3 // 4)"
        elif selected_y == floor_y - tile_height // 2 - (wall_height // 2):
            formula = "screen_y - tile_height // 2 - (wall_height // 2)"
        elif selected_y == floor_y - tile_height // 2 - (wall_height // 4):
            formula = "screen_y - tile_height // 2 - (wall_height // 4)"
        elif selected_y == floor_y - tile_height:
            formula = "screen_y - tile_height"
        elif selected_y == floor_y - tile_height // 2:
            formula = "screen_y - tile_height // 2"
        elif selected_y == floor_y - tile_height // 4:
            formula = "screen_y - tile_height // 4"
        else:
            formula = f"screen_y - {floor_y - selected_y}"
        
        print(f"Formula: roof_y = {formula}")
        return formula
    
    return None

if __name__ == "__main__":
    result = main()
    pygame.quit()
    if result:
        print(f"\nRecommended formula: {result}")
    sys.exit(0)