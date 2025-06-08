"""
Manages loading/unloading of world chunks
"""

import os
import math
from typing import Dict, List, Tuple, Optional, Set
from .chunk import Chunk
from .world_generator import WorldGenerator


class ChunkManager:
    """
    Manages world chunks - loading, unloading, and streaming
    """
    
    def __init__(self, world_seed: int, world_name: str = "default", asset_loader=None):
        """
        Initialize chunk manager
        
        Args:
            world_seed: Seed for world generation
            world_name: Name of the world (for save directory)
            asset_loader: Asset loader for entities
        """
        self.world_seed = world_seed
        self.world_name = world_name
        self.asset_loader = asset_loader
        self.world_generator = WorldGenerator(world_seed)
        
        # Loaded chunks cache
        self.loaded_chunks: Dict[Tuple[int, int], Chunk] = {}
        
        # World directory
        self.world_dir = f"saves/worlds/{world_name}"
        os.makedirs(self.world_dir, exist_ok=True)
        
        # Chunk loading parameters
        self.load_radius = 2  # Load chunks within 2 chunk radius (was 1)
        self.unload_radius = 4  # Unload chunks beyond 4 chunk radius (was 2)
        
        print(f"ChunkManager initialized for world '{world_name}' with seed {world_seed}")
    
    def world_to_chunk_coords(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to chunk coordinates"""
        chunk_x = int(math.floor(world_x / Chunk.CHUNK_SIZE))
        chunk_y = int(math.floor(world_y / Chunk.CHUNK_SIZE))
        return chunk_x, chunk_y
    
    def chunk_to_world_coords(self, chunk_x: int, chunk_y: int) -> Tuple[int, int]:
        """Convert chunk coordinates to world coordinates (top-left corner)"""
        world_x = chunk_x * Chunk.CHUNK_SIZE
        world_y = chunk_y * Chunk.CHUNK_SIZE
        return world_x, world_y
    
    def get_chunk(self, chunk_x: int, chunk_y: int) -> Optional[Chunk]:
        """Get a chunk, loading it if necessary"""
        chunk_key = (chunk_x, chunk_y)
        
        # Return if already loaded
        if chunk_key in self.loaded_chunks:
            return self.loaded_chunks[chunk_key]
        
        # Try to load from file
        chunk = Chunk(chunk_x, chunk_y, self.world_seed)
        if chunk.load_from_file(self.world_dir):
            self.loaded_chunks[chunk_key] = chunk
            return chunk
        
        # Generate new chunk
        chunk = self.world_generator.generate_chunk(chunk_x, chunk_y, self.asset_loader)
        chunk.save_to_file(self.world_dir)
        self.loaded_chunks[chunk_key] = chunk
        
        return chunk
    
    def get_tile(self, world_x: int, world_y: int) -> Optional[int]:
        """Get tile at world coordinates"""
        chunk_x, chunk_y = self.world_to_chunk_coords(world_x, world_y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        if not chunk:
            return None
        
        local_x = world_x - (chunk_x * Chunk.CHUNK_SIZE)
        local_y = world_y - (chunk_y * Chunk.CHUNK_SIZE)
        
        return chunk.get_tile(local_x, local_y)
    
    def get_biome(self, world_x: int, world_y: int) -> Optional[str]:
        """Get biome at world coordinates"""
        chunk_x, chunk_y = self.world_to_chunk_coords(world_x, world_y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        if not chunk:
            return None
        
        local_x = world_x - (chunk_x * Chunk.CHUNK_SIZE)
        local_y = world_y - (chunk_y * Chunk.CHUNK_SIZE)
        
        return chunk.get_biome(local_x, local_y)
    
    def set_tile(self, world_x: int, world_y: int, tile_type: int):
        """Set tile at world coordinates"""
        chunk_x, chunk_y = self.world_to_chunk_coords(world_x, world_y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        if chunk:
            local_x = world_x - (chunk_x * Chunk.CHUNK_SIZE)
            local_y = world_y - (chunk_y * Chunk.CHUNK_SIZE)
            chunk.set_tile(local_x, local_y, tile_type)
            
            # Save chunk after modification
            chunk.save_to_file(self.world_dir)
    
    def update_loaded_chunks(self, player_x: float, player_y: float):
        """Update which chunks are loaded based on player position"""
        player_chunk_x, player_chunk_y = self.world_to_chunk_coords(player_x, player_y)
        
        # Determine which chunks should be loaded
        chunks_to_load: Set[Tuple[int, int]] = set()
        for dx in range(-self.load_radius, self.load_radius + 1):
            for dy in range(-self.load_radius, self.load_radius + 1):
                chunk_x = player_chunk_x + dx
                chunk_y = player_chunk_y + dy
                chunks_to_load.add((chunk_x, chunk_y))
        
        # Load new chunks
        for chunk_key in chunks_to_load:
            if chunk_key not in self.loaded_chunks:
                chunk_x, chunk_y = chunk_key
                self.get_chunk(chunk_x, chunk_y)
        
        # Unload distant chunks
        chunks_to_unload = []
        for chunk_key, chunk in self.loaded_chunks.items():
            chunk_x, chunk_y = chunk_key
            distance = max(abs(chunk_x - player_chunk_x), abs(chunk_y - player_chunk_y))
            
            if distance > self.unload_radius:
                chunks_to_unload.append(chunk_key)
        
        for chunk_key in chunks_to_unload:
            chunk = self.loaded_chunks[chunk_key]
            chunk.save_to_file(self.world_dir)  # Save before unloading
            chunk.unload()
            del self.loaded_chunks[chunk_key]
    
    def get_loaded_chunks(self) -> List[Chunk]:
        """Get all currently loaded chunks"""
        return list(self.loaded_chunks.values())
    
    def get_entities_in_area(self, center_x: float, center_y: float, radius: int) -> List[Dict]:
        """Get all entities within a radius of the center point"""
        entities = []
        
        # Calculate chunk range
        min_chunk_x, min_chunk_y = self.world_to_chunk_coords(center_x - radius, center_y - radius)
        max_chunk_x, max_chunk_y = self.world_to_chunk_coords(center_x + radius, center_y + radius)
        
        # Check all chunks in range
        for chunk_x in range(min_chunk_x, max_chunk_x + 1):
            for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                chunk = self.get_chunk(chunk_x, chunk_y)
                if chunk:
                    # Add chunk offset to entity positions
                    chunk_world_x, chunk_world_y = self.chunk_to_world_coords(chunk_x, chunk_y)
                    for entity in chunk.entities:
                        # Adjust entity position to world coordinates
                        entity_copy = entity.copy()
                        entity_copy['world_x'] = entity['x'] + chunk_world_x
                        entity_copy['world_y'] = entity['y'] + chunk_world_y
                        entities.append(entity_copy)
        
        return entities
    
    def remove_entity_from_chunks(self, entity_id: str, world_x: float, world_y: float):
        """Remove an entity from the appropriate chunk"""
        chunk_x, chunk_y = self.world_to_chunk_coords(world_x, world_y)
        chunk = self.get_chunk(chunk_x, chunk_y)
        
        if chunk:
            chunk.remove_entity(entity_id)
            chunk.save_to_file(self.world_dir)  # Save immediately
            print(f"Removed entity {entity_id} from chunk ({chunk_x}, {chunk_y})")
    
    def save_all_chunks(self):
        """Save all loaded chunks to disk"""
        for chunk in self.loaded_chunks.values():
            chunk.save_to_file(self.world_dir)
    
    def get_world_info(self) -> Dict:
        """Get information about the world"""
        chunk_files = [f for f in os.listdir(self.world_dir) if f.startswith('chunk_') and f.endswith('.json')]
        
        return {
            'world_name': self.world_name,
            'world_seed': self.world_seed,
            'total_chunks_generated': len(chunk_files),
            'loaded_chunks': len(self.loaded_chunks),
            'world_directory': self.world_dir
        }
