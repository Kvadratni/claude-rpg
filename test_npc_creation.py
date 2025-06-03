#!/usr/bin/env python3
"""
Test NPC creation and asset loading in the enhanced settlement system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.world.settlement_manager import ChunkSettlementManager
from src.entities.npc import NPC
from src.core.assets import AssetLoader

def test_npc_creation():
    """Test creating NPCs with proper asset loading"""
    
    print("🎭 Testing NPC Creation and Asset Loading")
    print("=" * 45)
    
    # Initialize asset loader
    print("📦 Initializing asset loader...")
    asset_loader = AssetLoader()
    
    # Initialize settlement manager
    sm = ChunkSettlementManager(12345)
    
    # Test creating a few sample settlements and their NPCs
    test_settlements = [
        ('VILLAGE', (0, 0, {'PLAINS': 3000, 'FOREST': 1000})),
        ('DESERT_OUTPOST', (1, 1, {'DESERT': 4000})),
        ('SWAMP_VILLAGE', (2, 2, {'SWAMP': 4000})),
        ('MINING_CAMP', (3, 3, {'MOUNTAIN': 2000, 'HILLS': 2000})),
    ]
    
    total_npcs_tested = 0
    successful_creations = 0
    
    for settlement_type, (chunk_x, chunk_y, biome_data) in test_settlements:
        print(f"\n🏘️  Testing {settlement_type} Settlement:")
        print("-" * 30)
        
        # Check if settlement should generate
        should_generate = sm.should_generate_settlement(chunk_x, chunk_y, biome_data)
        if should_generate != settlement_type:
            print(f"   ⚠️  Settlement generation returned {should_generate}, forcing {settlement_type}")
        
        # Generate settlement data
        settlement_data = sm.generate_settlement_in_chunk(chunk_x, chunk_y, settlement_type)
        
        print(f"   📍 Settlement at ({settlement_data['world_x']}, {settlement_data['world_y']})")
        print(f"   🏠 Buildings: {len(settlement_data['buildings'])}")
        print(f"   👥 NPCs: {settlement_data['total_npcs']}")
        print(f"   🛒 Shops: {settlement_data['shops']}")
        
        # Test creating each NPC
        for npc_data in settlement_data['npcs']:
            total_npcs_tested += 1
            npc_name = npc_data['name']
            
            try:
                # Create NPC instance
                npc = NPC(
                    x=npc_data['x'], 
                    y=npc_data['y'], 
                    name=npc_name,
                    dialog=npc_data['dialog'],
                    asset_loader=asset_loader,
                    has_shop=npc_data['has_shop']
                )
                
                # Check if sprite was created successfully
                if hasattr(npc, 'sprite') and npc.sprite is not None:
                    successful_creations += 1
                    asset_status = "🎨 Asset" if hasattr(npc, 'direction_sprites') else "🎨 Generated"
                    shop_status = "🛒" if npc_data['has_shop'] else "💬"
                    print(f"   ✅ {shop_status} {npc_name} - {asset_status}")
                else:
                    print(f"   ❌ {npc_name} - Failed to create sprite")
                    
            except Exception as e:
                print(f"   ❌ {npc_name} - Error: {e}")
    
    # Summary
    print(f"\n📊 Test Results:")
    print("=" * 20)
    print(f"   Total NPCs Tested: {total_npcs_tested}")
    print(f"   Successful Creations: {successful_creations}")
    print(f"   Success Rate: {successful_creations/total_npcs_tested*100:.1f}%")
    
    if successful_creations == total_npcs_tested:
        print(f"\n🎉 SUCCESS: All NPCs created successfully with proper assets!")
        
        # Show sample of unique NPCs created
        print(f"\n🎭 Sample NPCs Created:")
        unique_npcs = set()
        for settlement_type, (chunk_x, chunk_y, biome_data) in test_settlements:
            settlement_data = sm.generate_settlement_in_chunk(chunk_x, chunk_y, settlement_type)
            for npc_data in settlement_data['npcs'][:3]:  # Show first 3 from each settlement
                unique_npcs.add(npc_data['name'])
        
        for npc_name in sorted(list(unique_npcs)[:10]):  # Show first 10 unique NPCs
            print(f"   🎭 {npc_name}")
        
        if len(unique_npcs) > 10:
            print(f"   ... and {len(unique_npcs) - 10} more unique NPCs")
            
        return True
    else:
        print(f"\n⚠️  Some NPCs failed to create properly")
        return False

if __name__ == "__main__":
    test_npc_creation()