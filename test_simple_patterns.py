#!/usr/bin/env python3
"""
Simple test script for settlement patterns (standalone)
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import just the pattern generator directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'world'))

def test_patterns():
    """Test settlement patterns directly"""
    
    print("=== Settlement Pattern Test ===")
    
    try:
        # Import the pattern generator directly
        from settlement_patterns import SettlementPatternGenerator
        
        # Create generator
        gen = SettlementPatternGenerator()
        print("✅ Created pattern generator")
        
        # Test village pattern
        village = gen.get_pattern('village')
        print(f"✅ Village pattern: {village.width}x{village.height}")
        print(f"   Buildings: {len(village.get_building_positions())}")
        
        # Visualize village pattern
        print("\n🏘️ Village Pattern (12x12):")
        print("Legend: . = grass, , = dirt, # = stone paths")
        
        tile_symbols = {0: '.', 1: ',', 2: '#', 13: '='}
        
        for y in range(village.height):
            row = ""
            for x in range(village.width):
                tile = village.get_tile_at(x, y)
                symbol = tile_symbols.get(tile, '?')
                row += symbol + " "
            print(row)
        
        print("\nBuildings:")
        for building in village.get_building_positions():
            print(f"  {building['type']}: ({building['x']}, {building['y']}) {building['width']}x{building['height']}")
        
        # Test biome adaptation
        desert_village = gen.adapt_pattern_to_biome(village, 'DESERT')
        print(f"\n✅ Desert adaptation: {desert_village.name}")
        
        print("\n🎉 Pattern system working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_patterns()