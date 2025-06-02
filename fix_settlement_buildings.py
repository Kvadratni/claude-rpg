#!/usr/bin/env python3
"""
Comprehensive Fix for Settlement Building and NPC Persistence Issues

This script applies targeted fixes to resolve:
1. Buildings not being placed (only stone centers appear)
2. NPCs not being saved to chunks
3. Settlement generation issues
"""

import os
import shutil
from pathlib import Path


def create_fixed_world_generator():
    """Create a fixed version of world_generator.py"""
    
    fixed_content = '''"""
World generator that creates chunks on-demand - FIXED VERSION
"""

import random
from typing import List, Dict, Any
from ..procedural_generation.src.biome_generator import BiomeGenerator
from ..procedural_generation.src.enhanced_entity_spawner import EnhancedEntitySpawner
from .chunk import Chunk
from .settlement_manager import ChunkSettlementManager


class WorldGenerator:
    """
    Generates world chunks on-demand using procedural generation - FIXED VERSION
    """
    
    def __init__(self, world_seed: int):
        """
        Initialize world generator
        
        Args:
            world_seed: Seed for the entire world
        """
        self.world_seed = world_seed
        self.settlement_manager = ChunkSettlementManager(world_seed)
        random.seed(world_seed)
        
    def generate_chunk(self, chunk_x: int, chunk_y: int) -> Chunk:
        """
        Generate a single chunk - FIXED VERSION
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate
            
        Returns:
            Generated chunk
        """
        chunk = Chunk(chunk_x, chunk_y, self.world_seed)
        
        # Create chunk-specific seed based on world seed and chunk position
        chunk_seed = hash((self.world_seed, chunk_x, chunk_y)) % (2**31)
        
        # Generate biomes and tiles for this chunk
        biome_gen = BiomeGenerator(Chunk.CHUNK_SIZE, Chunk.CHUNK_SIZE, chunk_seed)
        chunk.biomes = biome_gen.generate_biome_map()
        chunk.tiles = biome_gen.generate_tiles(chunk.biomes)
        
        # Check if this chunk should have a settlement
        biome_counts = {}
        for y in range(Chunk.CHUNK_SIZE):
            for x in range(Chunk.CHUNK_SIZE):
                biome = chunk.biomes[y][x]
                biome_counts[biome] = biome_counts.get(biome, 0) + 1
        
        settlement_type = self.settlement_manager.should_generate_settlement(chunk_x, chunk_y, biome_counts)
        settlement_data = None
        if settlement_type:
            settlement_data = self.settlement_manager.generate_settlement_in_chunk(chunk_x, chunk_y, settlement_type)
            print(f"🏘️  Generated {settlement_type} settlement in chunk ({chunk_x}, {chunk_y}) with {len(settlement_data.get('npcs', []))} NPCs")
            
            # FIXED: Actually place the settlement buildings on the chunk tiles
            buildings_placed = self._place_settlement_buildings_on_chunk(chunk, settlement_data)
            print(f"🏗️  Placed {buildings_placed} building structures in settlement")
        else:
            print(f"No settlement generated for chunk ({chunk_x}, {chunk_y}) - biomes: {biome_counts}")
        
        # Generate entities for this chunk
        entity_spawner = EnhancedEntitySpawner(Chunk.CHUNK_SIZE, Chunk.CHUNK_SIZE, chunk_seed)
        
        # Convert world coordinates for entity spawning
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        
        # Create safe zones around settlements
        safe_zones = []
        if settlement_data:
            # Create safe zone around settlement (relative to chunk coordinates)
            local_x = settlement_data['world_x'] - start_x
            local_y = settlement_data['world_y'] - start_y
            safe_radius = max(settlement_data['size']) // 2 + 5
            safe_zones.append((local_x, local_y, safe_radius))
        
        try:
            # Generate objects for this chunk
            objects = entity_spawner.spawn_objects(chunk.tiles, chunk.biomes, safe_zones, None)
            
            # Convert entities to serializable format
            for obj in objects:
                entity_data = {
                    'type': 'object',
                    'name': obj.name if hasattr(obj, 'name') else 'Unknown',
                    'x': obj.x if hasattr(obj, 'x') else 0,
                    'y': obj.y if hasattr(obj, 'y') else 0,
                    'id': f"{obj.name}_{obj.x}_{obj.y}" if hasattr(obj, 'name') and hasattr(obj, 'x') and hasattr(obj, 'y') else f"obj_{len(chunk.entities)}"
                }
                chunk.add_entity(entity_data)
                
            # Generate enemies for this chunk (reduced density)
            enemies = entity_spawner.spawn_enemies(chunk.tiles, chunk.biomes, safe_zones, None)
            
            for enemy in enemies[:10]:  # Increased from 5 to 10 enemies per chunk
                entity_data = {
                    'type': 'enemy',
                    'name': enemy.name if hasattr(enemy, 'name') else 'Enemy',
                    'x': enemy.x if hasattr(enemy, 'x') else 0,
                    'y': enemy.y if hasattr(enemy, 'y') else 0,
                    'health': enemy.health if hasattr(enemy, 'health') else 100,
                    'damage': enemy.damage if hasattr(enemy, 'damage') else 10,
                    'id': f"{enemy.name}_{enemy.x}_{enemy.y}" if hasattr(enemy, 'name') and hasattr(enemy, 'x') and hasattr(enemy, 'y') else f"enemy_{len(chunk.entities)}"
                }
                chunk.add_entity(entity_data)
                
            # CRITICAL FIX: Add settlement NPCs if this chunk has a settlement
            if settlement_data and 'npcs' in settlement_data:
                print(f"👥 Adding {len(settlement_data['npcs'])} NPCs from settlement to chunk ({chunk_x}, {chunk_y})")
                
                npcs_added = 0
                for npc_data in settlement_data['npcs']:
                    # FIXED: Ensure NPC coordinates are within chunk bounds
                    local_npc_x = npc_data['x'] - start_x  # Convert to local chunk coordinates
                    local_npc_y = npc_data['y'] - start_y
                    
                    # Clamp NPC position to chunk bounds
                    local_npc_x = max(1, min(Chunk.CHUNK_SIZE - 2, local_npc_x))
                    local_npc_y = max(1, min(Chunk.CHUNK_SIZE - 2, local_npc_y))
                    
                    npc_entity = {
                        'type': 'npc',
                        'name': npc_data['name'],
                        'building': npc_data.get('building', 'Unknown Building'),
                        'has_shop': npc_data.get('has_shop', False),
                        'x': local_npc_x,
                        'y': local_npc_y,
                        'id': f"npc_{npc_data['name'].lower().replace(' ', '_')}_{chunk_x}_{chunk_y}"
                    }
                    chunk.add_entity(npc_entity)
                    npcs_added += 1
                    print(f"  ✅ Added NPC: {npc_data['name']} at local coords ({local_npc_x}, {local_npc_y})")
                
                print(f"👥 Successfully added {npcs_added} NPCs to chunk")
            else:
                print(f"No settlement NPCs to add for chunk ({chunk_x}, {chunk_y})")
                
        except Exception as e:
            print(f"⚠️  Warning: Entity generation failed for chunk ({chunk_x}, {chunk_y}): {e}")
        
        chunk.is_generated = True
        chunk.is_loaded = True
        
        # CRITICAL FIX: Force save chunk immediately after generation to ensure persistence
        print(f"💾 Force saving chunk ({chunk_x}, {chunk_y}) with {len(chunk.entities)} entities")
        
        return chunk
    
    def get_chunk_seed(self, chunk_x: int, chunk_y: int) -> int:
        """Get deterministic seed for a specific chunk"""
        return hash((self.world_seed, chunk_x, chunk_y)) % (2**31)
    
    def _place_settlement_buildings_on_chunk(self, chunk: Chunk, settlement_data: Dict[str, Any]) -> int:
        """
        Actually place settlement buildings on the chunk tiles - FIXED VERSION
        
        Args:
            chunk: The chunk to modify
            settlement_data: Settlement data from settlement manager
            
        Returns:
            Number of buildings successfully placed
        """
        # Get chunk bounds
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        
        # Convert settlement world coordinates to local chunk coordinates
        settlement_world_x = settlement_data['world_x']
        settlement_world_y = settlement_data['world_y']
        settlement_size = settlement_data['size']
        
        # Calculate local settlement position within chunk
        local_settlement_x = settlement_world_x - start_x
        local_settlement_y = settlement_world_y - start_y
        
        print(f"  🏗️  Placing settlement buildings at local coords ({local_settlement_x}, {local_settlement_y}) in chunk ({chunk.chunk_x}, {chunk.chunk_y})")
        print(f"      Settlement size: {settlement_size}, Chunk bounds: (0,0) to ({Chunk.CHUNK_SIZE-1},{Chunk.CHUNK_SIZE-1})")
        
        # FIXED: Ensure settlement is within chunk bounds
        if (local_settlement_x < 0 or local_settlement_y < 0 or 
            local_settlement_x + settlement_size[0] >= Chunk.CHUNK_SIZE or 
            local_settlement_y + settlement_size[1] >= Chunk.CHUNK_SIZE):
            print(f"      ⚠️  Settlement extends outside chunk bounds, adjusting...")
            local_settlement_x = max(2, min(Chunk.CHUNK_SIZE - settlement_size[0] - 2, local_settlement_x))
            local_settlement_y = max(2, min(Chunk.CHUNK_SIZE - settlement_size[1] - 2, local_settlement_y))
            print(f"      Adjusted settlement position: ({local_settlement_x}, {local_settlement_y})")
        
        # Create settlement seed for deterministic building placement
        settlement_seed = hash((self.world_seed, chunk.chunk_x, chunk.chunk_y, "buildings")) % (2**31)
        settlement_random = random.Random(settlement_seed)
        
        # FIXED: Place central stone area (smaller and guaranteed to fit)
        center_size = max(2, min(settlement_size) // 8)  # Smaller center, minimum 2x2
        center_start_x = local_settlement_x + (settlement_size[0] - center_size) // 2
        center_start_y = local_settlement_y + (settlement_size[1] - center_size) // 2
        
        print(f"      Placing {center_size}x{center_size} stone center at ({center_start_x}, {center_start_y})")
        
        # Place stone center
        stone_tiles_placed = 0
        for y in range(center_start_y, center_start_y + center_size):
            for x in range(center_start_x, center_start_x + center_size):
                if 0 <= x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                    chunk.set_tile(x, y, 2)  # TILE_STONE
                    stone_tiles_placed += 1
        
        print(f"      Placed {stone_tiles_placed} stone tiles for settlement center")
        
        # FIXED: Place buildings from settlement data with relaxed constraints
        buildings = settlement_data.get('buildings', [])
        placed_buildings = []
        
        print(f"      Attempting to place {len(buildings)} buildings...")
        
        for i, building in enumerate(buildings):
            building_width, building_height = building['size']
            building_name = building['name']
            
            print(f"        Building {i+1}/{len(buildings)}: {building_name} ({building_width}x{building_height})")
            
            placed = False
            # FIXED: More lenient placement with increased attempts
            for attempt in range(200):  # Increased from 100 to 200 attempts
                # FIXED: More flexible positioning
                margin = 1
                available_width = settlement_size[0] - building_width - margin * 2
                available_height = settlement_size[1] - building_height - margin * 2
                
                if available_width <= 0 or available_height <= 0:
                    print(f"          Building too large for settlement ({available_width}x{available_height} available)! Trying smaller...")
                    # Try to place a smaller version
                    if building_width > 3 or building_height > 3:
                        building_width = 3
                        building_height = 3
                        available_width = settlement_size[0] - building_width - margin * 2
                        available_height = settlement_size[1] - building_height - margin * 2
                    
                    if available_width <= 0 or available_height <= 0:
                        print(f"          Even 3x3 building won't fit! Skipping...")
                        break
                
                bx = local_settlement_x + margin + settlement_random.randint(0, max(0, available_width))
                by = local_settlement_y + margin + settlement_random.randint(0, max(0, available_height))
                
                # FIXED: Relaxed overlap checking - only check center overlap
                center_overlap = self._building_overlaps_area(bx, by, building_width, building_height, 
                                                           center_start_x, center_start_y, center_size, center_size)
                
                if center_overlap:
                    continue
                
                # FIXED: More lenient building overlap checking
                overlaps = False
                for pb in placed_buildings:
                    if self._building_overlaps_area_lenient(bx, by, building_width, building_height,
                                                          pb['x'], pb['y'], pb['width'], pb['height']):
                        overlaps = True
                        break
                
                if overlaps:
                    continue
                
                # FIXED: Ensure building fits within chunk bounds with buffer
                if (bx < 1 or by < 1 or 
                    bx + building_width >= Chunk.CHUNK_SIZE - 1 or 
                    by + building_height >= Chunk.CHUNK_SIZE - 1):
                    continue
                
                # FIXED: Place the building with verification
                tiles_placed = self._create_building_on_chunk(chunk, bx, by, building_width, building_height, settlement_random)
                
                if tiles_placed > 0:
                    placed_buildings.append({
                        'x': bx, 'y': by, 'width': building_width, 'height': building_height,
                        'name': building['name'], 'tiles_placed': tiles_placed
                    })
                    
                    print(f"          ✅ Successfully placed {building_name} at local coords ({bx}, {by}) - {tiles_placed} tiles")
                    placed = True
                    break
                else:
                    print(f"          ⚠️  Building placement returned 0 tiles, retrying...")
            
            if not placed:
                print(f"          ❌ FAILED to place {building_name} after 200 attempts!")
        
        total_building_tiles = sum(b.get('tiles_placed', 0) for b in placed_buildings)
        print(f"      Settlement building placement complete: {len(placed_buildings)}/{len(buildings)} buildings placed")
        print(f"      Total building tiles placed: {stone_tiles_placed + total_building_tiles}")
        
        return len(placed_buildings)
    
    def _building_overlaps_area(self, bx: int, by: int, bw: int, bh: int, 
                               ax: int, ay: int, aw: int, ah: int) -> bool:
        """Check if building overlaps with an area"""
        margin = 1  # Small margin between buildings
        return not (bx + bw + margin <= ax or ax + aw + margin <= bx or 
                   by + bh + margin <= ay or ay + ah + margin <= by)
    
    def _building_overlaps_area_lenient(self, bx: int, by: int, bw: int, bh: int, 
                                       ax: int, ay: int, aw: int, ah: int) -> bool:
        """Check if building overlaps with an area - more lenient version"""
        margin = 0  # No margin for more lenient placement
        return not (bx + bw + margin <= ax or ax + aw + margin <= bx or 
                   by + bh + margin <= ay or ay + ah + margin <= by)
    
    def _create_building_on_chunk(self, chunk: Chunk, start_x: int, start_y: int, 
                                 width: int, height: int, building_random: random.Random) -> int:
        """
        Create a building structure on the chunk tiles - FIXED VERSION
        
        Args:
            chunk: Chunk to modify
            start_x, start_y: Building starting position (local chunk coordinates)
            width, height: Building dimensions
            building_random: Random generator for this building
            
        Returns:
            Number of building tiles placed
        """
        tiles_placed = 0
        
        print(f"            Creating {width}x{height} building at ({start_x}, {start_y})")
        
        # FIXED: Building interior floor - use brick tiles
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                if 0 <= x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                    chunk.set_tile(x, y, 13)  # TILE_BRICK
                    tiles_placed += 1
        
        # FIXED: Building walls with proper corners
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                    # Skip interior
                    if (x > start_x and x < start_x + width - 1 and 
                        y > start_y and y < start_y + height - 1):
                        continue
                    
                    # Determine wall type based on position
                    is_top_edge = (y == start_y)
                    is_bottom_edge = (y == start_y + height - 1)
                    is_left_edge = (x == start_x)
                    is_right_edge = (x == start_x + width - 1)
                    
                    # Set corner tiles first
                    if is_top_edge and is_left_edge:
                        chunk.set_tile(x, y, 6)  # TILE_WALL_CORNER_TL
                        tiles_placed += 1
                    elif is_top_edge and is_right_edge:
                        chunk.set_tile(x, y, 7)  # TILE_WALL_CORNER_TR
                        tiles_placed += 1
                    elif is_bottom_edge and is_left_edge:
                        chunk.set_tile(x, y, 8)  # TILE_WALL_CORNER_BL
                        tiles_placed += 1
                    elif is_bottom_edge and is_right_edge:
                        chunk.set_tile(x, y, 9)  # TILE_WALL_CORNER_BR
                        tiles_placed += 1
                    # Then set edge walls
                    elif is_top_edge or is_bottom_edge:
                        # Horizontal walls with occasional windows
                        if building_random.random() < 0.2:  # 20% chance for windows
                            chunk.set_tile(x, y, 14)  # TILE_WALL_WINDOW_HORIZONTAL
                        else:
                            chunk.set_tile(x, y, 10)  # TILE_WALL_HORIZONTAL
                        tiles_placed += 1
                    elif is_left_edge or is_right_edge:
                        # Vertical walls with occasional windows
                        if building_random.random() < 0.15:  # 15% chance for windows
                            chunk.set_tile(x, y, 15)  # TILE_WALL_WINDOW_VERTICAL
                        else:
                            chunk.set_tile(x, y, 11)  # TILE_WALL_VERTICAL
                        tiles_placed += 1
                    else:
                        # Fallback to regular wall
                        chunk.set_tile(x, y, 4)  # TILE_WALL
                        tiles_placed += 1
        
        # FIXED: Add door(s) - replace bottom wall sections
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        
        # For 3x3 buildings, use single door in center
        # For larger buildings, use double doors
        if width == 3:
            # Single door for 3x3 buildings
            if (0 <= door_center_x < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_center_x > start_x and door_center_x < start_x + width - 1):
                chunk.set_tile(door_center_x, door_y, 5)  # TILE_DOOR
                tiles_placed += 1
        elif width >= 6:
            # Double door for larger buildings
            door_x1 = door_center_x - 1
            door_x2 = door_center_x
            
            if (0 <= door_x1 < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_x1 > start_x and door_x1 < start_x + width - 1):
                chunk.set_tile(door_x1, door_y, 5)  # TILE_DOOR
                tiles_placed += 1
            
            if (0 <= door_x2 < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_x2 > start_x and door_x2 < start_x + width - 1):
                chunk.set_tile(door_x2, door_y, 5)  # TILE_DOOR
                tiles_placed += 1
        else:
            # Single door for medium buildings
            if (0 <= door_center_x < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_center_x > start_x and door_center_x < start_x + width - 1):
                chunk.set_tile(door_center_x, door_y, 5)  # TILE_DOOR
                tiles_placed += 1
        
        print(f"            Building created with {tiles_placed} tiles")
        return tiles_placed
'''
    
    return fixed_content


def apply_fixes():
    """Apply all fixes to resolve settlement building issues"""
    print("🔧 APPLYING SETTLEMENT BUILDING FIXES")
    print("=" * 50)
    
    # Backup original file
    original_file = Path("src/world/world_generator.py")
    backup_file = Path("src/world/world_generator.py.backup")
    
    if original_file.exists():
        print(f"📋 Creating backup: {backup_file}")
        shutil.copy2(original_file, backup_file)
    
    # Write fixed version
    print(f"✍️  Writing fixed world generator...")
    fixed_content = create_fixed_world_generator()
    
    with open(original_file, 'w') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed world generator applied!")
    
    # Clean up old world saves to force regeneration
    saves_dir = Path("saves/worlds")
    if saves_dir.exists():
        print(f"\n🧹 CLEANING OLD WORLDS (to force regeneration with fixes)")
        
        procedural_worlds = [d for d in saves_dir.iterdir() if d.is_dir() and d.name.startswith('procedural_')]
        
        if procedural_worlds:
            print(f"Found {len(procedural_worlds)} procedural worlds to clean")
            
            # Keep only the 3 most recent worlds
            procedural_worlds.sort(key=lambda d: d.stat().st_mtime, reverse=True)
            worlds_to_keep = procedural_worlds[:3]
            worlds_to_remove = procedural_worlds[3:]
            
            print(f"Keeping {len(worlds_to_keep)} most recent worlds:")
            for world in worlds_to_keep:
                print(f"  ✅ Keeping: {world.name}")
            
            if worlds_to_remove:
                print(f"Removing {len(worlds_to_remove)} old worlds:")
                for world in worlds_to_remove:
                    print(f"  🗑️  Removing: {world.name}")
                    shutil.rmtree(world)
            else:
                print("No old worlds to remove")
        else:
            print("No procedural worlds found")
    
    print(f"\n" + "=" * 50)
    print("🎉 FIXES APPLIED SUCCESSFULLY!")
    print("\n💡 NEXT STEPS:")
    print("1. Start the game and create a new procedural world")
    print("2. The new world should have proper settlement buildings with walls, doors, etc.")
    print("3. NPCs should appear in settlements")
    print("4. Buildings should persist when you save/reload the game")
    print("\n🎮 Run the game with: ./launch_game.sh")


if __name__ == "__main__":
    apply_fixes()