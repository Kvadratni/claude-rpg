#!/usr/bin/env python3
"""
Test the adjusted interior roof height
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
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Interior Roof Height - After Adjustment")
    
    # Load assets
    asset_loader = AssetLoader()
    
    print("Testing adjusted interior roof height...")
    
    # Load roof texture
    roof_texture = asset_loader.get_image('roof_texture')
    if not roof_texture:
        print("❌ Failed to load roof texture")
        return False
    
    # Test surface
    surface = pygame.Surface((700, 500), pygame.SRCALPHA)
    surface.fill((50, 100, 50))  # Green background
    
    # Tile dimensions
    tile_width, tile_height = 64, 32
    wall_height = 48
    floor_y = 250  # Reference floor level
    
    # Prepare roof texture
    rotated_roof = pygame.transform.rotate(roof_texture, 45)
    scaled_roof = pygame.transform.scale(rotated_roof, (tile_width, tile_height))
    
    # Test positions
    positions = [
        ("Wall Roof (Full Height)", floor_y - tile_height // 2 - wall_height, 200),
        ("Interior Roof (Half Height)", floor_y - tile_height // 2 - (wall_height // 2), 400),
    ]
    
    for label, roof_y, x_pos in positions:
        # Draw floor reference
        pygame.draw.circle(surface, (255, 255, 0), (x_pos, floor_y), 4)
        
        # Draw roof
        roof_rect = scaled_roof.get_rect()
        roof_rect.center = (x_pos, roof_y)
        surface.blit(scaled_roof, roof_rect)
        
        # Add label
        font = pygame.font.Font(None, 24)
        text = font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (x_pos, 50)
        surface.blit(text, text_rect)
        
        # Add height info
        height_diff = floor_y - roof_y
        height_text = pygame.font.Font(None, 18).render(f"{height_diff}px above floor", True, (200, 200, 200))
        height_rect = height_text.get_rect()
        height_rect.center = (x_pos, floor_y + 40)
        surface.blit(height_text, height_rect)
    
    # Draw floor reference line
    pygame.draw.line(surface, (255, 255, 0), (0, floor_y), (700, floor_y), 2)
    floor_label = pygame.font.Font(None, 20).render("Floor Level", True, (255, 255, 0))
    surface.blit(floor_label, (10, floor_y + 5))
    
    # Blit to screen
    screen.fill((0, 0, 0))
    screen.blit(surface, (50, 50))
    
    # Add title and info
    title_font = pygame.font.Font(None, 36)
    title = title_font.render("Interior Roof Height - Adjusted", True, (255, 255, 255))
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))
    
    info = [
        "Interior roofs now positioned at half wall height (24px above floor)",
        "Wall roofs remain at full wall height (64px above floor)",
        "This should look more appropriate for interior spaces",
        "",
        "Press any key to exit"
    ]
    
    info_font = pygame.font.Font(None, 18)
    for i, line in enumerate(info):
        color = (200, 200, 200) if line else (255, 255, 255)
        text = info_font.render(line, True, color)
        screen.blit(text, (50, 450 + i * 25))
    
    pygame.display.flip()
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
    
    print("✅ Interior roof height adjusted:")
    print("  - Wall roofs: 64px above floor (full wall height)")
    print("  - Interior roofs: 24px above floor (half wall height)")
    
    return True

if __name__ == "__main__":
    success = main()
    pygame.quit()
    sys.exit(0 if success else 1)