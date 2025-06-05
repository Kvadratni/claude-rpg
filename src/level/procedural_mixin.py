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
        
        # Track settlements found during generation
        settlements_found = []
        
        for chunk_y in range(spawn_chunk_y - generation_radius, spawn_chunk_y + generation_radius + 1):
            for chunk_x in range(spawn_chunk_x - generation_radius, spawn_chunk_x + generation_radius + 1):
                print(f"Generating chunk ({chunk_x}, {chunk_y}) - {generated_chunks + 1}/{total_chunks}")
                
                # Generate the chunk (this will save it to disk)
                chunk = self.chunk_manager.get_chunk(chunk_x, chunk_y)
                generated_chunks += 1
                
                # Check if this chunk has a settlement by looking for NPCs
                npc_entities = [e for e in chunk.entities if e['type'] == 'npc']
                if npc_entities:
                    settlement_info = {
                        'chunk_x': chunk_x,
                        'chunk_y': chunk_y,
                        'npc_count': len(npc_entities),
                        'npcs': npc_entities
                    }
                    settlements_found.append(settlement_info)
                    print(f"  Found settlement in chunk ({chunk_x}, {chunk_y}) with {len(npc_entities)} NPCs")
                
                # Update progress
                progress = (generated_chunks / total_chunks) * 100
                if generated_chunks % 5 == 0 or generated_chunks == total_chunks:
                    print(f"World generation progress: {progress:.1f}% ({generated_chunks}/{total_chunks})")
        
        print(f"Pre-generated {total_chunks} chunks successfully!")
        print(f"Found {len(settlements_found)} settlements during generation")
        
        # Determine spawn location - prefer first settlement found, but prioritize safer settlements
        if settlements_found:
            # Sort settlements by safety (prefer non-swamp settlements)
            def settlement_safety_score(settlement):
                # Get the first NPC to determine settlement type
                first_npc = settlement['npcs'][0]['name'] if settlement['npcs'] else ''
                if 'Swamp' in first_npc:
                    return 1  # Lower priority for swamp settlements
                elif 'Village' in first_npc or 'Merchant' in first_npc:
                    return 3  # High priority for villages
                else:
                    return 2  # Medium priority for other settlements
            
            # Sort by safety score (highest first)
            settlements_found.sort(key=settlement_safety_score, reverse=True)
            
            # Use the safest settlement found
            first_settlement = settlements_found[0]
            settlement_chunk_x = first_settlement['chunk_x']
            settlement_chunk_y = first_settlement['chunk_y']
            
            print(f"Spawning player near safest settlement in chunk ({settlement_chunk_x}, {settlement_chunk_y})")
            print(f"Settlement has NPCs: {[npc['name'] for npc in first_settlement['npcs']]}")
            
            # Get the settlement chunk
            spawn_chunk = self.chunk_manager.get_chunk(settlement_chunk_x, settlement_chunk_y)
            if spawn_chunk:
                spawn_x, spawn_y = self.find_safe_spawn_in_chunk(spawn_chunk)
            else:
                # Fallback to center of settlement chunk
                spawn_x = settlement_chunk_x * 64 + 32
                spawn_y = settlement_chunk_y * 64 + 32
            
            print(f"Player spawn set to ({spawn_x}, {spawn_y}) near settlement with {first_settlement['npc_count']} NPCs")
        else:
            # No settlements found, use center chunk
            print("No settlements found, spawning at center chunk (0, 0)")
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
            'generation_radius': generation_radius,
            'settlements': settlements_found
        }
        
        # Load initial entities from pre-generated chunks around the actual spawn location
        self.load_entities_from_pregenerated_chunks(spawn_x, spawn_y)
        
        # Initialize camera to center on spawn location
        self.initialize_camera_for_spawn(spawn_x, spawn_y)
        
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
        print(f"Finding safe spawn in chunk ({chunk.chunk_x}, {chunk.chunk_y})")
        
        # Look for walkable areas, prioritizing safer biomes
        best_spawn = None
        fallback_spawn = None
        
        for y in range(10, chunk.CHUNK_SIZE - 10):  # Avoid edges
            for x in range(10, chunk.CHUNK_SIZE - 10):
                tile = chunk.get_tile(x, y)
                biome = chunk.get_biome(x, y)
                
                # Check if tile is walkable
                walkable_tiles = [0, 1, 16, 17, 18, 19]  # All walkable tile types
                if tile not in walkable_tiles:
                    continue
                
                # Convert to world coordinates
                world_x = chunk.chunk_x * chunk.CHUNK_SIZE + x
                world_y = chunk.chunk_y * chunk.CHUNK_SIZE + y
                
                # Prefer safer biomes for spawn
                safe_biomes = ['PLAINS', 'FOREST', 'DESERT', 'SNOW']
                if biome in safe_biomes:
                    print(f"Found safe spawn at ({world_x}, {world_y}) in {biome} biome")
                    return world_x, world_y
                
                # Keep track of any walkable position as fallback
                if fallback_spawn is None:
                    fallback_spawn = (world_x, world_y)
                    print(f"Fallback spawn candidate at ({world_x}, {world_y}) in {biome} biome")
        
        # Use fallback if no safe biome found
        if fallback_spawn:
            print(f"Using fallback spawn at {fallback_spawn}")
            return fallback_spawn
        
        # Last resort: chunk center
        center_x = chunk.chunk_x * chunk.CHUNK_SIZE + chunk.CHUNK_SIZE // 2
        center_y = chunk.chunk_y * chunk.CHUNK_SIZE + chunk.CHUNK_SIZE // 2
        print(f"Using chunk center as spawn: ({center_x}, {center_y})")
        return center_x, center_y
    
    def load_entities_from_pregenerated_chunks(self, spawn_x, spawn_y):
        """Load entities from chunks around player spawn - limited initial load"""
        print("Loading entities from chunks around spawn...")
        
        # Convert spawn coordinates to chunk coordinates
        spawn_chunk_x, spawn_chunk_y = self.chunk_manager.world_to_chunk_coords(spawn_x, spawn_y)
        print(f"Spawn at ({spawn_x}, {spawn_y}) = chunk ({spawn_chunk_x}, {spawn_chunk_y})")
        
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
                                print(f"  Loaded NPC: {entity_data.get('name', 'Unknown')} at ({world_x}, {world_y})")
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
    
    def initialize_camera_for_spawn(self, spawn_x, spawn_y):
        """Initialize camera to center on spawn location"""
        print(f"Initializing camera for spawn at ({spawn_x}, {spawn_y})")
        
        # Convert spawn position to isometric coordinates
        player_iso_x, player_iso_y = self.iso_renderer.cart_to_iso(spawn_x, spawn_y)
        
        # Center camera on spawn location (use reasonable screen dimensions)
        screen_width = 1200  # Default screen width
        screen_height = 800  # Default screen height
        
        self.camera_x = player_iso_x - screen_width // 2
        self.camera_y = player_iso_y - screen_height // 2
        
        print(f"Camera initialized to ({self.camera_x}, {self.camera_y})")
    
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
            
            # Update entities every 300 frames (roughly once per 5 seconds at 60 FPS) - less aggressive
            if self.entity_update_counter >= 300:
                self.entity_update_counter = 0
                # Only update if player has moved significantly
                if not hasattr(self, 'last_entity_update_pos'):
                    self.last_entity_update_pos = (self.player.x, self.player.y)
                    self.update_entities_from_chunks()
                else:
                    last_x, last_y = self.last_entity_update_pos
                    distance_moved = ((self.player.x - last_x) ** 2 + (self.player.y - last_y) ** 2) ** 0.5
                    if distance_moved > 32:  # Only update if player moved more than half a chunk
                        self.last_entity_update_pos = (self.player.x, self.player.y)
                        self.update_entities_from_chunks()
    
    def update_entities_from_chunks(self):
        """Update entity lists from currently loaded chunks around player"""
        if not hasattr(self, 'chunk_manager'):
            return
        
        print("Updating entities from chunks...")
        
        # Get player chunk coordinates
        player_chunk_x, player_chunk_y = self.chunk_manager.world_to_chunk_coords(self.player.x, self.player.y)
        print(f"Player at chunk ({player_chunk_x}, {player_chunk_y}), world pos ({self.player.x:.1f}, {self.player.y:.1f})")
        
        # Only load entities from chunks within a reasonable radius
        entity_load_radius = 2  # Load entities from 5x5 chunks around player
        
        # Store current entity counts before clearing
        old_counts = {
            'npcs': len(self.npcs),
            'enemies': len(self.enemies), 
            'objects': len(self.objects)
        }
        
        # Clear current entity lists
        self.npcs.clear()
        self.enemies.clear()
        self.objects.clear()
        self.items.clear()
        self.chests.clear()
        
        # Load entities from chunks around player
        total_entities_found = 0
        for chunk_y in range(player_chunk_y - entity_load_radius, player_chunk_y + entity_load_radius + 1):
            for chunk_x in range(player_chunk_x - entity_load_radius, player_chunk_x + entity_load_radius + 1):
                chunk = self.chunk_manager.get_chunk(chunk_x, chunk_y)
                if chunk:
                    chunk_world_x = chunk.chunk_x * chunk.CHUNK_SIZE
                    chunk_world_y = chunk.chunk_y * chunk.CHUNK_SIZE
                    
                    chunk_entities = len(chunk.entities)
                    total_entities_found += chunk_entities
                    if chunk_entities > 0:
                        print(f"  Chunk ({chunk_x}, {chunk_y}) has {chunk_entities} entities")
                    
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
                                print(f"    Loaded NPC: {entity_data.get('name', 'Unknown')} at ({world_x:.1f}, {world_y:.1f})")
                                
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
        
        new_counts = {
            'npcs': len(self.npcs),
            'enemies': len(self.enemies), 
            'objects': len(self.objects)
        }
        
        print(f"Entity update complete:")
        print(f"  Total entities found in chunks: {total_entities_found}")
        for entity_type in ['npcs', 'enemies', 'objects']:
            print(f"  {entity_type}: {old_counts[entity_type]} -> {new_counts[entity_type]}")
    
    def create_npc_from_data(self, entity_data, world_x, world_y):
        """Create AI-powered NPC object from entity data"""
        try:
            npc_name = entity_data.get('name', 'Unknown NPC')
            has_shop = entity_data.get('has_shop', False)
            
            # Map NPC names to their AI classes (same as EnhancedEntitySpawner)
            ai_npc_mappings = {
                'Master Merchant': 'MasterMerchantNPC',
                'Village Elder': 'VillageElderNPC', 
                'Master Smith': 'MasterSmithNPC',
                'Innkeeper': 'InnkeeperNPC',
                'Guard Captain': 'GuardCaptainNPC',
                'Caravan Master': 'CaravanMasterNPC',
                'High Priest': 'HealerNPC',  # Use HealerNPC for priests
                'Mine Foreman': 'BlacksmithNPC',  # Use BlacksmithNPC for miners
                'Harbor Master': 'MasterMerchantNPC',  # Use MasterMerchantNPC for harbor masters
                'Master Herbalist': 'HealerNPC',  # Use HealerNPC for herbalists
                'Archbishop': 'HealerNPC',  # Use HealerNPC for religious figures
                'Mayor': 'VillageElderNPC',  # Use VillageElderNPC for mayors
                'Market Master': 'MasterMerchantNPC',  # Use MasterMerchantNPC for market masters
                'Inn Master': 'InnkeeperNPC',  # Use InnkeeperNPC for inn masters
                'Weapon Master': 'MasterSmithNPC',  # Use MasterSmithNPC for weapon masters
                'Court Wizard': 'HealerNPC',  # Use HealerNPC for wizards
                'Commander': 'GuardCaptainNPC',  # Use GuardCaptainNPC for commanders
                'Rich Merchant': 'MasterMerchantNPC',  # Use MasterMerchantNPC for rich merchants
                'Master Woodcutter': 'MasterSmithNPC',  # Use MasterSmithNPC for woodcutters
                'Forest Druid': 'HealerNPC',  # Use HealerNPC for druids
                'Scout Leader': 'GuardCaptainNPC',  # Use GuardCaptainNPC for scouts
                'Tree Keeper': 'HealerNPC',  # Use HealerNPC for nature keepers
                'Swamp Alchemist': 'HealerNPC',  # Use HealerNPC for alchemists
                'Fisherman': 'MasterMerchantNPC',  # Use MasterMerchantNPC for fishermen
                'Swamp Witch': 'HealerNPC',  # Use HealerNPC for witches
                'Boat Builder': 'MasterSmithNPC',  # Use MasterSmithNPC for builders
                'Herb Gatherer': 'HealerNPC',  # Use HealerNPC for herb gatherers
            }
            
            ai_class_name = ai_npc_mappings.get(npc_name)
            
            if ai_class_name:
                # Try to import the specific AI NPC class
                try:
                    from ..entities.npcs.master_merchant import MasterMerchantNPC
                    from ..entities.npcs.village_elder import VillageElderNPC
                    from ..entities.npcs.master_smith import MasterSmithNPC
                    from ..entities.npcs.innkeeper import InnkeeperNPC
                    from ..entities.npcs.guard_captain import GuardCaptainNPC
                    from ..entities.npcs.caravan_master import CaravanMasterNPC
                    from ..entities.npcs.healer import HealerNPC
                    from ..entities.npcs.blacksmith import BlacksmithNPC
                    
                    # Get the class by name
                    ai_class = locals()[ai_class_name]
                    
                    # Create AI NPC instance
                    npc = ai_class(world_x, world_y, asset_loader=self.asset_loader)
                    
                    # Override name if needed (for cases like High Priest using HealerNPC)
                    if npc.name != npc_name:
                        npc.name = npc_name
                    
                    print(f"        ✓ Created AI-powered {npc_name} using {ai_class_name}")
                    return npc
                    
                except ImportError as e:
                    print(f"        ⚠️  Failed to import AI NPC class {ai_class_name}: {e}")
                    # Fall back to regular NPC with AI-ready flag
                    pass
            
            # Fallback: Create regular NPC but mark it as AI-ready
            print(f"        ⚠️  No AI class found for {npc_name}, creating AI-ready regular NPC")
            from ..entities.npc import NPC
            
            npc = NPC(
                x=world_x,
                y=world_y,
                name=npc_name,
                dialog=None,  # Will be set by NPC class based on name
                shop_items=None,
                asset_loader=self.asset_loader,
                has_shop=has_shop
            )
            
            # Mark as AI-ready so it will be enabled on first interaction
            npc.ai_ready = True
            
            return npc
            
        except Exception as e:
            print(f"Error creating NPC from data: {e}")
            import traceback
            traceback.print_exc()
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