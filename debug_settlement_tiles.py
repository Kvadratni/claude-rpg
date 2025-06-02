#!/usr/bin/env python3
"""
Debug script to check settlement tile placement
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

# Import from the src directory
import src.world.world_generator as world_gen
import src.world.chunk as chunk_mod

def debug_settlement_tiles():
    """Debug settlement tile placement"""
    print("=== Settlement Tile Debug ===")
    
    # Create world generator with fixed seed
    world_seed = 903315  # Same seed from our test
    generator = world_gen.WorldGenerator(world_seed)
    
    # Generate the chunk that had a successful village (chunk -3,-3 from our test)
    print("Generating chunk (-3, -3) with VILLAGE settlement...")
    chunk = generator.generate_chunk(-3, -3)
    
    print(f"Chunk generated: {chunk.is_generated}")
    print(f"Chunk loaded: {chunk.is_loaded}")
    print(f"Chunk has {len(chunk.entities)} entities")
    
    # Check NPCs
    npcs = [e for e in chunk.entities if e.get('type') == 'npc']
    print(f"NPCs in chunk: {len(npcs)}")
    for npc in npcs:
        print(f"  - {npc.get('name')} at ({npc.get('x')}, {npc.get('y')})")
    
    # Check tiles around NPC locations
    print("\n=== Tile Analysis Around NPCs ===")
    for npc in npcs[:3]:  # Check first 3 NPCs
        npc_x = int(npc.get('x', 0))
        npc_y = int(npc.get('y', 0))
        print(f"\nNPC: {npc.get('name')} at ({npc_x}, {npc_y})")
        
        # Check 5x5 area around NPC
        for dy in range(-2, 3):
            row = []
            for dx in range(-2, 3):
                tile_x = npc_x + dx
                tile_y = npc_y + dy
                tile = chunk.get_tile(tile_x, tile_y)
                if tile is None:
                    row.append("?")
                else:
                    row.append(str(tile))
            print(f"  {' '.join(f'{t:>2}' for t in row)}")
    
    # Check a larger area for building patterns
    print("\n=== Settlement Area Tile Map (20x20 around center) ===")
    center_x, center_y = 32, 32  # Center of 64x64 chunk
    
    print("Tile Legend:")
    print("  0=GRASS, 1=DIRT, 2=STONE, 4=WALL, 5=DOOR, 13=BRICK")
    print("  6-9=WALL_CORNERS, 10-11=WALL_H/V, 14-15=WALL_WINDOWS")
    print("")
    
    for y in range(center_y - 10, center_y + 10):
        row = []
        for x in range(center_x - 10, center_x + 10):
            tile = chunk.get_tile(x, y)
            if tile is None:
                row.append("?")
            else:
                row.append(str(tile))
        print(f"  {' '.join(f'{t:>2}' for t in row)}")
    
    # Count tile types
    print("\n=== Tile Type Counts ===")
    tile_counts = {}
    for y in range(chunk_mod.Chunk.CHUNK_SIZE):
        for x in range(chunk_mod.Chunk.CHUNK_SIZE):
            tile = chunk.get_tile(x, y)
            if tile is not None:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1
    
    for tile_type, count in sorted(tile_counts.items()):
        print(f"  Tile {tile_type}: {count} tiles")
    
    # Check if building tiles exist
    building_tiles = [4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]  # Wall and building related tiles
    building_count = sum(tile_counts.get(tile, 0) for tile in building_tiles)
    print(f"\nTotal building-related tiles: {building_count}")
    
    if building_count == 0:
        print("❌ NO BUILDING TILES FOUND! Buildings are not being placed in chunk data.")
    else:
        print(f"✅ Building tiles found! {building_count} building-related tiles in chunk.")

if __name__ == "__main__":
    debug_settlement_tiles()