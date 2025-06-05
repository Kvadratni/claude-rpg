#!/usr/bin/env python3
"""
Test script to visualize all building patterns for review
Creates a visual representation of all settlement patterns and their buildings
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly without relative imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'world'))

from settlement_patterns import SettlementPatternGenerator

def visualize_pattern(pattern, pattern_name):
    """Create a visual representation of a settlement pattern"""
    print(f"\n{'='*60}")
    print(f"PATTERN: {pattern_name.upper()}")
    print(f"Size: {pattern.width}x{pattern.height}")
    print(f"Buildings: {len(pattern.building_positions)}")
    print(f"{'='*60}")
    
    # Create tile legend
    tile_symbols = {
        0: '.',   # TILE_GRASS
        1: ':',   # TILE_DIRT  
        2: '#',   # TILE_STONE
        3: '~',   # TILE_WATER
        4: '█',   # TILE_WALL
        5: 'D',   # TILE_DOOR
        13: '▓',  # TILE_BRICK
        16: '░',  # TILE_SAND
        17: '*',  # TILE_SNOW
        18: 'T',  # TILE_FOREST_FLOOR
        19: 'M',  # TILE_SWAMP
    }
    
    # Print the pattern with building overlays
    print("\nPattern Layout:")
    print("Legend: . = grass, : = dirt, # = stone, ~ = water, ░ = sand, * = snow, T = forest, M = swamp")
    print("        █ = wall, D = door, ▓ = brick, Numbers = building IDs")
    print()
    
    # Create a copy of the tile pattern for visualization
    visual_grid = []
    for y in range(pattern.height):
        row = []
        for x in range(pattern.width):
            tile_type = pattern.get_tile_at(x, y)
            symbol = tile_symbols.get(tile_type, '?')
            row.append(symbol)
        visual_grid.append(row)
    
    # Overlay building positions with numbers
    for i, building in enumerate(pattern.building_positions):
        building_id = str(i + 1) if i < 9 else chr(ord('A') + i - 9)  # 1-9, then A-Z
        
        # Mark building area
        for dy in range(building['height']):
            for dx in range(building['width']):
                bx = building['x'] + dx
                by = building['y'] + dy
                if 0 <= bx < pattern.width and 0 <= by < pattern.height:
                    # Only mark corners and center to avoid cluttering
                    if (dx == 0 and dy == 0) or \
                       (dx == building['width']//2 and dy == building['height']//2):
                        visual_grid[by][bx] = building_id
    
    # Print the grid with coordinates
    print("   ", end="")
    for x in range(pattern.width):
        print(f"{x%10}", end="")
    print()
    
    for y in range(pattern.height):
        print(f"{y:2d} ", end="")
        for x in range(pattern.width):
            print(visual_grid[y][x], end="")
        print()
    
    # Print building details
    print(f"\nBuilding Details:")
    for i, building in enumerate(pattern.building_positions):
        building_id = str(i + 1) if i < 9 else chr(ord('A') + i - 9)
        interior_width = building['width'] - 2 if building['width'] > 2 else 0
        interior_height = building['height'] - 2 if building['height'] > 2 else 0
        interior_area = interior_width * interior_height
        
        status = "✓" if interior_area >= 9 else "✗"  # 3x3 minimum interior
        print(f"  {building_id}: {building['type']} at ({building['x']}, {building['y']}) "
              f"size {building['width']}x{building['height']} "
              f"interior {interior_width}x{interior_height} ({interior_area} tiles) {status}")

def main():
    """Test all settlement patterns"""
    print("BUILDING PATTERN VISUALIZATION TEST")
    print("Checking all settlement patterns for proper building sizes...")
    
    generator = SettlementPatternGenerator()
    
    # Test all pattern types
    settlement_types = [
        'VILLAGE', 'TOWN', 'DESERT_OUTPOST', 'SNOW_SETTLEMENT', 
        'SWAMP_VILLAGE', 'FOREST_CAMP', 'MINING_CAMP', 'FISHING_VILLAGE'
    ]
    
    total_buildings = 0
    undersized_buildings = 0
    
    for settlement_type in settlement_types:
        print(f"\n{'#'*80}")
        print(f"TESTING SETTLEMENT TYPE: {settlement_type}")
        print(f"{'#'*80}")
        
        # Get multiple pattern variations for this settlement type
        for seed in [1, 42, 100]:
            pattern = generator.get_pattern(settlement_type, seed)
            pattern_name = f"{settlement_type}_seed_{seed}"
            
            visualize_pattern(pattern, pattern_name)
            
            # Count building size issues
            for building in pattern.building_positions:
                total_buildings += 1
                interior_width = building['width'] - 2 if building['width'] > 2 else 0
                interior_height = building['height'] - 2 if building['height'] > 2 else 0
                interior_area = interior_width * interior_height
                
                if interior_area < 9:  # Less than 3x3 interior
                    undersized_buildings += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total buildings tested: {total_buildings}")
    print(f"Undersized buildings (< 3x3 interior): {undersized_buildings}")
    print(f"Properly sized buildings: {total_buildings - undersized_buildings}")
    
    if undersized_buildings > 0:
        print(f"\n⚠️  WARNING: {undersized_buildings} buildings are too small!")
        print("   Buildings need minimum 5x5 total size for 3x3 interior")
    else:
        print(f"\n✅ All buildings are properly sized!")

if __name__ == "__main__":
    main()