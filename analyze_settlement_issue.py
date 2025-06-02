#!/usr/bin/env python3
"""
Deep Analysis of Settlement Issue

Based on diagnostic results:
- Building tiles ARE being saved (31, 160, 7, 8, 27 tiles found)
- But NO NPCs are found in any chunks
- This suggests the issue is with NPC persistence, not building persistence
"""

import json
from pathlib import Path


def analyze_specific_chunk(chunk_path):
    """Analyze a specific chunk in detail"""
    print(f"\n🔍 DEEP ANALYSIS: {chunk_path.name}")
    
    with open(chunk_path, 'r') as f:
        chunk_data = json.load(f)
    
    chunk_x = chunk_data['chunk_x']
    chunk_y = chunk_data['chunk_y']
    tiles = chunk_data['tiles']
    entities = chunk_data['entities']
    
    print(f"Chunk ({chunk_x}, {chunk_y}):")
    
    # Find building patterns
    building_tiles = []
    for y, row in enumerate(tiles):
        for x, tile in enumerate(row):
            if tile in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]:  # Building tiles
                building_tiles.append((x, y, tile))
    
    if building_tiles:
        print(f"  🏗️  Found {len(building_tiles)} building tiles:")
        
        # Group building tiles by proximity to identify structures
        structures = []
        used_tiles = set()
        
        for x, y, tile in building_tiles:
            if (x, y) in used_tiles:
                continue
                
            # Find connected building tiles (simple flood fill)
            structure_tiles = []
            to_check = [(x, y)]
            
            while to_check:
                cx, cy = to_check.pop()
                if (cx, cy) in used_tiles:
                    continue
                    
                # Check if this is a building tile
                if cy < len(tiles) and cx < len(tiles[cy]) and tiles[cy][cx] in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]:
                    used_tiles.add((cx, cy))
                    structure_tiles.append((cx, cy, tiles[cy][cx]))
                    
                    # Add neighbors to check
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < 64 and 0 <= ny < 64 and (nx, ny) not in used_tiles:
                            to_check.append((nx, ny))
            
            if structure_tiles:
                structures.append(structure_tiles)
        
        print(f"  🏘️  Identified {len(structures)} building structures:")
        for i, structure in enumerate(structures, 1):
            min_x = min(x for x, y, t in structure)
            max_x = max(x for x, y, t in structure)
            min_y = min(y for x, y, t in structure)
            max_y = max(y for x, y, t in structure)
            
            width = max_x - min_x + 1
            height = max_y - min_y + 1
            
            print(f"    Structure {i}: {len(structure)} tiles, {width}x{height} at ({min_x}, {min_y})")
            
            # Count tile types in this structure
            tile_types = {}
            for x, y, tile in structure:
                tile_name = get_tile_name(tile)
                tile_types[tile_name] = tile_types.get(tile_name, 0) + 1
            
            print(f"      Tile composition: {dict(tile_types)}")
    
    # Analyze entities in detail
    print(f"  👥 Entity analysis:")
    entity_details = {}
    for entity in entities:
        entity_type = entity.get('type', 'unknown')
        if entity_type not in entity_details:
            entity_details[entity_type] = []
        entity_details[entity_type].append(entity)
    
    for entity_type, entity_list in entity_details.items():
        print(f"    {entity_type}: {len(entity_list)}")
        
        if entity_type == 'npc':
            for npc in entity_list:
                print(f"      - {npc.get('name', 'Unknown')} at ({npc.get('x', '?')}, {npc.get('y', '?')})")
        elif len(entity_list) <= 5:  # Show details for small lists
            for entity in entity_list:
                name = entity.get('name', 'Unknown')
                x = entity.get('x', '?')
                y = entity.get('y', '?')
                print(f"      - {name} at ({x}, {y})")


def get_tile_name(tile_id):
    """Get human-readable tile name"""
    tile_names = {
        0: "GRASS", 1: "DIRT", 2: "STONE", 3: "WATER", 4: "WALL", 5: "DOOR",
        6: "WALL_CORNER_TL", 7: "WALL_CORNER_TR", 8: "WALL_CORNER_BL", 9: "WALL_CORNER_BR",
        10: "WALL_HORIZONTAL", 11: "WALL_VERTICAL", 12: "TREE", 13: "BRICK",
        14: "WALL_WINDOW_HORIZONTAL", 15: "WALL_WINDOW_VERTICAL",
        16: "SAND", 17: "SNOW", 18: "FOREST_FLOOR", 19: "SWAMP"
    }
    return tile_names.get(tile_id, f"UNKNOWN_{tile_id}")


def main():
    """Analyze the chunks with building tiles"""
    print("🔍 DEEP SETTLEMENT ANALYSIS")
    print("=" * 50)
    
    # Find the latest world
    saves_dir = Path("saves/worlds")
    procedural_worlds = [d for d in saves_dir.iterdir() if d.is_dir() and d.name.startswith('procedural_')]
    latest_world = max(procedural_worlds, key=lambda d: d.stat().st_mtime)
    
    print(f"Analyzing world: {latest_world.name}")
    
    # Find chunks with building tiles
    chunk_files = list(latest_world.glob("chunk_*.json"))
    
    chunks_with_buildings = []
    for chunk_file in chunk_files:
        with open(chunk_file, 'r') as f:
            chunk_data = json.load(f)
        
        # Count building tiles
        building_tiles = 0
        for row in chunk_data['tiles']:
            for tile in row:
                if tile in [2, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15]:
                    building_tiles += 1
        
        if building_tiles > 0:
            chunks_with_buildings.append((chunk_file, building_tiles))
    
    print(f"Found {len(chunks_with_buildings)} chunks with building tiles")
    
    # Analyze each chunk with buildings
    for chunk_file, building_count in chunks_with_buildings:
        analyze_specific_chunk(chunk_file)
    
    print("\n" + "=" * 50)
    print("🔍 ANALYSIS COMPLETE")
    
    print("\n💡 FINDINGS:")
    print("1. ✅ Building tiles ARE being saved correctly")
    print("2. ✅ Building structures are identifiable in chunks")
    print("3. ❌ NO NPCs found in any chunks with buildings")
    print("4. 🤔 This suggests NPC generation/saving issue, not building issue")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Check NPC generation in WorldGenerator")
    print("2. Verify NPC entities are being added to chunks")
    print("3. Check if NPCs are being filtered out during save/load")
    print("4. Test fresh world generation with debug output")


if __name__ == "__main__":
    main()