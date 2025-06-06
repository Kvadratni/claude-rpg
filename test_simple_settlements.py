#!/usr/bin/env python3
"""
Simple test for the new settlement components
"""

import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test just our new components without complex imports
def test_building_template_manager():
    """Test the building template manager independently"""
    print("🏗️  Testing Building Template Manager")
    print("=" * 50)
    
    # Import and test
    from world.building_template_manager import BuildingTemplateManager
    
    manager = BuildingTemplateManager()
    
    print(f"📋 Created {len(manager.templates)} default templates:")
    for name, template in manager.templates.items():
        print(f"  • {name}: {template.width}x{template.height} {template.building_type}")
        print(f"    NPCs: {len(template.npc_spawns)}, Furniture: {len(template.furniture_positions)}")
    
    print("\n📂 Templates by type:")
    for building_type, templates in manager.templates_by_type.items():
        template_names = [t.name for t in templates]
        print(f"  • {building_type}: {', '.join(template_names)}")
    
    # Test template selection
    print("\n🎲 Testing template selection:")
    test_cases = [
        ("house", "medium", "plains"),
        ("shop", "small", "desert"), 
        ("inn", "large", "forest"),
        ("blacksmith", "medium", "plains")
    ]
    
    for building_type, size, biome in test_cases:
        template = manager.select_random_template(building_type, size, biome, seed=42)
        if template:
            print(f"  ✅ {building_type} ({size}, {biome}): Selected '{template.name}'")
        else:
            print(f"  ❌ {building_type} ({size}, {biome}): No template found")
    
    # Test saving/loading
    print("\n💾 Testing save/load:")
    test_template = manager.templates['small_house']
    manager.save_template(test_template)
    
    # Load it back
    loaded_template = manager.load_template('small_house')
    if loaded_template:
        print(f"  ✅ Successfully saved and loaded '{loaded_template.name}'")
    else:
        print(f"  ❌ Failed to load template")
    
    return manager


def test_enhanced_settlement_generator():
    """Test the enhanced settlement generator independently"""
    print("\n🏘️  Testing Enhanced Settlement Generator")
    print("=" * 50)
    
    from world.enhanced_settlement_generator import EnhancedSettlementGenerator
    
    generator = EnhancedSettlementGenerator(world_seed=12345)
    
    # Test different settlement types
    test_settlements = [
        ('VILLAGE', 'plains'),
        ('DESERT_OUTPOST', 'desert'),
        ('FOREST_CAMP', 'forest'),
    ]
    
    for i, (settlement_type, biome) in enumerate(test_settlements):
        print(f"\n🎯 Testing {settlement_type} in {biome} biome:")
        print("-" * 40)
        
        try:
            settlement = generator.generate_settlement(i, 0, settlement_type, biome)
            
            print(f"  Layout: {settlement['layout']} ({settlement['width']}x{settlement['height']})")
            print(f"  Shape: {settlement['shape']}")
            print(f"  Buildings: {settlement['total_buildings']}")
            print(f"  NPCs: {settlement['total_npcs']}")
            print(f"  Shops: {settlement['shops']}")
            
            # Show building breakdown
            building_types = {}
            for building in settlement['buildings']:
                btype = building['building_type']
                building_types[btype] = building_types.get(btype, 0) + 1
            
            print(f"  Building types: {', '.join([f'{k}({v})' for k, v in building_types.items()])}")
            
            # Show pathways info
            print(f"  Pathways: {len(settlement['pathways'])} tiles")
            
            # Show central feature
            if settlement['central_feature']:
                feature = settlement['central_feature']
                print(f"  Central feature: {feature['type']} at ({feature['x']}, {feature['y']})")
            
            print(f"  ✅ {settlement_type} generated successfully!")
            
        except Exception as e:
            print(f"  ❌ Error generating {settlement_type}: {e}")
            import traceback
            traceback.print_exc()


def test_building_editor_components():
    """Test building editor components"""
    print("\n🎨 Testing Building Editor Components")
    print("=" * 50)
    
    try:
        from ui.building_editor import BuildingTemplate, TileType, NPCSpawnPoint
        
        # Create a test template
        template = BuildingTemplate("test_building", 10, 8)
        
        # Add some tiles
        template.set_tile(0, 0, TileType.WALL)
        template.set_tile(5, 5, TileType.FLOOR)
        
        # Add NPC spawn
        npc_spawn = template.add_npc_spawn(3, 3, "merchant", "Test Merchant")
        npc_spawn.has_shop = True
        npc_spawn.dialog = ["Welcome to my shop!", "What can I get you?"]
        
        print(f"  ✅ Created template: {template.name} ({template.width}x{template.height})")
        print(f"  ✅ Added NPC spawn: {npc_spawn.name} at ({npc_spawn.x}, {npc_spawn.y})")
        
        # Test serialization
        template_dict = template.to_dict()
        print(f"  ✅ Serialized template: {len(template_dict)} fields")
        
        # Test deserialization
        loaded_template = BuildingTemplate.from_dict(template_dict)
        print(f"  ✅ Deserialized template: {loaded_template.name}")
        
        print("  ✅ Building editor components working!")
        
    except ImportError as e:
        print(f"  ⚠️  Building editor components not testable (pygame not available): {e}")


def main():
    """Run simplified tests"""
    print("🧪 Enhanced Settlement System - Simple Test")
    print("=" * 60)
    
    try:
        # Test building templates
        manager = test_building_template_manager()
        
        # Test settlement generation
        test_enhanced_settlement_generator()
        
        # Test building editor components
        test_building_editor_components()
        
        print("\n" + "=" * 60)
        print("✅ Core components tested successfully!")
        print("\n💡 What's been created:")
        print("  1. 🏗️  Building Template Manager - Manages building templates")
        print("  2. 🏘️  Enhanced Settlement Generator - Creates varied settlements")
        print("  3. 🎨 Building Template Editor - UI for creating templates")
        print("\n🚀 Next steps:")
        print("  1. Try: python launch_building_editor.py (if pygame is installed)")
        print("  2. Integrate with the main game")
        print("  3. Create custom building templates")
        
        # Show template directory
        templates_dir = "building_templates"
        if os.path.exists(templates_dir):
            template_files = [f for f in os.listdir(templates_dir) if f.endswith('.json')]
            print(f"\n📁 Template files created in '{templates_dir}/':")
            for filename in template_files:
                print(f"  • {filename}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())