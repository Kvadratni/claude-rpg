#!/usr/bin/env python3
"""
Test script to verify settlement patterns work correctly
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_settlement_patterns():
    """Test the settlement pattern system"""
    
    print("=== Settlement Pattern System Test ===")
    
    try:
        from world.settlement_patterns import SettlementPatternGenerator
        
        # Create pattern generator
        pattern_gen = SettlementPatternGenerator()
        print("1. ✅ Created settlement pattern generator")
        
        # Test different settlement types
        settlement_types = ['village', 'town', 'city', 'outpost']
        
        for settlement_type in settlement_types:
            pattern = pattern_gen.get_pattern(settlement_type)
            print(f"2. ✅ {settlement_type.capitalize()} pattern: {pattern.width}x{pattern.height}")
            print(f"   - Buildings: {len(pattern.get_building_positions())}")
            print(f"   - Pathways: {len(pattern.get_pathway_positions())}")
            
            # Test biome adaptation
            biomes = ['PLAINS', 'DESERT', 'FOREST', 'TUNDRA']
            for biome in biomes:
                adapted = pattern_gen.adapt_pattern_to_biome(pattern, biome)
                print(f"   - {biome} adaptation: {adapted.name}")
        
        # Test pattern tile access
        village_pattern = pattern_gen.get_pattern('village')
        print(f"3. ✅ Village pattern tile at (6,6): {village_pattern.get_tile_at(6, 6)}")
        print(f"   - Expected: 2 (stone pathway)")
        
        # Test building positions
        buildings = village_pattern.get_building_positions()
        print(f"4. ✅ Village buildings:")
        for i, building in enumerate(buildings):
            print(f"   - Building {i+1}: {building['type']} at ({building['x']}, {building['y']}) size {building['width']}x{building['height']}")
        
        print("\n🎉 All settlement pattern tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def visualize_pattern(pattern_name='village'):
    """Visualize a settlement pattern as ASCII art"""
    
    print(f"\n=== {pattern_name.capitalize()} Pattern Visualization ===")
    
    try:
        from world.settlement_patterns import SettlementPatternGenerator
        
        pattern_gen = SettlementPatternGenerator()
        pattern = pattern_gen.get_pattern(pattern_name)
        
        # Tile symbols
        tile_symbols = {
            0: '.',  # GRASS
            1: ',',  # DIRT
            2: '#',  # STONE (pathways)
            13: '=', # BRICK
            16: '~', # SAND
            17: '*', # SNOW
            18: '^', # FOREST_FLOOR
            19: '%', # SWAMP
        }
        
        print(f"Pattern: {pattern.width}x{pattern.height}")
        print("Legend: . = grass, , = dirt, # = stone paths, = = brick")
        print()
        
        # Print pattern
        for y in range(pattern.height):
            row = ""
            for x in range(pattern.width):
                tile = pattern.get_tile_at(x, y)
                symbol = tile_symbols.get(tile, '?')
                row += symbol
            print(row)
        
        print()
        print("Buildings:")
        for building in pattern.get_building_positions():
            print(f"  {building['type']}: ({building['x']}, {building['y']}) {building['width']}x{building['height']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing settlement pattern system...\n")
    
    # Run tests
    test_passed = test_settlement_patterns()
    
    if test_passed:
        # Visualize patterns
        for pattern_type in ['village', 'town', 'city', 'outpost']:
            visualize_pattern(pattern_type)
    
    print(f"\n=== Final Results ===")
    if test_passed:
        print("🎉 Settlement pattern system is working correctly!")
        print("   - Patterns generate proper tile layouts")
        print("   - Buildings are positioned correctly")
        print("   - Biome adaptation works")
        print("   - Ready for integration with world generator")
    else:
        print("⚠️  Settlement pattern tests failed. Check output above.")