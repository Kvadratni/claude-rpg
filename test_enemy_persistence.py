#!/usr/bin/env python3
"""
Test script to verify enemy persistence fixes
"""

import os
import sys
import json
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_enemy_persistence():
    """Test that enemies are properly removed from chunks when killed"""
    
    print("=== Enemy Persistence Test ===")
    
    # Test chunk directory
    test_world_dir = "saves/worlds/test_enemy_persistence"
    
    # Clean up any existing test data
    if os.path.exists(test_world_dir):
        import shutil
        shutil.rmtree(test_world_dir)
    
    try:
        from world.chunk_manager import ChunkManager
        from world.world_generator import WorldGenerator
        
        # Create chunk manager
        chunk_manager = ChunkManager(12345, "test_enemy_persistence")
        
        print(f"1. Created chunk manager for world: {test_world_dir}")
        
        # Load a chunk (this will generate it)
        chunk = chunk_manager.get_chunk(0, 0)
        
        print(f"2. Generated chunk (0, 0) with {len(chunk.entities)} entities")
        
        # Count initial enemies
        initial_enemies = [e for e in chunk.entities if e['type'] == 'enemy']
        print(f"3. Initial enemies in chunk: {len(initial_enemies)}")
        
        if initial_enemies:
            # Simulate killing the first enemy
            enemy_to_kill = initial_enemies[0]
            enemy_id = enemy_to_kill['id']
            enemy_x = enemy_to_kill['x']
            enemy_y = enemy_to_kill['y']
            
            print(f"4. Simulating death of enemy: {enemy_id} at ({enemy_x}, {enemy_y})")
            
            # Remove enemy from chunk
            chunk_manager.remove_entity_from_chunks(enemy_id, enemy_x, enemy_y)
            
            # Reload the chunk to verify persistence
            chunk_manager.loaded_chunks.clear()  # Force reload
            reloaded_chunk = chunk_manager.get_chunk(0, 0)
            
            # Count enemies after reload
            remaining_enemies = [e for e in reloaded_chunk.entities if e['type'] == 'enemy']
            print(f"5. Enemies after reload: {len(remaining_enemies)}")
            
            # Verify the specific enemy is gone
            enemy_still_exists = any(e['id'] == enemy_id for e in remaining_enemies)
            
            if enemy_still_exists:
                print("❌ FAILED: Enemy still exists in chunk after being killed!")
                return False
            else:
                print("✅ SUCCESS: Enemy was properly removed from chunk!")
                
            # Verify other enemies are still there
            if len(remaining_enemies) == len(initial_enemies) - 1:
                print("✅ SUCCESS: Other enemies remain intact!")
                return True
            else:
                print(f"❌ FAILED: Expected {len(initial_enemies) - 1} enemies, got {len(remaining_enemies)}")
                return False
        else:
            print("❌ FAILED: No enemies found in generated chunk!")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test data
        if os.path.exists(test_world_dir):
            import shutil
            shutil.rmtree(test_world_dir)
            print("6. Cleaned up test data")

def test_enemy_loading():
    """Test that enemies are properly loaded from chunks"""
    
    print("\n=== Enemy Loading Test ===")
    
    try:
        from world.chunked_level import ChunkedLevel
        from core.assets import AssetLoader
        
        # Mock player object
        class MockPlayer:
            def __init__(self):
                self.x = 32  # Center of chunk
                self.y = 32
        
        # Create mock asset loader
        asset_loader = AssetLoader()
        player = MockPlayer()
        
        # Create chunked level
        level = ChunkedLevel("test_level", player, asset_loader, world_seed=12345)
        
        print("1. Created chunked level")
        
        # Update entities from chunks (this should load enemies)
        level.update_entities_from_chunks()
        
        print(f"2. Loaded entities: {len(level.enemies)} enemies, {len(level.npcs)} NPCs, {len(level.objects)} objects")
        
        if len(level.enemies) > 0:
            print("✅ SUCCESS: Enemies were loaded from chunks!")
            
            # Test enemy properties
            enemy = level.enemies[0]
            print(f"3. First enemy: {enemy.name} at ({enemy.x}, {enemy.y}) with {enemy.health} health")
            
            return True
        else:
            print("❌ FAILED: No enemies were loaded from chunks!")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing enemy persistence fixes...\n")
    
    # Run tests
    test1_passed = test_enemy_persistence()
    test2_passed = test_enemy_loading()
    
    print(f"\n=== Test Results ===")
    print(f"Enemy Persistence Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Enemy Loading Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Enemy persistence should now work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")