#!/usr/bin/env python3
"""
Debug script to check if pre-generated chunks have buildings
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import from the src directory
import src.world.chunk_manager as chunk_mgr

def test_pregenerated_chunks():
    """Test if pre-generated chunks have buildings"""
    print("=== Pre-generated Chunk Test ===")
    
    # Use the same seed from our game test
    world_seed = 903315
    world_name = f"procedural_{world_seed}"
    
    # Create chunk manager (this will use existing saved chunks if they exist)
    chunk_manager = chunk_mgr.ChunkManager(world_seed, world_name)
    
    # Test several chunks that should have settlements
    test_chunks = [(-3, -3), (-2, -3), (0, 0), (1, 2), (2, -3)]
    
    for chunk_x, chunk_y in test_chunks:
        print(f"\n--- Testing chunk ({chunk_x}, {chunk_y}) ---")
        
        # Get the chunk (will load from disk if it exists, or generate new)
        chunk = chunk_manager.get_chunk(chunk_x, chunk_y)
        
        if chunk:
            print(f"Chunk loaded: {chunk.is_loaded}")
            print(f"Chunk generated: {chunk.is_generated}")
            print(f"Entities in chunk: {len(chunk.entities)}")
            
            # Check for NPCs (indicates settlement)
            npcs = [e for e in chunk.entities if e.get('type') == 'npc']
            print(f"NPCs in chunk: {len(npcs)}")
            for npc in npcs:
                print(f"  - {npc.get('name')} at ({npc.get('x')}, {npc.get('y')})")
            
            # Count building tiles
            building_tiles = [4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]
            building_count = 0
            
            for y in range(chunk.CHUNK_SIZE):
                for x in range(chunk.CHUNK_SIZE):
                    tile = chunk.get_tile(x, y)
                    if tile in building_tiles:
                        building_count += 1
            
            print(f"Building tiles in chunk: {building_count}")
            
            if len(npcs) > 0 and building_count == 0:
                print("❌ PROBLEM: Settlement has NPCs but NO BUILDINGS!")
            elif len(npcs) > 0 and building_count > 0:
                print(f"✅ Settlement has both NPCs and buildings ({building_count} building tiles)")
            elif len(npcs) == 0 and building_count == 0:
                print("⚪ No settlement in this chunk")
            else:
                print(f"⚠️  Unusual: {building_count} building tiles but no NPCs")
        else:
            print("❌ Failed to load/generate chunk")

if __name__ == "__main__":
    test_pregenerated_chunks()