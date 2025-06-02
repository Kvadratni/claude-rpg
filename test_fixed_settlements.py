#!/usr/bin/env python3
"""
Test script to verify the settlement building fixes work correctly
"""

import sys
import os
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, 'src')

def test_settlement_generation():
    """Test settlement generation with the fixes"""
    print("🧪 TESTING FIXED SETTLEMENT GENERATION")
    print("=" * 50)
    
    try:
        # Import the fixed modules
        from world.chunk_manager import ChunkManager
        from world.world_generator import WorldGenerator
        
        # Test with a specific seed
        test_seed = 999888
        print(f"Testing with seed: {test_seed}")
        
        # Create world generator
        world_generator = WorldGenerator(test_seed)
        
        # Test generating a few chunks
        test_chunks = [(0, 0), (1, 0), (0, 1)]
        
        for chunk_x, chunk_y in test_chunks:
            print(f"\n--- Testing chunk ({chunk_x}, {chunk_y}) ---")
            
            # Generate chunk
            chunk = world_generator.generate_chunk(chunk_x, chunk_y)
            
            if chunk:
                print(f"✅ Generated chunk successfully")
                print(f"   Chunk size: {len(chunk.tiles)}x{len(chunk.tiles[0]) if chunk.tiles else 0}")
                print(f"   Total entities: {len(chunk.entities)}")
                
                # Count different tile types
                tile_counts = {}
                for row in chunk.tiles:
                    for tile in row:
                        tile_counts[tile] = tile_counts.get(tile, 0) + 1
                
                # Count building tiles
                building_tiles = [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]
                total_building_tiles = sum(tile_counts.get(tile, 0) for tile in building_tiles)
                
                print(f"   Building tiles: {total_building_tiles}")
                
                if total_building_tiles > 0:
                    print("   Building tile breakdown:")
                    tile_names = {
                        2: "STONE", 4: "WALL", 5: "DOOR", 6: "WALL_CORNER_TL", 7: "WALL_CORNER_TR",
                        8: "WALL_CORNER_BL", 9: "WALL_CORNER_BR", 10: "WALL_HORIZONTAL", 11: "WALL_VERTICAL",
                        13: "BRICK", 14: "WALL_WINDOW_HORIZONTAL", 15: "WALL_WINDOW_VERTICAL"
                    }
                    for tile_id in building_tiles:
                        count = tile_counts.get(tile_id, 0)
                        if count > 0:
                            print(f"     {tile_names[tile_id]}: {count}")
                
                # Count entity types
                entity_types = {}
                for entity in chunk.entities:
                    entity_type = entity.get('type', 'unknown')
                    entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
                
                print(f"   Entity breakdown:")
                for entity_type, count in entity_types.items():
                    print(f"     {entity_type}: {count}")
                
                # Show NPCs specifically
                npcs = [e for e in chunk.entities if e['type'] == 'npc']
                if npcs:
                    print(f"   🧙 NPCs found:")
                    for npc in npcs:
                        print(f"     - {npc['name']} at ({npc['x']}, {npc['y']})")
                
                # Test result
                has_buildings = total_building_tiles > 10  # More than just stone center
                has_npcs = len(npcs) > 0
                
                if has_buildings and has_npcs:
                    print(f"   🎉 SUCCESS: Chunk has both buildings ({total_building_tiles} tiles) and NPCs ({len(npcs)})")
                elif has_buildings:
                    print(f"   ⚠️  PARTIAL: Chunk has buildings ({total_building_tiles} tiles) but no NPCs")
                elif has_npcs:
                    print(f"   ⚠️  PARTIAL: Chunk has NPCs ({len(npcs)}) but no proper buildings")
                else:
                    print(f"   ℹ️  No settlement in this chunk")
            else:
                print(f"❌ Failed to generate chunk")
        
        print(f"\n" + "=" * 50)
        print("🧪 TEST COMPLETE")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


def test_chunk_persistence():
    """Test that chunks save and load correctly"""
    print("\n🧪 TESTING CHUNK PERSISTENCE")
    print("=" * 30)
    
    try:
        from world.chunk_manager import ChunkManager
        
        test_seed = 999888
        world_name = f"test_persistence_{test_seed}"
        
        # Create chunk manager
        chunk_manager = ChunkManager(test_seed, world_name)
        
        # Generate a chunk
        print("Generating test chunk...")
        chunk = chunk_manager.get_chunk(0, 0)
        
        if chunk:
            # Count entities and building tiles before save
            entities_before = len(chunk.entities)
            building_tiles_before = 0
            for row in chunk.tiles:
                for tile in row:
                    if tile in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]:
                        building_tiles_before += 1
            
            print(f"Before save: {entities_before} entities, {building_tiles_before} building tiles")
            
            # Force save
            chunk.save_to_file(chunk_manager.world_dir)
            print("Chunk saved")
            
            # Clear from memory and reload
            del chunk_manager.loaded_chunks[(0, 0)]
            
            # Reload chunk
            print("Reloading chunk...")
            reloaded_chunk = chunk_manager.get_chunk(0, 0)
            
            if reloaded_chunk:
                # Count entities and building tiles after reload
                entities_after = len(reloaded_chunk.entities)
                building_tiles_after = 0
                for row in reloaded_chunk.tiles:
                    for tile in row:
                        if tile in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]:
                            building_tiles_after += 1
                
                print(f"After reload: {entities_after} entities, {building_tiles_after} building tiles")
                
                # Check persistence
                if entities_before == entities_after and building_tiles_before == building_tiles_after:
                    print("✅ PERSISTENCE TEST PASSED")
                else:
                    print("❌ PERSISTENCE TEST FAILED")
                    print(f"   Entities: {entities_before} -> {entities_after}")
                    print(f"   Building tiles: {building_tiles_before} -> {building_tiles_after}")
            else:
                print("❌ Failed to reload chunk")
        else:
            print("❌ Failed to generate test chunk")
            
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")


if __name__ == "__main__":
    test_settlement_generation()
    test_chunk_persistence()