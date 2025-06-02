#!/usr/bin/env python3
"""
Create simple NPC sprite variants for missing NPCs
"""

import pygame
import os

def create_npc_sprite(name, base_color, feature_color, feature_type, size=64):
    """Create a simple NPC sprite"""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    
    # Draw base character
    pygame.draw.circle(sprite, base_color, center, size // 3)
    pygame.draw.circle(sprite, (255, 255, 255), center, size // 4)
    pygame.draw.circle(sprite, (0, 0, 0), center, size // 3, 3)
    
    # Add distinguishing features
    if feature_type == "hat":
        pygame.draw.rect(sprite, feature_color, (size//2 - 12, 3, 24, 12))
    elif feature_type == "turban":
        pygame.draw.ellipse(sprite, feature_color, (size//2 - 12, 2, 24, 16))
    elif feature_type == "hood":
        pygame.draw.ellipse(sprite, feature_color, (size//2 - 14, 2, 28, 20))
    elif feature_type == "helmet":
        pygame.draw.rect(sprite, feature_color, (size//2 - 10, 5, 20, 8))
        pygame.draw.rect(sprite, (169, 169, 169), (size//2 - 8, 8, 16, 4))
    elif feature_type == "apron":
        pygame.draw.rect(sprite, feature_color, (size//2 - 8, size//2 + 5, 16, 12))
    elif feature_type == "beard":
        pygame.draw.circle(sprite, feature_color, (size//2, size//2 + 8), 9)
    
    # Add eyes
    pygame.draw.circle(sprite, (0, 0, 0), (center[0] - 6, center[1] - 4), 2)
    pygame.draw.circle(sprite, (0, 0, 0), (center[0] + 6, center[1] - 4), 2)
    
    return sprite

def main():
    pygame.init()
    
    assets_dir = "/Users/mnovich/Development/claude-rpg/assets/images"
    
    # Define NPCs that need unique sprites
    npcs_to_create = [
        {
            "name": "desert_guide",
            "display_name": "Desert Guide", 
            "base_color": (218, 165, 32),  # Goldenrod
            "feature_color": (184, 134, 11),  # Darker goldenrod
            "feature_type": "turban"
        },
        {
            "name": "head_miner", 
            "display_name": "Head Miner",
            "base_color": (85, 85, 85),  # Dark gray
            "feature_color": (169, 169, 169),  # Light gray
            "feature_type": "helmet"
        },
        {
            "name": "master_fisher",
            "display_name": "Master Fisher", 
            "base_color": (0, 139, 139),  # Dark cyan
            "feature_color": (0, 100, 100),  # Darker cyan
            "feature_type": "hat"
        },
        {
            "name": "trade_master",
            "display_name": "Trade Master",
            "base_color": (255, 140, 0),  # Dark orange
            "feature_color": (205, 102, 0),  # Darker orange
            "feature_type": "hat"
        },
        {
            "name": "stable_master",
            "display_name": "Stable Master", 
            "base_color": (160, 82, 45),  # Saddle brown
            "feature_color": (139, 69, 19),  # Brown
            "feature_type": "hat"
        },
        {
            "name": "water_keeper",
            "display_name": "Water Keeper",
            "base_color": (30, 144, 255),  # Dodger blue
            "feature_color": (0, 100, 200),  # Darker blue
            "feature_type": "hood"
        },
        {
            "name": "lodge_keeper",
            "display_name": "Lodge Keeper",
            "base_color": (205, 92, 92),  # Indian red
            "feature_color": (255, 255, 255),  # White
            "feature_type": "apron"
        }
    ]
    
    created_count = 0
    
    for npc in npcs_to_create:
        sprite = create_npc_sprite(
            npc["name"],
            npc["base_color"], 
            npc["feature_color"],
            npc["feature_type"]
        )
        
        filepath = os.path.join(assets_dir, f"{npc['name']}.png")
        pygame.image.save(sprite, filepath)
        
        print(f"Created sprite for {npc['display_name']}: {filepath}")
        created_count += 1
    
    print(f"\nCreated {created_count} new NPC sprites!")
    pygame.quit()

if __name__ == "__main__":
    main()