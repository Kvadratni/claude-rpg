#!/usr/bin/env python3
"""
Debug script for building generation issues
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from procedural_generation.src.procedural_generator import ProceduralGenerator

def debug_single_building():
    """Debug a single building creation"""
    print("Debugging Single Building Creation")
    print("=" * 40)
    
    generator = ProceduralGenerator(50, 50, seed=12345)
    
    # Create empty tiles grid
    tiles = [[0 for _ in range(50)] for _ in range(50)]
    
    # Create a single building directly
    print("Creating building at (10, 10) with size (8, 6)")
    generator.create_building(tiles, 10, 10, 8, 6)
    
    # Analyze the tiles around the building
    print("\nTile analysis around building:")
    for y in range(8, 18):
        row_str = ""
        for x in range(8, 20):
            tile = tiles[y][x]
            if tile == 0:
                row_str += "."
            elif tile == 4:
                row_str += "W"
            elif tile == 5:
                row_str += "D"
            elif tile == 10:
                row_str += "H"
            elif tile == 11:
                row_str += "V"
            elif tile == 13:
                row_str += "B"
            elif tile == 14:
                row_str += "h"
            elif tile == 15:
                row_str += "v"
            else:
                row_str += str(tile)
        print(f"Row {y:2d}: {row_str}")
    
    # Count tile types
    tile_counts = {}
    for y in range(50):
        for x in range(50):
            tile_type = tiles[y][x]
            tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
    
    print(f"\nTile counts:")
    tile_names = {
        0: "Grass",
        4: "Wall",
        5: "Door", 
        10: "Wall_Horizontal",
        11: "Wall_Vertical",
        13: "Brick",
        14: "Window_Horizontal",
        15: "Window_Vertical"
    }
    
    for tile_type, count in tile_counts.items():
        if count > 0 and tile_type in tile_names:
            print(f"  {tile_names[tile_type]}: {count}")
    
    return tile_counts

def debug_settlement_building():
    """Debug settlement building process"""
    print("\nDebugging Settlement Building Process")
    print("=" * 40)
    
    generator = ProceduralGenerator(100, 100, seed=12345)
    tiles = generator.generate_tiles()
    
    # Get the VILLAGE template
    village_template = generator.SETTLEMENT_TEMPLATES['VILLAGE']
    
    print(f"Village template:")
    print(f"  Size: {village_template['size']}")
    print(f"  Buildings: {len(village_template['buildings'])}")
    
    # Manually place a settlement to debug
    start_x, start_y = 30, 30
    print(f"\nPlacing settlement at ({start_x}, {start_y})")
    
    # Count tiles before building
    def count_special_tiles(tiles):
        counts = {}
        for y in range(100):
            for x in range(100):
                tile_type = tiles[y][x]
                if tile_type in [4, 5, 10, 11, 13, 14, 15]:
                    counts[tile_type] = counts.get(tile_type, 0) + 1
        return counts
    
    before_counts = count_special_tiles(tiles)
    print(f"Before building - special tiles: {before_counts}")
    
    # Place buildings
    placed_buildings = generator.place_settlement_buildings(tiles, start_x, start_y, village_template)
    
    after_counts = count_special_tiles(tiles)
    print(f"After building - special tiles: {after_counts}")
    
    print(f"\nBuildings placed: {len(placed_buildings)}")
    for building in placed_buildings:
        print(f"  {building['name']} at ({building['x']}, {building['y']}) size {building['width']}x{building['height']}")
    
    # Check specific building area
    if placed_buildings:
        building = placed_buildings[0]
        bx, by = building['x'], building['y']
        bw, bh = building['width'], building['height']
        
        print(f"\nDetailed view of {building['name']} at ({bx}, {by}):")
        for y in range(by - 1, by + bh + 1):
            row_str = ""
            for x in range(bx - 1, bx + bw + 1):
                if 0 <= x < 100 and 0 <= y < 100:
                    tile = tiles[y][x]
                    if tile == 0:
                        row_str += "."
                    elif tile == 1:
                        row_str += "d"
                    elif tile == 2:
                        row_str += "S"
                    elif tile == 4:
                        row_str += "W"
                    elif tile == 5:
                        row_str += "D"
                    elif tile == 10:
                        row_str += "H"
                    elif tile == 11:
                        row_str += "V"
                    elif tile == 13:
                        row_str += "B"
                    elif tile == 14:
                        row_str += "h"
                    elif tile == 15:
                        row_str += "v"
                    else:
                        row_str += str(tile)
                else:
                    row_str += " "
            print(f"Row {y:2d}: {row_str}")
    
    return after_counts

if __name__ == "__main__":
    # Test single building
    single_counts = debug_single_building()
    
    # Test settlement building
    settlement_counts = debug_settlement_building()
    
    print(f"\n" + "=" * 50)
    print("DEBUGGING SUMMARY")
    print("=" * 50)
    
    print(f"Single building test:")
    for tile_type, count in single_counts.items():
        if count > 0 and tile_type != 0:
            print(f"  Tile {tile_type}: {count}")
    
    print(f"\nSettlement building test:")
    for tile_type, count in settlement_counts.items():
        if count > 0:
            print(f"  Tile {tile_type}: {count}")