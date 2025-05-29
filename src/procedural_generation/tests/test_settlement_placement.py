#!/usr/bin/env python3
"""
Test script for procedural settlement placement
Tests settlement placement with collision detection
"""

import sys
import os
import random
import math

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_settlement_placement():
    """Test settlement placement logic directly"""
    print("Testing Settlement Placement Logic")
    print("=" * 40)
    
    # Test the core logic without full class instantiation
    from procedural_generator import ProceduralGenerator
    
    # Temporarily patch the entity imports
    import procedural_generator
    
    class MockEntity:
        def __init__(self, *args, **kwargs):
            pass
    
    procedural_generator.Entity = MockEntity
    procedural_generator.NPC = MockEntity
    procedural_generator.Enemy = MockEntity
    procedural_generator.Item = MockEntity
    procedural_generator.Chest = MockEntity
    
    # Now test the generator
    width, height = 100, 100
    seed = 12345
    
    print(f"Creating {width}x{height} world with seed {seed}")
    
    # Create generator
    generator = ProceduralGenerator(width, height, seed)
    
    # Test biome distribution first
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
    
    # Generate base tiles
    tiles = generator.generate_tiles()
    
    # Test settlement templates
    print(f"\nTesting settlement templates...")
    for template_name, template_config in generator.SETTLEMENT_TEMPLATES.items():
        print(f"  {template_name}:")
        print(f"    Size: {template_config['size']}")
        print(f"    Biomes: {template_config['biomes']}")
        print(f"    Buildings: {len(template_config['buildings'])}")
        print(f"    Safe radius: {template_config['safe_radius']}")
    
    # Test collision detection methods
    print(f"\nTesting collision detection methods...")
    
    # Test rectangle overlap
    rect1 = (10, 10, 20, 20)
    rect2 = (15, 15, 20, 20)  # Overlapping
    rect3 = (40, 40, 20, 20)  # Not overlapping
    
    overlap_test1 = generator.rectangles_overlap(rect1, rect2)
    overlap_test2 = generator.rectangles_overlap(rect1, rect3)
    
    print(f"  Rectangle overlap test 1 (should overlap): {'✅ YES' if overlap_test1 else '❌ NO'}")
    print(f"  Rectangle overlap test 2 (should not overlap): {'✅ NO' if not overlap_test2 else '❌ YES'}")
    
    # Test area collision (with empty occupied_areas)
    collision_test1 = generator.check_area_collision(10, 10, 20, 20)
    print(f"  Area collision test (empty areas): {'✅ NO' if not collision_test1 else '❌ YES'}")
    
    # Add an occupied area and test again
    generator.occupied_areas.append((15, 15, 10, 10))
    collision_test2 = generator.check_area_collision(10, 10, 20, 20)
    print(f"  Area collision test (with occupied area): {'✅ YES' if collision_test2 else '❌ NO'}")
    
    # Test settlement placement
    print(f"\nTesting settlement placement...")
    settlements = generator.place_settlements(tiles)
    
    print(f"Successfully placed {len(settlements)} settlements")
    
    # Analyze settlements
    for i, settlement in enumerate(settlements):
        print(f"\nSettlement {i+1}: {settlement['name']}")
        print(f"  Location: ({settlement['x']}, {settlement['y']})")
        print(f"  Size: {settlement['size']}")
        print(f"  Biome: {settlement['biome']}")
        print(f"  Center: ({settlement['center_x']}, {settlement['center_y']})")
        print(f"  Buildings: {len(settlement['buildings'])}")
    
    # Test safe zone functionality
    print(f"\nTesting safe zones...")
    print(f"Safe zones created: {len(generator.settlement_safe_zones)}")
    
    safe_zone_tests = 0
    safe_zone_hits = 0
    
    for _ in range(1000):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        safe_zone_tests += 1
        
        if generator.is_in_safe_zone(x, y):
            safe_zone_hits += 1
    
    safe_zone_coverage = (safe_zone_hits / safe_zone_tests) * 100
    print(f"Safe zone coverage: {safe_zone_coverage:.1f}% of random points")
    
    # Verify no overlapping settlements
    print(f"\nChecking for settlement overlaps...")
    overlaps = 0
    for i, settlement1 in enumerate(settlements):
        for j, settlement2 in enumerate(settlements):
            if i >= j:
                continue
            
            # Check if settlements overlap
            rect1 = (settlement1['x'], settlement1['y'], settlement1['size'][0], settlement1['size'][1])
            rect2 = (settlement2['x'], settlement2['y'], settlement2['size'][0], settlement2['size'][1])
            
            if generator.rectangles_overlap(rect1, rect2):
                overlaps += 1
                print(f"  ❌ Overlap detected between {settlement1['name']} and {settlement2['name']}")
    
    if overlaps == 0:
        print("  ✅ No settlement overlaps detected")
    
    # Test biome appropriateness
    print(f"\nChecking biome appropriateness...")
    biome_errors = 0
    for settlement in settlements:
        template_name = settlement['name']
        settlement_biome = settlement['biome']
        
        # Get allowed biomes for this template
        template_config = generator.SETTLEMENT_TEMPLATES.get(template_name, {})
        allowed_biomes = template_config.get('biomes', [])
        
        if settlement_biome not in allowed_biomes:
            biome_errors += 1
            print(f"  ❌ {template_name} placed in {settlement_biome}, but only allowed in {allowed_biomes}")
        else:
            print(f"  ✅ {template_name} correctly placed in {settlement_biome}")
    
    if biome_errors == 0:
        print("  ✅ All settlements placed in appropriate biomes")
    
    print("\n" + "=" * 40)
    print("Settlement placement test completed!")
    
    return generator, settlements

if __name__ == "__main__":
    try:
        # Test settlement placement
        generator, settlements = test_settlement_placement()
        
        print("\n🎉 Settlement placement tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()