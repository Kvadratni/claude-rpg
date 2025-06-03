#!/usr/bin/env python3
"""
Test NPC asset coverage for the enhanced settlement system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.world.settlement_manager import ChunkSettlementManager

def test_npc_asset_coverage():
    """Test that all NPCs have proper asset coverage"""
    
    print("🎨 Testing NPC Asset Coverage")
    print("=" * 40)
    
    # Get all NPCs from settlement system
    sm = ChunkSettlementManager(12345)
    all_npcs = set()
    for settlement_type, config in sm.SETTLEMENT_TEMPLATES.items():
        for building in config['buildings']:
            if 'npc' in building:
                all_npcs.add(building['npc'])
    
    # Updated mapping from NPC.py (expanded)
    npc_mappings = {
        # Merchants and Traders
        'Master Merchant': 'npc_shopkeeper',
        'Shopkeeper': 'npc_shopkeeper', 
        'Trader': 'trade_master',
        'Rich Merchant': 'trade_master',
        'Market Master': 'trade_master',
        
        # Authority Figures
        'Village Elder': 'elder_npc',
        'Elder': 'elder_npc',
        'Mayor': 'mayor',  # NEW ASSET
        'Noble': 'noble',  # NEW ASSET
        
        # Military and Guards
        'Guard Captain': 'guard_captain',
        'Guard': 'village_guard_sprite',
        'Commander': 'guard_captain',
        'Barracks Chief': 'guard_captain',
        
        # Crafters and Smiths
        'Master Smith': 'master_smith',
        'Blacksmith': 'master_smith',
        'Tool Maker': 'master_smith',
        'Weapon Master': 'master_smith',
        'Craftsman': 'craftsman',  # NEW ASSET
        
        # Hospitality
        'Innkeeper': 'innkeeper',
        'Inn Master': 'innkeeper',
        'Lodge Keeper': 'innkeeper',
        'Barkeeper': 'barkeeper',  # NEW ASSET
        
        # Religious
        'High Priest': 'high_priest',
        'Archbishop': 'high_priest',
        'Forest Priest': 'high_priest',
        
        # Mining
        'Mine Foreman': 'mine_foreman',
        'Ore Master': 'mine_foreman',
        'Veteran Miner': 'mine_foreman',
        'Assayer': 'assayer',  # NEW ASSET
        
        # Maritime
        'Harbor Master': 'harbor_master',
        'Dock Master': 'harbor_master',
        'Fisherman': 'master_fisher',
        'Old Fisherman': 'master_fisher',
        'Fish Merchant': 'master_fisher',
        'Net Weaver': 'master_fisher',
        'Smoke Master': 'master_fisher',
        'Sailor': 'master_fisher',
        'Boat Builder': 'boat_builder',  # NEW ASSET
        
        # Desert/Caravan
        'Caravan Master': 'caravan_master',
        'Desert Guide': 'caravan_master',
        'Desert Nomad': 'caravan_master',
        'Oasis Keeper': 'caravan_master',
        
        # Forest/Nature
        'Forest Ranger': 'forest_ranger',
        'Scout Leader': 'forest_ranger',
        'Hunter': 'forest_ranger',
        'Tree Keeper': 'forest_ranger',
        'Master Woodcutter': 'master_woodcutter',  # NEW ASSET
        
        # Herbalists/Magic
        'Master Herbalist': 'master_herbalist',
        'Herb Gatherer': 'master_herbalist',
        'Forest Druid': 'master_herbalist',
        'Swamp Alchemist': 'master_herbalist',
        'Mysterious Wizard': 'mysterious_wizard',
        'Court Wizard': 'mysterious_wizard',
        'Swamp Witch': 'swamp_witch',  # NEW ASSET
        
        # General/Misc
        'Old Hermit': 'old_hermit',
        'Swamp Dweller': 'old_hermit',
        'Villager': 'old_hermit',
        'Stable Master': 'stable_master',
        
        # Specialized Workers
        'Banker': 'banker',  # NEW ASSET
        'Librarian': 'librarian',  # NEW ASSET
        'Guild Master': 'guild_master',  # NEW ASSET
        'Miller': 'miller',  # NEW ASSET
        'Fur Trader': 'fur_trader',  # NEW ASSET
        'Ice Keeper': 'ice_keeper',  # NEW ASSET
        'Water Keeper': 'water_keeper',  # NEW ASSET
        'Mushroom Farmer': 'mushroom_farmer',  # NEW ASSET
    }
    
    # Get existing files
    existing_files = set()
    assets_dir = 'assets/images'
    if os.path.exists(assets_dir):
        existing_files = set(f.replace('.png', '') for f in os.listdir(assets_dir) if f.endswith('.png'))
    
    # Test coverage
    print(f"📊 Coverage Analysis:")
    print(f"   Total NPCs: {len(all_npcs)}")
    print(f"   Mapped NPCs: {len([npc for npc in all_npcs if npc in npc_mappings])}")
    print(f"   Available Assets: {len(existing_files)}")
    
    # Check each NPC
    print(f"\n🎭 NPC Asset Status:")
    print("-" * 25)
    
    mapped_count = 0
    assets_found = 0
    assets_missing = 0
    
    for npc_name in sorted(all_npcs):
        asset_name = npc_mappings.get(npc_name)
        if asset_name:
            mapped_count += 1
            if asset_name in existing_files:
                assets_found += 1
                print(f"✅ {npc_name} → {asset_name}.png")
            else:
                assets_missing += 1
                print(f"❌ {npc_name} → {asset_name}.png (MISSING)")
        else:
            print(f"⚠️  {npc_name} → NO MAPPING")
    
    # Summary
    print(f"\n📈 Final Results:")
    print(f"   NPCs Mapped: {mapped_count}/{len(all_npcs)} ({mapped_count/len(all_npcs)*100:.1f}%)")
    print(f"   Assets Found: {assets_found}/{mapped_count} ({assets_found/mapped_count*100:.1f}%)")
    print(f"   Assets Missing: {assets_missing}")
    
    if assets_missing == 0 and mapped_count == len(all_npcs):
        print(f"\n🎉 SUCCESS: All NPCs have proper asset coverage!")
        return True
    else:
        print(f"\n⚠️  Issues found - some NPCs may use fallback generation")
        return False

if __name__ == "__main__":
    test_npc_asset_coverage()