#!/usr/bin/env python3
"""
Test script for the new modular procedural generation system
Tests individual components and the integrated system
"""

import sys
import os
import time

# Add the procedural generation directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the modular components
from src.biome_generator import BiomeGenerator
from src.settlement_generator import SettlementGenerator
from src.entity_spawner import EntitySpawner
from src.modular_generator import ProceduralWorldGenerator


def test_biome_generator():
    """Test the BiomeGenerator component"""
    print("=" * 50)
    print("Testing BiomeGenerator")
    print("=" * 50)
    
    # Create a small world for testing
    width, height = 50, 50
    seed = 12345
    
    biome_gen = BiomeGenerator(width, height, seed)
    
    # Test biome map generation
    print("Generating biome map...")
    start_time = time.time()
    biome_map = biome_gen.generate_biome_map()
    biome_time = time.time() - start_time
    
    print(f"Biome map generated in {biome_time:.4f} seconds")
    print(f"Dimensions: {len(biome_map)}x{len(biome_map[0])}")
    
    # Get biome statistics
    biome_stats = biome_gen.get_biome_stats(biome_map)
    total_tiles = width * height
    
    print("\nBiome Distribution:")
    for biome, count in biome_stats.items():
        percentage = (count / total_tiles) * 100
        print(f"  {biome}: {count} tiles ({percentage:.1f}%)")
    
    # Test tile generation
    print("\nGenerating tiles...")
    start_time = time.time()
    tiles = biome_gen.generate_tiles(biome_map)
    tile_time = time.time() - start_time
    
    print(f"Tiles generated in {tile_time:.4f} seconds")
    
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
    
    # Test consistency
    print("\nTesting seed consistency...")
    biome_gen2 = BiomeGenerator(width, height, seed)
    biome_map2 = biome_gen2.generate_biome_map()
    
    maps_match = biome_map == biome_map2
    print(f"Same seed produces identical maps: {'✅ YES' if maps_match else '❌ NO'}")
    
    return biome_map, tiles


def test_settlement_generator(tiles, biome_map):
    """Test the SettlementGenerator component"""
    print("\n" + "=" * 50)
    print("Testing SettlementGenerator")
    print("=" * 50)
    
    width, height = len(tiles[0]), len(tiles)
    seed = 12345
    
    settlement_gen = SettlementGenerator(width, height, seed)
    
    print("Placing settlements...")
    start_time = time.time()
    settlements = settlement_gen.place_settlements(tiles, biome_map)
    settlement_time = time.time() - start_time
    
    print(f"Settlements placed in {settlement_time:.4f} seconds")
    print(f"Total settlements placed: {len(settlements)}")
    
    for settlement in settlements:
        print(f"  {settlement['name']} at ({settlement['x']}, {settlement['y']}) "
              f"in {settlement['biome']} biome")
        print(f"    Buildings: {len(settlement['buildings'])}")
    
    # Count building features
    total_windows = 0
    total_doors = 0
    total_brick_tiles = 0
    
    for y in range(height):
        for x in range(width):
            tile_type = tiles[y][x]
            if tile_type == 14 or tile_type == 15:  # Window tiles
                total_windows += 1
            elif tile_type == 5:  # Door tiles
                total_doors += 1
            elif tile_type == 13:  # Brick tiles (interiors)
                total_brick_tiles += 1
    
    print(f"\nBuilding Features:")
    print(f"  Windows: {total_windows} tiles")
    print(f"  Doors: {total_doors} tiles")
    print(f"  Interior floors: {total_brick_tiles} tiles")
    
    return settlements


def test_entity_spawner(tiles, biome_map, settlements):
    """Test the EntitySpawner component (without actual entities)"""
    print("\n" + "=" * 50)
    print("Testing EntitySpawner (Mock Mode)")
    print("=" * 50)
    
    width, height = len(tiles[0]), len(tiles)
    seed = 12345
    
    entity_spawner = EntitySpawner(width, height, seed)
    
    # Mock asset loader
    class MockAssetLoader:
        pass
    
    mock_asset_loader = MockAssetLoader()
    
    # Get safe zones from settlements
    safe_zones = []
    for settlement in settlements:
        center_x = settlement['center_x']
        center_y = settlement['center_y']
        # Use default safe radius
        safe_radius = 20 if settlement['name'] == 'VILLAGE' else 15
        safe_zones.append((center_x, center_y, safe_radius))
    
    print(f"Safe zones: {len(safe_zones)}")
    for i, (x, y, r) in enumerate(safe_zones):
        print(f"  Zone {i+1}: Center ({x}, {y}), Radius {r}")
    
    # Test NPC dialog generation
    print("\nTesting NPC dialog generation...")
    npc_types = ['Master Merchant', 'Village Elder', 'Master Smith', 'Innkeeper']
    for npc_type in npc_types:
        dialog = entity_spawner.get_npc_dialog(npc_type)
        print(f"  {npc_type}: {len(dialog)} dialog lines")
    
    # Test safe zone detection
    print("\nTesting safe zone detection...")
    test_positions = [(10, 10), (25, 25), (40, 40)]
    for x, y in test_positions:
        in_safe_zone = entity_spawner._is_in_safe_zone(x, y, safe_zones)
        distance = entity_spawner._distance_to_nearest_settlement(x, y, safe_zones)
        print(f"  Position ({x}, {y}): Safe zone = {in_safe_zone}, Distance = {distance:.1f}")
    
    print("\nNote: Entity spawning requires actual asset loader and entity classes")
    print("This test only validates the spawning logic without creating entities")


def test_integrated_system():
    """Test the integrated ProceduralWorldGenerator"""
    print("\n" + "=" * 50)
    print("Testing ProceduralWorldGenerator (Integrated)")
    print("=" * 50)
    
    width, height = 100, 100
    seed = 54321
    
    world_gen = ProceduralWorldGenerator(width, height, seed)
    
    print("Generating complete world (without entities)...")
    start_time = time.time()
    world_data = world_gen.generate_world()  # No asset_loader = no entities
    generation_time = time.time() - start_time
    
    print(f"World generated in {generation_time:.4f} seconds")
    
    # Display world statistics
    stats = world_gen.get_world_stats()
    print(f"\nWorld Statistics:")
    print(f"  Seed: {stats['seed']}")
    print(f"  Dimensions: {stats['dimensions']}")
    
    print(f"\nBiome Distribution:")
    for biome, count in stats['biome_stats'].items():
        print(f"  {biome}: {count} tiles")
    
    print(f"\nSettlements:")
    settlement_stats = stats['settlement_stats']
    print(f"  Total: {settlement_stats['total_settlements']}")
    for settlement_type, count in settlement_stats['settlement_types'].items():
        print(f"  {settlement_type}: {count}")
    
    # Test individual component access
    print("\nTesting individual component methods...")
    
    # Test biome-only generation
    biome_map = world_gen.generate_biome_map_only()
    print(f"Biome map: {len(biome_map)}x{len(biome_map[0])}")
    
    # Test tiles-only generation
    tiles = world_gen.generate_tiles_only()
    print(f"Tile map: {len(tiles)}x{len(tiles[0])}")
    
    # Test settlements-only generation
    settlements = world_gen.place_settlements_only()
    print(f"Settlements: {len(settlements)}")
    
    return world_data


def test_performance():
    """Test performance with different world sizes"""
    print("\n" + "=" * 50)
    print("Performance Testing")
    print("=" * 50)
    
    world_sizes = [(50, 50), (100, 100), (200, 200)]
    
    for width, height in world_sizes:
        print(f"\nTesting {width}x{height} world...")
        
        world_gen = ProceduralWorldGenerator(width, height, 12345)
        
        start_time = time.time()
        world_data = world_gen.generate_world()
        generation_time = time.time() - start_time
        
        total_tiles = width * height
        tiles_per_second = total_tiles / generation_time if generation_time > 0 else float('inf')
        
        print(f"  Generation time: {generation_time:.4f} seconds")
        print(f"  Tiles per second: {tiles_per_second:.0f}")
        print(f"  Settlements: {len(world_data['settlements'])}")


def main():
    """Run all tests"""
    print("Modular Procedural Generation System Test Suite")
    print("=" * 60)
    
    try:
        # Test individual components
        biome_map, tiles = test_biome_generator()
        settlements = test_settlement_generator(tiles, biome_map)
        test_entity_spawner(tiles, biome_map, settlements)
        
        # Test integrated system
        test_integrated_system()
        
        # Performance testing
        test_performance()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        print("The modular procedural generation system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)