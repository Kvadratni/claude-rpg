"""
World generator that creates chunks on-demand
"""

import random
from typing import List, Dict, Any
from ..procedural_generation.src.biome_generator import BiomeGenerator
from ..procedural_generation.src.enhanced_entity_spawner import EnhancedEntitySpawner
from .chunk import Chunk
from .settlement_manager import ChunkSettlementManager


class WorldGenerator:
    """
    Generates world chunks on-demand using procedural generation
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
        Generate a single chunk
        
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
            print(f"Generated {settlement_type} settlement in chunk ({chunk_x}, {chunk_y}) with {len(settlement_data.get('npcs', []))} NPCs")
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
                
            # Add settlement NPCs if this chunk has a settlement
            if settlement_data:
                print(f"Adding {len(settlement_data['npcs'])} NPCs from settlement to chunk ({chunk_x}, {chunk_y})")
                for npc_data in settlement_data['npcs']:
                    npc_entity = {
                        'type': 'npc',
                        'name': npc_data['name'],
                        'building': npc_data['building'],
                        'has_shop': npc_data['has_shop'],
                        'x': npc_data['x'] - start_x,  # Convert to local chunk coordinates
                        'y': npc_data['y'] - start_y,
                        'id': f"npc_{npc_data['name'].lower().replace(' ', '_')}_{chunk_x}_{chunk_y}"
                    }
                    chunk.add_entity(npc_entity)
                    print(f"  Added NPC: {npc_data['name']} at local coords ({npc_entity['x']}, {npc_entity['y']})")
            else:
                print(f"No settlement data for chunk ({chunk_x}, {chunk_y}) - no NPCs to add")
                
        except Exception as e:
            print(f"Warning: Entity generation failed for chunk ({chunk_x}, {chunk_y}): {e}")
        
        chunk.is_generated = True
        chunk.is_loaded = True
        
        return chunk
    
    def get_chunk_seed(self, chunk_x: int, chunk_y: int) -> int:
        """Get deterministic seed for a specific chunk"""
        return hash((self.world_seed, chunk_x, chunk_y)) % (2**31)
