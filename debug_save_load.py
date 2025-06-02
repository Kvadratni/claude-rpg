#!/usr/bin/env python3
"""
Debug script to test chunk save/load with buildings
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import from the src directory
import src.world.world_generator as world_gen
import src.world.chunk as chunk_mod

def test_chunk_save_load():
    """Test if buildings survive the save/load process"""
    print("=== Chunk Save/Load Test ===")
    
    # Create world generator
    world_seed = 12345
    generator = world_gen.WorldGenerator(world_seed)
    
    # Generate a chunk with forced settlement
    print("1. Generating chunk with buildings...")
    chunk = generator.generate_chunk(0, 0)
    
    # Force a settlement for testing
    fake_settlement = {
        'world_x': 20,
        'world_y': 20, 
        'size': (12, 12),
        'buildings': [
            {'name': 'Test Building', 'size': (3, 3), 'npc': 'Test NPC'}
        ]
    }
    
    generator._place_settlement_buildings_on_chunk(chunk, fake_settlement)
    
    # Count building tiles before save
    building_tiles = [4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]
    building_count_before = 0
    for y in range(chunk_mod.Chunk.CHUNK_SIZE):
        for x in range(chunk_mod.Chunk.CHUNK_SIZE):
            tile = chunk.get_tile(x, y)
            if tile in building_tiles:
                building_count_before += 1
    
    print(f"Building tiles before save: {building_count_before}")
    
    # Save chunk to file
    print("2. Saving chunk to file...")
    test_dir = "test_save"
    os.makedirs(test_dir, exist_ok=True)
    chunk.save_to_file(test_dir)
    
    # Load chunk from file
    print("3. Loading chunk from file...")
    new_chunk = chunk_mod.Chunk(0, 0, world_seed)
    success = new_chunk.load_from_file(test_dir)
    print(f"Load successful: {success}")
    
    if success:
        # Count building tiles after load
        building_count_after = 0
        for y in range(chunk_mod.Chunk.CHUNK_SIZE):
            for x in range(chunk_mod.Chunk.CHUNK_SIZE):
                tile = new_chunk.get_tile(x, y)
                if tile in building_tiles:
                    building_count_after += 1
        
        print(f"Building tiles after load: {building_count_after}")
        
        if building_count_before == building_count_after and building_count_after > 0:
            print("✅ Buildings survive save/load process!")
        elif building_count_after == 0:
            print("❌ Buildings lost during save/load!")
        else:
            print(f"⚠️  Building count changed: {building_count_before} -> {building_count_after}")
            
        # Check the saved JSON file directly
        print("4. Checking saved JSON file...")
        json_file = os.path.join(test_dir, "chunk_0_0.json")
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        tiles = data['tiles']
        tile_counts = {}
        for row in tiles:
            for tile in row:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1
        
        json_building_count = sum(tile_counts.get(tile, 0) for tile in building_tiles)
        print(f"Building tiles in JSON file: {json_building_count}")
        
        if json_building_count > 0:
            print("✅ Buildings are saved in JSON file!")
        else:
            print("❌ Buildings missing from JSON file!")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)

if __name__ == "__main__":
    test_chunk_save_load()