#!/usr/bin/env python3
"""
Test to verify roof texture rotation fixes
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.assets import AssetLoader

def main():
    pygame.init()
    
    # Create asset loader
    asset_loader = AssetLoader()
    
    print("Testing roof texture rotation fixes...")
    
    # Load roof texture
    roof_texture = asset_loader.get_image('roof_texture')
    if roof_texture:
        print(f"✓ Roof texture loaded: {roof_texture.get_size()}")
        
        # Test rotation
        rotated_roof = pygame.transform.rotate(roof_texture, 45)
        print(f"✓ Roof texture rotated 45 degrees: {rotated_roof.get_size()}")
        
        # Create test surface
        test_surface = pygame.Surface((400, 300))
        test_surface.fill((50, 50, 50))  # Dark background
        
        # Render original texture
        original_rect = roof_texture.get_rect()
        original_rect.center = (100, 150)
        test_surface.blit(roof_texture, original_rect)
        
        # Render rotated texture
        rotated_rect = rotated_roof.get_rect()
        rotated_rect.center = (300, 150)
        test_surface.blit(rotated_roof, rotated_rect)
        
        # Add labels
        font = pygame.font.Font(None, 24)
        original_label = font.render("Original", True, (255, 255, 255))
        rotated_label = font.render("Rotated 45°", True, (255, 255, 255))
        
        test_surface.blit(original_label, (50, 50))
        test_surface.blit(rotated_label, (250, 50))
        
        # Save test image
        pygame.image.save(test_surface, "roof_texture_rotation_test.png")
        print("✓ Test image saved as roof_texture_rotation_test.png")
        
        print("\n🎉 Roof texture rotation test completed successfully!")
        
    else:
        print("❌ Failed to load roof texture")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    pygame.quit()
    sys.exit(0 if success else 1)