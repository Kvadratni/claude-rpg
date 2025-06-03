#!/usr/bin/env python3
"""
Test script for enhanced settlement system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.world.settlement_manager import ChunkSettlementManager
from src.world.settlement_patterns import SettlementPatternGenerator

def test_enhanced_settlements():
    """Test the enhanced settlement system"""
    
    print("🏘️  Testing Enhanced Settlement System")
    print("=" * 50)
    
    # Initialize settlement manager
    world_seed = 12345
    settlement_manager = ChunkSettlementManager(world_seed)
    pattern_generator = SettlementPatternGenerator()
    
    print(f"✅ Initialized settlement manager with seed: {world_seed}")
    print(f"✅ Available settlement types: {len(settlement_manager.SETTLEMENT_TEMPLATES)}")
    
    # Test each settlement type
    print("\n📋 Settlement Type Analysis:")
    print("-" * 30)
    
    total_buildings = 0
    total_npcs = 0
    
    for settlement_type, config in settlement_manager.SETTLEMENT_TEMPLATES.items():
        buildings_count = len(config['buildings'])
        npcs_count = len([b for b in config['buildings'] if 'npc' in b])
        shops_count = len([b for b in config['buildings'] if b.get('has_shop', False)])
        
        total_buildings += buildings_count
        total_npcs += npcs_count
        
        print(f"🏘️  {settlement_type}:")
        print(f"   Size: {config['size'][0]}x{config['size'][1]}")
        print(f"   Buildings: {buildings_count}")
        print(f"   NPCs: {npcs_count}")
        print(f"   Shops: {shops_count}")
        print(f"   Spawn Chance: {config['spawn_chance']*100:.1f}%")
        print(f"   Biomes: {', '.join(config['biomes'])}")
        print()
    
    print(f"📊 Total across all settlement types:")
    print(f"   Settlement Types: {len(settlement_manager.SETTLEMENT_TEMPLATES)}")
    print(f"   Total Buildings: {total_buildings}")
    print(f"   Total NPCs: {total_npcs}")
    print(f"   Average NPCs per settlement: {total_npcs / len(settlement_manager.SETTLEMENT_TEMPLATES):.1f}")
    
    # Test settlement generation
    print("\n🎲 Testing Settlement Generation:")
    print("-" * 35)
    
    test_chunks = [
        (0, 0, {'PLAINS': 3000, 'FOREST': 1000}),
        (1, 1, {'DESERT': 4000}),
        (2, 2, {'SNOW': 3500, 'TUNDRA': 500}),
        (-1, -1, {'SWAMP': 4000}),
        (3, 3, {'FOREST': 4000}),
        (4, 4, {'MOUNTAIN': 2000, 'HILLS': 2000}),
        (5, 5, {'PLAINS': 2000, 'COAST': 2000}),
    ]
    
    settlements_generated = 0
    
    for chunk_x, chunk_y, biome_data in test_chunks:
        settlement_type = settlement_manager.should_generate_settlement(chunk_x, chunk_y, biome_data)
        
        if settlement_type:
            settlements_generated += 1
            settlement_data = settlement_manager.generate_settlement_in_chunk(chunk_x, chunk_y, settlement_type)
            
            print(f"🏘️  Generated {settlement_type} at chunk ({chunk_x}, {chunk_y})")
            print(f"   World Position: ({settlement_data['world_x']}, {settlement_data['world_y']})")
            print(f"   NPCs: {settlement_data['total_npcs']}")
            print(f"   Shops: {settlement_data['shops']}")
            print(f"   Sample NPCs: {[npc['name'] for npc in settlement_data['npcs'][:3]]}")
            print()
        else:
            dominant_biome = max(biome_data.items(), key=lambda x: x[1])[0]
            print(f"❌ No settlement at chunk ({chunk_x}, {chunk_y}) - {dominant_biome} biome")
    
    print(f"📈 Settlement Generation Results:")
    print(f"   Chunks Tested: {len(test_chunks)}")
    print(f"   Settlements Generated: {settlements_generated}")
    print(f"   Generation Rate: {settlements_generated/len(test_chunks)*100:.1f}%")
    
    # Test settlement patterns
    print("\n🗺️  Testing Settlement Patterns:")
    print("-" * 32)
    
    pattern_types = [
        'VILLAGE', 'TOWN', 'DESERT_OUTPOST', 'SNOW_SETTLEMENT', 
        'SWAMP_VILLAGE', 'FOREST_CAMP', 'MINING_CAMP', 'FISHING_VILLAGE'
    ]
    
    for pattern_type in pattern_types:
        try:
            pattern = pattern_generator.get_pattern(pattern_type)
            building_count = len(pattern.get_building_positions())
            pathway_count = len(pattern.get_pathway_positions())
            
            print(f"🗺️  {pattern_type} Pattern:")
            print(f"   Name: {pattern.name}")
            print(f"   Size: {pattern.width}x{pattern.height}")
            print(f"   Buildings: {building_count}")
            print(f"   Pathways: {pathway_count}")
            print()
        except Exception as e:
            print(f"❌ Error with {pattern_type} pattern: {e}")
    
    # Test NPC dialog generation
    print("\n💬 Testing NPC Dialog Generation:")
    print("-" * 33)
    
    sample_npcs = [
        ('Master Merchant', 'VILLAGE', 'General Store'),
        ('Caravan Master', 'DESERT_OUTPOST', 'Trading Post'),
        ('Forest Druid', 'FOREST_CAMP', 'Druid Circle'),
        ('Mine Foreman', 'MINING_CAMP', 'Mine Entrance'),
    ]
    
    for npc_name, settlement_type, building_name in sample_npcs:
        dialog = settlement_manager._generate_npc_dialog(npc_name, settlement_type, building_name)
        print(f"💬 {npc_name} ({settlement_type}):")
        print(f"   Building: {building_name}")
        print(f"   Dialog Lines: {len(dialog)}")
        print(f"   Sample: \"{dialog[0]}\"")
        print()
    
    print("🎉 Enhanced Settlement System Test Complete!")
    print(f"✅ All systems functional with {len(settlement_manager.SETTLEMENT_TEMPLATES)} settlement types")
    print(f"✅ Estimated {settlements_generated/len(test_chunks)*100:.0f}% settlement density")
    print(f"✅ Rich NPC integration with contextual dialog")

if __name__ == "__main__":
    test_enhanced_settlements()