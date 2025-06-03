#!/usr/bin/env python3
"""
Final verification of NPC asset coverage
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.world.settlement_manager import ChunkSettlementManager

def verify_npc_assets():
    """Verify all NPC assets exist and are properly mapped"""
    
    print("🎯 Final NPC Asset Verification")
    print("=" * 35)
    
    # Get all NPCs from settlement system
    sm = ChunkSettlementManager(12345)
    all_npcs = set()
    npc_to_settlement = {}
    
    for settlement_type, config in sm.SETTLEMENT_TEMPLATES.items():
        for building in config['buildings']:
            if 'npc' in building:
                npc_name = building['npc']
                all_npcs.add(npc_name)
                if npc_name not in npc_to_settlement:
                    npc_to_settlement[npc_name] = []
                npc_to_settlement[npc_name].append(settlement_type)
    
    # NPC to asset mapping (from our updated NPC.py)
    npc_mappings = {
        'Master Merchant': 'npc_shopkeeper',
        'Trader': 'trade_master',
        'Rich Merchant': 'trade_master',
        'Market Master': 'trade_master',
        'Village Elder': 'elder_npc',
        'Mayor': 'mayor',
        'Noble': 'noble',
        'Guard Captain': 'guard_captain',
        'Commander': 'guard_captain',
        'Barracks Chief': 'guard_captain',
        'Master Smith': 'master_smith',
        'Tool Maker': 'master_smith',
        'Weapon Master': 'master_smith',
        'Craftsman': 'craftsman',
        'Innkeeper': 'innkeeper',
        'Inn Master': 'innkeeper',
        'Lodge Keeper': 'innkeeper',
        'Barkeeper': 'barkeeper',
        'High Priest': 'high_priest',
        'Archbishop': 'high_priest',
        'Forest Priest': 'high_priest',
        'Mine Foreman': 'mine_foreman',
        'Ore Master': 'mine_foreman',
        'Veteran Miner': 'mine_foreman',
        'Assayer': 'assayer',
        'Harbor Master': 'harbor_master',
        'Dock Master': 'harbor_master',
        'Fisherman': 'master_fisher',
        'Old Fisherman': 'master_fisher',
        'Fish Merchant': 'master_fisher',
        'Net Weaver': 'master_fisher',
        'Smoke Master': 'master_fisher',
        'Sailor': 'master_fisher',
        'Boat Builder': 'boat_builder',
        'Caravan Master': 'caravan_master',
        'Desert Guide': 'caravan_master',
        'Desert Nomad': 'caravan_master',
        'Oasis Keeper': 'caravan_master',
        'Forest Ranger': 'forest_ranger',
        'Scout Leader': 'forest_ranger',
        'Hunter': 'forest_ranger',
        'Tree Keeper': 'forest_ranger',
        'Master Woodcutter': 'master_woodcutter',
        'Master Herbalist': 'master_herbalist',
        'Herb Gatherer': 'master_herbalist',
        'Forest Druid': 'master_herbalist',
        'Swamp Alchemist': 'master_herbalist',
        'Mysterious Wizard': 'mysterious_wizard',
        'Court Wizard': 'mysterious_wizard',
        'Swamp Witch': 'swamp_witch',
        'Old Hermit': 'old_hermit',
        'Swamp Dweller': 'old_hermit',
        'Villager': 'old_hermit',
        'Stable Master': 'stable_master',
        'Banker': 'banker',
        'Librarian': 'librarian',
        'Guild Master': 'guild_master',
        'Miller': 'miller',
        'Fur Trader': 'fur_trader',
        'Ice Keeper': 'ice_keeper',
        'Water Keeper': 'water_keeper',
        'Mushroom Farmer': 'mushroom_farmer',
    }
    
    # Check which assets exist
    assets_dir = 'assets/images'
    existing_assets = set()
    if os.path.exists(assets_dir):
        existing_assets = set(f.replace('.png', '') for f in os.listdir(assets_dir) if f.endswith('.png'))
    
    # Verify coverage
    print(f"📊 Settlement System Overview:")
    print(f"   Settlement Types: {len(sm.SETTLEMENT_TEMPLATES)}")
    print(f"   Total Unique NPCs: {len(all_npcs)}")
    print(f"   Available Assets: {len(existing_assets)}")
    
    # Check each NPC
    print(f"\n🎭 NPC Verification by Settlement Type:")
    print("-" * 40)
    
    all_good = True
    total_mapped = 0
    total_assets_found = 0
    
    for settlement_type, config in sm.SETTLEMENT_TEMPLATES.items():
        print(f"\n🏘️  {settlement_type}:")
        settlement_npcs = [b['npc'] for b in config['buildings'] if 'npc' in b]
        
        for npc_name in settlement_npcs:
            total_mapped += 1
            asset_name = npc_mappings.get(npc_name)
            
            if asset_name and asset_name in existing_assets:
                total_assets_found += 1
                shop_indicator = "🛒" if any(b.get('has_shop') for b in config['buildings'] if b.get('npc') == npc_name) else "💬"
                print(f"   ✅ {shop_indicator} {npc_name} → {asset_name}.png")
            elif asset_name:
                print(f"   ❌ {npc_name} → {asset_name}.png (MISSING)")
                all_good = False
            else:
                print(f"   ⚠️  {npc_name} → NO MAPPING")
                all_good = False
    
    # New assets we generated
    new_assets = [
        'mayor', 'noble', 'banker', 'librarian', 'guild_master', 'barkeeper',
        'craftsman', 'master_woodcutter', 'miller', 'boat_builder', 'swamp_witch',
        'fur_trader', 'ice_keeper', 'water_keeper', 'mushroom_farmer', 'assayer'
    ]
    
    print(f"\n🎨 Newly Generated Assets:")
    print("-" * 25)
    new_assets_found = 0
    for asset in new_assets:
        if asset in existing_assets:
            new_assets_found += 1
            print(f"   ✅ {asset}.png")
        else:
            print(f"   ❌ {asset}.png (MISSING)")
    
    # Final summary
    print(f"\n📈 Final Verification Results:")
    print("=" * 30)
    print(f"   Total NPCs: {len(all_npcs)}")
    print(f"   Mapped NPCs: {total_mapped}")
    print(f"   Assets Found: {total_assets_found}/{total_mapped} ({total_assets_found/total_mapped*100:.1f}%)")
    print(f"   New Assets Generated: {new_assets_found}/{len(new_assets)} ({new_assets_found/len(new_assets)*100:.1f}%)")
    
    if all_good and total_assets_found == total_mapped:
        print(f"\n🎉 PERFECT! All {len(all_npcs)} NPCs have proper asset coverage!")
        print(f"✅ Enhanced settlement system is ready with full NPC asset support")
        return True
    else:
        print(f"\n⚠️  Some issues found, but fallback generation will handle missing assets")
        return False

if __name__ == "__main__":
    verify_npc_assets()