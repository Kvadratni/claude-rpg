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
from .enhanced_settlement_generator import EnhancedSettlementGenerator
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
        self.enhanced_settlement_generator = EnhancedSettlementGenerator(world_seed)  # Add enhanced generator
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
        
        # STEP 4: SETTLEMENT OVERRIDE - Use Enhanced Settlement Generator with Building Templates
        if settlement_type:
            print(f"  🏘️  Generating {settlement_type} settlement using building templates...")
            
            # Use the enhanced settlement generator which supports building templates
            dominant_biome = max(biome_counts.items(), key=lambda x: x[1])[0].lower()
            settlement_data = self.enhanced_settlement_generator.generate_settlement(
                chunk_x, chunk_y, settlement_type, dominant_biome
            )
            
            # Calculate local settlement coordinates
            start_x, start_y, end_x, end_y = chunk.get_world_bounds()
            settlement_world_x = settlement_data['world_x']
            settlement_world_y = settlement_data['world_y']
            local_settlement_x = settlement_world_x - start_x
            local_settlement_y = settlement_world_y - start_y
            
            # Apply pathways from settlement data FIRST
            pathways_applied = self._apply_pathways_to_chunk(chunk, settlement_data, local_settlement_x, local_settlement_y)
            print(f"  🛤️  Applied {pathways_applied} pathway tiles")
            
            # Apply central feature from settlement data SECOND
            central_feature_applied = self._apply_central_feature_to_chunk(chunk, settlement_data, local_settlement_x, local_settlement_y)
            if central_feature_applied:
                print(f"  🏛️  Applied central feature: {settlement_data.get('central_feature', {}).get('type', 'unknown')}")
            
            # Apply building templates to the chunk THIRD
            buildings_placed = self._apply_building_templates_to_chunk(chunk, settlement_data, local_settlement_x, local_settlement_y)
            print(f"  🏗️  Applied {buildings_placed} building templates to chunk")
            
            # Spawn furniture from building templates
            furniture_spawned = self._spawn_furniture_from_templates(chunk, settlement_data, local_settlement_x, local_settlement_y)
            print(f"  🪑 Spawned {furniture_spawned} furniture pieces from templates")
            
            # Add NPCs from building templates
            if 'npcs' in settlement_data:
                npcs_added = 0
                for npc_data in settlement_data['npcs']:
                    # Convert settlement-relative coordinates to local chunk coordinates
                    local_npc_x = local_settlement_x + npc_data['x']
                    local_npc_y = local_settlement_y + npc_data['y']
                    
                    # Ensure NPC is within chunk bounds
                    if 0 <= local_npc_x < Chunk.CHUNK_SIZE and 0 <= local_npc_y < Chunk.CHUNK_SIZE:
                        npc_entity = {
                            'type': 'npc',
                            'name': npc_data['name'],
                            'building': npc_data.get('building', 'Unknown Building'),
                            'building_type': npc_data.get('building_type', 'generic'),
                            'has_shop': npc_data.get('has_shop', False),
                            'importance': npc_data.get('importance', 'medium'),
                            'template_spawn': npc_data.get('template_spawn', False),
                            'ai_ready': True,  # Enable AI for template NPCs
                            'x': local_npc_x,
                            'y': local_npc_y,
                            'world_x': start_x + local_npc_x,
                            'world_y': start_y + local_npc_y,
                            'id': f"npc_{npc_data['name'].lower().replace(' ', '_')}_{chunk_x}_{chunk_y}",
                            'dialog': npc_data.get('dialog', [])
                        }
                        chunk.add_entity(npc_entity)
                        npcs_added += 1
                        print(f"    👤 Placed {npc_data['name']} from template at ({local_npc_x}, {local_npc_y})")
                
                print(f"  👥 Added {npcs_added} NPCs from building templates")
        else:
            print(f"  ❌ No settlement for chunk ({chunk_x}, {chunk_y})")
        
        chunk.is_generated = True
        chunk.is_loaded = True
        
        print(f"🎉 Chunk ({chunk_x}, {chunk_y}) generation complete!")
        return chunk
    
    def _apply_building_templates_to_chunk(self, chunk: Chunk, settlement_data: Dict[str, Any], 
                                         local_x: int, local_y: int) -> int:
        """
        Apply building templates from settlement data to the chunk
        
        Args:
            chunk: The chunk to modify
            settlement_data: Settlement data from enhanced generator
            local_x, local_y: Local settlement position in chunk
            
        Returns:
            Number of buildings successfully placed
        """
        buildings_placed = 0
        
        # Clear the settlement area first (but preserve some base terrain)
        settlement_width = settlement_data.get('width', 20)
        settlement_height = settlement_data.get('height', 20)
        self._clear_settlement_area_selectively(chunk, local_x, local_y, settlement_width, settlement_height)
        
        # Apply each building template
        for building_data in settlement_data.get('buildings', []):
            # building_data['x'] and ['y'] are already world coordinates from _building_to_dict
            # Convert directly to chunk coordinates
            start_x, start_y, end_x, end_y = chunk.get_world_bounds()
            chunk_x = building_data['x'] - start_x
            chunk_y = building_data['y'] - start_y
            
            # Ensure building fits in chunk
            building_width = building_data['width']
            building_height = building_data['height']
            
            if (chunk_x + building_width <= Chunk.CHUNK_SIZE and 
                chunk_y + building_height <= Chunk.CHUNK_SIZE and
                chunk_x >= 0 and chunk_y >= 0):
                
                # Apply building template tiles
                building_tiles = building_data.get('tiles', [])
                if building_tiles:
                    tiles_placed = self._apply_building_template_tiles(
                        chunk, chunk_x, chunk_y, building_tiles
                    )
                    if tiles_placed > 0:
                        buildings_placed += 1
                        print(f"    🏠 Applied {building_data['template_name']} template at ({chunk_x}, {chunk_y}) - {tiles_placed} tiles")
                else:
                    # Fallback to basic building if no template tiles
                    settlement_random = random.Random(hash((self.world_seed, chunk.chunk_x, chunk.chunk_y, building_data['template_name'])))
                    tiles_placed = self._create_building_on_chunk(chunk, chunk_x, chunk_y, 
                                                                building_width, building_height, settlement_random)
                    if tiles_placed > 0:
                        buildings_placed += 1
                        print(f"    🏠 Created fallback building at ({chunk_x}, {chunk_y}) - {tiles_placed} tiles")
        
        return buildings_placed
    
    def _spawn_furniture_from_templates(self, chunk: Chunk, settlement_data: Dict[str, Any], 
                                      local_x: int, local_y: int) -> int:
        """
        Spawn furniture from building templates
        
        Args:
            chunk: The chunk to add furniture to
            settlement_data: Settlement data from enhanced generator
            local_x, local_y: Local settlement position in chunk
            
        Returns:
            Number of furniture pieces spawned
        """
        furniture_spawned = 0
        
        # Get chunk bounds for coordinate conversion
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        
        # Process each building's furniture
        for building_data in settlement_data.get('buildings', []):
            # building_data['x'] and ['y'] are world coordinates
            # Convert to chunk coordinates
            chunk_building_x = building_data['x'] - start_x
            chunk_building_y = building_data['y'] - start_y
            
            # Get furniture positions from building template
            furniture_positions = building_data.get('furniture_positions', [])
            
            for furniture_pos in furniture_positions:
                if len(furniture_pos) >= 3:
                    rel_x, rel_y, furniture_type = furniture_pos[:3]
                    
                    # Calculate world position
                    world_x = building_data['x'] + rel_x
                    world_y = building_data['y'] + rel_y
                    
                    # Convert to chunk-local coordinates
                    local_furniture_x = world_x - start_x
                    local_furniture_y = world_y - start_y
                    
                    # Ensure furniture is within chunk bounds
                    if (0 <= local_furniture_x < Chunk.CHUNK_SIZE and 
                        0 <= local_furniture_y < Chunk.CHUNK_SIZE):
                        
                        # Create furniture entity data
                        furniture_entity = {
                            'type': 'furniture',
                            'furniture_type': furniture_type,
                            'x': local_furniture_x,
                            'y': local_furniture_y,
                            'world_x': world_x,
                            'world_y': world_y,
                            'id': f"furniture_{furniture_type}_{world_x}_{world_y}",
                            'template_spawn': True
                        }
                        
                        # Add to chunk entities
                        chunk.add_entity(furniture_entity)
                        furniture_spawned += 1
                        print(f"    🪑 Spawned {furniture_type} at chunk ({local_furniture_x}, {local_furniture_y}) / world ({world_x}, {world_y})")
        
        return furniture_spawned
    
    def _apply_pathways_to_chunk(self, chunk: Chunk, settlement_data: Dict[str, Any], 
                                local_x: int, local_y: int) -> int:
        """
        Apply pathways from settlement data to the chunk
        
        Args:
            chunk: The chunk to modify
            settlement_data: Settlement data from enhanced generator
            local_x, local_y: Local settlement position in chunk
            
        Returns:
            Number of pathway tiles applied
        """
        pathways_applied = 0
        
        # Get chunk bounds for coordinate conversion
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        
        # Get pathways from settlement data
        pathways = settlement_data.get('pathways', [])
        
        for pathway_x, pathway_y in pathways:
            # Convert settlement-relative coordinates to world coordinates
            world_x = settlement_data['world_x'] + pathway_x
            world_y = settlement_data['world_y'] + pathway_y
            
            # Convert to chunk-local coordinates
            local_pathway_x = world_x - start_x
            local_pathway_y = world_y - start_y
            
            # Ensure pathway is within chunk bounds
            if (0 <= local_pathway_x < Chunk.CHUNK_SIZE and 
                0 <= local_pathway_y < Chunk.CHUNK_SIZE):
                
                # Apply pathway tile (use stone for pathways)
                chunk.set_tile(local_pathway_x, local_pathway_y, 2)  # TILE_STONE
                pathways_applied += 1
        
        return pathways_applied
    
    def _apply_central_feature_to_chunk(self, chunk: Chunk, settlement_data: Dict[str, Any], 
                                      local_x: int, local_y: int) -> bool:
        """
        Apply central feature from settlement data to the chunk
        
        Args:
            chunk: The chunk to modify
            settlement_data: Settlement data from enhanced generator
            local_x, local_y: Local settlement position in chunk
            
        Returns:
            True if central feature was applied, False otherwise
        """
        central_feature = settlement_data.get('central_feature')
        if not central_feature:
            return False
        
        # Get chunk bounds for coordinate conversion
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        
        # Convert settlement-relative coordinates to world coordinates
        feature_world_x = settlement_data['world_x'] + central_feature['x']
        feature_world_y = settlement_data['world_y'] + central_feature['y']
        
        # Convert to chunk-local coordinates
        local_feature_x = feature_world_x - start_x
        local_feature_y = feature_world_y - start_y
        
        feature_width = central_feature['width']
        feature_height = central_feature['height']
        feature_type = central_feature['type']
        
        # Apply central feature tiles
        tiles_applied = 0
        for y in range(feature_height):
            for x in range(feature_width):
                chunk_x = local_feature_x + x
                chunk_y = local_feature_y + y
                
                # Ensure within chunk bounds
                if (0 <= chunk_x < Chunk.CHUNK_SIZE and 
                    0 <= chunk_y < Chunk.CHUNK_SIZE):
                    
                    # Choose tile type based on feature type
                    if feature_type == 'plaza':
                        chunk.set_tile(chunk_x, chunk_y, 2)  # TILE_STONE
                    elif feature_type == 'well':
                        chunk.set_tile(chunk_x, chunk_y, 3)  # TILE_WATER
                    elif feature_type == 'market':
                        chunk.set_tile(chunk_x, chunk_y, 13)  # TILE_BRICK
                    elif feature_type == 'fire_pit':
                        chunk.set_tile(chunk_x, chunk_y, 1)  # TILE_DIRT
                    else:
                        chunk.set_tile(chunk_x, chunk_y, 2)  # Default to stone
                    
                    tiles_applied += 1
        
        return tiles_applied > 0
    
    def _apply_building_template_tiles(self, chunk: Chunk, start_x: int, start_y: int, 
                                     template_tiles: List[List[int]]) -> int:
        """
        Apply building template tiles to the chunk with improved wall mapping
        
        Args:
            chunk: Chunk to modify
            start_x, start_y: Starting position for the building
            template_tiles: 2D array of tile types from template
            
        Returns:
            Number of tiles placed
        """
        tiles_placed = 0
        template_height = len(template_tiles)
        template_width = len(template_tiles[0]) if template_tiles else 0
        
        for y, row in enumerate(template_tiles):
            for x, tile_value in enumerate(row):
                chunk_x = start_x + x
                chunk_y = start_y + y
                
                if (0 <= chunk_x < Chunk.CHUNK_SIZE and 
                    0 <= chunk_y < Chunk.CHUNK_SIZE and
                    tile_value != 0):  # Don't place empty tiles
                    
                    # Map template tile types to chunk tile types with position awareness
                    chunk_tile_type = self._map_template_tile_to_chunk_tile_with_position(
                        tile_value, x, y, template_width, template_height
                    )
                    chunk.set_tile(chunk_x, chunk_y, chunk_tile_type)
                    tiles_placed += 1
        
        return tiles_placed
    
    def _map_template_tile_to_chunk_tile_with_position(self, template_tile: int, x: int, y: int, 
                                                      width: int, height: int) -> int:
        """
        Map building template tile types to chunk tile types with position awareness
        
        Template tile types:
        0 = EMPTY, 1 = WALL, 2 = DOOR, 3 = FLOOR, 4 = FURNITURE, 5 = NPC_SPAWN, 6 = WINDOW
        
        Chunk tile types (improved mapping):
        4 = TILE_WALL, 5 = TILE_DOOR, 6-9 = TILE_WALL_CORNER_*, 10-11 = TILE_WALL_H/V, 13 = TILE_BRICK, 14/15 = TILE_WALL_WINDOW_*
        """
        if template_tile == 0:
            return 0  # EMPTY
        elif template_tile == 1:  # WALL - use position-aware mapping
            # Determine position within building
            is_top_edge = (y == 0)
            is_bottom_edge = (y == height - 1)
            is_left_edge = (x == 0)
            is_right_edge = (x == width - 1)
            
            # Map to appropriate wall tile based on position
            if is_top_edge and is_left_edge:
                return 6  # TILE_WALL_CORNER_TL
            elif is_top_edge and is_right_edge:
                return 7  # TILE_WALL_CORNER_TR
            elif is_bottom_edge and is_left_edge:
                return 8  # TILE_WALL_CORNER_BL
            elif is_bottom_edge and is_right_edge:
                return 9  # TILE_WALL_CORNER_BR
            elif is_top_edge or is_bottom_edge:
                return 10  # TILE_WALL_HORIZONTAL
            elif is_left_edge or is_right_edge:
                return 11  # TILE_WALL_VERTICAL
            else:
                return 4  # TILE_WALL (interior wall)
        elif template_tile == 2:
            return 5  # DOOR -> TILE_DOOR
        elif template_tile == 3:
            return 13  # FLOOR -> TILE_BRICK
        elif template_tile == 4:
            return 13  # FURNITURE -> TILE_BRICK (furniture rendered separately)
        elif template_tile == 5:
            return 13  # NPC_SPAWN -> TILE_BRICK (NPC placed separately)
        elif template_tile == 6:  # WINDOW - use position-aware mapping
            # Determine if this is a horizontal or vertical wall
            is_top_edge = (y == 0)
            is_bottom_edge = (y == height - 1)
            is_left_edge = (x == 0)
            is_right_edge = (x == width - 1)
            
            if is_top_edge or is_bottom_edge:
                return 14  # TILE_WALL_WINDOW_HORIZONTAL
            elif is_left_edge or is_right_edge:
                return 15  # TILE_WALL_WINDOW_VERTICAL
            else:
                return 14  # Default to horizontal
        else:
            return 4  # Default to wall
    
    def _map_template_tile_to_chunk_tile(self, template_tile: int) -> int:
        """
        Map building template tile types to chunk tile types
        
        Template tile types:
        0 = EMPTY, 1 = WALL, 2 = DOOR, 3 = FLOOR, 4 = FURNITURE, 5 = NPC_SPAWN, 6 = WINDOW
        
        Chunk tile types:
        4 = TILE_WALL, 5 = TILE_DOOR, 13 = TILE_BRICK (floor), 14/15 = TILE_WALL_WINDOW_*
        """
        tile_mapping = {
            0: 0,   # EMPTY -> EMPTY (don't place)
            1: 4,   # WALL -> TILE_WALL
            2: 5,   # DOOR -> TILE_DOOR
            3: 13,  # FLOOR -> TILE_BRICK
            4: 13,  # FURNITURE -> TILE_BRICK (furniture rendered separately)
            5: 13,  # NPC_SPAWN -> TILE_BRICK (NPC placed separately)
            6: 14   # WINDOW -> TILE_WALL_WINDOW_HORIZONTAL (simplified)
        }
        
        return tile_mapping.get(template_tile, 4)  # Default to wall
    
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
    
    def _clear_settlement_area_selectively(self, chunk: Chunk, x: int, y: int, width: int, height: int):
        """Clear entities from settlement area but preserve some terrain features"""
        # Remove any entities that fall within the settlement area
        entities_to_remove = []
        
        for entity in chunk.entities:
            entity_x = entity.get('x', 0)
            entity_y = entity.get('y', 0)
            
            # Check if entity is within settlement bounds
            if (x <= entity_x < x + width and y <= entity_y < y + height):
                # Only remove objects and enemies, keep NPCs and furniture if they exist
                if entity.get('type') in ['object', 'enemy']:
                    entities_to_remove.append(entity)
        
        # Remove the entities
        for entity in entities_to_remove:
            chunk.entities.remove(entity)
        
        print(f"    🧹 Selectively cleared {len(entities_to_remove)} entities from settlement area")
    
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
        Create a building structure on the chunk tiles - IMPROVED VERSION
        
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
        
        # STEP 1: Building interior floor - use brick tiles
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                if 0 <= x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                    chunk.set_tile(x, y, 13)  # TILE_BRICK
                    tiles_placed += 1
        
        # STEP 2: Building walls - only regular walls first
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
                    
                    # Place corner tiles first
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
                    # Then set edge walls (no windows yet - we'll add them strategically)
                    elif is_top_edge or is_bottom_edge:
                        chunk.set_tile(x, y, 10)  # TILE_WALL_HORIZONTAL
                        tiles_placed += 1
                    elif is_left_edge or is_right_edge:
                        chunk.set_tile(x, y, 11)  # TILE_WALL_VERTICAL
                        tiles_placed += 1
                    else:
                        # Fallback to regular wall
                        chunk.set_tile(x, y, 4)  # TILE_WALL
                        tiles_placed += 1
        
        # STEP 3: Add windows strategically - only on exterior walls, not near corners
        self._add_strategic_windows(chunk, start_x, start_y, width, height, building_random)
        
        # STEP 4: Add doors - only on building perimeter, preferably on bottom or sides
        doors_added = self._add_perimeter_doors(chunk, start_x, start_y, width, height, building_random)
        tiles_placed += doors_added
        
        # STEP 5: Add internal features for larger buildings (multi-room layouts)
        if width >= 7 and height >= 7:
            internal_features = self._add_internal_features(chunk, start_x, start_y, width, height, building_random)
            tiles_placed += internal_features
        
        print(f"            Building created with {tiles_placed} tiles, {doors_added} doors")
        return tiles_placed
    
    def _add_strategic_windows(self, chunk: Chunk, start_x: int, start_y: int, 
                              width: int, height: int, building_random: random.Random):
        """Add windows strategically - only on exterior walls, away from corners"""
        
        # Only add windows to buildings that are large enough (at least 5x5)
        if width < 5 or height < 5:
            return
        
        # Add windows to longer walls, avoiding corners and doors
        window_chance = 0.3  # 30% chance per eligible wall segment
        
        # Top wall windows (avoid corners)
        for x in range(start_x + 2, start_x + width - 2):
            if building_random.random() < window_chance:
                if 0 <= x < Chunk.CHUNK_SIZE and 0 <= start_y < Chunk.CHUNK_SIZE:
                    chunk.set_tile(x, start_y, 14)  # TILE_WALL_WINDOW_HORIZONTAL
        
        # Bottom wall windows (avoid corners)
        for x in range(start_x + 2, start_x + width - 2):
            if building_random.random() < window_chance:
                if 0 <= x < Chunk.CHUNK_SIZE and 0 <= start_y + height - 1 < Chunk.CHUNK_SIZE:
                    chunk.set_tile(x, start_y + height - 1, 14)  # TILE_WALL_WINDOW_HORIZONTAL
        
        # Left wall windows (avoid corners)
        for y in range(start_y + 2, start_y + height - 2):
            if building_random.random() < window_chance:
                if 0 <= start_x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                    chunk.set_tile(start_x, y, 15)  # TILE_WALL_WINDOW_VERTICAL
        
        # Right wall windows (avoid corners)
        for y in range(start_y + 2, start_y + height - 2):
            if building_random.random() < window_chance:
                if 0 <= start_x + width - 1 < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                    chunk.set_tile(start_x + width - 1, y, 15)  # TILE_WALL_WINDOW_VERTICAL
    
    def _add_perimeter_doors(self, chunk: Chunk, start_x: int, start_y: int, 
                            width: int, height: int, building_random: random.Random) -> int:
        """Add doors only on building perimeter - prefer bottom/sides over top"""
        doors_placed = 0
        
        # Define door placement preferences (weighted)
        door_sides = ['bottom', 'left', 'right', 'top']
        door_weights = [0.5, 0.2, 0.2, 0.1]  # Strongly prefer bottom doors
        
        # Choose a random side for the main door
        chosen_side = building_random.choices(door_sides, weights=door_weights)[0]
        
        # Place door based on chosen side
        if chosen_side == 'bottom':
            doors_placed += self._place_door_bottom_chunk(chunk, start_x, start_y, width, height)
        elif chosen_side == 'top':
            doors_placed += self._place_door_top_chunk(chunk, start_x, start_y, width, height)
        elif chosen_side == 'left':
            doors_placed += self._place_door_left_chunk(chunk, start_x, start_y, width, height)
        elif chosen_side == 'right':
            doors_placed += self._place_door_right_chunk(chunk, start_x, start_y, width, height)
        
        # For larger buildings, occasionally add a second door on a different side
        if (width >= 8 or height >= 8) and building_random.random() < 0.3:
            # Choose a different side for second door
            remaining_sides = [s for s in door_sides if s != chosen_side]
            if remaining_sides:
                second_side = building_random.choice(remaining_sides)
                if second_side == 'bottom':
                    doors_placed += self._place_door_bottom_chunk(chunk, start_x, start_y, width, height)
                elif second_side == 'top':
                    doors_placed += self._place_door_top_chunk(chunk, start_x, start_y, width, height)
                elif second_side == 'left':
                    doors_placed += self._place_door_left_chunk(chunk, start_x, start_y, width, height)
                elif second_side == 'right':
                    doors_placed += self._place_door_right_chunk(chunk, start_x, start_y, width, height)
        
        return doors_placed
    
    def _add_internal_features(self, chunk: Chunk, start_x: int, start_y: int, 
                              width: int, height: int, building_random: random.Random) -> int:
        """Add internal features for larger buildings - rooms, internal doorways, etc."""
        features_placed = 0
        
        # Only add internal features to buildings that are large enough
        if width < 7 or height < 7:
            return 0
        
        # Add internal wall divisions for multi-room buildings
        if width >= 9 and height >= 7:
            # Vertical room divider (not full wall - leave gaps for doorways)
            divider_x = start_x + width // 2
            for y in range(start_y + 1, start_y + height - 1):
                # Leave gaps for internal doorways
                if y == start_y + height // 2:
                    # Internal doorway - just floor
                    if 0 <= divider_x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                        chunk.set_tile(divider_x, y, 13)  # TILE_BRICK (floor)
                else:
                    # Internal wall
                    if 0 <= divider_x < Chunk.CHUNK_SIZE and 0 <= y < Chunk.CHUNK_SIZE:
                        chunk.set_tile(divider_x, y, 11)  # TILE_WALL_VERTICAL
                        features_placed += 1
        
        if width >= 7 and height >= 9:
            # Horizontal room divider
            divider_y = start_y + height // 2
            for x in range(start_x + 1, start_x + width - 1):
                # Leave gaps for internal doorways
                if x == start_x + width // 2:
                    # Internal doorway - just floor
                    if 0 <= x < Chunk.CHUNK_SIZE and 0 <= divider_y < Chunk.CHUNK_SIZE:
                        chunk.set_tile(x, divider_y, 13)  # TILE_BRICK (floor)
                else:
                    # Internal wall
                    if 0 <= x < Chunk.CHUNK_SIZE and 0 <= divider_y < Chunk.CHUNK_SIZE:
                        chunk.set_tile(x, divider_y, 10)  # TILE_WALL_HORIZONTAL
                        features_placed += 1
        
        return features_placed
    
    def _add_randomized_doors_to_chunk(self, chunk: Chunk, start_x: int, start_y: int, 
                                      width: int, height: int) -> int:
        """
        Add doors to buildings with randomized placement on different sides
        
        Args:
            chunk: Chunk to modify
            start_x, start_y: Building starting position
            width, height: Building dimensions
            
        Returns:
            Number of door tiles placed
        """
        # Define possible door sides with weights
        door_sides = ['bottom', 'top', 'left', 'right']
        door_weights = [0.35, 0.2, 0.2, 0.25]  # Bottom slightly favored, but all sides possible
        
        # Choose a random side for the door
        chosen_side = random.choices(door_sides, weights=door_weights)[0]
        
        # Place door based on chosen side
        if chosen_side == 'bottom':
            return self._place_door_bottom_chunk(chunk, start_x, start_y, width, height)
        elif chosen_side == 'top':
            return self._place_door_top_chunk(chunk, start_x, start_y, width, height)
        elif chosen_side == 'left':
            return self._place_door_left_chunk(chunk, start_x, start_y, width, height)
        elif chosen_side == 'right':
            return self._place_door_right_chunk(chunk, start_x, start_y, width, height)
        
        return 0
    
    def _place_door_bottom_chunk(self, chunk: Chunk, start_x: int, start_y: int, 
                                width: int, height: int) -> int:
        """Place door(s) on the bottom wall of the building"""
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        doors_placed = 0
        
        if width >= 6:
            # Double door for larger buildings
            door_x1 = door_center_x - 1
            door_x2 = door_center_x
            
            if (0 <= door_x1 < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_x1 > start_x and door_x1 < start_x + width - 1):
                chunk.set_tile(door_x1, door_y, 5)  # TILE_DOOR
                doors_placed += 1
            
            if (0 <= door_x2 < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_x2 > start_x and door_x2 < start_x + width - 1):
                chunk.set_tile(door_x2, door_y, 5)  # TILE_DOOR
                doors_placed += 1
        else:
            # Single door for smaller buildings
            if (0 <= door_center_x < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_center_x > start_x and door_center_x < start_x + width - 1):
                chunk.set_tile(door_center_x, door_y, 5)  # TILE_DOOR
                doors_placed += 1
        
        return doors_placed
    
    def _place_door_top_chunk(self, chunk: Chunk, start_x: int, start_y: int, 
                             width: int, height: int) -> int:
        """Place door(s) on the top wall of the building"""
        door_center_x = start_x + width // 2
        door_y = start_y
        doors_placed = 0
        
        if width >= 6:
            # Double door for larger buildings
            door_x1 = door_center_x - 1
            door_x2 = door_center_x
            
            if (0 <= door_x1 < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_x1 > start_x and door_x1 < start_x + width - 1):
                chunk.set_tile(door_x1, door_y, 5)  # TILE_DOOR
                doors_placed += 1
            
            if (0 <= door_x2 < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_x2 > start_x and door_x2 < start_x + width - 1):
                chunk.set_tile(door_x2, door_y, 5)  # TILE_DOOR
                doors_placed += 1
        else:
            # Single door for smaller buildings
            if (0 <= door_center_x < Chunk.CHUNK_SIZE and 0 <= door_y < Chunk.CHUNK_SIZE and 
                door_center_x > start_x and door_center_x < start_x + width - 1):
                chunk.set_tile(door_center_x, door_y, 5)  # TILE_DOOR
                doors_placed += 1
        
        return doors_placed
    
    def _place_door_left_chunk(self, chunk: Chunk, start_x: int, start_y: int, 
                              width: int, height: int) -> int:
        """Place door(s) on the left wall of the building"""
        door_x = start_x
        door_center_y = start_y + height // 2
        doors_placed = 0
        
        if height >= 6:
            # Double door for taller buildings
            door_y1 = door_center_y - 1
            door_y2 = door_center_y
            
            if (0 <= door_x < Chunk.CHUNK_SIZE and 0 <= door_y1 < Chunk.CHUNK_SIZE and 
                door_y1 > start_y and door_y1 < start_y + height - 1):
                chunk.set_tile(door_x, door_y1, 5)  # TILE_DOOR
                doors_placed += 1
            
            if (0 <= door_x < Chunk.CHUNK_SIZE and 0 <= door_y2 < Chunk.CHUNK_SIZE and 
                door_y2 > start_y and door_y2 < start_y + height - 1):
                chunk.set_tile(door_x, door_y2, 5)  # TILE_DOOR
                doors_placed += 1
        else:
            # Single door for smaller buildings
            if (0 <= door_x < Chunk.CHUNK_SIZE and 0 <= door_center_y < Chunk.CHUNK_SIZE and 
                door_center_y > start_y and door_center_y < start_y + height - 1):
                chunk.set_tile(door_x, door_center_y, 5)  # TILE_DOOR
                doors_placed += 1
        
        return doors_placed
    
    def _place_door_right_chunk(self, chunk: Chunk, start_x: int, start_y: int, 
                               width: int, height: int) -> int:
        """Place door(s) on the right wall of the building"""
        door_x = start_x + width - 1
        door_center_y = start_y + height // 2
        doors_placed = 0
        
        if height >= 6:
            # Double door for taller buildings
            door_y1 = door_center_y - 1
            door_y2 = door_center_y
            
            if (0 <= door_x < Chunk.CHUNK_SIZE and 0 <= door_y1 < Chunk.CHUNK_SIZE and 
                door_y1 > start_y and door_y1 < start_y + height - 1):
                chunk.set_tile(door_x, door_y1, 5)  # TILE_DOOR
                doors_placed += 1
            
            if (0 <= door_x < Chunk.CHUNK_SIZE and 0 <= door_y2 < Chunk.CHUNK_SIZE and 
                door_y2 > start_y and door_y2 < start_y + height - 1):
                chunk.set_tile(door_x, door_y2, 5)  # TILE_DOOR
                doors_placed += 1
        else:
            # Single door for smaller buildings
            if (0 <= door_x < Chunk.CHUNK_SIZE and 0 <= door_center_y < Chunk.CHUNK_SIZE and 
                door_center_y > start_y and door_center_y < start_y + height - 1):
                chunk.set_tile(door_x, door_center_y, 5)  # TILE_DOOR
                doors_placed += 1
        
        return doors_placed
