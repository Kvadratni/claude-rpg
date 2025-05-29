"""
Level system for the RPG
"""

import os
import pygame
import random
import heapq
import math
try:
    from .isometric import IsometricRenderer, sort_by_depth
    from .entity import Entity, NPC, Enemy, Item
    from .game_log import GameLog
    from .door_pathfinder import DoorPathfinder
    from .door_renderer import DoorRenderer
    from .wall_renderer import WallRenderer
    from .template_level import integrate_template_generation
    from .spawning import SpawningMixin
except ImportError:
    # Fallback for direct execution
    from isometric import IsometricRenderer, sort_by_depth
    from entity import Entity, NPC, Enemy, Item
    from game_log import GameLog
    from door_pathfinder import DoorPathfinder
    from door_renderer import DoorRenderer
    from wall_renderer import WallRenderer
    from template_level import integrate_template_generation
    from spawning import SpawningMixin

class Level(SpawningMixin):
    """Game level class"""
    
    # Tile types
    TILE_GRASS = 0
    TILE_DIRT = 1
    TILE_STONE = 2
    TILE_WATER = 3
    TILE_WALL = 4
    TILE_DOOR = 5
    # New wall variations
    TILE_WALL_CORNER_TL = 6  # Top-left corner
    TILE_WALL_CORNER_TR = 7  # Top-right corner
    TILE_WALL_CORNER_BL = 8  # Bottom-left corner
    TILE_WALL_CORNER_BR = 9  # Bottom-right corner
    TILE_WALL_HORIZONTAL = 10  # Horizontal wall
    TILE_WALL_VERTICAL = 11    # Vertical wall
    TILE_WALL_WINDOW = 12      # Wall with window (generic)
    TILE_BRICK = 13            # Brick floor for building interiors
    # Specific window wall types
    TILE_WALL_WINDOW_HORIZONTAL = 14  # Horizontal wall with window
    TILE_WALL_WINDOW_VERTICAL = 15    # Vertical wall with window
    
    def __init__(self, level_name, player, asset_loader):
        self.name = level_name
        self.player = player
        self.asset_loader = asset_loader
        self.width = 200  # Default size, may be overridden by template
        self.height = 200
        
        # Isometric renderer
        self.iso_renderer = IsometricRenderer(64, 32)
        self.tile_width = self.iso_renderer.tile_width
        self.tile_height = self.iso_renderer.tile_height
        
        # Door rendering and pathfinding systems
        self.door_renderer = DoorRenderer(asset_loader, self.iso_renderer)
        self.door_pathfinder = DoorPathfinder(self)
        
        # Wall rendering system
        self.wall_renderer = WallRenderer(self)
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Template generator (will be set if template is used)
        self.template_generator = None
        
        # Try template-based generation first
        template_path = "assets/maps/main_world.png"
        if os.path.exists(template_path):
            print("Using template-based map generation...")
            success = integrate_template_generation(self, template_path)
            if success:
                print("Template-based generation successful!")
            else:
                print("Template generation failed, no fallback available")
                raise RuntimeError("Template generation failed and no fallback is available")
        else:
            print("No template found, template is required")
            raise RuntimeError("Template file not found and no fallback is available")
        
        # Generate heightmap and walkable grid if not already done
        if not hasattr(self, 'heightmap') or self.heightmap is None:
            self.heightmap = self.generate_heightmap()
        if not hasattr(self, 'walkable') or self.walkable is None:
            self.walkable = self.generate_walkable_grid()
        
        # Combat state tracking
        self.enemies_in_combat = set()  # Track which enemies are in combat
        self.combat_music_timer = 0     # Timer for combat music fade out
        
        # Create tile sprites
        self.create_tile_sprites()
    

    

    

    

    

    

    

    

    

    

    

    
    def create_test_corner_building(self, tiles, start_x, start_y, corner_test_type):
        """Create a small test building to test corner orientations"""
        width, height = 4, 4
        
        # Interior
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                tiles[y][x] = self.TILE_BRICK
        
        # Walls
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if (x > start_x and x < start_x + width - 1 and 
                    y > start_y and y < start_y + height - 1):
                    continue
                
                is_top = (y == start_y)
                is_bottom = (y == start_y + height - 1)
                is_left = (x == start_x)
                is_right = (x == start_x + width - 1)
                
                # Test different corner mappings
                if corner_test_type == 0:  # Test mapping 1
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    else:
                        tiles[y][x] = self.TILE_WALL
                elif corner_test_type == 1:  # Test mapping 2
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    else:
                        tiles[y][x] = self.TILE_WALL
                elif corner_test_type == 2:  # Test mapping 3
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    else:
                        tiles[y][x] = self.TILE_WALL
                elif corner_test_type == 3:  # Test mapping 4
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    else:
                        tiles[y][x] = self.TILE_WALL
    
    def create_building(self, tiles, start_x, start_y, width, height):
        """Create a building structure with varied wall types and windows"""
        # Building interior floor - use brick tiles for more realistic interiors
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                tiles[y][x] = self.TILE_BRICK  # Interior brick floor
        
        # Building walls - use simple, consistent approach
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                # Skip interior
                if (x > start_x and x < start_x + width - 1 and 
                    y > start_y and y < start_y + height - 1):
                    continue
                
                # Use regular walls for all positions - no complex corner logic
                tiles[y][x] = self.TILE_WALL
        
        # Add some variety with horizontal and vertical walls
        # Top and bottom walls
        for x in range(start_x + 1, start_x + width - 1):
            # Top wall
            if random.random() < 0.2:  # 20% chance for windows
                tiles[start_y][x] = self.TILE_WALL_WINDOW_HORIZONTAL
            else:
                tiles[start_y][x] = self.TILE_WALL_HORIZONTAL
            
            # Bottom wall (will be overridden by doors)
            if random.random() < 0.2:  # 20% chance for windows
                tiles[start_y + height - 1][x] = self.TILE_WALL_WINDOW_HORIZONTAL
            else:
                tiles[start_y + height - 1][x] = self.TILE_WALL_HORIZONTAL
        
        # Left and right walls
        for y in range(start_y + 1, start_y + height - 1):
            # Left wall
            if random.random() < 0.15:  # 15% chance for windows
                tiles[y][start_x] = self.TILE_WALL_WINDOW_VERTICAL
            else:
                tiles[y][start_x] = self.TILE_WALL_VERTICAL
            
            # Right wall
            if random.random() < 0.15:  # 15% chance for windows
                tiles[y][start_x + width - 1] = self.TILE_WALL_WINDOW_VERTICAL
            else:
                tiles[y][start_x + width - 1] = self.TILE_WALL_VERTICAL
        
        # Add double doors (2 tiles wide) - replace bottom wall sections
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        
        # Create 2-tile wide door centered on the building
        door_x1 = door_center_x - 1
        door_x2 = door_center_x
        
        # Make sure both door positions are valid and within the building wall
        if (0 <= door_x1 < self.width and 0 <= door_y < self.height and 
            door_x1 > start_x and door_x1 < start_x + width - 1):
            tiles[door_y][door_x1] = self.TILE_DOOR
        
        if (0 <= door_x2 < self.width and 0 <= door_y < self.height and 
            door_x2 > start_x and door_x2 < start_x + width - 1):
            tiles[door_y][door_x2] = self.TILE_DOOR
    
    def create_lake(self, tiles, center_x, center_y, radius):
        """Create a circular lake"""
        for y in range(max(1, center_y - radius), min(self.height - 1, center_y + radius)):
            for x in range(max(1, center_x - radius), min(self.width - 1, center_x + radius)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance < radius - 2:
                    tiles[y][x] = self.TILE_WATER
                elif distance < radius:
                    tiles[y][x] = self.TILE_DIRT  # Shore
    
    def create_forest_clearing(self, tiles, center_x, center_y, size):
        """Create a forest clearing area"""
        for y in range(max(1, center_y - size//2), min(self.height - 1, center_y + size//2)):
            for x in range(max(1, center_x - size//2), min(self.width - 1, center_x + size//2)):
                if random.random() < 0.3:  # 30% chance for dirt patches
                    tiles[y][x] = self.TILE_DIRT
    
    def create_dirt_path(self, tiles, start_x, start_y, end_x, end_y):
        """Create a dirt path between two points"""
        # Simple straight line path
        if start_x == end_x:  # Vertical path
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                if 1 <= y < self.height - 1:
                    tiles[y][start_x] = self.TILE_DIRT
        elif start_y == end_y:  # Horizontal path
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                if 1 <= x < self.width - 1:
                    tiles[start_y][x] = self.TILE_DIRT
    
    def generate_heightmap(self):
        """Generate a heightmap for the level"""
        heightmap = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Default height
                height = 0
                
                # Walls are higher
                if self.tiles[y][x] == self.TILE_WALL:
                    height = 1
                # Water is lower
                elif self.tiles[y][x] == self.TILE_WATER:
                    height = -0.5
                # Add some random height variations
                elif random.random() < 0.1:
                    height = random.uniform(-0.1, 0.1)
                
                row.append(height)
            heightmap.append(row)
        
        # Don't mirror the heightmap 
        return heightmap
    
    def generate_walkable_grid(self):
        """Generate enhanced walkable grid that includes object influence"""
        walkable = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Start with basic tile walkability
                tile_type = self.tiles[y][x]
                tile_walkable = tile_type in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE, self.TILE_DOOR, self.TILE_BRICK]
                
                if not tile_walkable:
                    row.append(0)  # Completely blocked
                    continue
                
                # Calculate object influence
                influence_score = self.calculate_object_influence(x, y)
                
                # Convert to walkability score (0 = blocked, 1 = free, 0.5 = restricted)
                if influence_score > 0.8:
                    row.append(0)  # Too close to objects
                elif influence_score > 0.4:
                    row.append(0.3)  # Restricted but passable
                else:
                    row.append(1)  # Fully walkable
            
            walkable.append(row)
        
        return walkable
    
    def calculate_object_influence(self, x, y):
        """Calculate how much objects influence this tile's walkability"""
        center_x, center_y = x + 0.5, y + 0.5
        max_influence = 0
        
        # Check all objects within influence range
        for obj in self.objects:
            if not obj.blocks_movement:
                continue
            
            distance = math.sqrt((center_x - obj.x)**2 + (center_y - obj.y)**2)
            
            # Objects have influence within 1.5 tiles
            if distance < 1.5:
                # Closer objects have more influence
                influence = max(0, 1.0 - (distance / 1.5))
                max_influence = max(max_influence, influence)
        
        return max_influence
    
    def create_tile_sprites(self):
        """Create isometric tile sprites using loaded assets"""
        self.tile_sprites = {}
        
        # Try to use loaded images, fall back to generated sprites
        grass_image = self.asset_loader.get_image("grass_tile")
        if grass_image:
            # Rotate the tile 45 degrees for proper isometric alignment
            rotated_grass = pygame.transform.rotate(grass_image, 45)
            self.tile_sprites[self.TILE_GRASS] = pygame.transform.scale(rotated_grass, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_GRASS] = self.iso_renderer.create_diamond_tile((50, 150, 50))
        
        stone_image = self.asset_loader.get_image("stone_tile")
        if stone_image:
            rotated_stone = pygame.transform.rotate(stone_image, 45)
            self.tile_sprites[self.TILE_STONE] = pygame.transform.scale(rotated_stone, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_STONE] = self.iso_renderer.create_diamond_tile((150, 150, 150))
        
        water_image = self.asset_loader.get_image("water_tile")
        if water_image:
            rotated_water = pygame.transform.rotate(water_image, 45)
            self.tile_sprites[self.TILE_WATER] = pygame.transform.scale(rotated_water, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_WATER] = self.iso_renderer.create_diamond_tile((50, 100, 200))
        
        # Load base wall image - try improved isometric version first
        wall_image = self.asset_loader.get_image("wall_tile_isometric")
        if not wall_image:
            wall_image = self.asset_loader.get_image("wall_tile")
        
        if wall_image:
            # Scale wall to be taller and more prominent
            wall_height = self.tile_height + 32  # Make walls taller
            base_wall_sprite = pygame.transform.scale(wall_image, (self.tile_width + 8, wall_height))
            
            # Create variations of the wall sprite
            self.tile_sprites[self.TILE_WALL] = base_wall_sprite
            
            # Load dedicated wall assets instead of creating programmatically
            self.wall_renderer.load_corner_wall_sprites()
            self.wall_renderer.load_directional_wall_sprites()
            self.wall_renderer.load_window_wall_sprites()
            
        else:
            # Fallback to generated sprites with improved isometric cube rendering
            base_wall = self.iso_renderer.create_cube_tile((220, 220, 220), (180, 180, 180), (140, 140, 140))
            self.tile_sprites[self.TILE_WALL] = base_wall
            
            # Create variations for different wall types with different colors
            # Corner walls - slightly darker for distinction
            corner_wall = self.iso_renderer.create_cube_tile((200, 200, 200), (160, 160, 160), (120, 120, 120))
            self.tile_sprites[self.TILE_WALL_CORNER_TL] = corner_wall
            self.tile_sprites[self.TILE_WALL_CORNER_TR] = corner_wall
            self.tile_sprites[self.TILE_WALL_CORNER_BL] = corner_wall
            self.tile_sprites[self.TILE_WALL_CORNER_BR] = corner_wall
            
            # Directional walls - slightly different tint
            horizontal_wall = self.iso_renderer.create_cube_tile((210, 210, 210), (170, 170, 170), (130, 130, 130))
            self.tile_sprites[self.TILE_WALL_HORIZONTAL] = horizontal_wall
            self.tile_sprites[self.TILE_WALL_VERTICAL] = horizontal_wall
            
            # Window walls - lighter color to suggest windows
            window_wall = self.iso_renderer.create_cube_tile((230, 230, 250), (190, 190, 210), (150, 150, 170))
            self.tile_sprites[self.TILE_WALL_WINDOW] = window_wall
            self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = window_wall
            self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = window_wall
        
        dirt_image = self.asset_loader.get_image("dirt_tile")
        if dirt_image:
            rotated_dirt = pygame.transform.rotate(dirt_image, 45)
            self.tile_sprites[self.TILE_DIRT] = pygame.transform.scale(rotated_dirt, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_DIRT] = self.iso_renderer.create_diamond_tile((150, 100, 50))
        
        # Brick tile for building interiors
        brick_image = self.asset_loader.get_image("brick_tile")
        if brick_image:
            rotated_brick = pygame.transform.rotate(brick_image, 45)
            self.tile_sprites[self.TILE_BRICK] = pygame.transform.scale(rotated_brick, (self.tile_width, self.tile_height))
        else:
            # Fallback to a reddish-brown color for brick
            self.tile_sprites[self.TILE_BRICK] = self.iso_renderer.create_diamond_tile((150, 80, 60))
        
        # Door - try improved isometric version first
        door_image = self.asset_loader.get_image("door_tile_isometric")
        if not door_image:
            door_image = self.asset_loader.get_image("door_tile")
        
        if door_image:
            # Scale door to be taller and more prominent
            door_height = self.tile_height + 24  # Make doors taller than normal tiles
            scaled_door = pygame.transform.scale(door_image, (self.tile_width, door_height))
            
            # Use the scaled door directly - no need for complex enhancement that might cause issues
            self.tile_sprites[self.TILE_DOOR] = scaled_door
        else:
            # Create enhanced door sprite with proper isometric proportions
            door_sprite = self.door_renderer.create_enhanced_door_sprite(self.tile_width, self.tile_height)
            self.tile_sprites[self.TILE_DOOR] = door_sprite
    
    
    
    def check_collision(self, x, y, size=0.4, exclude_entity=None):
        """Check collision with level geometry and entities - improved precision with enhanced door handling"""
        # Check if the position is within level bounds with proper margin
        margin = size + 0.1
        if x < margin or x >= self.width - margin or y < margin or y >= self.height - margin:
            return True
        
        # Enhanced door area detection
        tile_x = int(x)
        tile_y = int(y)
        door_context = self.door_pathfinder.analyze_door_context(tile_x, tile_y, x, y)
        
        # For door areas, use much more lenient collision
        if door_context['is_door_area']:
            effective_size = size * 0.4  # Very small collision box for doors
            
            # Special handling for multi-tile door areas
            if door_context['is_double_door']:
                effective_size = size * 0.3  # Even smaller for double doors
        else:
            effective_size = size * 0.7  # Normal collision
        
        half_size = effective_size
        
        corners = [
            (x - half_size, y - half_size),  # Top-left
            (x + half_size, y - half_size),  # Top-right
            (x - half_size, y + half_size),  # Bottom-left
            (x + half_size, y + half_size),  # Bottom-right
        ]
        
        # Check each corner against tiles
        for corner_x, corner_y in corners:
            corner_tile_x = int(corner_x)
            corner_tile_y = int(corner_y)
            
            # Ensure tile coordinates are within bounds
            if 0 <= corner_tile_x < self.width and 0 <= corner_tile_y < self.height:
                if self.walkable[corner_tile_y][corner_tile_x] <= 0:
                    # For door areas, be more forgiving about walkability
                    if not door_context['is_door_area']:
                        return True
        
        # Also check center point
        center_tile_x = int(x)
        center_tile_y = int(y)
        if 0 <= center_tile_x < self.width and 0 <= center_tile_y < self.height:
            if self.walkable[center_tile_y][center_tile_x] <= 0:
                if not door_context['is_door_area']:
                    return True
        
        # Skip object collision checking in door areas to allow easier passage
        if door_context['is_door_area']:
            return False
        
        # Check collision with objects using circular collision (only when not in door areas)
        for obj in self.objects:
            if obj.blocks_movement and obj != exclude_entity:
                dist_x = x - obj.x
                dist_y = y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use circular collision for objects
                collision_distance = size + 0.35  # Slightly tighter collision
                if distance < collision_distance:
                    return True
        
        # Check collision with chests using circular collision
        for chest in self.chests:
            if chest.blocks_movement and chest != exclude_entity:
                dist_x = x - chest.x
                dist_y = y - chest.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use circular collision for chests
                collision_distance = size + 0.35  # Same as objects
                if distance < collision_distance:
                    return True
        
        # Check collision with NPCs using circular collision
        for npc in self.npcs:
            if npc != exclude_entity:
                dist_x = x - npc.x
                dist_y = y - npc.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # NPCs have collision
                collision_distance = size + 0.4
                if distance < collision_distance:
                    return True
        
        # Check collision with enemies (prevent stacking)
        for enemy in self.enemies:
            if enemy != exclude_entity:
                dist_x = x - enemy.x
                dist_y = y - enemy.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Enemies should not overlap too much
                collision_distance = size + 0.3
                if distance < collision_distance:
                    return True
        
        return False
    
    def render_path_debug(self, surface, path):
        """Render debug visualization of the current path"""
        if len(path) < 2:
            return
        
        # Draw path lines
        for i in range(len(path) - 1):
            start_world = path[i]
            end_world = path[i + 1]
            
            # Convert world coordinates to screen coordinates
            start_screen = self.iso_renderer.world_to_screen(start_world[0], start_world[1], self.camera_x, self.camera_y)
            end_screen = self.iso_renderer.world_to_screen(end_world[0], end_world[1], self.camera_x, self.camera_y)
            
            # Draw line between waypoints
            pygame.draw.line(surface, (255, 255, 0), start_screen, end_screen, 2)  # Yellow line
        
        # Draw waypoint circles
        for i, waypoint in enumerate(path):
            screen_pos = self.iso_renderer.world_to_screen(waypoint[0], waypoint[1], self.camera_x, self.camera_y)
            
            # Different colors for different waypoint types
            if i == 0:
                color = (0, 255, 0)  # Green for start
            elif i == len(path) - 1:
                color = (255, 0, 0)  # Red for end
            else:
                # Check if this waypoint is near a door
                tile_x, tile_y = int(waypoint[0]), int(waypoint[1])
                is_door_waypoint = False
                
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        check_x, check_y = tile_x + dx, tile_y + dy
                        if (0 <= check_x < self.width and 0 <= check_y < self.height):
                            if self.tiles[check_y][check_x] == self.TILE_DOOR:
                                is_door_waypoint = True
                                break
                    if is_door_waypoint:
                        break
                
                color = (0, 255, 255) if is_door_waypoint else (255, 255, 255)  # Cyan for door waypoints, white for others
            
            pygame.draw.circle(surface, color, screen_pos, 4)
            pygame.draw.circle(surface, (0, 0, 0), screen_pos, 4, 1)  # Black border
    
    def find_path(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Find a path using multi-resolution pathfinding with corner smoothing"""
        # Phase 1: Coarse pathfinding on tile grid
        coarse_path = self.find_coarse_path(start_x, start_y, end_x, end_y, entity_size)
        if not coarse_path:
            return []
        
        # Phase 2: Apply corner detection and smoothing
        smoothed_path = self.apply_corner_smoothing(coarse_path, entity_size)
        
        # Phase 3: Add door navigation waypoints
        enhanced_path = self.door_pathfinder.enhance_door_pathfinding(smoothed_path, entity_size)
        
        # Phase 4: Validate path with entity simulation
        validated_path = self.validate_path_with_entity_simulation(enhanced_path, entity_size)
        
        return validated_path
    
    def find_coarse_path(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Find a coarse path using A* algorithm with sub-tile precision"""
        # Convert to grid coordinates but allow sub-tile positioning
        start_grid_x = int(start_x)
        start_grid_y = int(start_y)
        end_grid_x = int(end_x)
        end_grid_y = int(end_y)
        
        # Check if start and end are valid
        if not (0 <= start_grid_x < self.width and 0 <= start_grid_y < self.height):
            return []
        if not (0 <= end_grid_x < self.width and 0 <= end_grid_y < self.height):
            return []
        
        # If end position is not walkable, find nearest walkable position
        if self.walkable[end_grid_y][end_grid_x] <= 0:
            end_grid_x, end_grid_y = self.find_nearest_walkable(end_grid_x, end_grid_y, entity_size)
            if end_grid_x is None:
                return []  # No walkable position found
        
        # For very short distances, create direct path with sub-tile precision
        if abs(start_grid_x - end_grid_x) <= 1 and abs(start_grid_y - end_grid_y) <= 1:
            return self.create_direct_sub_tile_path(start_x, start_y, end_x, end_y, entity_size)
        
        # A* algorithm with enhanced walkability scoring
        open_set = []
        heapq.heappush(open_set, (0, start_grid_x, start_grid_y))
        
        came_from = {}
        g_score = {(start_grid_x, start_grid_y): 0}
        f_score = {(start_grid_x, start_grid_y): self.heuristic(start_grid_x, start_grid_y, end_grid_x, end_grid_y)}
        
        visited = set()
        max_iterations = 500
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current_f, current_x, current_y = heapq.heappop(open_set)
            
            if (current_x, current_y) in visited:
                continue
            
            visited.add((current_x, current_y))
            
            # Check if we reached the goal
            if current_x == end_grid_x and current_y == end_grid_y:
                # Reconstruct path with sub-tile precision
                path = []
                while (current_x, current_y) in came_from:
                    # Use sub-tile positioning instead of forcing tile centers
                    path.append(self.calculate_sub_tile_position(current_x, current_y, entity_size))
                    current_x, current_y = came_from[(current_x, current_y)]
                path.reverse()
                
                # Add final destination with sub-tile precision
                path.append(self.calculate_sub_tile_position(end_grid_x, end_grid_y, entity_size))
                
                return path
            
            # Check all 8 neighbors
            neighbors = [
                (current_x + 1, current_y),     # Right
                (current_x - 1, current_y),     # Left
                (current_x, current_y + 1),     # Down
                (current_x, current_y - 1),     # Up
                (current_x + 1, current_y + 1), # Down-Right
                (current_x - 1, current_y + 1), # Down-Left
                (current_x + 1, current_y - 1), # Up-Right
                (current_x - 1, current_y - 1), # Up-Left
            ]
            
            for next_x, next_y in neighbors:
                if (next_x, next_y) in visited:
                    continue
                
                # Check bounds
                if not (0 <= next_x < self.width and 0 <= next_y < self.height):
                    continue
                
                # Enhanced walkability check with influence scoring
                walkability = self.walkable[next_y][next_x]
                if walkability <= 0:
                    continue  # Completely blocked
                
                # Calculate movement cost with influence penalty
                is_diagonal = abs(next_x - current_x) == 1 and abs(next_y - current_y) == 1
                base_cost = 1.414 if is_diagonal else 1.0
                
                # Apply walkability penalty for restricted areas
                influence_penalty = (1.0 - walkability) * 2.0  # 0-2x penalty for restricted areas
                move_cost = base_cost * (1.0 + influence_penalty)
                
                # Heavily favor doors to force pathfinding through them
                if self.tiles[next_y][next_x] == self.TILE_DOOR:
                    move_cost *= 0.1  # 90% cost reduction for doors
                elif walkability > 0.9:
                    move_cost *= 0.8  # Prefer open areas
                
                tentative_g_score = g_score.get((current_x, current_y), float('inf')) + move_cost
                
                if tentative_g_score < g_score.get((next_x, next_y), float('inf')):
                    came_from[(next_x, next_y)] = (current_x, current_y)
                    g_score[(next_x, next_y)] = tentative_g_score
                    f_score[(next_x, next_y)] = tentative_g_score + self.heuristic(next_x, next_y, end_grid_x, end_grid_y)
                    
                    heapq.heappush(open_set, (f_score[(next_x, next_y)], next_x, next_y))
        
        return []  # No path found
    
    def calculate_sub_tile_position(self, grid_x, grid_y, entity_size):
        """Calculate optimal sub-tile position for smoother movement"""
        # Instead of forcing tile center, find the best position within the tile
        base_x = grid_x + 0.5
        base_y = grid_y + 0.5
        
        # Check if we can optimize position based on nearby obstacles
        best_x, best_y = base_x, base_y
        best_score = self.evaluate_position_quality(base_x, base_y, entity_size)
        
        # Try slight offsets to find better positions
        offsets = [(-0.3, 0), (0.3, 0), (0, -0.3), (0, 0.3), (-0.2, -0.2), (0.2, 0.2), (-0.2, 0.2), (0.2, -0.2)]
        
        for dx, dy in offsets:
            test_x = base_x + dx
            test_y = base_y + dy
            
            # Ensure position is still within the tile and valid
            if (grid_x <= test_x < grid_x + 1 and grid_y <= test_y < grid_y + 1 and
                not self.check_collision(test_x, test_y, entity_size)):
                
                score = self.evaluate_position_quality(test_x, test_y, entity_size)
                if score > best_score:
                    best_x, best_y = test_x, test_y
                    best_score = score
        
        return (best_x, best_y)
    
    def evaluate_position_quality(self, x, y, entity_size):
        """Evaluate how good a position is for pathfinding (higher = better)"""
        score = 1.0
        
        # Penalize positions close to obstacles
        for obj in self.objects:
            if obj.blocks_movement:
                distance = math.sqrt((x - obj.x)**2 + (y - obj.y)**2)
                if distance < 1.0:
                    penalty = max(0, 1.0 - distance)
                    score -= penalty * 0.5
        
        # Bonus for positions away from walls
        tile_x, tile_y = int(x), int(y)
        wall_bonus = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x, check_y = tile_x + dx, tile_y + dy
                if (0 <= check_x < self.width and 0 <= check_y < self.height):
                    if self.walkable[check_y][check_x] > 0.5:
                        wall_bonus += 0.1
        
        score += wall_bonus
        return max(0, score)
    
    def create_direct_sub_tile_path(self, start_x, start_y, end_x, end_y, entity_size):
        """Create a direct path with sub-tile precision for short distances"""
        # Check if direct path is clear
        if self.has_line_of_sight((start_x, start_y), (end_x, end_y), entity_size):
            return [(end_x, end_y)]
        
        # If not clear, create intermediate waypoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Find best intermediate position
        best_mid = self.find_best_intermediate_position(start_x, start_y, end_x, end_y, entity_size)
        if best_mid:
            return [best_mid, (end_x, end_y)]
        
        # Fallback to tile center
        return [(int(end_x) + 0.5, int(end_y) + 0.5)]
    
    def find_best_intermediate_position(self, start_x, start_y, end_x, end_y, entity_size):
        """Find the best intermediate position for a short path"""
        # Try positions around the midpoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        candidates = [
            (mid_x, mid_y),
            (mid_x + 0.3, mid_y),
            (mid_x - 0.3, mid_y),
            (mid_x, mid_y + 0.3),
            (mid_x, mid_y - 0.3)
        ]
        
        for pos in candidates:
            if (not self.check_collision(pos[0], pos[1], entity_size) and
                self.has_line_of_sight((start_x, start_y), pos, entity_size) and
                self.has_line_of_sight(pos, (end_x, end_y), entity_size)):
                return pos
        
        return None
    
    def heuristic(self, x1, y1, x2, y2):
        """Heuristic function for A* (Manhattan distance with diagonal movement)"""
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        # Use diagonal distance heuristic
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)
    
    def apply_corner_smoothing(self, path, entity_size):
        """Apply intelligent corner smoothing to the path"""
        if len(path) < 3:
            return path
        
        corners = self.detect_corners_in_path(path)
        if not corners:
            return path
        
        smoothed_path = path.copy()
        
        # Process corners from end to start to maintain indices
        for corner in reversed(corners):
            smoothed_segment = self.create_smooth_corner(
                smoothed_path, 
                corner['index'], 
                corner['severity'],
                entity_size
            )
            
            # Replace sharp corner with smooth curve
            start_idx = max(0, corner['index'] - 1)
            end_idx = min(len(smoothed_path), corner['index'] + 2)
            smoothed_path[start_idx:end_idx] = smoothed_segment
        
        return smoothed_path
    
    def detect_corners_in_path(self, path):
        """Detect corners that need smoothing"""
        corners = []
        
        for i in range(1, len(path) - 1):
            prev_point = path[i - 1]
            current_point = path[i]
            next_point = path[i + 1]
            
            # Calculate angle between segments
            angle = self.calculate_turn_angle(prev_point, current_point, next_point)
            
            # If angle is sharp (> 45 degrees), mark as corner
            if abs(angle) > 45:
                corner_info = {
                    'index': i,
                    'angle': angle,
                    'position': current_point,
                    'severity': min(abs(angle) / 90.0, 1.0)  # 0-1 scale
                }
                corners.append(corner_info)
        
        return corners
    
    def calculate_turn_angle(self, p1, p2, p3):
        """Calculate the turn angle at point p2 between p1->p2 and p2->p3"""
        # Vector from p1 to p2
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        # Vector from p2 to p3
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # Calculate angle between vectors
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        angle = math.degrees(math.atan2(cross_product, dot_product))
        return angle
    
    def create_smooth_corner(self, path, corner_idx, severity, entity_size):
        """Create a smooth curve around a corner"""
        if corner_idx < 1 or corner_idx >= len(path) - 1:
            return [path[corner_idx]]
        
        p0 = path[corner_idx - 1]
        p1 = path[corner_idx]
        p2 = path[corner_idx + 1]
        
        # Calculate curve control points
        curve_distance = 0.2 + (severity * 0.3)  # 0.2 to 0.5 tiles
        
        # Ensure curve doesn't cause collisions
        curve_distance = min(curve_distance, entity_size * 1.5)
        
        # Generate smooth curve points
        curve_points = self.generate_smooth_curve(p0, p1, p2, curve_distance, entity_size)
        
        return curve_points
    
    def generate_smooth_curve(self, p0, p1, p2, curve_distance, entity_size):
        """Generate a smooth curve between three points"""
        # Calculate control points for the curve
        # Direction vectors
        d1 = math.sqrt((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)
        d2 = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        if d1 == 0 or d2 == 0:
            return [p1]
        
        # Normalized direction vectors
        u1 = ((p1[0] - p0[0]) / d1, (p1[1] - p0[1]) / d1)
        u2 = ((p2[0] - p1[0]) / d2, (p2[1] - p1[1]) / d2)
        
        # Control points for the curve
        c1 = (p1[0] - u1[0] * curve_distance, p1[1] - u1[1] * curve_distance)
        c2 = (p1[0] + u2[0] * curve_distance, p1[1] + u2[1] * curve_distance)
        
        # Generate curve points using quadratic Bezier
        curve_points = []
        num_points = max(3, int(curve_distance * 8))  # More points for larger curves
        
        for i in range(num_points + 1):
            t = i / num_points
            # Quadratic Bezier curve: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
            x = (1-t)**2 * c1[0] + 2*(1-t)*t * p1[0] + t**2 * c2[0]
            y = (1-t)**2 * c1[1] + 2*(1-t)*t * p1[1] + t**2 * c2[1]
            
            # Validate curve point for collisions
            if not self.check_collision(x, y, entity_size):
                curve_points.append((x, y))
            else:
                # If curve causes collision, fall back to original point
                curve_points.append(p1)
                break
        
        return curve_points if curve_points else [p1]
    
    def determine_approach_side(self, from_point, door_pos, orientation):
        """Determine which side we're approaching the door from"""
        dx = from_point[0] - door_pos[0]
        dy = from_point[1] - door_pos[1]
        
        if orientation == "horizontal":
            # For horizontal doors, check if approaching from north or south
            return "north" if dy < 0 else "south"
        else:
            # For vertical doors, check if approaching from east or west
            return "west" if dx < 0 else "east"
    
    def validate_path_with_entity_simulation(self, path, entity_size):
        """Simulate entity movement along path to detect issues"""
        if len(path) < 2:
            return path
        
        validated_path = [path[0]]  # Always include start
        
        for i in range(1, len(path)):
            current_pos = validated_path[-1]
            target_pos = path[i]
            
            # Simulate movement from current to target
            movement_valid, corrected_pos = self.simulate_movement_step(
                current_pos, target_pos, entity_size
            )
            
            if movement_valid:
                validated_path.append(target_pos)
            else:
                # Find alternative waypoint
                alternative = self.find_alternative_waypoint(
                    current_pos, target_pos, entity_size
                )
                if alternative:
                    validated_path.append(alternative)
                else:
                    # Can't proceed, truncate path
                    break
        
        return validated_path
    
    def simulate_movement_step(self, start, end, entity_size):
        """Simulate movement step and detect collision issues"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return True, end
        
        # Check multiple points along the movement path
        steps = max(int(distance * 4), 3)  # At least 3 steps
        
        for i in range(1, steps + 1):
            t = i / steps
            check_x = start[0] + dx * t
            check_y = start[1] + dy * t
            
            # Use enhanced collision detection
            if self.check_enhanced_collision(check_x, check_y, entity_size):
                # Find the last valid position
                if i == 1:
                    return False, start  # Can't move at all
                else:
                    # Return last valid position
                    valid_t = (i - 1) / steps
                    valid_x = start[0] + dx * valid_t
                    valid_y = start[1] + dy * valid_t
                    return False, (valid_x, valid_y)
        
        return True, end
    
    def check_enhanced_collision(self, x, y, entity_size):
        """Enhanced collision detection with predictive elements"""
        # Standard collision check
        if self.check_collision(x, y, entity_size):
            return True
        
        # Check for "squeeze" situations
        if self.is_squeeze_situation(x, y, entity_size):
            return True
        
        return False
    
    def is_squeeze_situation(self, x, y, entity_size):
        """Detect if entity would be squeezed between obstacles"""
        # Check if there are obstacles on opposite sides
        check_distance = entity_size + 0.2
        
        # Check cardinal directions for opposing obstacles
        obstacles = {
            'north': self.check_collision(x, y - check_distance, entity_size * 0.5),
            'south': self.check_collision(x, y + check_distance, entity_size * 0.5),
            'east': self.check_collision(x + check_distance, y, entity_size * 0.5),
            'west': self.check_collision(x - check_distance, y, entity_size * 0.5)
        }
        
        # If opposing sides have obstacles, it's a squeeze
        return (obstacles['north'] and obstacles['south']) or (obstacles['east'] and obstacles['west'])
    
    def find_alternative_waypoint(self, current_pos, target_pos, entity_size):
        """Find an alternative waypoint when direct movement fails"""
        # Try positions around the target
        offsets = [
            (0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3),
            (0.3, 0.3), (-0.3, 0.3), (0.3, -0.3), (-0.3, -0.3)
        ]
        
        for dx, dy in offsets:
            alt_x = target_pos[0] + dx
            alt_y = target_pos[1] + dy
            
            # Check if alternative position is valid and reachable
            if (not self.check_collision(alt_x, alt_y, entity_size) and
                self.has_line_of_sight(current_pos, (alt_x, alt_y), entity_size)):
                return (alt_x, alt_y)
        
        return None
    
    def has_line_of_sight(self, start, end, entity_size=0.4):
        """Check if there's a clear line of sight between two points"""
        start_x, start_y = start
        end_x, end_y = end
        
        # Calculate the number of steps to check along the line
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return True
        
        # Check points along the line
        steps = int(distance * 2)  # Check every 0.5 units
        for i in range(1, steps):
            t = i / steps
            check_x = start_x + dx * t
            check_y = start_y + dy * t
            
            # Check if this point is walkable
            grid_x = int(check_x)
            grid_y = int(check_y)
            
            if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
                return False
            
            if self.walkable[grid_y][grid_x] <= 0:
                return False
            
            # Check for blocking objects
            if self.check_collision(check_x, check_y, entity_size):
                return False
        
        return True
    
    def is_position_walkable(self, x, y, entity_size=0.4):
        """Check if a grid position is walkable for pathfinding"""
        # Check basic tile walkability
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        if self.walkable[y][x] <= 0:
            return False
        
        # Check for objects that block movement
        center_x = x + 0.5
        center_y = y + 0.5
        
        for obj in self.objects:
            if obj.blocks_movement:
                dist_x = center_x - obj.x
                dist_y = center_y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use slightly larger collision for pathfinding to avoid tight squeezes
                collision_distance = entity_size + 0.4
                if distance < collision_distance:
                    return False
        
        return True
    
    def is_position_walkable_lenient(self, x, y, entity_size=0.4):
        """Check if a grid position is walkable for pathfinding with more lenient rules"""
        # Check basic tile walkability
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        if self.walkable[y][x] <= 0:
            return False
        
        # Special handling for doors - be more lenient around door tiles
        current_tile = self.tiles[y][x]
        is_door_area = current_tile == self.TILE_DOOR
        
        # Also check adjacent tiles for doors
        if not is_door_area:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x, check_y = x + dx, y + dy
                    if (0 <= check_x < self.width and 0 <= check_y < self.height):
                        if self.tiles[check_y][check_x] == self.TILE_DOOR:
                            is_door_area = True
                            break
                if is_door_area:
                    break
        
        # Check for objects that block movement with smaller collision for pathfinding
        center_x = x + 0.5
        center_y = y + 0.5
        
        for obj in self.objects:
            if obj.blocks_movement:
                dist_x = center_x - obj.x
                dist_y = center_y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use much smaller collision for door areas, normal for others
                if is_door_area:
                    collision_distance = entity_size + 0.1  # Very lenient for doors
                else:
                    collision_distance = entity_size + 0.2  # Reduced from 0.4
                
                if distance < collision_distance:
                    return False
        
        return True
    
    def is_direct_path_clear(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Check if there's a clear direct path between two points"""
        # Calculate the distance and direction
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return True
        
        # Normalize direction
        step_x = dx / distance
        step_y = dy / distance
        
        # Check points along the path
        steps = int(distance * 4)  # Check every 0.25 units
        for i in range(1, steps + 1):
            check_x = start_x + (step_x * i * 0.25)
            check_y = start_y + (step_y * i * 0.25)
            
            # Check if we're near a door - if so, be more lenient with collision
            tile_x = int(check_x)
            tile_y = int(check_y)
            is_near_door = False
            
            if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
                # Check current tile and adjacent tiles for doors
                for dx_check in [-1, 0, 1]:
                    for dy_check in [-1, 0, 1]:
                        check_tile_x = tile_x + dx_check
                        check_tile_y = tile_y + dy_check
                        if (0 <= check_tile_x < self.width and 0 <= check_tile_y < self.height):
                            if self.tiles[check_tile_y][check_tile_x] == self.TILE_DOOR:
                                is_near_door = True
                                break
                    if is_near_door:
                        break
            
            # Use more lenient collision checking near doors
            if is_near_door:
                # Use smaller entity size for door areas
                if self.check_collision(check_x, check_y, entity_size * 0.7):
                    return False
            else:
                # Normal collision checking
                if self.check_collision(check_x, check_y, entity_size):
                    return False
        
        return True
    
    def find_nearest_walkable(self, x, y, entity_size=0.4, max_radius=5):
        """Find the nearest walkable position to the given coordinates"""
        # Check the position itself first
        if (0 <= x < self.width and 0 <= y < self.height and 
            self.walkable[y][x] > 0):
            return x, y
        
        # Search in expanding circles
        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Only check positions on the edge of the current radius
                    if abs(dx) == radius or abs(dy) == radius:
                        check_x = x + dx
                        check_y = y + dy
                        
                        if (0 <= check_x < self.width and 0 <= check_y < self.height and
                            self.walkable[check_y][check_x] > 0):
                            return check_x, check_y
        
        return None, None  # No walkable position found
    
    def update_camera(self, screen_width, screen_height):
        """Update camera to follow player"""
        # Convert player position to isometric coordinates
        player_iso_x, player_iso_y = self.iso_renderer.cart_to_iso(self.player.x, self.player.y)
        
        # Center camera on player
        self.camera_x = player_iso_x - screen_width // 2
        self.camera_y = player_iso_y - screen_height // 2
    
    def handle_event(self, event):
        """Handle level events"""
        # Check if dialogue window is open and handle its events first
        if self.player.current_dialogue and self.player.current_dialogue.show:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.current_dialogue.handle_click(event.pos):
                    return  # Dialogue consumed the event
        
        # Check if any shop is open and handle shop events
        for npc in self.npcs:
            if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if npc.shop.handle_click(event.pos, self.player):
                        return  # Shop consumed the event
        
        # Handle mouse clicks for interaction and movement
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos)
            elif event.button == 3:  # Right click
                self.handle_right_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                print("Zoom in (not implemented)")
            elif event.button == 5:  # Mouse wheel down
                print("Zoom out (not implemented)")
    
    def handle_click(self, pos):
        """Handle mouse click at position"""
        # Check if clicking on inventory button
        if hasattr(self, 'inventory_button_rect') and self.inventory_button_rect.collidepoint(pos):
            # Toggle inventory
            self.player.inventory.show = not self.player.inventory.show
            if self.player.game_log:
                if self.player.inventory.show:
                    self.player.game_log.add_message("Inventory opened", "system")
                else:
                    self.player.game_log.add_message("Inventory closed", "system")
            return
        
        # Convert screen position to world position
        world_x, world_y = self.iso_renderer.screen_to_world(pos[0], pos[1], self.camera_x, self.camera_y)
        
        # Let the player handle the click
        self.player.handle_mouse_click(world_x, world_y, self)
    
    def handle_right_click(self, pos):
        """Handle right mouse click for context actions"""
        # Convert screen position to world position
        world_x, world_y = self.iso_renderer.screen_to_world(pos[0], pos[1], self.camera_x, self.camera_y)
        
        # Check what was right-clicked
        clicked_entity = None
        
        # Check enemies for info
        for enemy in self.enemies:
            if abs(world_x - enemy.x) < 1.2 and abs(world_y - enemy.y) < 1.2:
                if self.player.game_log:
                    self.player.game_log.add_message(f"{enemy.name}: Health {enemy.health}/{enemy.max_health}, Damage {enemy.damage}", "system")
                clicked_entity = enemy
                break
        
        # Check NPCs for info
        if not clicked_entity:
            for npc in self.npcs:
                if abs(world_x - npc.x) < 1.2 and abs(world_y - npc.y) < 1.2:
                    if self.player.game_log:
                        # Just show NPC info on right-click, not dialog
                        npc_info = f"{npc.name}"
                        if npc.has_shop:
                            npc_info += " (Shopkeeper)"
                        self.player.game_log.add_message(npc_info, "system")
                    clicked_entity = npc
                    break
        
        # Check chests for info
        if not clicked_entity:
            for chest in self.chests:
                if abs(world_x - chest.x) < 1.2 and abs(world_y - chest.y) < 1.2:
                    if self.player.game_log:
                        status = "Empty" if chest.is_opened else "Unopened"
                        chest_info = f"{chest.name} ({status})"
                        if not chest.is_opened:
                            chest_info += f" - {len(chest.loot_items)} items inside"
                        self.player.game_log.add_message(chest_info, "system")
                    clicked_entity = chest
                    break
        
        # Check items for info
        if not clicked_entity:
            for item in self.items:
                if abs(world_x - item.x) < 1.2 and abs(world_y - item.y) < 1.2:
                    effect_str = ", ".join([f"{k}: {v}" for k, v in item.effect.items()])
                    if self.player.game_log:
                        self.player.game_log.add_message(f"{item.name} ({item.item_type}): {effect_str}", "item")
                    clicked_entity = item
                    break
        
        if not clicked_entity:
            # Show tile info
            tile_x = int(world_x)
            tile_y = int(world_y)
            if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
                tile_names = {
                    self.TILE_GRASS: "Grass",
                    self.TILE_DIRT: "Dirt",
                    self.TILE_STONE: "Stone Path",
                    self.TILE_WATER: "Water",
                    self.TILE_WALL: "Wall",
                    self.TILE_DOOR: "Door",
                    self.TILE_BRICK: "Brick Floor"
                }
                tile_type = self.tiles[tile_y][tile_x]
                tile_name = tile_names.get(tile_type, "Unknown")
                walkable_value = self.walkable[tile_y][tile_x]
                if walkable_value <= 0:
                    walkable = "blocked"
                elif walkable_value < 1:
                    walkable = f"restricted ({walkable_value:.1f})"
                else:
                    walkable = "walkable"
                if self.player.game_log:
                    self.player.game_log.add_message(f"Tile ({tile_x}, {tile_y}): {tile_name} ({walkable})", "system")
    
    def update(self):
        """Update level logic"""
        # Handle player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self)  # Pass level to handle_input
        
        # Update player
        self.player.update(self)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self, self.player)
            
            # Track combat state for music
            enemy_in_combat = enemy.state in ["chasing", "attacking"]
            enemy_id = id(enemy)  # Use object id as unique identifier
            
            if enemy_in_combat:
                if enemy_id not in self.enemies_in_combat:
                    self.enemies_in_combat.add(enemy_id)
                    # Start combat music if this is the first enemy to enter combat
                    if len(self.enemies_in_combat) == 1:
                        audio = getattr(self.asset_loader, 'audio_manager', None)
                        if audio:
                            audio.start_combat_music()
            else:
                if enemy_id in self.enemies_in_combat:
                    self.enemies_in_combat.discard(enemy_id)
            
            # Check if enemy is dead
            if enemy.health <= 0:
                # Remove from combat tracking if dead
                if enemy_id in self.enemies_in_combat:
                    self.enemies_in_combat.discard(enemy_id)
                
                # Update quest progress for enemy kills
                if hasattr(self.player, 'game') and hasattr(self.player.game, 'quest_manager'):
                    quest_manager = self.player.game.quest_manager
                    quest_manager.update_quest_progress("kill", enemy.name)
                    quest_manager.update_quest_progress("kill", "any")  # For generic kill quests
                
                self.enemies.remove(enemy)
                self.player.gain_experience(enemy.experience)
                
                # Improved loot drops - more frequent and varied
                drop_chance = 0.9 if enemy.is_boss else 0.8  # 90% for bosses, 80% for regular enemies
                if random.random() < drop_chance:
                    # Multiple possible drops for bosses
                    num_drops = 2 if enemy.is_boss else 1
                    
                    for _ in range(num_drops):
                        item_type = random.choice(["consumable", "weapon", "armor", "misc"])
                        if item_type == "consumable":
                            potion_types = ["Health Potion", "Stamina Potion", "Mana Potion", "Antidote", "Strength Potion"]
                            potion_type = random.choice(potion_types)
                            
                            if potion_type == "Health Potion":
                                item = Item(enemy.x, enemy.y, "Health Potion", item_type="consumable", 
                                          effect={"health": 50}, asset_loader=self.asset_loader)
                            elif potion_type == "Stamina Potion":
                                item = Item(enemy.x, enemy.y, "Stamina Potion", item_type="consumable", 
                                          effect={"stamina": 30}, asset_loader=self.asset_loader)
                            elif potion_type == "Mana Potion":
                                item = Item(enemy.x, enemy.y, "Mana Potion", item_type="consumable", 
                                          effect={"mana": 40}, asset_loader=self.asset_loader)
                            elif potion_type == "Antidote":
                                item = Item(enemy.x, enemy.y, "Antidote", item_type="consumable", 
                                          effect={"cure_poison": True}, asset_loader=self.asset_loader)
                            else:  # Strength Potion
                                item = Item(enemy.x, enemy.y, "Strength Potion", item_type="consumable", 
                                          effect={"damage_boost": 10, "duration": 60}, asset_loader=self.asset_loader)
                        elif item_type == "weapon":
                            weapon_names = ["Iron Sword", "Steel Axe", "Bronze Mace", "Silver Dagger", "War Hammer", 
                                          "Magic Bow", "Crystal Staff", "Throwing Knife", "Crossbow"]
                            weapon_name = random.choice(weapon_names)
                            damage_bonus = (10 if enemy.is_boss else 5) + random.randint(0, 10)
                            item = Item(enemy.x, enemy.y, weapon_name, item_type="weapon", 
                                      effect={"damage": damage_bonus}, asset_loader=self.asset_loader)
                        elif item_type == "armor":
                            armor_names = ["Leather Armor", "Chain Mail", "Plate Armor", "Studded Leather", "Scale Mail",
                                         "Dragon Scale Armor", "Mage Robes", "Royal Armor"]
                            armor_name = random.choice(armor_names)
                            defense_bonus = (8 if enemy.is_boss else 4) + random.randint(0, 8)
                            item = Item(enemy.x, enemy.y, armor_name, item_type="armor", 
                                      effect={"defense": defense_bonus}, asset_loader=self.asset_loader)
                        else:  # misc items
                            misc_items = [
                                ("Gold Ring", {"magic_resistance": 5}),
                                ("Magic Scroll", {"spell_power": 15}),
                                ("Crystal Gem", {"value": 100})
                            ]
                            item_name, effect = random.choice(misc_items)
                            item = Item(enemy.x, enemy.y, item_name, item_type="misc", 
                                      effect=effect, asset_loader=self.asset_loader)
                        
                        self.items.append(item)
                        
                        # Offset multiple drops slightly
                        if num_drops > 1:
                            item.x += random.uniform(-0.5, 0.5)
                            item.y += random.uniform(-0.5, 0.5)
        
        # Handle combat music transitions
        if len(self.enemies_in_combat) == 0:
            # No enemies in combat, start timer to end combat music
            self.combat_music_timer += 1
            if self.combat_music_timer >= 180:  # 3 seconds at 60 FPS
                audio = getattr(self.asset_loader, 'audio_manager', None)
                if audio and audio.is_combat_music_active():
                    audio.end_combat_music()
                self.combat_music_timer = 0
        else:
            # Reset timer if combat is active
            self.combat_music_timer = 0
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(self)
        
        # Update items
        for item in self.items:
            item.update(self)
    
    def render(self, screen):
        """Render the level with improved isometric building rendering"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Reserve space for bottom UI
        ui_height = 150
        game_area_height = screen_height - ui_height
        
        # Update camera
        self.update_camera(screen_width, game_area_height)
        
        # Create game area surface
        game_surface = pygame.Surface((screen_width, game_area_height))
        game_surface.fill((0, 0, 0))
        
        # Calculate visible tile range - much larger rendering area
        visible_width = (screen_width // self.tile_width) + 30  # Much larger area
        visible_height = (game_area_height // (self.tile_height // 2)) + 30  # Much larger area
        
        # Calculate center tile
        center_x = int(self.player.x)
        center_y = int(self.player.y)
        
        # Calculate tile range - render much more area
        start_x = max(0, center_x - visible_width)  # Remove // 2 to get full range
        end_x = min(self.width, center_x + visible_width)
        start_y = max(0, center_y - visible_height)  # Remove // 2 to get full range
        end_y = min(self.height, center_y + visible_height)
        
        # Render tiles in proper isometric order (back to front)
        # This ensures proper depth sorting for buildings
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.render_tile_at_position(game_surface, x, y)
        
        # Collect all entities for depth sorting
        all_entities = []
        all_entities.append(self.player)
        all_entities.extend(self.enemies)
        all_entities.extend(self.npcs)
        all_entities.extend(self.items)
        all_entities.extend(self.objects)
        all_entities.extend(self.chests)
        
        # Sort entities by depth
        sorted_entities = sort_by_depth(all_entities)
        
        # Render entities to game surface
        for entity in sorted_entities:
            entity.render(game_surface, self.iso_renderer, self.camera_x, self.camera_y)
        
        # Debug: Render pathfinding visualization if player has a path
        if hasattr(self.player, 'path') and self.player.path and len(self.player.path) > 1:
            self.render_path_debug(game_surface, self.player.path)
        
        # Blit game surface to main screen
        screen.blit(game_surface, (0, 0))
        
        # Render XP bar at the top
        self.render_xp_bar(screen)
        
        # Render UI on top
        self.render_ui(screen)
        
        # Render shops on top of everything
        for npc in self.npcs:
            if hasattr(npc, 'shop') and npc.shop:
                # Set player items for sell mode
                npc.shop.set_player_items(self.player.inventory.items)
                npc.shop.render(screen)
        
        # Render dialogue window on top of everything
        if self.player.current_dialogue and self.player.current_dialogue.show:
            self.player.current_dialogue.render(screen)
    
    def render_tile_at_position(self, surface, x, y):
        """Render a single tile with new flat surface wall system"""
        tile_type = self.tiles[y][x]
        height = self.heightmap[y][x]
        
        # Calculate screen position using proper isometric conversion
        screen_x, screen_y = self.iso_renderer.world_to_screen(x, y, self.camera_x, self.camera_y)
        
        # Adjust for height
        screen_y -= height * 16
        
        # ALWAYS render floor tile first (even under walls)
        floor_sprite = None
        if self.wall_renderer.is_wall_tile(tile_type):
            # Render appropriate floor tile underneath walls
            if tile_type == self.TILE_DOOR:
                floor_sprite = self.tile_sprites[self.TILE_STONE]  # Stone under doors
            else:
                floor_sprite = self.tile_sprites[self.TILE_BRICK]  # Brick under walls (interior)
        else:
            # Normal floor tiles
            floor_sprite = self.tile_sprites[tile_type]
        
        if floor_sprite:
            floor_rect = floor_sprite.get_rect()
            floor_rect.center = (screen_x, screen_y)
            surface.blit(floor_sprite, floor_rect)
        
        # Now render walls using flat surfaces
        if self.wall_renderer.is_wall_tile(tile_type):
            self.wall_renderer.render_flat_wall(surface, screen_x, screen_y, tile_type, x, y)
        elif tile_type == self.TILE_DOOR:
            self.door_renderer.render_door_tile(surface, screen_x, screen_y, tile_type, self, self.tile_width, self.tile_height)
    
    
    
    
    
    
    
    
    def render_ui(self, screen):
        """Render enhanced game UI"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create UI panel at bottom
        ui_height = 150
        ui_panel = pygame.Surface((screen_width, ui_height))
        ui_panel.fill((40, 40, 40))  # Dark gray background
        
        # Draw border
        pygame.draw.rect(ui_panel, (100, 100, 100), (0, 0, screen_width, ui_height), 2)
        
        # Left side - Player stats with circular health/stamina bars
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        # Render circular health and stamina bars
        self.render_circular_bars(ui_panel, 20, 30)
        
        # Player level and gold (moved to top right of circles area)
        stats_x = 160
        level_text = f"Level {self.player.level}"
        gold_text = f"Gold: {self.player.gold}"
        
        level_surface = small_font.render(level_text, True, (255, 215, 0))  # Gold color for level
        gold_surface = small_font.render(gold_text, True, (255, 215, 0))   # Gold color for gold
        ui_panel.blit(level_surface, (stats_x, 15))
        ui_panel.blit(gold_surface, (stats_x, 35))
        
        # Center-left - Equipment display
        equipment_x = 280
        slot_size = 80
        slot_y = 30
        
        # Current weapon display
        weapon_rect = pygame.Rect(equipment_x, slot_y, slot_size, slot_size)
        pygame.draw.rect(ui_panel, (60, 60, 60), weapon_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), weapon_rect, 2)
        
        # Weapon label above slot
        weapon_text = font.render("Weapon", True, (255, 255, 255))
        ui_panel.blit(weapon_text, (equipment_x, slot_y - 25))
        
        if self.player.equipped_weapon:
            # Draw actual weapon sprite if available
            if hasattr(self.player.equipped_weapon, 'sprite') and self.player.equipped_weapon.sprite:
                scaled_weapon = pygame.transform.scale(self.player.equipped_weapon.sprite, (slot_size - 8, slot_size - 8))
                weapon_sprite_rect = scaled_weapon.get_rect()
                weapon_sprite_rect.center = weapon_rect.center
                ui_panel.blit(scaled_weapon, weapon_sprite_rect)
            else:
                # Fallback to simple shape
                pygame.draw.rect(ui_panel, (192, 192, 192), (equipment_x + 20, slot_y + 15, slot_size - 40, slot_size - 20))
            
            # Weapon name below slot
            weapon_name = small_font.render(self.player.equipped_weapon.name[:12], True, (255, 255, 255))
            ui_panel.blit(weapon_name, (equipment_x, slot_y + slot_size + 5))
        else:
            no_weapon = small_font.render("No Weapon", True, (150, 150, 150))
            no_weapon_rect = no_weapon.get_rect(center=weapon_rect.center)
            ui_panel.blit(no_weapon, no_weapon_rect)
        
        # Current armor display
        armor_x = equipment_x + slot_size + 30
        armor_rect = pygame.Rect(armor_x, slot_y, slot_size, slot_size)
        pygame.draw.rect(ui_panel, (60, 60, 60), armor_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), armor_rect, 2)
        
        # Armor label above slot
        armor_text = font.render("Armor", True, (255, 255, 255))
        ui_panel.blit(armor_text, (armor_x, slot_y - 25))
        
        if self.player.equipped_armor:
            # Draw actual armor sprite if available
            if hasattr(self.player.equipped_armor, 'sprite') and self.player.equipped_armor.sprite:
                scaled_armor = pygame.transform.scale(self.player.equipped_armor.sprite, (slot_size - 8, slot_size - 8))
                armor_sprite_rect = scaled_armor.get_rect()
                armor_sprite_rect.center = armor_rect.center
                ui_panel.blit(scaled_armor, armor_sprite_rect)
            else:
                # Fallback to simple shape
                pygame.draw.ellipse(ui_panel, (139, 69, 19), (armor_x + 20, slot_y + 15, slot_size - 40, slot_size - 20))
            
            # Armor name below slot
            armor_name = small_font.render(self.player.equipped_armor.name[:12], True, (255, 255, 255))
            ui_panel.blit(armor_name, (armor_x, slot_y + slot_size + 5))
        else:
            no_armor = small_font.render("No Armor", True, (150, 150, 150))
            no_armor_rect = no_armor.get_rect(center=armor_rect.center)
            ui_panel.blit(no_armor, no_armor_rect)
        
        # Inventory button
        inv_button_x = armor_x + slot_size + 20
        inv_button = pygame.Rect(inv_button_x, 20, 100, 40)
        pygame.draw.rect(ui_panel, (80, 80, 80), inv_button)
        pygame.draw.rect(ui_panel, (120, 120, 120), inv_button, 2)
        
        inv_text = font.render("Inventory", True, (255, 255, 255))
        text_rect = inv_text.get_rect(center=inv_button.center)
        ui_panel.blit(inv_text, text_rect)
        
        # Store button rect for click detection (adjust for screen position)
        self.inventory_button_rect = pygame.Rect(inv_button_x, screen_height - ui_height + 20, 100, 40)
        
        # Right side - Game log with proper message rendering
        log_x = screen_width - 350
        log_width = 340
        log_height = ui_height - 20
        
        log_panel = pygame.Surface((log_width, log_height))
        log_panel.fill((30, 30, 30))  # Darker background for log
        pygame.draw.rect(log_panel, (80, 80, 80), (0, 0, log_width, log_height), 2)
        
        # Game log title
        log_title = font.render("Game Log:", True, (200, 200, 200))
        log_panel.blit(log_title, (5, 5))
        
        # Render recent messages properly
        if hasattr(self.player, 'game_log') and self.player.game_log:
            recent_messages = self.player.game_log.messages[-6:]  # Last 6 messages
            for i, message_data in enumerate(recent_messages):
                # Handle both old tuple format and new dict format
                if isinstance(message_data, dict):
                    message = message_data.get('text', str(message_data))
                    msg_type = message_data.get('type', 'system')
                elif isinstance(message_data, tuple) and len(message_data) >= 2:
                    message, msg_type = message_data[:2]
                else:
                    message = str(message_data)
                    msg_type = "system"
                
                color = self.player.game_log.get_message_color(msg_type)
                # Truncate long messages to fit in the log panel
                if len(message) > 40:
                    message = message[:37] + "..."
                msg_surface = small_font.render(message, True, color)
                log_panel.blit(msg_surface, (5, 30 + i * 18))
        
        ui_panel.blit(log_panel, (log_x, 10))
        
        # Blit the entire UI panel to screen
        screen.blit(ui_panel, (0, screen_height - ui_height))
        
        # Instructions removed - UI is now self-explanatory
    
    def render_circular_bars(self, surface, x, y):
        """Render circular health and stamina bars"""
        import math
        
        # Circle parameters
        radius = 35
        thickness = 8
        
        # Health circle (red)
        health_center = (x + radius, y + radius)
        health_percentage = self.player.health / self.player.max_health
        
        # Draw background circle for health
        pygame.draw.circle(surface, (60, 20, 20), health_center, radius, thickness)
        
        # Draw health arc
        if health_percentage > 0:
            # Calculate arc angle (0 to 2*pi)
            end_angle = health_percentage * 2 * math.pi - math.pi/2  # Start from top
            start_angle = -math.pi/2
            
            # Draw filled arc for health
            points = [health_center]
            for angle in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi) + 1):
                angle_rad = angle * math.pi / 180
                point_x = health_center[0] + (radius - thickness//2) * math.cos(angle_rad)
                point_y = health_center[1] + (radius - thickness//2) * math.sin(angle_rad)
                points.append((point_x, point_y))
            
            if len(points) > 2:
                # Draw the health arc as a thick line
                for i in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
                    angle_rad = i * math.pi / 180
                    start_x = health_center[0] + (radius - thickness) * math.cos(angle_rad)
                    start_y = health_center[1] + (radius - thickness) * math.sin(angle_rad)
                    end_x = health_center[0] + radius * math.cos(angle_rad)
                    end_y = health_center[1] + radius * math.sin(angle_rad)
                    pygame.draw.line(surface, (220, 50, 50), (start_x, start_y), (end_x, end_y), 2)
        
        # Health text - show current/max format
        health_text = f"{self.player.health}/{self.player.max_health}"
        font = pygame.font.Font(None, 18)  # Smaller font to fit the text
        text_surface = font.render(health_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=health_center)
        surface.blit(text_surface, text_rect)
        
        # Health label
        health_label = font.render("Health", True, (255, 255, 255))
        surface.blit(health_label, (x, y + radius * 2 + 10))
        
        # Stamina circle (blue) - using stamina instead of mana
        stamina_center = (x + radius * 3, y + radius)
        stamina_percentage = self.player.stamina / self.player.max_stamina
        
        # Draw background circle for stamina
        pygame.draw.circle(surface, (20, 20, 60), stamina_center, radius, thickness)
        
        # Draw stamina arc
        if stamina_percentage > 0:
            # Calculate arc angle (0 to 2*pi)
            end_angle = stamina_percentage * 2 * math.pi - math.pi/2  # Start from top
            start_angle = -math.pi/2
            
            # Draw the stamina arc as a thick line
            for i in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
                angle_rad = i * math.pi / 180
                start_x = stamina_center[0] + (radius - thickness) * math.cos(angle_rad)
                start_y = stamina_center[1] + (radius - thickness) * math.sin(angle_rad)
                end_x = stamina_center[0] + radius * math.cos(angle_rad)
                end_y = stamina_center[1] + radius * math.sin(angle_rad)
                pygame.draw.line(surface, (50, 150, 220), (start_x, start_y), (end_x, end_y), 2)
        
        # Stamina text - show current/max format
        stamina_text = f"{self.player.stamina}/{self.player.max_stamina}"
        text_surface = font.render(stamina_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=stamina_center)
        surface.blit(text_surface, text_rect)
        
        # Stamina label
        stamina_label = font.render("Stamina", True, (255, 255, 255))
        surface.blit(stamina_label, (x + radius * 2, y + radius * 2 + 10))
    
    def render_xp_bar(self, screen):
        """Render experience bar at the top of the screen"""
        screen_width = screen.get_width()
        
        # XP bar dimensions
        bar_width = screen_width - 40  # Leave 20px margin on each side
        bar_height = 20
        bar_x = 20
        bar_y = 10
        
        # Calculate XP percentage
        xp_percentage = self.player.experience / self.player.experience_to_next
        
        # Draw background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw XP fill
        if xp_percentage > 0:
            fill_width = int(bar_width * xp_percentage)
            # Gradient effect - brighter in the middle
            for i in range(fill_width):
                intensity = 1.0 - abs(i - fill_width/2) / (fill_width/2) if fill_width > 0 else 1.0
                color = (
                    int(255 * intensity * 0.8),  # Gold color
                    int(215 * intensity * 0.8),
                    int(0 * intensity * 0.8)
                )
                pygame.draw.line(screen, color, (bar_x + i, bar_y + 2), (bar_x + i, bar_y + bar_height - 2))
        
        # Draw XP text
        font = pygame.font.Font(None, 18)
        xp_text = f"XP: {self.player.experience}/{self.player.experience_to_next}"
        text_surface = font.render(xp_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
        screen.blit(text_surface, text_rect)
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "name": self.name,
            "tiles": self.tiles,
            "heightmap": self.heightmap,
            "enemies": [enemy.get_save_data() for enemy in self.enemies],
            "npcs": [npc.get_save_data() for npc in self.npcs],
            "items": [item.get_save_data() for item in self.items],
            "objects": [obj.get_save_data() for obj in self.objects],
            "chests": [chest.get_save_data() for chest in self.chests],
            "camera_x": self.camera_x,
            "camera_y": self.camera_y
            # Note: Combat state is not saved as it should reset on load
        }
    
    @classmethod
    def from_save_data(cls, data, player, asset_loader):
        """Create level from save data"""
        level = cls(data["name"], player, asset_loader)
        level.tiles = data["tiles"]
        level.heightmap = data["heightmap"]
        level.camera_x = data["camera_x"]
        level.camera_y = data["camera_y"]
        
        # Reset combat state on load
        level.enemies_in_combat = set()
        level.combat_music_timer = 0
        
        # Recreate entities
        level.enemies = []
        for enemy_data in data["enemies"]:
            enemy = Enemy.from_save_data(enemy_data, asset_loader)
            level.enemies.append(enemy)
        
        level.npcs = []
        for npc_data in data["npcs"]:
            npc = NPC.from_save_data(npc_data, asset_loader)
            level.npcs.append(npc)
        
        level.items = []
        for item_data in data["items"]:
            item = Item.from_save_data(item_data, asset_loader)
            level.items.append(item)
        
        level.objects = []
        for obj_data in data["objects"]:
            obj = Entity.from_save_data(obj_data, asset_loader)
            level.objects.append(obj)
        
        level.chests = []
        for chest_data in data.get("chests", []):  # Use get() for backward compatibility
            chest = Chest.from_save_data(chest_data, asset_loader)
            level.chests.append(chest)
        
        return level