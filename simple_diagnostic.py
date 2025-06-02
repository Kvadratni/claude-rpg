#!/usr/bin/env python3
"""
Simple Settlement Building Diagnostic Script

Analyzes existing chunk files to identify the building persistence issue.
"""

import json
import os
from pathlib import Path


def get_tile_name(tile_id):
    """Get human-readable tile name"""
    tile_names = {
        0: "GRASS",
        1: "DIRT", 
        2: "STONE",
        3: "WATER",
        4: "WALL",
        5: "DOOR",
        6: "WALL_CORNER_TL",
        7: "WALL_CORNER_TR", 
        8: "WALL_CORNER_BL",
        9: "WALL_CORNER_BR",
        10: "WALL_HORIZONTAL",
        11: "WALL_VERTICAL",
        12: "TREE",
        13: "BRICK",
        14: "WALL_WINDOW_HORIZONTAL",
        15: "WALL_WINDOW_VERTICAL",
        16: "SAND",
        17: "SNOW",
        18: "FOREST_FLOOR",
        19: "SWAMP"
    }
    return tile_names.get(tile_id, f"UNKNOWN_{tile_id}")


def analyze_chunk_file(chunk_path):
    """Analyze a chunk file to see what tiles it contains"""
    print(f"\n=== ANALYZING: {chunk_path.name} ===")
    
    try:
        with open(chunk_path, 'r') as f:
            chunk_data = json.load(f)
        
        chunk_x = chunk_data['chunk_x']
        chunk_y = chunk_data['chunk_y']
        tiles = chunk_data['tiles']
        entities = chunk_data['entities']
        
        print(f"Chunk ({chunk_x}, {chunk_y}):")
        print(f"  Dimensions: {len(tiles)}x{len(tiles[0]) if tiles else 0}")
        print(f"  Total entities: {len(entities)}")
        
        # Count tile types
        tile_counts = {}
        building_tiles = 0
        
        for y, row in enumerate(tiles):
            for x, tile in enumerate(row):
                tile_counts[tile] = tile_counts.get(tile, 0) + 1
                
                # Count building-related tiles
                if tile in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]:  # Building tiles
                    building_tiles += 1
        
        print(f"  🏗️  Building tiles found: {building_tiles}")
        
        # Show tile distribution (only non-zero counts)
        print(f"  📊 Tile distribution:")
        for tile_type in sorted(tile_counts.keys()):
            count = tile_counts[tile_type]
            if count > 0:
                tile_name = get_tile_name(tile_type)
                print(f"    {tile_type:2d} ({tile_name:20s}): {count:4d}")
        
        # Analyze entities by type
        entity_types = {}
        for entity in entities:
            entity_type = entity.get('type', 'unknown')
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print(f"  👥 Entity distribution:")
        for entity_type, count in entity_types.items():
            print(f"    {entity_type}: {count}")
        
        # Show NPCs specifically
        npcs = [e for e in entities if e['type'] == 'npc']
        if npcs:
            print(f"  🧙 NPCs found:")
            for npc in npcs:
                print(f"    - {npc['name']} at ({npc['x']}, {npc['y']})")
        
        return {
            'chunk_coords': (chunk_x, chunk_y),
            'building_tiles': building_tiles,
            'npc_count': len(npcs),
            'total_entities': len(entities),
            'tile_counts': tile_counts,
            'has_settlement': len(npcs) > 0,
            'has_buildings': building_tiles > 0
        }
        
    except Exception as e:
        print(f"❌ Error analyzing chunk file: {e}")
        return None


def main():
    """Main diagnostic function"""
    print("🏘️  SETTLEMENT BUILDING DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Find saves directory
    saves_dir = Path("saves/worlds")
    if not saves_dir.exists():
        print("❌ No saves directory found")
        return
    
    print(f"📁 Found saves directory: {saves_dir}")
    
    # Find procedural world directories
    procedural_worlds = [d for d in saves_dir.iterdir() if d.is_dir() and d.name.startswith('procedural_')]
    
    if not procedural_worlds:
        print("❌ No procedural worlds found")
        return
    
    print(f"🌍 Found {len(procedural_worlds)} procedural worlds:")
    for world in procedural_worlds:
        print(f"  - {world.name}")
    
    # Analyze the most recent world
    latest_world = max(procedural_worlds, key=lambda d: d.stat().st_mtime)
    print(f"\n🔍 Analyzing latest world: {latest_world.name}")
    
    # Find chunk files
    chunk_files = list(latest_world.glob("chunk_*.json"))
    print(f"📦 Found {len(chunk_files)} chunk files")
    
    if not chunk_files:
        print("❌ No chunk files found")
        return
    
    # Analyze all chunks
    settlement_chunks = []
    chunks_with_buildings = []
    total_analyzed = 0
    
    print(f"\n📊 ANALYZING CHUNKS...")
    
    for chunk_file in chunk_files:
        result = analyze_chunk_file(chunk_file)
        if result:
            total_analyzed += 1
            
            if result['has_settlement']:
                settlement_chunks.append(result)
                
                if result['has_buildings']:
                    chunks_with_buildings.append(result)
    
    # Summary
    print(f"\n" + "=" * 60)
    print(f"📈 ANALYSIS SUMMARY")
    print(f"=" * 60)
    
    print(f"📦 Total chunks analyzed: {total_analyzed}")
    print(f"🏘️  Chunks with settlements (NPCs): {len(settlement_chunks)}")
    print(f"🏗️  Chunks with buildings: {len(chunks_with_buildings)}")
    
    if len(settlement_chunks) == 0:
        print("ℹ️  No settlements found in any chunks")
    elif len(chunks_with_buildings) == 0:
        print("❌ CRITICAL ISSUE: Settlement chunks have NPCs but NO building tiles!")
        print("   This confirms the building persistence bug.")
    elif len(chunks_with_buildings) == len(settlement_chunks):
        print("✅ SUCCESS: All settlement chunks have building tiles!")
    else:
        missing_buildings = len(settlement_chunks) - len(chunks_with_buildings)
        print(f"⚠️  PARTIAL ISSUE: {missing_buildings} settlement chunks missing buildings")
    
    # Detailed settlement analysis
    if settlement_chunks:
        print(f"\n🏘️  SETTLEMENT DETAILS:")
        for i, chunk_info in enumerate(settlement_chunks, 1):
            chunk_x, chunk_y = chunk_info['chunk_coords']
            status = "✅ HAS BUILDINGS" if chunk_info['has_buildings'] else "❌ NO BUILDINGS"
            print(f"  {i}. Chunk ({chunk_x:2d}, {chunk_y:2d}): {chunk_info['npc_count']} NPCs, {chunk_info['building_tiles']} building tiles - {status}")
    
    # Building tile analysis
    if chunks_with_buildings:
        print(f"\n🏗️  BUILDING TILE BREAKDOWN:")
        for chunk_info in chunks_with_buildings:
            chunk_x, chunk_y = chunk_info['chunk_coords']
            print(f"  Chunk ({chunk_x:2d}, {chunk_y:2d}): {chunk_info['building_tiles']} building tiles")
            
            # Show building tile types
            building_tile_types = {}
            for tile_type, count in chunk_info['tile_counts'].items():
                if tile_type in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15] and count > 0:
                    building_tile_types[tile_type] = count
            
            for tile_type, count in building_tile_types.items():
                tile_name = get_tile_name(tile_type)
                print(f"    {tile_name}: {count}")
    
    print(f"\n" + "=" * 60)
    print("🔧 DIAGNOSTIC COMPLETE")
    
    # Provide recommendations
    if len(settlement_chunks) > 0 and len(chunks_with_buildings) == 0:
        print("\n💡 RECOMMENDATIONS:")
        print("1. The building placement code is not persisting tiles to chunks")
        print("2. Check WorldGenerator._place_settlement_buildings_on_chunk() method")
        print("3. Ensure chunk.set_tile() calls are working correctly")
        print("4. Verify chunk saving happens after building placement")
        print("5. Test with a fresh world generation to confirm the fix")


if __name__ == "__main__":
    main()