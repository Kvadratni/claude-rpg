#!/usr/bin/env python3
"""
Test script for enhanced building generation in procedural system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from procedural_generation.src.procedural_generator import ProceduralGenerator

def test_enhanced_building_generation():
    """Test the enhanced building generation system"""
    print("Testing Enhanced Building Generation")
    print("=" * 50)
    
    # Test with a specific seed for reproducible results
    test_seed = 12345
    generator = ProceduralGenerator(100, 100, seed=test_seed)
    
    # Generate tiles
    tiles = generator.generate_tiles()
    
    # Place settlements (which will use the enhanced building system)
    settlements = generator.place_settlements(tiles)
    
    print(f"\nGeneration Results:")
    print(f"- Seed: {test_seed}")
    print(f"- Map size: 100x100")
    print(f"- Settlements placed: {len(settlements)}")
    
    # Analyze building details
    total_buildings = 0
    building_details = []
    
    for settlement in settlements:
        print(f"\n{settlement['name']} Settlement:")
        print(f"  Location: ({settlement['x']}, {settlement['y']})")
        print(f"  Size: {settlement['size']}")
        print(f"  Biome: {settlement['biome']}")
        
        buildings = settlement.get('buildings', [])
        total_buildings += len(buildings)
        
        for building in buildings:
            building_info = {
                'name': building['name'],
                'size': building['size'],
                'has_npc': 'npc' in building and building['npc'] is not None,
                'has_shop': building.get('has_shop', False)
            }
            building_details.append(building_info)
            
            print(f"    - {building['name']}: {building['size']} " +
                  f"{'(Shop)' if building.get('has_shop') else ''}")
    
    print(f"\nBuilding Summary:")
    print(f"- Total buildings: {total_buildings}")
    print(f"- Buildings with NPCs: {sum(1 for b in building_details if b['has_npc'])}")
    print(f"- Buildings with shops: {sum(1 for b in building_details if b['has_shop'])}")
    
    # Test tile analysis around buildings
    print(f"\nTile Analysis:")
    wall_types = {
        4: "TILE_WALL",
        10: "TILE_WALL_HORIZONTAL", 
        11: "TILE_WALL_VERTICAL",
        14: "TILE_WALL_WINDOW_HORIZONTAL",
        15: "TILE_WALL_WINDOW_VERTICAL",
        5: "TILE_DOOR",
        13: "TILE_BRICK"
    }
    
    tile_counts = {}
    for y in range(100):
        for x in range(100):
            tile_type = tiles[y][x]
            if tile_type in wall_types:
                tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
    
    for tile_type, count in tile_counts.items():
        print(f"- {wall_types[tile_type]}: {count} tiles")
    
    # Test specific building features
    print(f"\nBuilding Features Test:")
    
    # Check for windows
    window_tiles = tile_counts.get(14, 0) + tile_counts.get(15, 0)
    print(f"- Window tiles: {window_tiles}")
    
    # Check for doors
    door_tiles = tile_counts.get(5, 0)
    print(f"- Door tiles: {door_tiles}")
    
    # Check for interior floors
    brick_tiles = tile_counts.get(13, 0)
    print(f"- Interior floor tiles: {brick_tiles}")
    
    # Verify building integrity
    print(f"\nBuilding Integrity Check:")
    
    # Each building should have doors
    expected_doors = total_buildings * 2  # Double doors
    if door_tiles >= expected_doors * 0.8:  # Allow some margin
        print(f"✅ Door count reasonable: {door_tiles} (expected ~{expected_doors})")
    else:
        print(f"❌ Door count low: {door_tiles} (expected ~{expected_doors})")
    
    # Should have reasonable window distribution
    if window_tiles > 0:
        print(f"✅ Windows present: {window_tiles} tiles")
    else:
        print(f"❌ No windows found")
    
    # Should have interior floors
    if brick_tiles > 0:
        print(f"✅ Interior floors present: {brick_tiles} tiles")
    else:
        print(f"❌ No interior floors found")
    
    print(f"\n" + "=" * 50)
    print("Enhanced Building Generation Test Complete!")
    
    return {
        'settlements': len(settlements),
        'buildings': total_buildings,
        'windows': window_tiles,
        'doors': door_tiles,
        'interiors': brick_tiles
    }

def test_multiple_seeds():
    """Test building generation with multiple seeds"""
    print("\nTesting Multiple Seeds")
    print("=" * 30)
    
    test_seeds = [11111, 22222, 33333, 44444, 55555]
    results = []
    
    for seed in test_seeds:
        print(f"\nTesting seed {seed}...")
        generator = ProceduralGenerator(100, 100, seed=seed)
        tiles = generator.generate_tiles()
        settlements = generator.place_settlements(tiles)
        
        # Count building features
        window_count = 0
        door_count = 0
        brick_count = 0
        
        for y in range(100):
            for x in range(100):
                tile_type = tiles[y][x]
                if tile_type in [14, 15]:  # Window tiles
                    window_count += 1
                elif tile_type == 5:  # Door tiles
                    door_count += 1
                elif tile_type == 13:  # Brick tiles
                    brick_count += 1
        
        result = {
            'seed': seed,
            'settlements': len(settlements),
            'windows': window_count,
            'doors': door_count,
            'interiors': brick_count
        }
        results.append(result)
        
        print(f"  Settlements: {len(settlements)}, Windows: {window_count}, " +
              f"Doors: {door_count}, Interiors: {brick_count}")
    
    # Summary
    print(f"\nMulti-Seed Summary:")
    avg_settlements = sum(r['settlements'] for r in results) / len(results)
    avg_windows = sum(r['windows'] for r in results) / len(results)
    avg_doors = sum(r['doors'] for r in results) / len(results)
    avg_interiors = sum(r['interiors'] for r in results) / len(results)
    
    print(f"- Average settlements: {avg_settlements:.1f}")
    print(f"- Average windows: {avg_windows:.1f}")
    print(f"- Average doors: {avg_doors:.1f}")
    print(f"- Average interiors: {avg_interiors:.1f}")
    
    return results

if __name__ == "__main__":
    # Run basic test
    basic_results = test_enhanced_building_generation()
    
    # Run multi-seed test
    multi_results = test_multiple_seeds()
    
    print(f"\n" + "=" * 60)
    print("BUILDING GENERATION TESTING COMPLETE")
    print("=" * 60)
    
    # Final validation
    success = True
    
    if basic_results['settlements'] < 1:
        print("❌ No settlements generated")
        success = False
    else:
        print(f"✅ Settlements generated: {basic_results['settlements']}")
    
    if basic_results['buildings'] < 1:
        print("❌ No buildings generated")
        success = False
    else:
        print(f"✅ Buildings generated: {basic_results['buildings']}")
    
    if basic_results['windows'] < 1:
        print("❌ No windows generated")
        success = False
    else:
        print(f"✅ Windows generated: {basic_results['windows']}")
    
    if basic_results['doors'] < 1:
        print("❌ No doors generated")
        success = False
    else:
        print(f"✅ Doors generated: {basic_results['doors']}")
    
    if basic_results['interiors'] < 1:
        print("❌ No interior floors generated")
        success = False
    else:
        print(f"✅ Interior floors generated: {basic_results['interiors']}")
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED! Enhanced building generation is working correctly.")
    else:
        print(f"\n❌ Some tests failed. Check the building generation system.")