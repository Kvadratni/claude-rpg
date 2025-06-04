"""
Test script for enhanced settlement generation
Demonstrates the new varied building shapes, road networks, and biome-specific architecture
"""

import sys
import os
import random

# Add the project root to the path
sys.path.append('/Users/mnovich/Development/claude-rpg')

from src.world.enhanced_settlement_generator import EnhancedSettlementGenerator
from src.world.settlement_integration import SettlementIntegrator


def create_test_world(width=100, height=100):
    """Create a test world with different biomes"""
    # Initialize tiles with grass
    tiles = [[0 for _ in range(width)] for _ in range(height)]
    
    # Create biome map with different regions
    biome_map = [['PLAINS' for _ in range(width)] for _ in range(height)]
    
    # Add different biome regions
    # Desert region (top-left)
    for y in range(0, height//3):
        for x in range(0, width//3):
            biome_map[y][x] = 'DESERT'
            tiles[y][x] = 16  # TILE_SAND
    
    # Forest region (top-right)
    for y in range(0, height//3):
        for x in range(2*width//3, width):
            biome_map[y][x] = 'FOREST'
            tiles[y][x] = 18  # TILE_FOREST_FLOOR
    
    # Snow region (bottom-left)
    for y in range(2*height//3, height):
        for x in range(0, width//3):
            biome_map[y][x] = 'SNOW'
            tiles[y][x] = 17  # TILE_SNOW
    
    # Swamp region (bottom-right)
    for y in range(2*height//3, height):
        for x in range(2*width//3, width):
            biome_map[y][x] = 'SWAMP'
            tiles[y][x] = 19  # TILE_SWAMP
    
    # Add some water features
    for _ in range(5):
        water_x = random.randint(10, width-10)
        water_y = random.randint(10, height-10)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if 0 <= water_x + dx < width and 0 <= water_y + dy < height:
                    if dx*dx + dy*dy <= 4:  # Circular water feature
                        tiles[water_y + dy][water_x + dx] = 3  # TILE_WATER
    
    return tiles, biome_map


def test_enhanced_settlement_generation():
    """Test the enhanced settlement generation system"""
    print("=== Testing Enhanced Settlement Generation ===")
    
    # Create test world
    width, height = 100, 100
    tiles, biome_map = create_test_world(width, height)
    
    # Initialize integrator
    integrator = SettlementIntegrator(width, height, seed=42)
    
    # Generate settlements
    print("Generating enhanced settlements...")
    settlements = integrator.generate_settlements_for_level(tiles, biome_map)
    
    # Report results
    print(f"\n=== Settlement Generation Results ===")
    print(f"Total settlements generated: {len(settlements)}")
    
    for i, settlement in enumerate(settlements):
        print(f"\nSettlement {i+1}: {settlement['name']}")
        print(f"  Location: ({settlement['x']}, {settlement['y']})")
        print(f"  Size: {settlement['size']}")
        print(f"  Biome: {settlement['biome']}")
        print(f"  Architectural Style: {settlement.get('architectural_style', 'Unknown')}")
        print(f"  Pattern Used: {settlement.get('pattern_used', 'Unknown')}")
        print(f"  Buildings: {len(settlement.get('buildings', []))}")
        print(f"  NPCs: {settlement.get('total_npcs', 0)}")
        print(f"  Shops: {settlement.get('shops', 0)}")
        
        # List building details
        for j, building in enumerate(settlement.get('buildings', [])):
            print(f"    Building {j+1}: {building.get('type', 'Unknown')} "
                  f"({building.get('width', 0)}x{building.get('height', 0)}) "
                  f"Shape: {building.get('shape', 'rectangle')}")
        
        # List NPC details
        for j, npc in enumerate(settlement.get('npcs', [])):
            print(f"    NPC {j+1}: {npc.get('name', 'Unknown')} "
                  f"at {npc.get('building', 'Unknown Building')} "
                  f"(Shop: {npc.get('has_shop', False)})")


def test_individual_settlement_types():
    """Test individual settlement types with different biomes"""
    print("\n=== Testing Individual Settlement Types ===")
    
    width, height = 50, 50
    generator = EnhancedSettlementGenerator(width, height, seed=123)
    
    # Test different settlement types in appropriate biomes
    test_cases = [
        ('VILLAGE', 'PLAINS'),
        ('TOWN', 'PLAINS'),
        ('DESERT_OUTPOST', 'DESERT'),
        ('SNOW_SETTLEMENT', 'SNOW'),
        ('SWAMP_VILLAGE', 'SWAMP'),
        ('FOREST_CAMP', 'FOREST'),
        ('MINING_CAMP', 'MOUNTAIN'),
        ('FISHING_VILLAGE', 'COAST')
    ]
    
    for settlement_type, biome in test_cases:
        print(f"\nTesting {settlement_type} in {biome} biome...")
        
        # Create simple test tiles
        tiles = [[1 for _ in range(width)] for _ in range(height)]  # All dirt
        
        # Generate settlement
        try:
            settlement = generator.generate_enhanced_settlement(
                tiles, 10, 10, settlement_type, biome
            )
            
            print(f"  ✓ Successfully generated {settlement_type}")
            print(f"    Size: {settlement['size']}")
            print(f"    Buildings: {len(settlement['buildings'])}")
            print(f"    Architectural Style: {settlement['architectural_style']}")
            
            # Show building variety
            shapes = {}
            for building in settlement['buildings']:
                shape = building.get('shape', 'rectangle')
                shapes[shape] = shapes.get(shape, 0) + 1
            
            print(f"    Building shapes: {dict(shapes)}")
            
        except Exception as e:
            print(f"  ✗ Failed to generate {settlement_type}: {e}")


def visualize_settlement(tiles, settlement, filename):
    """Create a simple ASCII visualization of a settlement"""
    print(f"\nCreating visualization: {filename}")
    
    # Define tile characters
    tile_chars = {
        0: '.',   # TILE_GRASS
        1: ',',   # TILE_DIRT
        2: '#',   # TILE_STONE
        3: '~',   # TILE_WATER
        4: '█',   # TILE_WALL
        5: '▒',   # TILE_DOOR
        6: '┌',   # TILE_WALL_CORNER_TL
        7: '┐',   # TILE_WALL_CORNER_TR
        8: '└',   # TILE_WALL_CORNER_BL
        9: '┘',   # TILE_WALL_CORNER_BR
        10: '─',  # TILE_WALL_HORIZONTAL
        11: '│',  # TILE_WALL_VERTICAL
        13: '▓',  # TILE_BRICK
        14: '═',  # TILE_WALL_WINDOW_HORIZONTAL
        15: '║',  # TILE_WALL_WINDOW_VERTICAL
        16: '∙',  # TILE_SAND
        17: '*',  # TILE_SNOW
        18: '♦',  # TILE_FOREST_FLOOR
        19: '≈',  # TILE_SWAMP
    }
    
    # Extract settlement area
    start_x, start_y = settlement['x'], settlement['y']
    width, height = settlement['size']
    
    with open(filename, 'w') as f:
        f.write(f"Settlement: {settlement['name']} ({settlement['biome']} biome)\n")
        f.write(f"Architectural Style: {settlement.get('architectural_style', 'Unknown')}\n")
        f.write(f"Location: ({start_x}, {start_y}), Size: {width}x{height}\n")
        f.write("=" * (width + 2) + "\n")
        
        for y in range(start_y, start_y + height):
            f.write("|")
            for x in range(start_x, start_x + width):
                if 0 <= x < len(tiles[0]) and 0 <= y < len(tiles):
                    tile_type = tiles[y][x]
                    char = tile_chars.get(tile_type, '?')
                    f.write(char)
                else:
                    f.write(' ')
            f.write("|\n")
        
        f.write("=" * (width + 2) + "\n")
        
        # Add legend
        f.write("\nLegend:\n")
        f.write("█ ┌┐└┘─│ = Walls and corners\n")
        f.write("▒ = Doors\n")
        f.write("▓ = Interior (brick floors)\n")
        f.write("# = Stone roads/paths\n")
        f.write("~ = Water\n")
        f.write(", = Dirt\n")
        f.write(". = Grass\n")
        f.write("∙ = Sand (desert)\n")
        f.write("* = Snow\n")
        f.write("♦ = Forest floor\n")
        f.write("≈ = Swamp\n")


def main():
    """Main test function"""
    print("Enhanced Settlement Generation Test Suite")
    print("=" * 50)
    
    # Test 1: Full integration test
    test_enhanced_settlement_generation()
    
    # Test 2: Individual settlement types
    test_individual_settlement_types()
    
    # Test 3: Create visualizations
    print("\n=== Creating Settlement Visualizations ===")
    
    width, height = 40, 40
    generator = EnhancedSettlementGenerator(width, height, seed=456)
    
    # Create a few example settlements for visualization
    examples = [
        ('VILLAGE', 'PLAINS'),
        ('DESERT_OUTPOST', 'DESERT'),
        ('SNOW_SETTLEMENT', 'SNOW')
    ]
    
    for settlement_type, biome in examples:
        tiles = [[1 for _ in range(width)] for _ in range(height)]  # All dirt
        
        try:
            settlement = generator.generate_enhanced_settlement(
                tiles, 5, 5, settlement_type, biome
            )
            
            filename = f"/Users/mnovich/Development/claude-rpg/settlement_{settlement_type.lower()}_{biome.lower()}.txt"
            visualize_settlement(tiles, settlement, filename)
            
        except Exception as e:
            print(f"Failed to create visualization for {settlement_type}: {e}")
    
    print("\n=== Test Suite Complete ===")
    print("Check the generated .txt files for ASCII visualizations of the settlements.")


if __name__ == "__main__":
    main()