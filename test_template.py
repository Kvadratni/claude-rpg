#!/usr/bin/env python3
"""
Test script for template-based map generation
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.level import Level
from src.player import Player
from src.assets import AssetLoader

def test_template_generation():
    """Test the template-based level generation"""
    pygame.init()
    
    # Create mock asset loader
    asset_loader = AssetLoader()
    
    # Create mock player
    player = Player(100, 102, asset_loader)  # Start at village center
    
    try:
        # Create level - should use template if available
        level = Level("Test Level", player, asset_loader)
        
        print(f"\nLevel Generation Results:")
        print(f"Map size: {level.width}x{level.height}")
        print(f"NPCs: {len(level.npcs)}")
        print(f"Enemies: {len(level.enemies)}")
        print(f"Objects: {len(level.objects)}")
        print(f"Chests: {len(level.chests)}")
        print(f"Items: {len(level.items)}")
        
        # Check if template was used
        if hasattr(level, 'template_generator') and level.template_generator:
            print("\n✅ Template-based generation was used!")
            
            # Validate no overlapping entities
            positions = set()
            overlaps = 0
            
            for entity_list in [level.npcs, level.enemies, level.objects, level.chests]:
                for entity in entity_list:
                    pos = (int(entity.x), int(entity.y))
                    if pos in positions:
                        overlaps += 1
                        print(f"⚠️  Overlap detected at {pos}")
                    positions.add(pos)
            
            if overlaps == 0:
                print("✅ No entity overlaps detected!")
            else:
                print(f"❌ Found {overlaps} entity overlaps")
            
            # Check NPC positions
            print("\nNPC Positions:")
            for npc in level.npcs:
                terrain = level.template_generator.template.get_terrain_type(int(npc.x), int(npc.y))
                print(f"  {npc.name}: ({int(npc.x)}, {int(npc.y)}) - {terrain}")
        else:
            print("\n⚠️  Fallback procedural generation was used")
        
        # Test collision system
        print("\nTesting collision system...")
        
        # Test valid position
        if level.check_collision(100, 102, 0.4):  # Village center should be walkable
            print("❌ Village center shows collision (should be walkable)")
        else:
            print("✅ Village center is walkable")
        
        # Test wall collision
        if level.check_collision(0, 0, 0.4):  # Border should be blocked
            print("✅ Border wall blocks movement")
        else:
            print("❌ Border wall doesn't block movement")
        
        print("\n🎉 Template generation test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_template_generation()
    sys.exit(0 if success else 1)