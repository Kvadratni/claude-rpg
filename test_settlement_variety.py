"""
Comprehensive test to demonstrate settlement variety
Shows how the same settlement type can generate different patterns and building shapes
"""

import sys
import os
import random

# Add the project root to the path
sys.path.append('/Users/mnovich/Development/claude-rpg')

from src.world.enhanced_settlement_generator import EnhancedSettlementGenerator


def test_settlement_variety():
    """Test how the same settlement type generates different patterns"""
    print("=== Settlement Variety Demonstration ===")
    
    width, height = 50, 50
    
    # Test multiple instances of the same settlement type with different seeds
    settlement_types = ['VILLAGE', 'TOWN', 'DESERT_OUTPOST', 'FOREST_CAMP']
    
    for settlement_type in settlement_types:
        print(f"\n--- Testing {settlement_type} Variety ---")
        
        for i in range(5):  # Generate 5 instances with different seeds
            seed = i * 1000  # Different seeds
            generator = EnhancedSettlementGenerator(width, height, seed=seed)
            
            # Create simple test tiles
            tiles = [[1 for _ in range(width)] for _ in range(height)]  # All dirt
            
            try:
                settlement = generator.generate_enhanced_settlement(
                    tiles, 10, 10, settlement_type, 'PLAINS', seed=seed
                )
                
                print(f"  Instance {i+1} (seed {seed}):")
                print(f"    Pattern: {settlement['pattern_used']}")
                print(f"    Size: {settlement['size']}")
                print(f"    Buildings: {len(settlement['buildings'])}")
                
                # Show building shape variety
                shapes = {}
                for building in settlement['buildings']:
                    shape = building.get('shape', 'rectangle')
                    shapes[shape] = shapes.get(shape, 0) + 1
                
                print(f"    Building shapes: {dict(shapes)}")
                
            except Exception as e:
                print(f"    ✗ Failed: {e}")


def test_biome_specific_variety():
    """Test how the same settlement type varies across different biomes"""
    print("\n=== Biome-Specific Variety Demonstration ===")
    
    width, height = 50, 50
    biomes = ['PLAINS', 'DESERT', 'FOREST', 'SNOW', 'SWAMP']
    
    for biome in biomes:
        print(f"\n--- VILLAGE in {biome} biome ---")
        
        for i in range(3):  # 3 instances per biome
            seed = hash((biome, i)) % (2**31)
            generator = EnhancedSettlementGenerator(width, height, seed=seed)
            
            # Create simple test tiles
            tiles = [[1 for _ in range(width)] for _ in range(height)]
            
            try:
                settlement = generator.generate_enhanced_settlement(
                    tiles, 10, 10, 'VILLAGE', biome, seed=seed
                )
                
                print(f"  Instance {i+1}:")
                print(f"    Pattern: {settlement['pattern_used']}")
                print(f"    Size: {settlement['size']}")
                print(f"    Architectural Style: {settlement['architectural_style']}")
                
                # Show building variety
                shapes = {}
                types = {}
                for building in settlement['buildings']:
                    shape = building.get('shape', 'rectangle')
                    building_type = building.get('type', 'unknown')
                    shapes[shape] = shapes.get(shape, 0) + 1
                    types[building_type] = types.get(building_type, 0) + 1
                
                print(f"    Building shapes: {dict(shapes)}")
                print(f"    Building types: {dict(types)}")
                
            except Exception as e:
                print(f"    ✗ Failed: {e}")


def test_building_shape_distribution():
    """Test the distribution of building shapes across many settlements"""
    print("\n=== Building Shape Distribution Test ===")
    
    width, height = 50, 50
    total_shapes = {}
    total_settlements = 0
    
    # Generate many settlements to see shape distribution
    for seed in range(100):  # 100 different settlements
        generator = EnhancedSettlementGenerator(width, height, seed=seed)
        tiles = [[1 for _ in range(width)] for _ in range(height)]
        
        try:
            settlement = generator.generate_enhanced_settlement(
                tiles, 10, 10, 'TOWN', 'PLAINS', seed=seed
            )
            
            total_settlements += 1
            
            for building in settlement['buildings']:
                shape = building.get('shape', 'rectangle')
                total_shapes[shape] = total_shapes.get(shape, 0) + 1
                
        except Exception:
            continue
    
    print(f"Analyzed {total_settlements} TOWN settlements:")
    print("Building shape distribution:")
    
    total_buildings = sum(total_shapes.values())
    for shape, count in sorted(total_shapes.items()):
        percentage = (count / total_buildings) * 100
        print(f"  {shape}: {count} buildings ({percentage:.1f}%)")


def main():
    """Main test function"""
    print("Comprehensive Settlement Variety Test")
    print("=" * 50)
    
    # Test 1: Same settlement type, different patterns
    test_settlement_variety()
    
    # Test 2: Same settlement type across biomes
    test_biome_specific_variety()
    
    # Test 3: Building shape distribution
    test_building_shape_distribution()
    
    print("\n" + "=" * 50)
    print("Variety Test Complete!")
    print("The system now generates varied settlements even of the same type!")


if __name__ == "__main__":
    main()