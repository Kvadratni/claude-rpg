#!/usr/bin/env python3
"""
Create a simple roof texture for the RPG game
"""

import pygame
import sys
import os

def create_roof_texture():
    """Create a simple roof texture"""
    # Initialize pygame
    pygame.init()
    
    # Create a 64x64 surface
    size = 64
    surface = pygame.Surface((size, size))
    
    # Base roof color - dark brown
    base_color = (60, 40, 20)
    surface.fill(base_color)
    
    # Add shingle pattern
    shingle_color = (80, 55, 30)
    highlight_color = (100, 70, 40)
    shadow_color = (40, 25, 15)
    
    # Draw horizontal shingle rows
    for y in range(0, size, 8):
        # Alternate row offset for realistic shingle pattern
        offset = 4 if (y // 8) % 2 else 0
        
        for x in range(-4 + offset, size + 4, 8):
            # Draw shingle
            shingle_rect = pygame.Rect(x, y, 8, 6)
            pygame.draw.rect(surface, shingle_color, shingle_rect)
            
            # Add highlight on top edge
            pygame.draw.line(surface, highlight_color, (x, y), (x + 7, y))
            
            # Add shadow on bottom edge
            pygame.draw.line(surface, shadow_color, (x, y + 5), (x + 7, y + 5))
    
    # Add some random weathering spots
    import random
    random.seed(42)  # Consistent pattern
    for _ in range(20):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        weather_color = (random.randint(45, 75), random.randint(30, 50), random.randint(10, 25))
        pygame.draw.circle(surface, weather_color, (x, y), 1)
    
    return surface

def main():
    """Main function"""
    # Create the texture
    roof_texture = create_roof_texture()
    
    # Save to assets directory
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'images')
    os.makedirs(assets_dir, exist_ok=True)
    
    output_path = os.path.join(assets_dir, 'roof_texture.png')
    pygame.image.save(roof_texture, output_path)
    
    print(f"Roof texture saved to: {output_path}")

if __name__ == "__main__":
    main()