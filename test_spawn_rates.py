#!/usr/bin/env python3
"""
Test script to verify spawn rates and procedural generation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.procedural_generation.src.enhanced_entity_spawner import EnhancedEntitySpawner
from src.procedural_generation.src.biome_generator import BiomeGenerator
from src.world.settlement_manager import ChunkSettlementManager

def test_spawn_rates():
    """Test the spawn rates with a small test area"""
    print("Testing spawn rates...")
    
    # Create a small test area
    width, height = 64, 64  # One chunk size
    seed = 12345
    
    # Generate biomes and tiles
    biome_gen = BiomeGenerator(width, height, seed)
    biome_map = biome_gen.generate_biome_map()
    tiles = biome_gen.generate_tiles(biome_map)
    
    # Count biomes
    biome_counts = {}
    for y in range(height):
        for x in range(width):
            biome = biome_map[y][x]
            biome_counts[biome] = biome_counts.get(biome, 0) + 1
    
    print(f"Biome distribution in {width}x{height} area:")
    for biome, count in biome_counts.items():
        percentage = (count / (width * height)) * 100
        print(f"  {biome}: {count} tiles ({percentage:.1f}%)")
    
    # Test entity spawning
    spawner = EnhancedEntitySpawner(width, height, seed)
    
    # Test object spawning
    print("\nTesting object spawning...")
    objects = spawner.spawn_objects(tiles, biome_map, [], None)
    print(f"Generated {len(objects)} objects")
    
    # Count objects by biome
    object_biomes = {}
    for obj in objects:
        if hasattr(obj, 'x') and hasattr(obj, 'y'):
            x, y = int(obj.x), int(obj.y)
            if 0 <= x < width and 0 <= y < height:
                biome = biome_map[y][x]
                object_biomes[biome] = object_biomes.get(biome, 0) + 1
    
    print("Objects by biome:")
    for biome, count in object_biomes.items():
        biome_tile_count = biome_counts.get(biome, 0)
        if biome_tile_count > 0:
            density = (count / biome_tile_count) * 100
            print(f"  {biome}: {count} objects ({density:.2f}% of {biome} tiles)")
    
    # Test enemy spawning
    print("\nTesting enemy spawning...")
    enemies = spawner.spawn_enemies(tiles, biome_map, [], None)
    print(f"Generated {len(enemies)} enemies")
    
    total_tiles = width * height
    enemy_density = (len(enemies) / total_tiles) * 100
    print(f"Enemy density: {enemy_density:.3f}% of total tiles")
    
    # Test settlement generation
    print("\nTesting settlement generation...")
    settlement_manager = ChunkSettlementManager(seed)
    
    # Test a few chunks
    settlements_found = 0
    npcs_found = 0
    
    for chunk_x in range(-2, 3):
        for chunk_y in range(-2, 3):
            settlement_type = settlement_manager.should_generate_settlement(chunk_x, chunk_y, biome_counts)
            if settlement_type:
                settlement_data = settlement_manager.generate_settlement_in_chunk(chunk_x, chunk_y, settlement_type)
                settlements_found += 1
                npcs_found += len(settlement_data.get('npcs', []))
                print(f"  Found {settlement_type} at chunk ({chunk_x}, {chunk_y}) with {len(settlement_data.get('npcs', []))} NPCs")
    
    print(f"\nSettlement summary:")
    print(f"  Settlements found in 5x5 chunk area: {settlements_found}")
    print(f"  Total NPCs from settlements: {npcs_found}")
    
    if settlements_found == 0:
        print("  WARNING: No settlements found! This might indicate a problem.")
    
    if npcs_found == 0:
        print("  WARNING: No NPCs found! This might indicate a problem.")

if __name__ == "__main__":
    test_spawn_rates()