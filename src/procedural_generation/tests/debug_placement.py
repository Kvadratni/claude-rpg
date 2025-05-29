#!/usr/bin/env python3
"""
Detailed debug for building placement in settlements
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from procedural_generation.src.procedural_generator import ProceduralGenerator
import random

def debug_building_placement():
    """Debug the building placement process step by step"""
    print("Debugging Building Placement Process")
    print("=" * 45)
    
    generator = ProceduralGenerator(100, 100, seed=12345)
    tiles = generator.generate_tiles()
    
    # Get the VILLAGE template
    village_template = generator.SETTLEMENT_TEMPLATES['VILLAGE']
    
    start_x, start_y = 30, 30
    settlement_width, settlement_height = village_template['size']
    
    print(f"Settlement area: ({start_x}, {start_y}) to ({start_x + settlement_width}, {start_y + settlement_height})")
    
    # Create stone square in center (like the actual method does)
    center_size = min(settlement_width, settlement_height) // 2
    center_start_x = start_x + (settlement_width - center_size) // 2
    center_start_y = start_y + (settlement_height - center_size) // 2
    
    print(f"Center square: ({center_start_x}, {center_start_y}) size {center_size}x{center_size}")
    
    for x in range(center_start_x, center_start_x + center_size):
        for y in range(center_start_y, center_start_y + center_size):
            if 0 <= x < generator.width and 0 <= y < generator.height:
                tiles[y][x] = 2  # TILE_STONE
    
    # Try to place each building manually with detailed logging
    buildings = village_template['buildings']
    placed_buildings = []
    
    for i, building in enumerate(buildings):
        building_width, building_height = building['size']
        print(f"\nTrying to place building {i+1}: {building['name']} ({building_width}x{building_height})")
        
        placed = False
        for attempt in range(20):
            # Random position within settlement bounds
            bx = start_x + random.randint(2, settlement_width - building_width - 2)
            by = start_y + random.randint(2, settlement_height - building_height - 2)
            
            print(f"  Attempt {attempt+1}: trying position ({bx}, {by})")
            
            # Check if building would overlap with center square
            center_overlap = generator.building_overlaps_area(bx, by, building_width, building_height, 
                                         center_start_x, center_start_y, center_size, center_size)
            print(f"    Center overlap: {center_overlap}")
            
            if center_overlap:
                print(f"    REJECTED: Overlaps with center square")
                continue
            
            # Check overlap with other buildings
            other_overlap = False
            for pb in placed_buildings:
                if generator.building_overlaps_area(bx, by, building_width, building_height,
                                                 pb['x'], pb['y'], pb['width'], pb['height']):
                    other_overlap = True
                    print(f"    REJECTED: Overlaps with {pb['name']}")
                    break
            
            if other_overlap:
                continue
            
            # Check if position is within bounds
            if (bx + building_width >= start_x + settlement_width or 
                by + building_height >= start_y + settlement_height):
                print(f"    REJECTED: Outside settlement bounds")
                continue
            
            # Success!
            print(f"    SUCCESS: Placing building at ({bx}, {by})")
            
            # Place the building
            generator.create_building(tiles, bx, by, building_width, building_height)
            
            placed_buildings.append({
                'x': bx, 'y': by, 'width': building_width, 'height': building_height,
                'name': building['name'], 'npc': building.get('npc'),
                'has_shop': building.get('has_shop', False)
            })
            placed = True
            break
        
        if not placed:
            print(f"    FAILED: Could not place {building['name']} after 20 attempts")
    
    print(f"\nPlacement Summary:")
    print(f"  Buildings attempted: {len(buildings)}")
    print(f"  Buildings placed: {len(placed_buildings)}")
    
    # Count special tiles
    tile_counts = {}
    for y in range(100):
        for x in range(100):
            tile_type = tiles[y][x]
            if tile_type in [4, 5, 10, 11, 13, 14, 15]:
                tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
    
    print(f"\nSpecial tile counts:")
    tile_names = {
        4: "Wall",
        5: "Door", 
        10: "Wall_Horizontal",
        11: "Wall_Vertical",
        13: "Brick",
        14: "Window_Horizontal",
        15: "Window_Vertical"
    }
    
    for tile_type, count in tile_counts.items():
        if count > 0:
            print(f"  {tile_names[tile_type]}: {count}")
    
    # Show settlement area
    print(f"\nSettlement area visualization:")
    for y in range(start_y - 2, start_y + settlement_height + 2):
        row_str = ""
        for x in range(start_x - 2, start_x + settlement_width + 2):
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
    
    return len(placed_buildings)

if __name__ == "__main__":
    # Set the same random seed for reproducible results
    random.seed(12345)
    
    buildings_placed = debug_building_placement()
    
    print(f"\n" + "=" * 50)
    print(f"RESULT: {buildings_placed} buildings successfully placed")
    print("=" * 50)