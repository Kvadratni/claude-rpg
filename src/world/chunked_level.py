"""
Level implementation that uses the chunk system
"""

from typing import List, Dict, Any, Optional
from ..level.level_base import LevelBase
from .chunk_manager import ChunkManager


class ChunkedLevel(LevelBase):
    """
    Level that uses chunk-based world loading
    """
    
    def __init__(self, level_name: str, player, asset_loader, game=None, world_seed: int = None):
        """Initialize chunked level"""
        # Initialize base class with minimal size (chunks will handle the real world)
        super().__init__(level_name, player, asset_loader, game)
        
        # Override the default small size - chunked world is theoretically infinite
        self.width = 999999  # Very large theoretical size
        self.height = 999999
        
        # Initialize chunk manager
        self.world_seed = world_seed or 12345
        self.chunk_manager = ChunkManager(self.world_seed, f"world_{self.world_seed}")
        
        # Override tile access methods to use chunks
        self._original_tiles = None  # Don't use the base class tiles array
        
        print(f"ChunkedLevel initialized with seed {self.world_seed}")
    
    def get_tile(self, x: int, y: int) -> int:
        """Get tile at world coordinates using chunk system"""
        if x < 0 or y < 0:
            return 4  # TILE_WALL for out of bounds
        
        tile = self.chunk_manager.get_tile(x, y)
        return tile if tile is not None else 4  # TILE_WALL as fallback
    
    def get_biome(self, x: int, y: int) -> str:
        """Get biome at world coordinates"""
        biome = self.chunk_manager.get_biome(x, y)
        return biome if biome is not None else "PLAINS"
    
    def set_tile(self, x: int, y: int, tile_type: int):
        """Set tile at world coordinates"""
        self.chunk_manager.set_tile(x, y, tile_type)
    
    def update(self):
        """Update the level - manage chunk loading"""
        # Update chunk loading based on player position
        self.chunk_manager.update_loaded_chunks(self.player.x, self.player.y)
        
        # Update entities from loaded chunks
        self.update_entities_from_chunks()
        
        # Call parent update
        super().update()
    
    def update_entities_from_chunks(self):
        """Update entity lists from loaded chunks"""
        # Get entities near player
        entities = self.chunk_manager.get_entities_in_area(
            self.player.x, self.player.y, radius=100
        )
        
        # Clear existing objects (they'll be repopulated from chunks)
        self.objects = []
        
        # Convert chunk entities back to game entities
        for entity_data in entities:
            if entity_data['type'] == 'object':
                try:
                    from ..entities.base import Entity
                    obj = Entity(
                        entity_data['world_x'], 
                        entity_data['world_y'],
                        entity_data['name'],
                        entity_type="object",
                        blocks_movement=True,
                        asset_loader=self.asset_loader
                    )
                    self.objects.append(obj)
                except Exception as e:
                    print(f"Warning: Failed to create object entity: {e}")
    
    def get_walkable(self, x: int, y: int) -> float:
        """Get walkability at world coordinates"""
        tile = self.get_tile(x, y)
        
        # Walkable tiles (same as before)
        walkable_tiles = {0, 1, 2, 5, 13, 16, 17, 18, 19}  # GRASS, DIRT, STONE, DOOR, BRICK, SAND, SNOW, FOREST_FLOOR, SWAMP
        
        return 1.0 if tile in walkable_tiles else 0.0
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is valid for movement"""
        return self.get_walkable(x, y) > 0
    
    def get_loaded_area_bounds(self) -> tuple:
        """Get bounds of currently loaded area"""
        loaded_chunks = self.chunk_manager.get_loaded_chunks()
        
        if not loaded_chunks:
            return (0, 0, 64, 64)
        
        min_x = min(chunk.chunk_x for chunk in loaded_chunks) * 64
        min_y = min(chunk.chunk_y for chunk in loaded_chunks) * 64
        max_x = (max(chunk.chunk_x for chunk in loaded_chunks) + 1) * 64
        max_y = (max(chunk.chunk_y for chunk in loaded_chunks) + 1) * 64
        
        return (min_x, min_y, max_x, max_y)
    
    def save_world(self):
        """Save the world state"""
        self.chunk_manager.save_all_chunks()
    
    def get_world_info(self) -> Dict:
        """Get world information"""
        return self.chunk_manager.get_world_info()
    
    # Override properties to use chunk system
    @property
    def tiles(self):
        """Tiles property - not used in chunk system but kept for compatibility"""
        return None
    
    @tiles.setter  
    def tiles(self, value):
        """Tiles setter - ignored in chunk system"""
        pass
    
    @property
    def walkable(self):
        """Walkable property - computed on demand"""
        return None
    
    @walkable.setter
    def walkable(self, value):
        """Walkable setter - ignored in chunk system"""
        pass
