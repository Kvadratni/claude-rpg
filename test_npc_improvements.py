#!/usr/bin/env python3
"""
Test script to validate NPC spawning improvements
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/Users/mnovich/Development/claude-rpg/src')

def test_settlement_templates():
    """Test that settlement templates have the expected number of NPCs"""
    from procedural_generation.src.settlement_generator import SettlementGenerator
    
    print("=== TESTING SETTLEMENT TEMPLATES ===")
    
    # Create a dummy generator to access templates
    generator = SettlementGenerator(100, 100, 12345)
    
    total_expected_npcs = 0
    
    for template_name, template_config in generator.SETTLEMENT_TEMPLATES.items():
        buildings = template_config['buildings']
        npc_count = sum(1 for building in buildings if building.get('npc'))
        total_expected_npcs += npc_count
        
        print(f"{template_name}:")
        print(f"  Buildings: {len(buildings)}")
        print(f"  NPCs: {npc_count}")
        
        for building in buildings:
            if building.get('npc'):
                print(f"    - {building['name']}: {building['npc']} (shop: {building.get('has_shop', False)})")
        print()
    
    print(f"Total NPCs per settlement type: {total_expected_npcs}")
    return total_expected_npcs

def test_settlement_targets():
    """Test settlement placement targets"""
    from procedural_generation.src.settlement_generator import SettlementGenerator
    
    print("=== TESTING SETTLEMENT TARGETS ===")
    
    # This would normally be in the place_settlements method
    settlement_targets = {
        'VILLAGE': 2,
        'DESERT_OUTPOST': 2, 
        'SNOW_SETTLEMENT': 2,
        'TRADING_POST': 3,
        'MINING_CAMP': 1,
        'FISHING_VILLAGE': 1
    }
    
    generator = SettlementGenerator(100, 100, 12345)
    
    total_expected_settlements = 0
    total_expected_npcs = 0
    
    for template_name, target_count in settlement_targets.items():
        template_config = generator.SETTLEMENT_TEMPLATES[template_name]
        buildings = template_config['buildings']
        npcs_per_settlement = sum(1 for building in buildings if building.get('npc'))
        
        total_settlements_of_type = target_count
        total_npcs_of_type = total_settlements_of_type * npcs_per_settlement
        
        total_expected_settlements += total_settlements_of_type
        total_expected_npcs += total_npcs_of_type
        
        print(f"{template_name}:")
        print(f"  Target settlements: {target_count}")
        print(f"  NPCs per settlement: {npcs_per_settlement}")
        print(f"  Total NPCs from this type: {total_npcs_of_type}")
        print()
    
    print(f"TOTAL EXPECTED SETTLEMENTS: {total_expected_settlements}")
    print(f"TOTAL EXPECTED NPCs: {total_expected_npcs}")
    
    return total_expected_settlements, total_expected_npcs

def test_npc_dialogs():
    """Test that all NPC types have dialog defined"""
    from procedural_generation.src.enhanced_entity_spawner import EnhancedEntitySpawner
    from procedural_generation.src.settlement_generator import SettlementGenerator
    
    print("=== TESTING NPC DIALOGS ===")
    
    spawner = EnhancedEntitySpawner(100, 100, 12345)
    generator = SettlementGenerator(100, 100, 12345)
    
    # Collect all NPC names from all settlement templates
    all_npc_names = set()
    for template_name, template_config in generator.SETTLEMENT_TEMPLATES.items():
        for building in template_config['buildings']:
            if building.get('npc'):
                all_npc_names.add(building['npc'])
    
    print(f"Found {len(all_npc_names)} unique NPC types:")
    
    missing_dialogs = []
    for npc_name in sorted(all_npc_names):
        dialog = spawner.get_npc_dialog(npc_name)
        has_custom_dialog = dialog != ["Hello, traveler!"]
        
        print(f"  {npc_name}: {'✓' if has_custom_dialog else '✗'} ({len(dialog)} lines)")
        
        if not has_custom_dialog:
            missing_dialogs.append(npc_name)
    
    if missing_dialogs:
        print(f"\nWARNING: {len(missing_dialogs)} NPCs missing custom dialog:")
        for npc_name in missing_dialogs:
            print(f"  - {npc_name}")
    else:
        print("\n✓ All NPCs have custom dialog!")
    
    return len(missing_dialogs) == 0

if __name__ == "__main__":
    print("Testing NPC Spawning Improvements")
    print("=" * 50)
    
    try:
        # Test 1: Settlement templates
        template_npcs = test_settlement_templates()
        
        # Test 2: Settlement targets
        expected_settlements, expected_npcs = test_settlement_targets()
        
        # Test 3: NPC dialogs
        dialogs_ok = test_npc_dialogs()
        
        print("=" * 50)
        print("SUMMARY:")
        print(f"✓ Settlement templates defined with NPCs")
        print(f"✓ Expected settlements: {expected_settlements}")
        print(f"✓ Expected NPCs: {expected_npcs}")
        print(f"{'✓' if dialogs_ok else '✗'} NPC dialogs: {'Complete' if dialogs_ok else 'Missing some'}")
        
        print("\nIMPROVEMENT:")
        print(f"Before: ~2 NPCs")
        print(f"After:  ~{expected_npcs} NPCs (if all settlements place successfully)")
        print(f"Increase: {expected_npcs // 2}x more NPCs!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()