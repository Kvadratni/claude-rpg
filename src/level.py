"""
Level system for the RPG
"""

import pygame
import random
import math
import heapq
from .isometric import IsometricRenderer, sort_by_depth
from .entity import Entity, NPC, Enemy, Item, Chest

class Level:
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
        self.width = 120  # Much bigger map
        self.height = 120
        
        # Isometric renderer
        self.iso_renderer = IsometricRenderer(64, 32)
        self.tile_width = self.iso_renderer.tile_width
        self.tile_height = self.iso_renderer.tile_height
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Generate level
        self.tiles = self.generate_level()
        self.heightmap = self.generate_heightmap()
        
        # Generate pathfinding grid AFTER tiles are created
        self.walkable = self.generate_walkable_grid()
        
        # Entities
        self.npcs = []
        self.enemies = []
        self.items = []
        self.objects = []  # Static objects like trees, rocks, etc.
        self.chests = []   # Treasure chests
        
        # Combat state tracking
        self.enemies_in_combat = set()  # Track which enemies are in combat
        self.combat_music_timer = 0     # Timer for combat music fade out
        
        # Spawn entities
        self.spawn_entities()
        
        # Create tile sprites
        self.create_tile_sprites()
    
    def generate_level(self):
        """Generate a well-designed static level layout"""
        tiles = []
        
        # Initialize with grass
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(self.TILE_GRASS)
            tiles.append(row)
        
        # Create border walls
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    tiles[y][x] = self.TILE_WALL
        
        # VILLAGE AREA (Center-South)
        village_center_x, village_center_y = 60, 80
        
        # Village square with stone paths
        for x in range(50, 71):
            for y in range(75, 86):
                tiles[y][x] = self.TILE_STONE
        
        # Village buildings
        self.create_building(tiles, 45, 70, 12, 8)   # Shopkeeper's store
        self.create_building(tiles, 65, 70, 12, 8)   # Elder's house
        self.create_building(tiles, 52, 88, 16, 10)  # Village hall
        
        # Village paths
        for x in range(30, 91):  # Main east-west road
            tiles[82][x] = self.TILE_STONE
            tiles[83][x] = self.TILE_STONE
        
        for y in range(60, 95):  # Main north-south road
            tiles[y][60] = self.TILE_STONE
            tiles[y][61] = self.TILE_STONE
        
        # FOREST AREA (North-West) - Goblin territory
        forest_center_x, forest_center_y = 30, 30
        for y in range(15, 45):
            for x in range(15, 45):
                if random.random() < 0.4:  # 40% dirt patches in forest
                    tiles[y][x] = self.TILE_DIRT
        
        # Forest clearing for combat
        for y in range(25, 35):
            for x in range(25, 35):
                tiles[y][x] = self.TILE_DIRT
        
        # MOUNTAIN PASS (North-East) - Orc Chief lair
        mountain_x, mountain_y = 90, 20
        
        # Rocky mountain path
        for y in range(15, 35):
            for x in range(80, 100):
                if (x + y) % 3 == 0:  # Create rocky pattern
                    tiles[y][x] = self.TILE_STONE
                elif (x + y) % 4 == 0:
                    tiles[y][x] = self.TILE_DIRT
        
        # Orc Chief arena
        for y in range(18, 28):
            for x in range(85, 95):
                tiles[y][x] = self.TILE_STONE
        
        # LAKE AREA (South-East) - Peaceful area
        lake_center_x, lake_center_y = 85, 85
        self.create_lake(tiles, lake_center_x, lake_center_y, 12)
        
        # Lake shore paths
        for x in range(75, 95):
            tiles[95][x] = self.TILE_DIRT
        for y in range(75, 95):
            tiles[y][95] = self.TILE_DIRT
        
        # CONNECTING PATHS
        # Village to Forest
        self.create_dirt_path(tiles, 45, 75, 30, 40)
        
        # Village to Mountain
        self.create_dirt_path(tiles, 70, 75, 85, 30)
        
        # Village to Lake
        self.create_dirt_path(tiles, 70, 85, 85, 85)
        
        # Ensure player starting area is clear (village center)
        start_x, start_y = 60, 82
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if 0 <= start_x + dx < self.width and 0 <= start_y + dy < self.height:
                    if tiles[start_y + dy][start_x + dx] == self.TILE_WALL:
                        tiles[start_y + dy][start_x + dx] = self.TILE_STONE
        
        return tiles
    
    def create_building(self, tiles, start_x, start_y, width, height):
        """Create a building structure with varied wall types and windows"""
        # Building interior floor - use brick tiles for more realistic interiors
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                tiles[y][x] = self.TILE_BRICK  # Interior brick floor
        
        # Building walls with proper corners and variations
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                # Skip interior
                if (x > start_x and x < start_x + width - 1 and 
                    y > start_y and y < start_y + height - 1):
                    continue
                
                # Determine wall type based on position
                is_top = (y == start_y)
                is_bottom = (y == start_y + height - 1)
                is_left = (x == start_x)
                is_right = (x == start_x + width - 1)
                
                # Corners - Swap TL with BR for isometric perspective
                if is_top and is_left:
                    tiles[y][x] = self.TILE_WALL_CORNER_BR  # Swap TL with BR
                elif is_top and is_right:
                    tiles[y][x] = self.TILE_WALL_CORNER_TR  # Keep TR as TR
                elif is_bottom and is_left:
                    tiles[y][x] = self.TILE_WALL_CORNER_BL  # Keep BL as BL  
                elif is_bottom and is_right:
                    tiles[y][x] = self.TILE_WALL_CORNER_TL  # Swap BR with TL
                # Horizontal walls (top and bottom)
                elif is_top or is_bottom:
                    # Add some windows to horizontal walls (not too many)
                    if random.random() < 0.3 and width > 6:  # 30% chance for windows on longer walls
                        tiles[y][x] = self.TILE_WALL_WINDOW_HORIZONTAL
                    else:
                        tiles[y][x] = self.TILE_WALL_HORIZONTAL
                # Vertical walls (left and right)
                elif is_left or is_right:
                    # Add some windows to vertical walls
                    if random.random() < 0.25 and height > 6:  # 25% chance for windows on taller walls
                        tiles[y][x] = self.TILE_WALL_WINDOW_VERTICAL
                    else:
                        tiles[y][x] = self.TILE_WALL_VERTICAL
                else:
                    # Fallback to regular wall
                    tiles[y][x] = self.TILE_WALL
        
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
        """Generate a grid of walkable tiles for pathfinding"""
        walkable = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Check if tile is walkable
                tile_type = self.tiles[y][x]
                if tile_type in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE, self.TILE_DOOR, self.TILE_BRICK]:
                    row.append(True)
                else:
                    # All wall types are not walkable
                    row.append(False)
            walkable.append(row)
        
        # Don't mirror the walkable grid
        return walkable
    
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
        
        # Load base wall image
        wall_image = self.asset_loader.get_image("wall_tile")
        if wall_image:
            # Scale wall to be taller and more prominent
            wall_height = self.tile_height + 32  # Make walls taller
            base_wall_sprite = pygame.transform.scale(wall_image, (self.tile_width + 8, wall_height))
            
            # Create variations of the wall sprite
            self.tile_sprites[self.TILE_WALL] = base_wall_sprite
            
            # Load dedicated wall assets instead of creating programmatically
            self.load_corner_wall_sprites()
            self.load_directional_wall_sprites()
            self.load_window_wall_sprites()
            
        else:
            # Fallback to generated sprites
            base_wall = self.iso_renderer.create_cube_tile((200, 200, 200), (150, 150, 150), (100, 100, 100))
            self.tile_sprites[self.TILE_WALL] = base_wall
            
            # Create simple variations for fallback
            self.tile_sprites[self.TILE_WALL_CORNER_TL] = base_wall
            self.tile_sprites[self.TILE_WALL_CORNER_TR] = base_wall
            self.tile_sprites[self.TILE_WALL_CORNER_BL] = base_wall
            self.tile_sprites[self.TILE_WALL_CORNER_BR] = base_wall
            self.tile_sprites[self.TILE_WALL_HORIZONTAL] = base_wall
            self.tile_sprites[self.TILE_WALL_VERTICAL] = base_wall
            self.tile_sprites[self.TILE_WALL_WINDOW] = base_wall
            self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = base_wall
            self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = base_wall
        
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
        
        # Door - create enhanced door with better visibility
        door_image = self.asset_loader.get_image("door_tile")
        if door_image:
            # Scale door to be taller and more prominent
            door_height = self.tile_height + 24  # Make doors taller than normal tiles
            scaled_door = pygame.transform.scale(door_image, (self.tile_width, door_height))
            
            # Create enhanced door sprite with shadow and highlight
            enhanced_door = pygame.Surface((self.tile_width + 4, door_height + 4), pygame.SRCALPHA)
            
            # Add shadow (dark outline)
            shadow_door = scaled_door.copy()
            shadow_door.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            enhanced_door.blit(shadow_door, (2, 2))
            
            # Add main door
            enhanced_door.blit(scaled_door, (0, 0))
            
            # Add highlight for better visibility
            highlight = pygame.Surface((self.tile_width, door_height), pygame.SRCALPHA)
            highlight.fill((255, 255, 200, 30))  # Subtle yellow highlight
            enhanced_door.blit(highlight, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
            
            self.tile_sprites[self.TILE_DOOR] = enhanced_door
        else:
            self.tile_sprites[self.TILE_DOOR] = self.iso_renderer.create_cube_tile((150, 100, 50), (120, 80, 40), (100, 60, 30))
    
    def create_wall_corner_sprites(self, base_wall_sprite):
        """Create corner wall variations from base wall sprite"""
        # Top-left corner - add corner accent
        tl_corner = base_wall_sprite.copy()
        # Add a small corner decoration (darker edge)
        corner_size = 8
        pygame.draw.rect(tl_corner, (120, 120, 120), (0, 0, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_TL] = tl_corner
        
        # Top-right corner
        tr_corner = base_wall_sprite.copy()
        pygame.draw.rect(tr_corner, (120, 120, 120), 
                        (base_wall_sprite.get_width() - corner_size, 0, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_TR] = tr_corner
        
        # Bottom-left corner
        bl_corner = base_wall_sprite.copy()
        pygame.draw.rect(bl_corner, (120, 120, 120), 
                        (0, base_wall_sprite.get_height() - corner_size, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_BL] = bl_corner
        
        # Bottom-right corner
        br_corner = base_wall_sprite.copy()
        pygame.draw.rect(br_corner, (120, 120, 120), 
                        (base_wall_sprite.get_width() - corner_size, 
                         base_wall_sprite.get_height() - corner_size, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_BR] = br_corner
    
    def create_wall_directional_sprites(self, base_wall_sprite):
        """Create horizontal and vertical wall variations"""
        # Horizontal wall - add horizontal line accent
        h_wall = base_wall_sprite.copy()
        wall_width = base_wall_sprite.get_width()
        wall_height = base_wall_sprite.get_height()
        # Add horizontal accent line
        pygame.draw.line(h_wall, (180, 180, 180), 
                        (wall_width // 4, wall_height // 2), 
                        (3 * wall_width // 4, wall_height // 2), 2)
        self.tile_sprites[self.TILE_WALL_HORIZONTAL] = h_wall
        
        # Vertical wall - add vertical line accent
        v_wall = base_wall_sprite.copy()
        # Add vertical accent line
        pygame.draw.line(v_wall, (180, 180, 180), 
                        (wall_width // 2, wall_height // 4), 
                        (wall_width // 2, 3 * wall_height // 4), 2)
        self.tile_sprites[self.TILE_WALL_VERTICAL] = v_wall
    
    def create_wall_window_sprite(self, base_wall_sprite):
        """Create window wall variation"""
        window_wall = base_wall_sprite.copy()
        wall_width = base_wall_sprite.get_width()
        wall_height = base_wall_sprite.get_height()
        
        # Create window rectangle
        window_width = wall_width // 3
        window_height = wall_height // 4
        window_x = (wall_width - window_width) // 2
        window_y = (wall_height - window_height) // 2
        
        # Draw window frame (darker)
        pygame.draw.rect(window_wall, (80, 80, 80), 
                        (window_x - 2, window_y - 2, window_width + 4, window_height + 4))
        
        # Draw window interior (lighter, like glass)
        pygame.draw.rect(window_wall, (150, 200, 255), 
                        (window_x, window_y, window_width, window_height))
        
        # Add window cross pattern
        pygame.draw.line(window_wall, (100, 100, 100), 
                        (window_x, window_y + window_height // 2), 
                        (window_x + window_width, window_y + window_height // 2), 1)
        pygame.draw.line(window_wall, (100, 100, 100), 
                        (window_x + window_width // 2, window_y), 
                        (window_x + window_width // 2, window_y + window_height), 1)
        
        self.tile_sprites[self.TILE_WALL_WINDOW] = window_wall
    
    def load_window_wall_sprites(self):
        """Load dedicated window wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Load horizontal window wall
        h_window_image = self.asset_loader.get_image("wall_window_horizontal")
        if h_window_image:
            scaled_h_window = pygame.transform.scale(h_window_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = scaled_h_window
            # Also use as generic window wall for backward compatibility
            self.tile_sprites[self.TILE_WALL_WINDOW] = scaled_h_window
        else:
            # Fallback to programmatically created window wall
            self.create_wall_window_sprite(self.tile_sprites[self.TILE_WALL])
        
        # Load vertical window wall
        v_window_image = self.asset_loader.get_image("wall_window_vertical")
        if v_window_image:
            scaled_v_window = pygame.transform.scale(v_window_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = scaled_v_window
        else:
            # Fallback to horizontal window wall or programmatic creation
            if hasattr(self, 'tile_sprites') and self.TILE_WALL_WINDOW_HORIZONTAL in self.tile_sprites:
                self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL]
            else:
                self.create_wall_window_sprite(self.tile_sprites[self.TILE_WALL])
    
    def load_corner_wall_sprites(self):
        """Load dedicated corner wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Load all corner wall assets
        corner_assets = {
            self.TILE_WALL_CORNER_TL: "wall_corner_tl",
            self.TILE_WALL_CORNER_TR: "wall_corner_tr", 
            self.TILE_WALL_CORNER_BL: "wall_corner_bl",
            self.TILE_WALL_CORNER_BR: "wall_corner_br"
        }
        
        # Track if any corner assets fail to load
        failed_corners = []
        
        for tile_type, asset_name in corner_assets.items():
            corner_image = self.asset_loader.get_image(asset_name)
            if corner_image:
                scaled_corner = pygame.transform.scale(corner_image, (self.tile_width + 8, wall_height))
                self.tile_sprites[tile_type] = scaled_corner
            else:
                failed_corners.append(tile_type)
        
        # If any corners failed to load, create programmatic fallbacks for all
        if failed_corners:
            print(f"Warning: {len(failed_corners)} corner assets failed to load, using programmatic fallbacks")
            self.create_wall_corner_sprites(self.tile_sprites[self.TILE_WALL])
    
    def load_directional_wall_sprites(self):
        """Load dedicated horizontal and vertical wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Load horizontal wall
        h_wall_image = self.asset_loader.get_image("wall_horizontal")
        if h_wall_image:
            scaled_h_wall = pygame.transform.scale(h_wall_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_HORIZONTAL] = scaled_h_wall
        else:
            # Fallback to programmatically created horizontal wall
            print("Warning: wall_horizontal asset not found, using programmatic fallback")
            self.create_wall_directional_sprites(self.tile_sprites[self.TILE_WALL])
        
        # Load vertical wall
        v_wall_image = self.asset_loader.get_image("wall_vertical")
        if v_wall_image:
            scaled_v_wall = pygame.transform.scale(v_wall_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_VERTICAL] = scaled_v_wall
        else:
            # Fallback to programmatically created vertical wall if horizontal also failed
            if self.TILE_WALL_HORIZONTAL not in self.tile_sprites:
                print("Warning: wall_vertical asset not found, using programmatic fallback")
                self.create_wall_directional_sprites(self.tile_sprites[self.TILE_WALL])
    
    def spawn_entities(self):
        """Spawn entities in specific story locations"""
        # Spawn enemies in designated areas
        self.spawn_story_enemies()
        
        # Spawn NPCs in village
        self.spawn_story_npcs()
        
        # Remove random item spawning - items only come from shops and enemy drops
        # self.spawn_items()  # Commented out
        
        # Spawn environmental objects
        self.spawn_story_objects()
        
        # Spawn treasure chests
        self.spawn_chests()
    
    def spawn_story_enemies(self):
        """Spawn enemies in specific story locations"""
        # Goblins in the forest (North-West)
        goblin_positions = [
            (25, 25), (30, 28), (35, 30), (28, 35), (32, 32),
            (20, 30), (35, 25), (25, 35), (30, 20), (40, 35)
        ]
        
        for x, y in goblin_positions:
            if self.is_valid_story_position(x, y):
                goblin = Enemy(x, y, "Goblin", health=40, damage=8, experience=25, asset_loader=self.asset_loader)
                self.enemies.append(goblin)
        
        # Orc Chief in mountain lair (North-East) - Boss fight
        orc_chief_x, orc_chief_y = 90, 23
        if self.is_valid_story_position(orc_chief_x, orc_chief_y):
            orc_chief = Enemy(orc_chief_x, orc_chief_y, "Orc Chief", 
                            health=300, damage=25, experience=200, 
                            is_boss=True, asset_loader=self.asset_loader)
            self.enemies.append(orc_chief)
        
        # A few roaming enemies near village for early game
        village_enemy_positions = [(40, 65), (75, 65), (45, 95)]
        for x, y in village_enemy_positions:
            if self.is_valid_story_position(x, y):
                goblin = Enemy(x, y, "Goblin Scout", health=30, damage=6, experience=15, asset_loader=self.asset_loader)
                self.enemies.append(goblin)
    
    def spawn_story_npcs(self):
        """Spawn NPCs in village locations"""
        # Shopkeeper in the shop building
        shopkeeper_x, shopkeeper_y = 51, 74  # Inside shop building
        shopkeeper = NPC(shopkeeper_x, shopkeeper_y, "Shopkeeper", 
                        dialog=[
                            "Welcome to my shop!",
                            "I have the finest goods in the village!",
                            "Stay safe out there, traveler.",
                            "The goblins have been more active lately..."
                        ], 
                        asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(shopkeeper)
        
        # Village Elder in his house - Quest giver
        elder_x, elder_y = 71, 74  # Inside elder's house
        elder = NPC(elder_x, elder_y, "Village Elder", 
                   dialog=[
                       "Welcome, brave traveler!",
                       "Our village faces a terrible threat.",
                       "Goblins from the northern forest raid our supplies.",
                       "Their leader, an Orc Chief, commands them from the mountains.",
                       "Please, help us defeat this menace!",
                       "The fate of our village rests in your hands."
                   ], 
                   asset_loader=self.asset_loader)
        self.npcs.append(elder)
        
        # Village Guard - Tutorial NPC
        guard_x, guard_y = 60, 78  # In village square
        guard = NPC(guard_x, guard_y, "Village Guard", 
                   dialog=[
                       "Greetings, newcomer!",
                       "Click to move, space to attack.",
                       "Visit the shopkeeper for supplies.",
                       "Be careful in the northern forest!",
                       "The goblins there are dangerous."
                   ], 
                   asset_loader=self.asset_loader)
        self.npcs.append(guard)
    
    def spawn_story_objects(self):
        """Spawn environmental objects in story-appropriate locations"""
        # Dense forest in goblin territory
        forest_tree_positions = []
        for y in range(15, 45):
            for x in range(15, 45):
                if random.random() < 0.3 and self.is_valid_tree_terrain(x, y):
                    # Avoid the combat clearing
                    if not (25 <= x <= 35 and 25 <= y <= 35):
                        forest_tree_positions.append((x, y))
        
        for x, y in forest_tree_positions:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Scattered trees around village and paths
        village_tree_positions = [
            (35, 70), (80, 70), (35, 90), (80, 90),
            (50, 60), (70, 60), (50, 100), (70, 100),
            (25, 82), (95, 82), (60, 55), (60, 105)
        ]
        
        for x, y in village_tree_positions:
            if self.is_valid_tree_terrain(x, y) and self.is_valid_story_position(x, y):
                tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(tree)
        
        # Rocks in mountain area
        mountain_rock_positions = [
            (82, 18), (88, 16), (95, 20), (85, 25), (92, 28),
            (80, 22), (97, 25), (83, 30), (90, 32), (86, 19)
        ]
        
        for x, y in mountain_rock_positions:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Decorative rocks around lake
        lake_rock_positions = [(78, 88), (92, 78), (88, 92), (82, 82)]
        for x, y in lake_rock_positions:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
    
    def spawn_chests(self):
        """Spawn treasure chests in strategic locations"""
        # Wooden chests - common, scattered around
        wooden_chest_positions = [
            (35, 35),   # Forest area
            (25, 85),   # Near village outskirts
            (85, 95),   # Lake area
            (45, 50),   # Between village and forest
            (75, 55),   # North of village
        ]
        
        for x, y in wooden_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "wooden", self.asset_loader)
                self.chests.append(chest)
        
        # Iron chests - better loot, fewer locations
        iron_chest_positions = [
            (30, 25),   # Deep in forest
            (95, 85),   # Far lake shore
            (40, 40),   # Forest clearing
        ]
        
        for x, y in iron_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "iron", self.asset_loader)
                self.chests.append(chest)
        
        # Gold chest - high-value loot, hidden location
        gold_chest_positions = [
            (90, 25),   # Mountain area (near orc chief)
        ]
        
        for x, y in gold_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "gold", self.asset_loader)
                self.chests.append(chest)
        
        # Magical chest - rare, powerful items
        magical_chest_positions = [
            (15, 15),   # Hidden corner of the map
        ]
        
        for x, y in magical_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "magical", self.asset_loader)
                self.chests.append(chest)
    
    def is_valid_story_position(self, x, y):
        """Check if a position is valid for story entity placement"""
        # Check if position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if tile is walkable
        if not self.walkable[y][x]:
            return False
        
        # Don't place entities too close to player starting position
        start_x, start_y = 60, 82
        if abs(x - start_x) < 3 and abs(y - start_y) < 3:
            return False
        
        return True
    
    def spawn_tree_at_valid_position(self):
        """Spawn a tree only on grass or dirt tiles"""
        attempts = 0
        max_attempts = 200
        
        while attempts < max_attempts:
            x = random.randint(5, self.width - 6)
            y = random.randint(5, self.height - 6)
            
            # Check if position is valid and on correct terrain
            if self.is_valid_position(x, y) and self.is_valid_tree_terrain(x, y):
                tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(tree)
                return tree
            
            attempts += 1
        
        return None
    
    def is_valid_tree_terrain(self, x, y):
        """Check if a tree can be placed on this terrain type"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        tile_type = self.tiles[y][x]
        # Trees can only spawn on grass or dirt
        return tile_type in [self.TILE_GRASS, self.TILE_DIRT]
    
    def spawn_entity_at_valid_position(self, entity_creator):
        """Spawn an entity at a valid position"""
        attempts = 0
        max_attempts = 200  # Increased attempts for larger map
        
        while attempts < max_attempts:
            x = random.randint(5, self.width - 6)  # Stay away from edges
            y = random.randint(5, self.height - 6)
            
            # Check if position is valid
            if self.is_valid_position(x, y):
                entity = entity_creator(x, y)
                
                # Add entity to appropriate list
                if isinstance(entity, Enemy):
                    self.enemies.append(entity)
                elif isinstance(entity, NPC):
                    self.npcs.append(entity)
                elif isinstance(entity, Item):
                    self.items.append(entity)
                else:
                    self.objects.append(entity)
                
                return entity
            
            attempts += 1
        
        # If we couldn't find a valid position, try a fallback position
        print(f"Warning: Could not find valid position after {max_attempts} attempts")
        return None
    
    def is_valid_position(self, x, y):
        """Check if a position is valid for entity placement"""
        # Check if position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if tile is walkable
        if not self.walkable[y][x]:
            return False
        
        # Check if position is too close to player
        player_x, player_y = int(self.player.x), int(self.player.y)
        if abs(x - player_x) < 5 and abs(y - player_y) < 5:
            return False
        
        # Check if position is too close to other entities
        for entity_list in [self.enemies, self.npcs, self.objects, self.items]:
            for entity in entity_list:
                if abs(x - entity.x) < 2 and abs(y - entity.y) < 2:
                    return False
        
        return True
    
    def check_collision(self, x, y, size=0.4, exclude_entity=None):
        """Check collision with level geometry and entities - improved precision with door handling"""
        # Check if the position is within level bounds with proper margin
        margin = size + 0.1
        if x < margin or x >= self.width - margin or y < margin or y >= self.height - margin:
            return True
        
        # Check if we're near a door - if so, use much more lenient collision
        tile_x = int(x)
        tile_y = int(y)
        is_near_door = False
        
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            # Check current tile and adjacent tiles for doors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x = tile_x + dx
                    check_y = tile_y + dy
                    if (0 <= check_x < self.width and 0 <= check_y < self.height):
                        if self.tiles[check_y][check_x] == self.TILE_DOOR:
                            is_near_door = True
                            break
                if is_near_door:
                    break
        
        # For door areas, use much smaller collision box
        effective_size = size * 0.5 if is_near_door else size * 0.7
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
                if not self.walkable[corner_tile_y][corner_tile_x]:
                    return True
        
        # Also check center point
        center_tile_x = int(x)
        center_tile_y = int(y)
        if 0 <= center_tile_x < self.width and 0 <= center_tile_y < self.height:
            if not self.walkable[center_tile_y][center_tile_x]:
                return True
        
        # Skip object collision checking near doors to allow easier passage
        if is_near_door:
            return False
        
        # Check collision with objects using circular collision (only when not near doors)
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
    
    def find_path(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Find a path from start to end using A* algorithm with forced tile-center movement"""
        # Convert to grid coordinates
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
        if not self.walkable[end_grid_y][end_grid_x]:
            end_grid_x, end_grid_y = self.find_nearest_walkable(end_grid_x, end_grid_y, entity_size)
            if end_grid_x is None:
                return []  # No walkable position found
        
        # For very short distances, just go direct to tile center
        if abs(start_grid_x - end_grid_x) <= 1 and abs(start_grid_y - end_grid_y) <= 1:
            return [(end_grid_x + 0.5, end_grid_y + 0.5)]
        
        # A* algorithm - simplified to only consider basic walkability
        open_set = []
        heapq.heappush(open_set, (0, start_grid_x, start_grid_y))
        
        came_from = {}
        g_score = {(start_grid_x, start_grid_y): 0}
        f_score = {(start_grid_x, start_grid_y): self.heuristic(start_grid_x, start_grid_y, end_grid_x, end_grid_y)}
        
        visited = set()
        max_iterations = 500  # Reduced iterations for faster pathfinding
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current_f, current_x, current_y = heapq.heappop(open_set)
            
            if (current_x, current_y) in visited:
                continue
            
            visited.add((current_x, current_y))
            
            # Check if we reached the goal
            if current_x == end_grid_x and current_y == end_grid_y:
                # Reconstruct path using only tile centers
                path = []
                while (current_x, current_y) in came_from:
                    # Force all waypoints to tile centers
                    path.append((current_x + 0.5, current_y + 0.5))
                    current_x, current_y = came_from[(current_x, current_y)]
                path.reverse()
                
                # Final destination is also tile center
                path.append((end_grid_x + 0.5, end_grid_y + 0.5))
                
                # Smooth the path to reduce unnecessary waypoints
                smoothed_path = self.smooth_path(path, entity_size)
                
                return smoothed_path
            
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
                
                # Simple walkability check - only check tile type, ignore objects for pathfinding
                if not self.walkable[next_y][next_x]:
                    continue
                
                # Calculate movement cost
                is_diagonal = abs(next_x - current_x) == 1 and abs(next_y - current_y) == 1
                move_cost = 1.414 if is_diagonal else 1.0
                
                # Heavily favor doors to force pathfinding through them
                if self.tiles[next_y][next_x] == self.TILE_DOOR:
                    move_cost *= 0.1  # 90% cost reduction for doors
                
                tentative_g_score = g_score.get((current_x, current_y), float('inf')) + move_cost
                
                if tentative_g_score < g_score.get((next_x, next_y), float('inf')):
                    came_from[(next_x, next_y)] = (current_x, current_y)
                    g_score[(next_x, next_y)] = tentative_g_score
                    f_score[(next_x, next_y)] = tentative_g_score + self.heuristic(next_x, next_y, end_grid_x, end_grid_y)
                    
                    heapq.heappush(open_set, (f_score[(next_x, next_y)], next_x, next_y))
        
        return []  # No path found
    
    def heuristic(self, x1, y1, x2, y2):
        """Heuristic function for A* (Manhattan distance with diagonal movement)"""
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        # Use diagonal distance heuristic
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)
    
    def smooth_path(self, path, entity_size=0.4):
        """Smooth path by removing unnecessary waypoints using line-of-sight checks"""
        if len(path) <= 2:
            return path
        
        smoothed = [path[0]]  # Always keep the start point
        current_index = 0
        
        while current_index < len(path) - 1:
            # Try to find the farthest point we can reach directly
            farthest_reachable = current_index + 1
            
            for i in range(current_index + 2, len(path)):
                if self.has_line_of_sight(path[current_index], path[i], entity_size):
                    farthest_reachable = i
                else:
                    break  # Can't reach further, stop checking
            
            # Add the farthest reachable point
            if farthest_reachable < len(path):
                smoothed.append(path[farthest_reachable])
                current_index = farthest_reachable
            else:
                break
        
        # Always ensure the final destination is included
        if smoothed[-1] != path[-1]:
            smoothed.append(path[-1])
        
        return smoothed
    
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
            
            if not self.walkable[grid_y][grid_x]:
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
        
        if not self.walkable[y][x]:
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
        
        if not self.walkable[y][x]:
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
        if self.is_position_walkable(x, y, entity_size):
            return x, y
        
        # Search in expanding circles
        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Only check positions on the edge of the current radius
                    if abs(dx) == radius or abs(dy) == radius:
                        check_x = x + dx
                        check_y = y + dy
                        
                        if self.is_position_walkable(check_x, check_y, entity_size):
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
                walkable = "walkable" if self.walkable[tile_y][tile_x] else "blocked"
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
        """Render the level"""
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
        
        # Render tiles to game surface
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                height = self.heightmap[y][x]
                
                # Calculate screen position
                screen_x, screen_y = self.iso_renderer.world_to_screen(x, y, self.camera_x, self.camera_y)
                
                # Adjust for height
                screen_y -= height * 16
                
                # Special handling for doors - render stone underneath first for better contrast
                if tile_type == self.TILE_DOOR:
                    # Render stone base first (better than dirt for door contrast)
                    stone_sprite = self.tile_sprites[self.TILE_STONE]
                    game_surface.blit(stone_sprite, (screen_x - self.tile_width // 2, screen_y - self.tile_height // 2))
                    
                    # Add subtle glow effect around door for better visibility
                    glow_radius = 3
                    glow_color = (255, 255, 150, 50)  # Soft yellow glow
                    glow_surface = pygame.Surface((self.tile_width + glow_radius * 2, self.tile_height + glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(glow_surface, glow_color, glow_surface.get_rect())
                    game_surface.blit(glow_surface, (screen_x - self.tile_width // 2 - glow_radius, screen_y - self.tile_height // 2 - glow_radius), special_flags=pygame.BLEND_ALPHA_SDL2)
                    
                    # Then render door on top with slight offset for better positioning
                    door_sprite = self.tile_sprites[self.TILE_DOOR]
                    door_rect = door_sprite.get_rect()
                    door_rect.centerx = screen_x
                    door_rect.bottom = screen_y + self.tile_height // 2 + 8  # Slightly lower positioning
                    game_surface.blit(door_sprite, door_rect)
                elif tile_type in [self.TILE_WALL, self.TILE_WALL_CORNER_TL, self.TILE_WALL_CORNER_TR, 
                                   self.TILE_WALL_CORNER_BL, self.TILE_WALL_CORNER_BR, 
                                   self.TILE_WALL_HORIZONTAL, self.TILE_WALL_VERTICAL, self.TILE_WALL_WINDOW,
                                   self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL]:
                    # Render all wall types with better positioning and subtle shadow
                    # Add shadow first
                    shadow_offset = 2
                    wall_sprite = self.tile_sprites[tile_type]
                    shadow_sprite = wall_sprite.copy()
                    shadow_sprite.fill((0, 0, 0, 80), special_flags=pygame.BLEND_RGBA_MULT)
                    shadow_rect = shadow_sprite.get_rect()
                    shadow_rect.centerx = screen_x + shadow_offset
                    shadow_rect.bottom = screen_y + self.tile_height // 2 + 16 + shadow_offset
                    game_surface.blit(shadow_sprite, shadow_rect)
                    
                    # Then render wall
                    wall_rect = wall_sprite.get_rect()
                    wall_rect.centerx = screen_x
                    wall_rect.bottom = screen_y + self.tile_height // 2 + 16  # Position walls properly
                    game_surface.blit(wall_sprite, wall_rect)
                else:
                    # Normal tile rendering
                    sprite = self.tile_sprites[tile_type]
                    game_surface.blit(sprite, (screen_x - self.tile_width // 2, screen_y - self.tile_height // 2))
        
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