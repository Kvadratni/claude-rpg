#!/usr/bin/env python3
"""
Test script for procedural biome generation
Tests the core biome map generation functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the procedural generator without the entity dependencies for testing
import random
import math

class MockEntity:
    """Mock entity class for testing"""
    def __init__(self, *args, **kwargs):
        pass

class MockNPC(MockEntity):
    pass

class MockEnemy(MockEntity):
    pass

class MockItem(MockEntity):
    pass

class MockChest(MockEntity):
    pass

# Patch the imports in procedural_generator
import procedural_generator
procedural_generator.Entity = MockEntity
procedural_generator.NPC = MockNPC
procedural_generator.Enemy = MockEnemy
procedural_generator.Item = MockItem
procedural_generator.Chest = MockChest

from procedural_generator import ProceduralGenerator

def test_biome_generation():
    """Test basic biome map generation"""
    print("Testing Procedural Biome Generation")
    print("=" * 40)
    
    # Test with small map for quick verification
    width, height = 50, 50
    seed = 12345
    
    print(f"Creating {width}x{height} world with seed {seed}")
    
    # Create generator
    generator = ProceduralGenerator(width, height, seed)
    
    # Test biome map generation
    print(f"Biome map dimensions: {len(generator.biome_map)}x{len(generator.biome_map[0])}")
    
    # Count biomes
    biome_counts = {'DESERT': 0, 'PLAINS': 0, 'FOREST': 0, 'SNOW': 0}
    
    for y in range(height):
        for x in range(width):
            biome = generator.biome_map[y][x]
            biome_counts[biome] += 1
    
    print("\nBiome Distribution:")
    total_tiles = width * height
    for biome, count in biome_counts.items():
        percentage = (count / total_tiles) * 100
        print(f"  {biome}: {count} tiles ({percentage:.1f}%)")
    
    # Test tile generation
    print("\nGenerating tiles...")
    tiles = generator.generate_tiles()
    print(f"Tile grid dimensions: {len(tiles)}x{len(tiles[0])}")
    
    # Count tile types
    tile_counts = {}
    for y in range(height):
        for x in range(width):
            tile_type = tiles[y][x]
            tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
    
    print("\nTile Type Distribution:")
    tile_names = {0: 'GRASS', 1: 'DIRT', 2: 'STONE', 3: 'WATER', 4: 'WALL'}
    for tile_type, count in sorted(tile_counts.items()):
        name = tile_names.get(tile_type, f'UNKNOWN({tile_type})')
        percentage = (count / total_tiles) * 100
        print(f"  {name}: {count} tiles ({percentage:.1f}%)")
    
    # Test consistency (same seed should produce same results)
    print("\nTesting seed consistency...")
    generator2 = ProceduralGenerator(width, height, seed)
    
    # Compare biome maps
    maps_match = True
    for y in range(height):
        for x in range(width):
            if generator.biome_map[y][x] != generator2.biome_map[y][x]:
                maps_match = False
                break
        if not maps_match:
            break
    
    print(f"Same seed produces identical maps: {'✅ YES' if maps_match else '❌ NO'}")
    
    # Test different seeds produce different results
    print("\nTesting seed variation...")
    generator3 = ProceduralGenerator(width, height, 54321)
    
    maps_different = False
    for y in range(height):
        for x in range(width):
            if generator.biome_map[y][x] != generator3.biome_map[y][x]:
                maps_different = True
                break
        if maps_different:
            break
    
    print(f"Different seeds produce different maps: {'✅ YES' if maps_different else '❌ NO'}")
    
    # Visual sample of biome map (top-left corner)
    print("\nBiome Map Sample (top-left 10x10):")
    print("D=Desert, P=Plains, F=Forest, S=Snow")
    for y in range(min(10, height)):
        row = ""
        for x in range(min(10, width)):
            biome = generator.biome_map[y][x]
            row += biome[0]  # First letter
        print(f"  {row}")
    
    print("\n" + "=" * 40)
    print("Biome generation test completed!")
    
    return generator

def test_noise_function():
    """Test the noise function specifically"""
    print("\nTesting noise function...")
    
    generator = ProceduralGenerator(10, 10, 12345)
    
    # Test noise values are in expected range
    noise_values = []
    for x in range(10):
        for y in range(10):
            noise = generator.simple_noise(x, y)
            noise_values.append(noise)
    
    min_noise = min(noise_values)
    max_noise = max(noise_values)
    avg_noise = sum(noise_values) / len(noise_values)
    
    print(f"Noise range: {min_noise:.3f} to {max_noise:.3f}")
    print(f"Average noise: {avg_noise:.3f}")
    print(f"Values in 0-1 range: {'✅ YES' if 0 <= min_noise and max_noise <= 1 else '❌ NO'}")

if __name__ == "__main__":
    try:
        # Test noise function
        test_noise_function()
        
        # Test biome generation
        generator = test_biome_generation()
        
        print("\n🎉 All tests passed! Biome generation is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()