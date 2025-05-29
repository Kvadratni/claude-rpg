#!/usr/bin/env python3
"""
Debug script to analyze why settlement placement is failing
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

def analyze_placement_failure():
    """Analyze why settlement placement is failing"""
    print("Analyzing Settlement Placement Failure")
    print("=" * 50)
    
    # Create generator
    width, height = 100, 100
    seed = 12345
    generator = ProceduralGenerator(width, height, seed)
    tiles = generator.generate_tiles()
    
    # Test each settlement type individually
    for template_name, template_config in generator.SETTLEMENT_TEMPLATES.items():
        print(f"\nAnalyzing {template_name}:")
        print(f"  Size: {template_config['size']}")
        print(f"  Required biomes: {template_config['biomes']}")
        
        settlement_width, settlement_height = template_config['size']
        suitable_biomes = template_config['biomes']
        
        # Count available biome tiles
        biome_counts = {}
        suitable_positions = 0
        water_blocked = 0
        margin_blocked = 0
        
        for attempt in range(100):  # Test 100 random positions
            # Random position with margins
            x = random.randint(10, width - settlement_width - 10)
            y = random.randint(10, height - settlement_height - 10)
            
            # Check if biome is suitable
            center_biome = generator.biome_map[y + settlement_height // 2][x + settlement_width // 2]
            biome_counts[center_biome] = biome_counts.get(center_biome, 0) + 1
            
            if center_biome not in suitable_biomes:
                continue
            
            suitable_positions += 1
            
            # Check terrain suitability (no water in settlement area)
            if generator.has_water_in_area(tiles, x, y, settlement_width, settlement_height):
                water_blocked += 1
                continue
        
        print(f"  Biome distribution in 100 random positions:")
        for biome, count in biome_counts.items():
            marker = "✅" if biome in suitable_biomes else "❌"
            print(f"    {marker} {biome}: {count}")
        
        print(f"  Suitable biome positions: {suitable_positions}/100")
        print(f"  Water-blocked positions: {water_blocked}")
        
        # Calculate actual biome coverage
        total_suitable_tiles = 0
        total_tiles = width * height
        
        for y in range(height):
            for x in range(width):
                if generator.biome_map[y][x] in suitable_biomes:
                    total_suitable_tiles += 1
        
        suitable_percentage = (total_suitable_tiles / total_tiles) * 100
        print(f"  Total suitable biome coverage: {suitable_percentage:.1f}%")
        
        # Test water density in suitable biomes
        water_in_suitable_biomes = 0
        suitable_area_samples = 0
        
        for y in range(10, height - settlement_height - 10):
            for x in range(10, width - settlement_width - 10):
                center_biome = generator.biome_map[y + settlement_height // 2][x + settlement_width // 2]
                if center_biome in suitable_biomes:
                    suitable_area_samples += 1
                    if generator.has_water_in_area(tiles, x, y, settlement_width, settlement_height):
                        water_in_suitable_biomes += 1
        
        if suitable_area_samples > 0:
            water_block_rate = (water_in_suitable_biomes / suitable_area_samples) * 100
            print(f"  Water blocking rate in suitable areas: {water_block_rate:.1f}%")
        else:
            print(f"  ❌ No suitable area samples found!")

def test_water_generation():
    """Test water generation rates"""
    print(f"\nTesting Water Generation")
    print("=" * 30)
    
    generator = ProceduralGenerator(100, 100, 12345)
    tiles = generator.generate_tiles()
    
    # Count water tiles by biome
    water_by_biome = {'DESERT': 0, 'PLAINS': 0, 'FOREST': 0, 'SNOW': 0}
    total_by_biome = {'DESERT': 0, 'PLAINS': 0, 'FOREST': 0, 'SNOW': 0}
    
    for y in range(generator.height):
        for x in range(generator.width):
            biome = generator.biome_map[y][x]
            total_by_biome[biome] += 1
            
            if tiles[y][x] == 3:  # TILE_WATER
                water_by_biome[biome] += 1
    
    print("Water generation by biome:")
    for biome in ['DESERT', 'PLAINS', 'FOREST', 'SNOW']:
        water_count = water_by_biome[biome]
        total_count = total_by_biome[biome]
        if total_count > 0:
            water_percentage = (water_count / total_count) * 100
            expected = generator.BIOME_TILES[biome]['water_chance'] * 100
            print(f"  {biome}: {water_count}/{total_count} ({water_percentage:.2f}%) - Expected: {expected:.2f}%")

def test_reduced_water():
    """Test with reduced water generation"""
    print(f"\nTesting with Reduced Water Generation")
    print("=" * 40)
    
    # Temporarily reduce water chances
    original_water_chances = {}
    for biome, config in ProceduralGenerator.BIOME_TILES.items():
        original_water_chances[biome] = config['water_chance']
        config['water_chance'] = config['water_chance'] * 0.1  # Reduce by 90%
    
    try:
        generator = ProceduralGenerator(100, 100, 12345)
        tiles = generator.generate_tiles()
        settlements = generator.place_settlements(tiles)
        
        print(f"With reduced water: Placed {len(settlements)} settlements")
        
        for settlement in settlements:
            print(f"  ✅ {settlement['name']} at ({settlement['x']}, {settlement['y']}) in {settlement['biome']}")
    
    finally:
        # Restore original water chances
        for biome, original_chance in original_water_chances.items():
            ProceduralGenerator.BIOME_TILES[biome]['water_chance'] = original_chance

if __name__ == "__main__":
    try:
        analyze_placement_failure()
        test_water_generation()
        test_reduced_water()
        
    except Exception as e:
        print(f"\n❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()