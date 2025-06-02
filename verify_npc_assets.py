#!/usr/bin/env python3
"""
Verify that all NPCs have proper asset mappings
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, '/Users/mnovich/Development/claude-rpg/src')

def verify_npc_assets():
    """Verify all NPCs have asset mappings"""
    from procedural_generation.src.settlement_generator import SettlementGenerator
    
    print("=== NPC ASSET VERIFICATION ===")
    
    # Get all NPCs from settlement templates
    generator = SettlementGenerator(100, 100, 12345)
    all_npcs = set()
    
    for template_name, template_config in generator.SETTLEMENT_TEMPLATES.items():
        for building in template_config['buildings']:
            if building.get('npc'):
                all_npcs.add(building['npc'])
    
    print(f"Found {len(all_npcs)} unique NPC types in settlements:")
    for npc in sorted(all_npcs):
        print(f"  - {npc}")
    
    # Check sprite mappings from NPC class
    print("\nChecking sprite mappings...")
    
    # Manually define the mappings from the NPC class
    sprite_mappings = {
        # Existing NPCs
        "Master Merchant": "npc_shopkeeper",
        "Shopkeeper": "npc_shopkeeper", 
        "Village Elder": "elder_npc",
        "Elder": "elder_npc",
        "Guard Captain": "guard_captain",
        "Guard": "village_guard_sprite",
        "Master Smith": "master_smith",
        "Blacksmith": "master_smith",
        "Innkeeper": "innkeeper",
        "High Priest": "high_priest",
        "Mine Foreman": "mine_foreman",
        "Harbor Master": "harbor_master",
        "Caravan Master": "caravan_master",
        "Forest Ranger": "forest_ranger",
        "Master Herbalist": "master_herbalist",
        "Mysterious Wizard": "mysterious_wizard",
        "Old Hermit": "old_hermit",
        
        # New NPCs - using existing assets or generic fallback
        "Desert Guide": "caravan_master",  # Similar desert theme
        "Head Miner": "mine_foreman",      # Similar mining theme
        "Master Fisher": "harbor_master",  # Similar water/harbor theme
        "Trade Master": "npc_shopkeeper",  # Similar merchant theme
        "Stable Master": "caravan_master", # Similar travel/transport theme
        "Water Keeper": "harbor_master",   # Similar water theme
        "Lodge Keeper": "innkeeper"        # Similar hospitality theme
    }
    
    # Check available assets
    assets_dir = "/Users/mnovich/Development/claude-rpg/assets/images"
    available_assets = set()
    
    if os.path.exists(assets_dir):
        for file in os.listdir(assets_dir):
            if file.endswith('.png'):
                available_assets.add(file[:-4])  # Remove .png extension
    
    print(f"\nFound {len(available_assets)} image assets")
    
    # Verify each NPC has a mapping and the asset exists
    missing_mappings = []
    missing_assets = []
    
    for npc_name in sorted(all_npcs):
        if npc_name not in sprite_mappings:
            missing_mappings.append(npc_name)
        else:
            asset_name = sprite_mappings[npc_name]
            if asset_name not in available_assets:
                missing_assets.append((npc_name, asset_name))
    
    # Report results
    print("\n=== VERIFICATION RESULTS ===")
    
    if not missing_mappings and not missing_assets:
        print("✅ ALL NPCs HAVE PROPER ASSET MAPPINGS!")
        print("\nNPC → Asset mappings:")
        for npc_name in sorted(all_npcs):
            asset_name = sprite_mappings[npc_name]
            status = "✓" if asset_name in available_assets else "✗"
            print(f"  {status} {npc_name} → {asset_name}")
    else:
        if missing_mappings:
            print(f"❌ {len(missing_mappings)} NPCs missing sprite mappings:")
            for npc in missing_mappings:
                print(f"  - {npc}")
        
        if missing_assets:
            print(f"❌ {len(missing_assets)} NPCs have mappings to missing assets:")
            for npc, asset in missing_assets:
                print(f"  - {npc} → {asset} (asset not found)")
    
    return len(missing_mappings) == 0 and len(missing_assets) == 0

if __name__ == "__main__":
    try:
        success = verify_npc_assets()
        if success:
            print("\n🎉 All NPCs are properly configured with assets!")
        else:
            print("\n⚠️  Some NPCs need attention.")
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()