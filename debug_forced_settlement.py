#!/usr/bin/env python3
"""
Debug script to force settlement placement and check tile array
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import from the src directory
import src.world.world_generator as world_gen
import src.world.chunk as chunk_mod
import src.world.settlement_manager as settlement_mgr

def debug_forced_settlement():
    """Debug settlement tile placement with forced settlement"""
    print("=== Forced Settlement Tile Debug ===")
    
    # Create world generator with fixed seed
    world_seed = 12345
    generator = world_gen.WorldGenerator(world_seed)
    
    # Generate a basic chunk first
    print("Generating basic chunk (0, 0)...")
    chunk = generator.generate_chunk(0, 0)
    
    print(f"Chunk generated: {chunk.is_generated}")
    print(f"Chunk loaded: {chunk.is_loaded}")
    print(f"Initial chunk tiles array length: {len(chunk.tiles) if chunk.tiles else 'None/Empty'}")
    
    if chunk.tiles and len(chunk.tiles) > 0:
        print(f"Tiles array dimensions: {len(chunk.tiles)}x{len(chunk.tiles[0])}")
        
        # Test setting a tile directly
        print("Testing direct tile setting...")
        original_tile = chunk.get_tile(10, 10)
        print(f"Original tile at (10, 10): {original_tile}")
        
        chunk.set_tile(10, 10, 4)  # Set to WALL
        new_tile = chunk.get_tile(10, 10)
        print(f"After setting to WALL (4), tile at (10, 10): {new_tile}")
        
        if new_tile == 4:
            print("✅ Direct tile setting works!")
        else:
            print("❌ Direct tile setting failed!")
            
        # Now test the building placement method
        print("\nTesting building placement method...")
        
        # Create a fake settlement data
        fake_settlement = {
            'world_x': 10,  # Will be converted to local coords
            'world_y': 10,
            'size': (12, 12),
            'buildings': [
                {'name': 'Test Building', 'size': (3, 3), 'npc': 'Test NPC'}
            ]
        }
        
        # Call the building placement method directly
        try:
            generator._place_settlement_buildings_on_chunk(chunk, fake_settlement)
            print("Building placement method completed")
            
            # Check if any building tiles were placed
            building_tiles = [4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]
            building_count = 0
            for y in range(chunk_mod.Chunk.CHUNK_SIZE):
                for x in range(chunk_mod.Chunk.CHUNK_SIZE):
                    tile = chunk.get_tile(x, y)
                    if tile in building_tiles:
                        building_count += 1
                        if building_count <= 5:  # Show first 5 building tiles found
                            print(f"Found building tile {tile} at ({x}, {y})")
            
            print(f"Total building tiles found: {building_count}")
            
        except Exception as e:
            print(f"Error in building placement: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Chunk tiles array is not initialized!")

if __name__ == "__main__":
    debug_forced_settlement()