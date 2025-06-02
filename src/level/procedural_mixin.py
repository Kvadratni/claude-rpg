"""
Procedural Generation Mixin for Level System
Adds chunk-based procedural world generation capability to the refactored Level architecture
"""

import random
from ..world.chunk_manager import ChunkManager


class ProceduralGenerationMixin:
    """
    Mixin to add chunk-based procedural generation capability to Level class
    Integrates with the existing mixin-based Level architecture
    """
    
    def generate_procedural_level(self, seed=None):
        """
        Initialize a chunk-based procedural level
        
        Args:
            seed: Random seed for deterministic generation
        """
        if seed is None:
            seed = random.randint(1, 1000000)
            
        print(f"Initializing chunk-based procedural level with seed: {seed}")
        
        # Initialize chunk manager for this world
        world_name = f"procedural_{seed}"
        self.chunk_manager = ChunkManager(seed, world_name)
        
        # Set up infinite world dimensions (chunks will be loaded as needed)
        # But set reasonable bounds for systems that need them
        self.width = 1000  # Large but finite for compatibility
        self.height = 1000
        self.is_infinite_world = True  # Flag to indicate this is chunk-based
        
        # Initialize empty entity lists (entities will come from chunks)
        if hasattr(self, 'npcs'):
            self.npcs.clear()
        else:
            self.npcs = []
            
        if hasattr(self, 'enemies'):
            self.enemies.clear()
        else:
            self.enemies = []
            
        if hasattr(self, 'objects'):
            self.objects.clear()
        else:
            self.objects = []
            
        if hasattr(self, 'items'):
            self.items.clear()
        else:
            self.items = []
            
        if hasattr(self, 'chests'):
            self.chests.clear()
        else:
            self.chests = []
        
        # Initialize empty tiles array (will be populated from chunks)
        self.tiles = []
        
        # Initialize walkable grid (will be updated as chunks load)
        # Create a basic walkable grid that defaults to walkable
        self.walkable = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Store procedural info for save/load
        self.procedural_info = {
            'is_procedural': True,
            'seed': seed,
            'world_name': world_name,
            'player_spawn': (0, 0)  # Will be updated when we find a good spawn
        }
        
        # Find a good spawn location
        spawn_chunk = self.chunk_manager.get_chunk(0, 0)  # Start at origin
        if spawn_chunk:
            # Find a safe spawn location in the chunk
            spawn_x, spawn_y = self.find_safe_spawn_in_chunk(spawn_chunk)
            self.procedural_info['player_spawn'] = (spawn_x, spawn_y)
            print(f"Player spawn set to: ({spawn_x}, {spawn_y})")
        
        print(f"Chunk-based procedural world initialized:")
        print(f"  Seed: {seed}")
        print(f"  World name: {world_name}")
        print(f"  Spawn location: {self.procedural_info['player_spawn']}")
        
        # Add message to game log if available
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'game_log'):
            self.game.game_log.add_message(f"Procedural world initialized (Seed: {seed})", "system")
            self.game.game_log.add_message("World will generate as you explore...", "exploration")
    
    def find_safe_spawn_in_chunk(self, chunk):
        """Find a safe spawn location within a chunk"""
        # Look for a grass or plains area
        for y in range(10, chunk.CHUNK_SIZE - 10):  # Avoid edges
            for x in range(10, chunk.CHUNK_SIZE - 10):
                tile = chunk.get_tile(x, y)
                biome = chunk.get_biome(x, y)
                
                # Look for safe spawn conditions
                if tile in [0, 1] and biome in ['PLAINS', 'FOREST']:  # Grass or dirt in safe biomes
                    # Convert to world coordinates
                    world_x = chunk.chunk_x * chunk.CHUNK_SIZE + x
                    world_y = chunk.chunk_y * chunk.CHUNK_SIZE + y
                    return world_x, world_y
        
        # Fallback to chunk center
        center_x = chunk.chunk_x * chunk.CHUNK_SIZE + chunk.CHUNK_SIZE // 2
        center_y = chunk.chunk_y * chunk.CHUNK_SIZE + chunk.CHUNK_SIZE // 2
        return center_x, center_y
    
    def update_chunks_around_player(self):
        """Update loaded chunks based on player position"""
        if hasattr(self, 'chunk_manager') and hasattr(self, 'player'):
            self.chunk_manager.update_loaded_chunks(self.player.x, self.player.y)
            
            # Update entities from currently loaded chunks
            self.update_entities_from_chunks()
    
    def update_entities_from_chunks(self):
        """Update entity lists from currently loaded chunks"""
        if not hasattr(self, 'chunk_manager'):
            return
            
        # Clear current entity lists
        self.npcs.clear()
        self.enemies.clear()
        self.objects.clear()
        self.items.clear()
        self.chests.clear()
        
        # Get entities from all loaded chunks
        for chunk in self.chunk_manager.get_loaded_chunks():
            chunk_world_x = chunk.chunk_x * chunk.CHUNK_SIZE
            chunk_world_y = chunk.chunk_y * chunk.CHUNK_SIZE
            
            for entity_data in chunk.entities:
                # Convert entity data to appropriate objects
                world_x = entity_data['x'] + chunk_world_x
                world_y = entity_data['y'] + chunk_world_y
                
                if entity_data['type'] == 'npc':
                    # Create NPC object (you may need to adjust this based on your NPC class)
                    npc_obj = self.create_npc_from_data(entity_data, world_x, world_y)
                    if npc_obj:
                        self.npcs.append(npc_obj)
                        
                elif entity_data['type'] == 'enemy':
                    # Create Enemy object
                    enemy_obj = self.create_enemy_from_data(entity_data, world_x, world_y)
                    if enemy_obj:
                        self.enemies.append(enemy_obj)
                        
                elif entity_data['type'] == 'object':
                    # Create Object
                    obj = self.create_object_from_data(entity_data, world_x, world_y)
                    if obj:
                        self.objects.append(obj)
    
    def create_npc_from_data(self, entity_data, world_x, world_y):
        """Create NPC object from entity data - implement based on your NPC class"""
        # This is a placeholder - you'll need to implement based on your actual NPC class
        return None
    
    def create_enemy_from_data(self, entity_data, world_x, world_y):
        """Create Enemy object from entity data - implement based on your Enemy class"""
        # This is a placeholder - you'll need to implement based on your actual Enemy class
        return None
    
    def create_object_from_data(self, entity_data, world_x, world_y):
        """Create Object from entity data - implement based on your Object class"""
        # This is a placeholder - you'll need to implement based on your actual Object class
        return None
    
    def get_tile(self, x, y):
        """Get tile at world coordinates using chunk system"""
        if hasattr(self, 'chunk_manager'):
            try:
                return self.chunk_manager.get_tile(int(x), int(y))
            except Exception as e:
                print(f"Error getting tile at ({x}, {y}): {e}")
                return 0  # Default to grass
        return 0  # Default to grass
    
    def get_biome(self, x, y):
        """Get biome at world coordinates using chunk system"""
        if hasattr(self, 'chunk_manager'):
            try:
                return self.chunk_manager.get_biome(int(x), int(y))
            except Exception as e:
                print(f"Error getting biome at ({x}, {y}): {e}")
                return 'PLAINS'  # Default biome
        return 'PLAINS'  # Default biome
    
    def is_position_walkable_chunk(self, x, y):
        """Check if position is walkable using chunk system"""
        if hasattr(self, 'chunk_manager'):
            try:
                tile = self.chunk_manager.get_tile(int(x), int(y))
                if tile is None:
                    return True  # Default to walkable for unloaded areas
                # Check if tile is walkable
                walkable_tiles = [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE, self.TILE_DOOR, self.TILE_BRICK, 
                                self.TILE_SAND, self.TILE_SNOW, self.TILE_FOREST_FLOOR]
                return tile in walkable_tiles
            except Exception as e:
                print(f"Error checking walkability at ({x}, {y}): {e}")
                return True  # Default to walkable
        return True
    
    def is_procedural_level(self):
        """
        Check if this level was procedurally generated
        
        Returns:
            bool: True if procedural, False if template-based
        """
        return hasattr(self, 'procedural_info') and self.procedural_info.get('is_procedural', False)
    
    def get_procedural_seed(self):
        """
        Get the seed used for procedural generation
        
        Returns:
            int or None: Seed if procedural, None if template-based
        """
        if self.is_procedural_level():
            return self.procedural_info.get('seed')
        return None
    
    def get_procedural_settlements(self):
        """
        Get information about procedurally generated settlements
        
        Returns:
            list: Settlement information if procedural, empty list otherwise
        """
        if self.is_procedural_level():
            return self.procedural_info.get('settlements', [])
        return []
    
    def regenerate_procedural_level(self):
        """
        Regenerate the procedural level with the same seed
        Useful for debugging or resetting the world
        """
        if self.is_procedural_level():
            seed = self.get_procedural_seed()
            print(f"Regenerating procedural level with seed: {seed}")
            self.generate_procedural_level(seed)
        else:
            print("Cannot regenerate: Level is not procedurally generated")
    
    def get_procedural_save_data(self):
        """
        Get save data for procedural levels (minimal - just seed)
        
        Returns:
            dict: Procedural save data
        """
        if self.is_procedural_level():
            return {
                'procedural_info': self.procedural_info
            }
        return {}
    
    def load_procedural_save_data(self, save_data):
        """
        Load procedural level from save data
        
        Args:
            save_data: Save data containing procedural info
        """
        if 'procedural_info' in save_data:
            procedural_info = save_data['procedural_info']
            if procedural_info.get('is_procedural'):
                seed = procedural_info.get('seed')
                print(f"Loading procedural level from save data (seed: {seed})")
                self.generate_procedural_level(seed)
                return True
        return False