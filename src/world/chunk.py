"""
Individual chunk representation
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple


class Chunk:
    """
    Represents a single chunk of the world (e.g., 64x64 tiles)
    """
    
    CHUNK_SIZE = 64  # 64x64 tiles per chunk
    
    def __init__(self, chunk_x: int, chunk_y: int, world_seed: int):
        """
        Initialize a chunk
        
        Args:
            chunk_x: Chunk X coordinate
            chunk_y: Chunk Y coordinate  
            world_seed: World seed for generation
        """
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.world_seed = world_seed
        
        # Chunk data
        self.tiles: List[List[int]] = []
        self.biomes: List[List[str]] = []
        self.entities: List[Dict[str, Any]] = []
        self.is_generated = False
        self.is_loaded = False
        
    def get_world_bounds(self) -> Tuple[int, int, int, int]:
        """Get world coordinates for this chunk"""
        start_x = self.chunk_x * self.CHUNK_SIZE
        start_y = self.chunk_y * self.CHUNK_SIZE
        end_x = start_x + self.CHUNK_SIZE
        end_y = start_y + self.CHUNK_SIZE
        return start_x, start_y, end_x, end_y
    
    def get_tile(self, local_x: int, local_y: int) -> Optional[int]:
        """Get tile at local chunk coordinates"""
        if not self.is_loaded or not (0 <= local_x < self.CHUNK_SIZE and 0 <= local_y < self.CHUNK_SIZE):
            return None
        return self.tiles[local_y][local_x]
    
    def get_biome(self, local_x: int, local_y: int) -> Optional[str]:
        """Get biome at local chunk coordinates"""
        if not self.is_loaded or not (0 <= local_x < self.CHUNK_SIZE and 0 <= local_y < self.CHUNK_SIZE):
            return None
        return self.biomes[local_y][local_x]
    
    def set_tile(self, local_x: int, local_y: int, tile_type: int):
        """Set tile at local chunk coordinates"""
        if self.is_loaded and 0 <= local_x < self.CHUNK_SIZE and 0 <= local_y < self.CHUNK_SIZE:
            self.tiles[local_y][local_x] = tile_type
    
    def add_entity(self, entity_data: Dict[str, Any]):
        """Add entity to this chunk"""
        self.entities.append(entity_data)
    
    def remove_entity(self, entity_id: str):
        """Remove entity from this chunk"""
        self.entities = [e for e in self.entities if e.get('id') != entity_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary for serialization"""
        return {
            'chunk_x': self.chunk_x,
            'chunk_y': self.chunk_y,
            'world_seed': self.world_seed,
            'tiles': self.tiles,
            'biomes': self.biomes,
            'entities': self.entities,
            'is_generated': self.is_generated
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load chunk from dictionary"""
        self.chunk_x = data['chunk_x']
        self.chunk_y = data['chunk_y']
        self.world_seed = data['world_seed']
        self.tiles = data['tiles']
        self.biomes = data['biomes']
        self.entities = data['entities']
        self.is_generated = data['is_generated']
        self.is_loaded = True
    
    def get_filename(self, world_dir: str) -> str:
        """Get filename for this chunk"""
        return os.path.join(world_dir, f"chunk_{self.chunk_x}_{self.chunk_y}.json")
    
    def save_to_file(self, world_dir: str):
        """Save chunk to file"""
        os.makedirs(world_dir, exist_ok=True)
        filename = self.get_filename(world_dir)
        
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, separators=(',', ':'))  # Compact JSON
    
    def load_from_file(self, world_dir: str) -> bool:
        """Load chunk from file. Returns True if successful."""
        filename = self.get_filename(world_dir)
        
        if not os.path.exists(filename):
            return False
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.from_dict(data)
            return True
        except (json.JSONDecodeError, KeyError, IOError):
            return False
    
    def unload(self):
        """Unload chunk data from memory"""
        self.tiles = []
        self.biomes = []
        self.entities = []
        self.is_loaded = False
