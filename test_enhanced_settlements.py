#!/usr/bin/env python3
"""
Test the enhanced settlement generation system
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from world.building_template_manager import BuildingTemplateManager
from world.enhanced_settlement_generator import EnhancedSettlementGenerator


def test_building_templates():
    """Test the building template manager"""
    print("🏗️  Testing Building Template Manager")
    print("=" * 50)
    
    manager = BuildingTemplateManager()
    
    print(f"📋 Loaded {len(manager.templates)} templates:")
    for name, template in manager.templates.items():
        print(f"  • {name}: {template.width}x{template.height} {template.building_type}")
        print(f"    NPCs: {len(template.npc_spawns)}, Description: {template.description}")
    
    print("\n📂 Templates by type:")
    for building_type, templates in manager.templates_by_type.items():
        template_names = [t.name for t in templates]
        print(f"  • {building_type}: {', '.join(template_names)}")
    
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
            print(f"  • {building_type} ({size}, {biome}): Selected '{template.name}'")
        else:
            print(f"  • {building_type} ({size}, {biome}): No template found")
    
    return manager


def test_settlement_generation():
    """Test the enhanced settlement generator"""
    print("\n🏘️  Testing Enhanced Settlement Generator")
    print("=" * 50)
    
    generator = EnhancedSettlementGenerator(world_seed=12345)
    
    # Test different settlement types
    test_settlements = [
        ('VILLAGE', 'plains'),
        ('TOWN', 'plains'), 
        ('DESERT_OUTPOST', 'desert'),
        ('FOREST_CAMP', 'forest'),
        ('FISHING_VILLAGE', 'coast'),
        ('MINING_CAMP', 'mountain'),
        ('SWAMP_VILLAGE', 'swamp')
    ]
    
    for i, (settlement_type, biome) in enumerate(test_settlements):
        print(f"\n🎯 Testing {settlement_type} in {biome} biome:")
        print("-" * 40)
        
        try:
            settlement = generator.generate_settlement(i, 0, settlement_type, biome)
            
            print(f"  Layout: {settlement['layout']} ({settlement['width']}x{settlement['height']})")
            print(f"  Shape: {settlement['shape']}")
            print(f"  Position: ({settlement['world_x']}, {settlement['world_y']})")
            print(f"  Buildings: {settlement['total_buildings']}")
            print(f"  NPCs: {settlement['total_npcs']}")
            print(f"  Shops: {settlement['shops']}")
            
            # Show building breakdown
            building_types = {}
            for building in settlement['buildings']:
                btype = building['building_type']
                building_types[btype] = building_types.get(btype, 0) + 1
            
            print(f"  Building types: {', '.join([f'{k}({v})' for k, v in building_types.items()])}")
            
            # Show some NPC details
            if settlement['npcs']:
                print(f"  Sample NPCs:")
                for npc in settlement['npcs'][:3]:  # Show first 3 NPCs
                    shop_indicator = " 🛒" if npc.get('has_shop') else ""
                    print(f"    • {npc['name']} ({npc['npc_type']}) in {npc['building']}{shop_indicator}")
            
            print(f"  ✅ {settlement_type} generated successfully!")
            
        except Exception as e:
            print(f"  ❌ Error generating {settlement_type}: {e}")
            import traceback
            traceback.print_exc()


def test_integration():
    """Test integration between components"""
    print("\n🔗 Testing System Integration")
    print("=" * 50)
    
    # Test that templates are properly used in settlements
    manager = BuildingTemplateManager()
    generator = EnhancedSettlementGenerator(world_seed=54321)
    
    # Generate a village and check that buildings use templates
    settlement = generator.generate_settlement(0, 0, 'VILLAGE', 'plains')
    
    print(f"🏘️  Generated village with {len(settlement['buildings'])} buildings:")
    
    template_usage = {}
    for building in settlement['buildings']:
        template_name = building['template_name']
        template_usage[template_name] = template_usage.get(template_name, 0) + 1
        
        # Verify template exists in manager
        if template_name in manager.templates:
            template = manager.templates[template_name]
            print(f"  ✅ {template_name}: {template.building_type} ({template.width}x{template.height})")
        else:
            print(f"  ❌ {template_name}: Template not found in manager!")
    
    print(f"\n📊 Template usage summary:")
    for template_name, count in template_usage.items():
        print(f"  • {template_name}: used {count} time(s)")
    
    # Check NPC assignment
    npcs_with_templates = [npc for npc in settlement['npcs'] if npc.get('template_spawn')]
    print(f"\n👥 NPCs from templates: {len(npcs_with_templates)}/{len(settlement['npcs'])}")
    
    for npc in npcs_with_templates[:5]:  # Show first 5
        print(f"  • {npc['name']} in {npc['building']} (from template)")


def main():
    """Run all tests"""
    print("🧪 Enhanced Settlement System Test Suite")
    print("=" * 60)
    
    try:
        # Test building templates
        manager = test_building_templates()
        
        # Test settlement generation
        test_settlement_generation()
        
        # Test integration
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("\n💡 Next steps:")
        print("  1. Run the building editor: python launch_building_editor.py")
        print("  2. Create custom building templates")
        print("  3. Test settlements in-game")
        print("  4. Adjust settlement generation parameters as needed")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())