"""
World generator that creates chunks on-demand with settlement pattern system
"""

import random
import math
from typing import List, Dict, Any, Tuple
from ..procedural_generation.src.biome_generator import BiomeGenerator
from ..procedural_generation.src.enhanced_entity_spawner import EnhancedEntitySpawner
from .chunk import Chunk
from .settlement_manager import ChunkSettlementManager
from .settlement_patterns import SettlementPatternGenerator


class WorldGenerator:
    """
    Generates world chunks on-demand using procedural generation - FIXED VERSION
    """
    
    def __init__(self, world_seed: int):
        """
        Initialize world generator with settlement patterns
        
        Args:
            world_seed: Seed for the entire world
        """
        self.world_seed = world_seed
        self.settlement_manager = ChunkSettlementManager(world_seed)
        self.pattern_generator = SettlementPatternGenerator()
        random.seed(world_seed)
        
    def generate_chunk(self, chunk_x: int, chunk_y: int) -> Chunk:
        """
        Generate a single chunk with settlements as final override step
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate
            
        Returns:
            Generated chunk
        """
        chunk = Chunk(chunk_x, chunk_y, self.world_seed)
        
        # Create chunk-specific seed based on world seed and chunk position
        chunk_seed = hash((self.world_seed, chunk_x, chunk_y)) % (2**31)
        
        print(f"🌍 Generating chunk ({chunk_x}, {chunk_y})...")
        
        # STEP 1: Generate base biomes and tiles
        biome_gen = BiomeGenerator(Chunk.CHUNK_SIZE, Chunk.CHUNK_SIZE, chunk_seed)
        chunk.biomes = biome_gen.generate_biome_map()
        chunk.tiles = biome_gen.generate_tiles(chunk.biomes)
        
        # CRITICAL: Set is_loaded = True so that set_tile() works during pattern application
        chunk.is_loaded = True
        
        print(f"  ✅ Generated base terrain")
        
        # STEP 2: Generate base entities (objects and enemies)
        entity_spawner = EnhancedEntitySpawner(Chunk.CHUNK_SIZE, Chunk.CHUNK_SIZE, chunk_seed)
        
        # Generate objects for this chunk
        try:
            objects = entity_spawner.spawn_objects(chunk.tiles, chunk.biomes, [], None)
            for obj in objects:
                entity_data = {
                    'type': 'object',
                    'name': obj.name if hasattr(obj, 'name') else 'Unknown',
                    'x': obj.x if hasattr(obj, 'x') else 0,
                    'y': obj.y if hasattr(obj, 'y') else 0,
                    'id': f"{obj.name}_{obj.x}_{obj.y}" if hasattr(obj, 'name') and hasattr(obj, 'x') and hasattr(obj, 'y') else f"obj_{len(chunk.entities)}"
                }
                chunk.add_entity(entity_data)
            
            # Generate enemies for this chunk
            enemies = entity_spawner.spawn_enemies(chunk.tiles, chunk.biomes, [], None)
            for enemy in enemies[:10]:
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
            
            print(f"  ✅ Generated {len(objects)} objects and {len(enemies)} enemies")
            
        except Exception as e:
            print(f"  ⚠️  Warning: Entity generation failed: {e}")
        
        # STEP 3: Check if this chunk should have a settlement
        biome_counts = {}
        for y in range(Chunk.CHUNK_SIZE):
            for x in range(Chunk.CHUNK_SIZE):
                biome = chunk.biomes[y][x]
                biome_counts[biome] = biome_counts.get(biome, 0) + 1
        
        settlement_type = self.settlement_manager.should_generate_settlement(chunk_x, chunk_y, biome_counts)
        
        # STEP 4: SETTLEMENT OVERRIDE - This is the final step that clears and replaces everything
        if settlement_type:
            print(f"  🏘️  Generating {settlement_type} settlement (FINAL OVERRIDE STEP)...")
            settlement_data = self.settlement_manager.generate_settlement_in_chunk(chunk_x, chunk_y, settlement_type)
            
            # HARDCORE OVERRIDE: Clear and replace the settlement area completely
            buildings_placed = self._override_area_with_settlement(chunk, settlement_data, settlement_type)
            print(f"  🏗️  Settlement override complete: {buildings_placed} buildings placed")
            
            # Add settlement NPCs after area override
            if 'npcs' in settlement_data:
                start_x, start_y, end_x, end_y = chunk.get_world_bounds()
                npcs_added = 0
                
                for npc_data in settlement_data['npcs']:
                    local_npc_x = npc_data['x'] - start_x
                    local_npc_y = npc_data['y'] - start_y
                    
                    # Ensure NPC is within chunk bounds
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
                
                print(f"  👥 Added {npcs_added} NPCs to settlement")
        else:
            print(f"  ❌ No settlement for chunk ({chunk_x}, {chunk_y})")
        
        chunk.is_generated = True
        chunk.is_loaded = True
        
        print(f"🎉 Chunk ({chunk_x}, {chunk_y}) generation complete!")
        return chunk
    
    def _override_area_with_settlement(self, chunk: Chunk, settlement_data: Dict[str, Any], settlement_type: str) -> int:
        """
        Apply settlement pattern to chunk area with proper tiles and buildings
        
        Args:
            chunk: The chunk to modify
            settlement_data: Settlement data from settlement manager
            settlement_type: Type of settlement (village, town, etc.)
            
        Returns:
            Number of buildings successfully placed
        """
        # Get chunk bounds and settlement info
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        settlement_world_x = settlement_data['world_x']
        settlement_world_y = settlement_data['world_y']
        
        # Convert to local chunk coordinates
        local_settlement_x = settlement_world_x - start_x
        local_settlement_y = settlement_world_y - start_y
        
        print(f"    🏗️  Applying {settlement_type} pattern at local coords ({local_settlement_x}, {local_settlement_y})")
        
        # Get settlement pattern
        base_pattern = self.pattern_generator.get_pattern(settlement_type)
        print(f"    📋 Base pattern: {base_pattern.name} ({base_pattern.width}x{base_pattern.height})")
        
        # Determine dominant biome for pattern adaptation
        dominant_biome = self._get_dominant_biome_in_area(chunk, local_settlement_x, local_settlement_y, 
                                                        base_pattern.width, base_pattern.height)
        
        # Adapt pattern to biome
        settlement_pattern = self.pattern_generator.adapt_pattern_to_biome(base_pattern, dominant_biome)
        
        print(f"    🌍 Using {settlement_pattern.name} pattern adapted for {dominant_biome}")
        print(f"    📐 Pattern size: {settlement_pattern.width}x{settlement_pattern.height} with {len(settlement_pattern.get_building_positions())} buildings")
        
        # Ensure settlement fits in chunk
        if (local_settlement_x + settlement_pattern.width >= Chunk.CHUNK_SIZE or 
            local_settlement_y + settlement_pattern.height >= Chunk.CHUNK_SIZE):
            # Adjust position if needed
            local_settlement_x = max(1, min(Chunk.CHUNK_SIZE - settlement_pattern.width - 1, local_settlement_x))
            local_settlement_y = max(1, min(Chunk.CHUNK_SIZE - settlement_pattern.height - 1, local_settlement_y))
            print(f"    📐 Adjusted settlement position to ({local_settlement_x}, {local_settlement_y})")
        
        # STEP 1: Clear entities from settlement area
        self._clear_settlement_area(chunk, local_settlement_x, local_settlement_y, 
                                  settlement_pattern.width, settlement_pattern.height)
        
        # STEP 2: Apply settlement tile pattern
        buildings_placed = self._apply_settlement_pattern(chunk, settlement_pattern, 
                                                        local_settlement_x, local_settlement_y)
        
        print(f"    ✅ Settlement pattern applied: {buildings_placed} buildings placed")
        return buildings_placed
    
    def _apply_settlement_pattern(self, chunk: Chunk, pattern: 'SettlementPattern', 
                                offset_x: int, offset_y: int) -> int:
        """Apply a settlement pattern to the chunk"""
        
        # Apply tile pattern
        tiles_applied = 0
        for y in range(pattern.height):
            for x in range(pattern.width):
                chunk_x = offset_x + x
                chunk_y = offset_y + y
                
                if 0 <= chunk_x < Chunk.CHUNK_SIZE and 0 <= chunk_y < Chunk.CHUNK_SIZE:
                    tile_type = pattern.get_tile_at(x, y)
                    chunk.set_tile(chunk_x, chunk_y, tile_type)
                    tiles_applied += 1
        
        print(f"      🗺️  Applied {tiles_applied} tiles from pattern")
        
        # Apply buildings from pattern
        buildings_placed = 0
        settlement_random = random.Random(hash((self.world_seed, chunk.chunk_x, chunk.chunk_y, "pattern_buildings")))
        
        for building_info in pattern.get_building_positions():
            building_x = offset_x + building_info['x']
            building_y = offset_y + building_info['y']
            building_width = building_info['width']
            building_height = building_info['height']
            building_type = building_info.get('type', 'house')
            
            # Ensure building fits in chunk
            if (building_x + building_width <= Chunk.CHUNK_SIZE and 
                building_y + building_height <= Chunk.CHUNK_SIZE):
                
                tiles_placed = self._create_building_on_chunk(chunk, building_x, building_y, 
                                                            building_width, building_height, settlement_random)
                
                if tiles_placed > 0:
                    buildings_placed += 1
                    print(f"      🏠 Placed {building_type} ({building_width}x{building_height}) at ({building_x}, {building_y})")
                else:
                    print(f"      ❌ Failed to place {building_type} at ({building_x}, {building_y})")
            else:
                print(f"      ⚠️  Skipped {building_type} - would extend outside chunk")
        
        return buildings_placed
    
    def _get_dominant_biome_in_area(self, chunk: Chunk, x: int, y: int, width: int, height: int) -> str:
        """Get the dominant biome in a specific area"""
        biome_counts = {}
        
        for dy in range(height):
            for dx in range(width):
                check_x = x + dx
                check_y = y + dy
                if 0 <= check_x < Chunk.CHUNK_SIZE and 0 <= check_y < Chunk.CHUNK_SIZE:
                    biome = chunk.biomes[check_y][check_x]
                    biome_counts[biome] = biome_counts.get(biome, 0) + 1
        
        return max(biome_counts.keys(), key=lambda k: biome_counts[k]) if biome_counts else "PLAINS"
    
    def _clear_settlement_area(self, chunk: Chunk, x: int, y: int, width: int, height: int):
        """Clear all entities from the settlement area"""
        # Remove any entities that fall within the settlement area
        entities_to_remove = []
        
        for entity in chunk.entities:
            entity_x = entity.get('x', 0)
            entity_y = entity.get('y', 0)
            
            # Check if entity is within settlement bounds
            if (x <= entity_x < x + width and y <= entity_y < y + height):
                entities_to_remove.append(entity)
        
        # Remove the entities
        for entity in entities_to_remove:
            chunk.entities.remove(entity)
        
        print(f"    🧹 Cleared {len(entities_to_remove)} entities from settlement area")
    
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
