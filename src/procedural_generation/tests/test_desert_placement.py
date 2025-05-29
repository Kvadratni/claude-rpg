#!/usr/bin/env python3
"""
Test specifically for desert settlement placement
"""

import sys
import os
import random
import math

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Mock the entity imports for testing
import procedural_generator

class MockEntity:
    def __init__(self, *args, **kwargs):
        pass

procedural_generator.Entity = MockEntity
procedural_generator.NPC = MockEntity
procedural_generator.Enemy = MockEntity
procedural_generator.Item = MockEntity
procedural_generator.Chest = MockEntity

from procedural_generator import ProceduralGenerator

def test_desert_placement_specifically():
    """Test desert settlement placement with different approaches"""
    print("Testing Desert Settlement Placement")
    print("=" * 40)
    
    # Try different seeds to find one with good desert coverage
    best_seed = None
    best_desert_coverage = 0
    
    for seed in [12345, 54321, 98765, 11111, 22222]:
        generator = ProceduralGenerator(100, 100, seed)
        
        # Count desert tiles
        desert_count = 0
        total_tiles = generator.width * generator.height
        
        for y in range(generator.height):
            for x in range(generator.width):
                if generator.biome_map[y][x] == 'DESERT':
                    desert_count += 1
        
        desert_coverage = (desert_count / total_tiles) * 100
        print(f"Seed {seed}: {desert_coverage:.1f}% desert coverage")
        
        if desert_coverage > best_desert_coverage:
            best_desert_coverage = desert_coverage
            best_seed = seed
    
    print(f"\nBest seed: {best_seed} with {best_desert_coverage:.1f}% desert coverage")
    
    # Test with the best seed
    if best_seed:
        generator = ProceduralGenerator(100, 100, best_seed)
        tiles = generator.generate_tiles()
        
        # Try to place just the desert outpost
        template_name = 'DESERT_OUTPOST'
        template_config = generator.SETTLEMENT_TEMPLATES[template_name]
        
        print(f"\nTrying to place {template_name} with best seed...")
        settlement = generator.try_place_settlement(template_name, template_config, tiles, max_attempts=100)
        
        if settlement:
            print(f"✅ Successfully placed {template_name}!")
            print(f"  Location: ({settlement['x']}, {settlement['y']})")
            print(f"  Biome: {settlement['biome']}")
        else:
            print(f"❌ Still failed to place {template_name}")
            
            # Let's see what's blocking it
            print("\nAnalyzing desert areas...")
            desert_positions = []
            
            for y in range(10, generator.height - 30):
                for x in range(10, generator.width - 30):
                    if generator.biome_map[y][x] == 'DESERT':
                        desert_positions.append((x, y))
            
            print(f"Found {len(desert_positions)} potential desert positions")
            
            if desert_positions:
                # Test a few desert positions manually
                for i, (x, y) in enumerate(desert_positions[:10]):
                    water_count = 0
                    for cy in range(y, y + 20):
                        for cx in range(x, x + 20):
                            if 0 <= cx < generator.width and 0 <= cy < generator.height:
                                if tiles[cy][cx] == 3:  # TILE_WATER
                                    water_count += 1
                    
                    print(f"  Desert position {i+1}: ({x}, {y}) - Water tiles: {water_count}")

def test_smaller_desert_outpost():
    """Test with a smaller desert outpost"""
    print(f"\nTesting Smaller Desert Outpost")
    print("=" * 35)
    
    # Temporarily make desert outpost smaller
    original_size = ProceduralGenerator.SETTLEMENT_TEMPLATES['DESERT_OUTPOST']['size']
    ProceduralGenerator.SETTLEMENT_TEMPLATES['DESERT_OUTPOST']['size'] = (12, 12)  # Smaller
    
    try:
        generator = ProceduralGenerator(100, 100, 12345)
        tiles = generator.generate_tiles()
        settlements = generator.place_settlements(tiles)
        
        desert_settlements = [s for s in settlements if 'DESERT' in s['name']]
        print(f"Placed {len(desert_settlements)} desert settlements with smaller size")
        
        for settlement in desert_settlements:
            print(f"  ✅ {settlement['name']} at ({settlement['x']}, {settlement['y']})")
    
    finally:
        # Restore original size
        ProceduralGenerator.SETTLEMENT_TEMPLATES['DESERT_OUTPOST']['size'] = original_size

if __name__ == "__main__":
    try:
        test_desert_placement_specifically()
        test_smaller_desert_outpost()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()