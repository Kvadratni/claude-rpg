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
        Generate a procedural level with pre-generated chunks around spawn
        
        Args:
            seed: Random seed for deterministic generation
        """
        if seed is None:
            seed = random.randint(1, 1000000)
            
        print(f"Generating procedural world with seed: {seed}")
        
        # Initialize chunk manager for this world
        world_name = f"procedural_{seed}"
        self.chunk_manager = ChunkManager(seed, world_name)
        
        # Set up world dimensions
        self.width = 1000  # Large but finite for compatibility
        self.height = 1000
        self.is_infinite_world = True  # Flag to indicate this is chunk-based
        
        # Initialize empty entity lists
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
        
        # Initialize walkable grid
        self.walkable = [[1 for _ in range(self.width)] for _ in range(self.height)]
        
        # Initialize empty tiles array for compatibility with template-based code
        self.tiles = []
        
        # PRE-GENERATE CHUNKS AROUND SPAWN (like Minecraft)
        print("Pre-generating world chunks...")
        
        # Generate a 7x7 grid of chunks around spawn (0,0)
        generation_radius = 3  # This creates a 7x7 grid of chunks
        total_chunks = (generation_radius * 2 + 1) ** 2
        generated_chunks = 0
        
        spawn_chunk_x, spawn_chunk_y = 0, 0  # Start at origin
        
        for chunk_y in range(spawn_chunk_y - generation_radius, spawn_chunk_y + generation_radius + 1):
            for chunk_x in range(spawn_chunk_x - generation_radius, spawn_chunk_x + generation_radius + 1):
                print(f"Generating chunk ({chunk_x}, {chunk_y}) - {generated_chunks + 1}/{total_chunks}")
                
                # Generate the chunk (this will save it to disk)
                chunk = self.chunk_manager.get_chunk(chunk_x, chunk_y)
                generated_chunks += 1
                
                # Update progress
                progress = (generated_chunks / total_chunks) * 100
                if generated_chunks % 5 == 0 or generated_chunks == total_chunks:
                    print(f"World generation progress: {progress:.1f}% ({generated_chunks}/{total_chunks})")
        
        print(f"Pre-generated {total_chunks} chunks successfully!")
        
        # Find a good spawn location in the center chunk
        spawn_chunk = self.chunk_manager.get_chunk(0, 0)
        if spawn_chunk:
            spawn_x, spawn_y = self.find_safe_spawn_in_chunk(spawn_chunk)
        else:
            spawn_x, spawn_y = 32, 32  # Fallback to center of chunk (0,0)
        
        # Store procedural info for save/load
        self.procedural_info = {
            'is_procedural': True,
            'seed': seed,
            'world_name': world_name,
            'player_spawn': (spawn_x, spawn_y),
            'pre_generated': True,
            'generation_radius': generation_radius
        }
        
        # Load initial entities from pre-generated chunks
        self.load_entities_from_pregenerated_chunks()
        
        print(f"Procedural world generation complete:")
        print(f"  Seed: {seed}")
        print(f"  World name: {world_name}")
        print(f"  Spawn location: ({spawn_x}, {spawn_y})")
        print(f"  Pre-generated chunks: {total_chunks}")
        print(f"  Loaded entities: NPCs={len(self.npcs)}, Enemies={len(self.enemies)}, Objects={len(self.objects)}")
        
        # Add message to game log if available
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'game_log'):
            self.game.game_log.add_message(f"Procedural world generated (Seed: {seed})", "system")
            self.game.game_log.add_message(f"Pre-generated {total_chunks} chunks around spawn", "exploration")
    
    def find_safe_spawn_in_chunk(self, chunk):
        """Find a safe spawn location within a chunk"""
        # Look for any walkable area - be more flexible with biomes
        for y in range(10, chunk.CHUNK_SIZE - 10):  # Avoid edges
            for x in range(10, chunk.CHUNK_SIZE - 10):
                tile = chunk.get_tile(x, y)
                biome = chunk.get_biome(x, y)
                
                # Look for safe spawn conditions - accept more biomes and tiles
                walkable_tiles = [0, 1, 16, 17, 18]  # Grass, dirt, sand, snow, forest floor
                safe_biomes = ['PLAINS', 'FOREST', 'DESERT', 'SNOW']  # Exclude swamp for spawn
                
                if tile in walkable_tiles and biome in safe_biomes:
                    # Convert to world coordinates
                    world_x = chunk.chunk_x * chunk.CHUNK_SIZE + x
                    world_y = chunk.chunk_y * chunk.CHUNK_SIZE + y
                    return world_x, world_y
        
        # If no safe biome found, look for any walkable tile (including swamp)
        for y in range(10, chunk.CHUNK_SIZE - 10):
            for x in range(10, chunk.CHUNK_SIZE - 10):
                tile = chunk.get_tile(x, y)
                walkable_tiles = [0, 1, 16, 17, 18, 19]  # Include swamp
                
                if tile in walkable_tiles:
                    world_x = chunk.chunk_x * chunk.CHUNK_SIZE + x
                    world_y = chunk.chunk_y * chunk.CHUNK_SIZE + y
                    return world_x, world_y
        
        # Fallback to chunk center
        center_x = chunk.chunk_x * chunk.CHUNK_SIZE + chunk.CHUNK_SIZE // 2
        center_y = chunk.chunk_y * chunk.CHUNK_SIZE + chunk.CHUNK_SIZE // 2
        return center_x, center_y
    
    def load_entities_from_pregenerated_chunks(self):
        """Load entities from chunks around player spawn - limited initial load"""
        print("Loading entities from chunks around spawn...")
        
        # Only load entities from a small radius around spawn initially
        spawn_chunk_x, spawn_chunk_y = 0, 0
        load_radius = 1  # Only load 3x3 chunks around spawn initially
        
        entity_counts = {'npcs': 0, 'enemies': 0, 'objects': 0, 'chests': 0, 'items': 0}
        
        for chunk_y in range(spawn_chunk_y - load_radius, spawn_chunk_y + load_radius + 1):
            for chunk_x in range(spawn_chunk_x - load_radius, spawn_chunk_x + load_radius + 1):
                chunk = self.chunk_manager.get_chunk(chunk_x, chunk_y)
                if chunk:
                    chunk_world_x = chunk.chunk_x * chunk.CHUNK_SIZE
                    chunk_world_y = chunk.chunk_y * chunk.CHUNK_SIZE
                    
                    for entity_data in chunk.entities:
                        # Convert entity data to world coordinates
                        world_x = entity_data['x'] + chunk_world_x
                        world_y = entity_data['y'] + chunk_world_y
                        
                        if entity_data['type'] == 'npc':
                            # Create and add NPC
                            npc_obj = self.create_npc_from_data(entity_data, world_x, world_y)
                            if npc_obj:
                                self.npcs.append(npc_obj)
                            entity_counts['npcs'] += 1
                            
                        elif entity_data['type'] == 'enemy':
                            # Create and add Enemy
                            enemy_obj = self.create_enemy_from_data(entity_data, world_x, world_y)
                            if enemy_obj:
                                self.enemies.append(enemy_obj)
                            entity_counts['enemies'] += 1
                            
                        elif entity_data['type'] == 'object':
                            # Create and add Object
                            obj = self.create_object_from_data(entity_data, world_x, world_y)
                            if obj:
                                self.objects.append(obj)
                            entity_counts['objects'] += 1
                            
                        elif entity_data['type'] == 'chest':
                            # TODO: Implement chest creation when needed
                            entity_counts['chests'] += 1
                            
                        elif entity_data['type'] == 'item':
                            # TODO: Implement item creation when needed
                            entity_counts['items'] += 1
        
        print(f"Loaded entities from {(load_radius * 2 + 1) ** 2} chunks around spawn:")
        for entity_type, count in entity_counts.items():
            print(f"  {entity_type}: {count}")
        
        print(f"Actually created entities:")
        print(f"  NPCs: {len(self.npcs)}")
        print(f"  Enemies: {len(self.enemies)}")
        print(f"  Objects: {len(self.objects)}")
    
    def update_chunks_around_player(self):
        """Update loaded chunks based on player position"""
        if hasattr(self, 'chunk_manager') and hasattr(self, 'player'):
            # For pre-generated worlds, we might not need to load/unload chunks as aggressively
            # since we already have a good area loaded
            self.chunk_manager.update_loaded_chunks(self.player.x, self.player.y)
            
            # Only update entities occasionally to avoid performance issues
            if not hasattr(self, 'entity_update_counter'):
                self.entity_update_counter = 0
            
            self.entity_update_counter += 1
            
            # Update entities every 60 frames (roughly once per second at 60 FPS)
            if self.entity_update_counter >= 60:
                self.entity_update_counter = 0
                self.update_entities_from_chunks()
    
    def update_entities_from_chunks(self):
        """Update entity lists from currently loaded chunks around player"""
        if not hasattr(self, 'chunk_manager'):
            return
        
        # Get player chunk coordinates
        player_chunk_x, player_chunk_y = self.chunk_manager.world_to_chunk_coords(self.player.x, self.player.y)
        
        # Only load entities from chunks within a reasonable radius
        entity_load_radius = 2  # Load entities from 5x5 chunks around player
        
        # Clear current entity lists
        self.npcs.clear()
        self.enemies.clear()
        self.objects.clear()
        self.items.clear()
        self.chests.clear()
        
        # Load entities from chunks around player
        for chunk_y in range(player_chunk_y - entity_load_radius, player_chunk_y + entity_load_radius + 1):
            for chunk_x in range(player_chunk_x - entity_load_radius, player_chunk_x + entity_load_radius + 1):
                chunk = self.chunk_manager.get_chunk(chunk_x, chunk_y)
                if chunk:
                    chunk_world_x = chunk.chunk_x * chunk.CHUNK_SIZE
                    chunk_world_y = chunk.chunk_y * chunk.CHUNK_SIZE
                    
                    for entity_data in chunk.entities:
                        # Convert entity data to world coordinates
                        world_x = entity_data['x'] + chunk_world_x
                        world_y = entity_data['y'] + chunk_world_y
                        
                        # Only load entities that are reasonably close to the player
                        distance_to_player = ((world_x - self.player.x) ** 2 + (world_y - self.player.y) ** 2) ** 0.5
                        if distance_to_player > entity_load_radius * 64 * 1.5:  # 1.5x chunk radius in world units
                            continue
                        
                        if entity_data['type'] == 'npc':
                            # Create NPC object
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
        """Create NPC object from entity data"""
        try:
            from ..entities.npc import NPC
            
            # Create NPC with data from chunk
            npc = NPC(
                x=world_x,
                y=world_y,
                name=entity_data.get('name', 'Unknown NPC'),
                dialog=None,  # Will be set by NPC class based on name
                shop_items=None,
                asset_loader=self.asset_loader,
                has_shop=entity_data.get('has_shop', False)
            )
            return npc
        except Exception as e:
            print(f"Error creating NPC from data: {e}")
            return None
    
    def create_enemy_from_data(self, entity_data, world_x, world_y):
        """Create Enemy object from entity data"""
        try:
            from ..entities.enemy import Enemy
            
            # Create Enemy with data from chunk
            enemy = Enemy(
                x=world_x,
                y=world_y,
                name=entity_data.get('name', 'Unknown Enemy'),
                health=entity_data.get('health', 50),
                damage=entity_data.get('damage', 10),
                experience=25,
                is_boss=False,
                asset_loader=self.asset_loader
            )
            return enemy
        except Exception as e:
            print(f"Error creating Enemy from data: {e}")
            return None
    
    def create_object_from_data(self, entity_data, world_x, world_y):
        """Create Object from entity data"""
        try:
            from ..entities.base import Entity
            
            # Create basic Entity object for now
            obj = Entity(
                x=world_x,
                y=world_y,
                name=entity_data.get('name', 'Unknown Object'),
                entity_type="object",
                blocks_movement=True,  # Most objects block movement
                asset_loader=self.asset_loader
            )
            return obj
        except Exception as e:
            print(f"Error creating Object from data: {e}")
            return None
    
    def get_tile(self, x, y):
        """Get tile at world coordinates using chunk system"""
        if hasattr(self, 'chunk_manager'):
            try:
                tile = self.chunk_manager.get_tile(int(x), int(y))
                if tile is None:
                    # If tile is None (unloaded chunk), try to load the chunk
                    chunk_x, chunk_y = self.chunk_manager.world_to_chunk_coords(x, y)
                    chunk = self.chunk_manager.get_chunk(chunk_x, chunk_y)
                    if chunk:
                        tile = self.chunk_manager.get_tile(int(x), int(y))
                    
                    # If still None, default to grass (walkable)
                    if tile is None:
                        return self.TILE_GRASS
                
                return tile
            except Exception as e:
                print(f"Error getting tile at ({x}, {y}): {e}")
                return self.TILE_GRASS  # Default to grass
        return self.TILE_GRASS  # Default to grass
    
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
                                self.TILE_SAND, self.TILE_SNOW, self.TILE_FOREST_FLOOR, self.TILE_SWAMP]
                return tile in walkable_tiles
            except Exception as e:
                print(f"Error checking walkability at ({x}, {y}): {e}")
                return True  # Default to walkable
        return True
    
    def check_collision_chunk_based(self, x, y, size=0.4, exclude_entity=None):
        """Chunk-based collision detection for infinite worlds"""
        import math
        
        # Ensure chunks around this position are loaded
        if hasattr(self, 'chunk_manager'):
            # Get the chunk coordinates for this position
            chunk_x, chunk_y = self.chunk_manager.world_to_chunk_coords(x, y)
            
            # Preload chunks in a small radius around the position
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    self.chunk_manager.get_chunk(chunk_x + dx, chunk_y + dy)
        
        # Get tile at position using chunk system
        tile = self.get_tile(x, y)
        if tile is None:
            return False  # Unloaded areas are walkable
        
        # Check if tile is walkable
        walkable_tiles = [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE, self.TILE_DOOR, self.TILE_BRICK, 
                         self.TILE_SAND, self.TILE_SNOW, self.TILE_FOREST_FLOOR, self.TILE_SWAMP]
        
        if tile not in walkable_tiles:
            return True  # Collision with non-walkable tile
        
        # Check collision with entities (simplified for now)
        half_size = size * 0.7
        
        # Check collision with objects
        for obj in self.objects:
            if obj.blocks_movement and obj != exclude_entity:
                dist_x = x - obj.x
                dist_y = y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                collision_distance = size + 0.35
                if distance < collision_distance:
                    return True
        
        # Check collision with chests
        for chest in self.chests:
            if chest.blocks_movement and chest != exclude_entity:
                dist_x = x - chest.x
                dist_y = y - chest.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                collision_distance = size + 0.35
                if distance < collision_distance:
                    return True
        
        # Check collision with NPCs
        for npc in self.npcs:
            if npc != exclude_entity:
                dist_x = x - npc.x
                dist_y = y - npc.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                collision_distance = size + 0.4
                if distance < collision_distance:
                    return True
        
        # Check collision with enemies
        for enemy in self.enemies:
            if enemy != exclude_entity:
                dist_x = x - enemy.x
                dist_y = y - enemy.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                collision_distance = size + 0.3
                if distance < collision_distance:
                    return True
        
        return False
    
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