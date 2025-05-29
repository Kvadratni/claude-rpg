#!/usr/bin/env python3
"""
Visual verification tool for template-based map generation
Creates a visual representation of the generated map
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.level import Level
from src.player import Player
from src.assets import AssetLoader

def create_map_visualization(level, output_path):
    """Create a visual representation of the generated map"""
    
    # Create a surface for the visualization
    map_surface = pygame.Surface((level.width, level.height))
    
    # Color scheme for visualization
    colors = {
        0: (50, 150, 50),    # GRASS - green
        1: (139, 69, 19),    # DIRT - brown
        2: (128, 128, 128),  # STONE - gray
        3: (0, 0, 255),      # WATER - blue
        4: (64, 64, 64),     # WALL - dark gray
        5: (139, 69, 19),    # DOOR - brown
        13: (150, 80, 60),   # BRICK - reddish brown
    }
    
    # Draw base tiles
    for y in range(level.height):
        for x in range(level.width):
            tile_type = level.tiles[y][x]
            color = colors.get(tile_type, (255, 0, 255))  # Magenta for unknown
            map_surface.set_at((x, y), color)
    
    # Draw entities with distinct colors
    # NPCs - bright yellow
    for npc in level.npcs:
        x, y = int(npc.x), int(npc.y)
        if 0 <= x < level.width and 0 <= y < level.height:
            map_surface.set_at((x, y), (255, 255, 0))
    
    # Enemies - red
    for enemy in level.enemies:
        x, y = int(enemy.x), int(enemy.y)
        if 0 <= x < level.width and 0 <= y < level.height:
            map_surface.set_at((x, y), (255, 0, 0))
    
    # Objects - dark green
    for obj in level.objects:
        x, y = int(obj.x), int(obj.y)
        if 0 <= x < level.width and 0 <= y < level.height:
            map_surface.set_at((x, y), (0, 100, 0))
    
    # Chests - orange
    for chest in level.chests:
        x, y = int(chest.x), int(chest.y)
        if 0 <= x < level.width and 0 <= y < level.height:
            map_surface.set_at((x, y), (255, 165, 0))
    
    # Player start position - bright white
    player_x, player_y = 100, 102
    map_surface.set_at((player_x, player_y), (255, 255, 255))
    
    # Scale up for better visibility
    scale_factor = 3
    scaled_surface = pygame.transform.scale(
        map_surface, 
        (level.width * scale_factor, level.height * scale_factor)
    )
    
    # Save the visualization
    pygame.image.save(scaled_surface, output_path)
    print(f"Map visualization saved to: {output_path}")
    
    return scaled_surface

def create_legend_image(output_path):
    """Create a legend for the map visualization"""
    legend_surface = pygame.Surface((300, 200))
    legend_surface.fill((255, 255, 255))  # White background
    
    font = pygame.font.Font(None, 24)
    
    legend_items = [
        ("Grass", (50, 150, 50)),
        ("Dirt/Paths", (139, 69, 19)),
        ("Stone Roads", (128, 128, 128)),
        ("Water", (0, 0, 255)),
        ("Walls", (64, 64, 64)),
        ("NPCs", (255, 255, 0)),
        ("Enemies", (255, 0, 0)),
        ("Objects", (0, 100, 0)),
        ("Chests", (255, 165, 0)),
        ("Player Start", (255, 255, 255))
    ]
    
    y_offset = 10
    for i, (label, color) in enumerate(legend_items):
        # Draw color square
        pygame.draw.rect(legend_surface, color, (10, y_offset, 20, 15))
        pygame.draw.rect(legend_surface, (0, 0, 0), (10, y_offset, 20, 15), 1)
        
        # Draw label
        text = font.render(label, True, (0, 0, 0))
        legend_surface.blit(text, (40, y_offset))
        
        y_offset += 20
    
    pygame.image.save(legend_surface, output_path)
    print(f"Legend saved to: {output_path}")

def main():
    """Main visualization function"""
    pygame.init()
    
    # Create mock asset loader and player
    asset_loader = AssetLoader()
    player = Player(100, 102, asset_loader)
    
    try:
        # Create level with template-based generation
        level = Level("Visualization Test", player, asset_loader)
        
        print(f"\nGenerating visualization for {level.width}x{level.height} map...")
        print(f"Entities: {len(level.npcs)} NPCs, {len(level.enemies)} enemies, {len(level.objects)} objects, {len(level.chests)} chests")
        
        # Create output directory
        output_dir = "/Users/mnovich/Development/claude-rpg/assets/maps"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create visualizations
        map_viz_path = os.path.join(output_dir, "generated_map_visualization.png")
        legend_path = os.path.join(output_dir, "map_legend.png")
        
        create_map_visualization(level, map_viz_path)
        create_legend_image(legend_path)
        
        print(f"\n✅ Visualization complete!")
        print(f"📊 Map: {map_viz_path}")
        print(f"📋 Legend: {legend_path}")
        
        # Print statistics
        print(f"\n📈 Generation Statistics:")
        print(f"  Map Size: {level.width}x{level.height} ({level.width * level.height:,} tiles)")
        print(f"  NPCs: {len(level.npcs)}")
        print(f"  Enemies: {len(level.enemies)}")
        print(f"  Objects: {len(level.objects)}")
        print(f"  Chests: {len(level.chests)}")
        
        # Verify no overlaps
        positions = set()
        overlaps = 0
        for entity_list in [level.npcs, level.enemies, level.objects, level.chests]:
            for entity in entity_list:
                pos = (int(entity.x), int(entity.y))
                if pos in positions:
                    overlaps += 1
                positions.add(pos)
        
        if overlaps == 0:
            print(f"  ✅ No entity overlaps detected!")
        else:
            print(f"  ❌ {overlaps} entity overlaps detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)