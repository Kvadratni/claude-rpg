"""
Level system for the RPG
"""

import pygame
import random
import math
import heapq
import os
from .isometric import IsometricRenderer, sort_by_depth
from .entity import Entity, NPC, Enemy, Item, Chest
from .template_level import integrate_template_generation

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
        self.width = 200  # Default size, may be overridden by template
        self.height = 200
        
        # Isometric renderer
        self.iso_renderer = IsometricRenderer(64, 32)
        self.tile_width = self.iso_renderer.tile_width
        self.tile_height = self.iso_renderer.tile_height
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Template generator (will be set if template is used)
        self.template_generator = None
        
        # Try template-based generation first
        template_path = "/Users/mnovich/Development/claude-rpg/assets/maps/main_world.png"
        if os.path.exists(template_path):
            print("Using template-based map generation...")
            success = integrate_template_generation(self, template_path)
            if success:
                print("Template-based generation successful!")
            else:
                print("Template generation failed, falling back to procedural generation")
                self.generate_fallback_level()
        else:
            print("No template found, using procedural generation")
            self.generate_fallback_level()
        
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
    
    def generate_fallback_level(self):
        """Generate level using original procedural method as fallback"""
        print("Generating level using procedural fallback...")
        
        # Initialize entity lists
        self.npcs = []
        self.enemies = []
        self.items = []
        self.objects = []  # Static objects like trees, rocks, etc.
        self.chests = []   # Treasure chests
        
        # Generate level using original method
        self.tiles = self.generate_level()
        self.heightmap = self.generate_heightmap()
        self.walkable = self.generate_walkable_grid()
        
        # Spawn entities using original method
        self.spawn_entities()
    
    def generate_level(self):
        """Generate a massive, well-designed world with multiple regions and content"""
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
        
        # CENTRAL VILLAGE AREA (Center of map) - Main hub
        village_center_x, village_center_y = 100, 100
        
        # Large village square with stone paths
        for x in range(85, 116):
            for y in range(85, 116):
                tiles[y][x] = self.TILE_STONE
        
        # Village buildings - Much larger and more varied
        self.create_building(tiles, 70, 80, 15, 10)   # Large shopkeeper's store
        self.create_building(tiles, 115, 80, 15, 10)  # Elder's house
        self.create_building(tiles, 85, 120, 20, 12)  # Village hall
        self.create_building(tiles, 70, 105, 12, 8)   # Blacksmith
        self.create_building(tiles, 115, 105, 12, 8)  # Inn/Tavern
        self.create_building(tiles, 92, 65, 16, 10)   # Temple/Church
        self.create_building(tiles, 60, 92, 10, 10)   # Guard house
        self.create_building(tiles, 130, 92, 10, 10)  # Storage house
        
        # Test corner mappings - create 4 small test buildings to see corner orientations
        self.create_test_corner_building(tiles, 50, 50, 0)  # Test mapping 1 (TL->TL, TR->TR, etc.)
        self.create_test_corner_building(tiles, 55, 50, 1)  # Test mapping 2 (TL->TR, TR->TL, etc.)
        self.create_test_corner_building(tiles, 60, 50, 2)  # Test mapping 3 (TL->BL, TR->BR, etc.)
        self.create_test_corner_building(tiles, 65, 50, 3)  # Test mapping 4 (TL->BR, TR->BL, etc.)
        
        # Major roads connecting all regions
        # Main east-west highway
        for x in range(10, 190):
            tiles[100][x] = self.TILE_STONE
            tiles[101][x] = self.TILE_STONE
        
        # Main north-south highway  
        for y in range(10, 190):
            tiles[y][100] = self.TILE_STONE
            tiles[y][101] = self.TILE_STONE
        
        # NORTHERN WILDERNESS (Multiple forest areas)
        # Dark Forest (North-West) - Goblin territory
        self.create_forest_region(tiles, 30, 30, 40, 40, density=0.5, dirt_patches=0.4)
        
        # Enchanted Grove (North-Center) - Magical creatures
        self.create_forest_region(tiles, 80, 25, 40, 30, density=0.3, dirt_patches=0.2)
        
        # Ancient Woods (North-East) - Old ruins
        self.create_forest_region(tiles, 140, 30, 50, 40, density=0.6, dirt_patches=0.3)
        
        # MOUNTAIN REGIONS (Multiple mountain areas)
        # Orc Stronghold (Far North-East)
        self.create_mountain_region(tiles, 160, 15, 35, 35)
        
        # Dragon's Peak (North-West corner)
        self.create_mountain_region(tiles, 15, 15, 30, 30)
        
        # Crystal Caves (East side)
        self.create_mountain_region(tiles, 170, 80, 25, 40)
        
        # WATER FEATURES (Multiple lakes and rivers)
        # Great Lake (South-East)
        self.create_lake(tiles, 150, 150, 20)
        
        # Twin Lakes (South-West)
        self.create_lake(tiles, 40, 140, 12)
        self.create_lake(tiles, 60, 155, 10)
        
        # Mountain Lake (North)
        self.create_lake(tiles, 100, 40, 8)
        
        # River system connecting lakes
        self.create_river(tiles, 100, 40, 150, 150)  # From mountain lake to great lake
        self.create_river(tiles, 40, 140, 60, 155)   # Connecting twin lakes
        
        # DESERT REGION (South-West corner)
        self.create_desert_region(tiles, 15, 140, 60, 45)
        
        # SWAMP REGION (West side)
        self.create_swamp_region(tiles, 15, 80, 40, 50)
        
        # ADDITIONAL SETTLEMENTS
        # Mining Town (Near mountains)
        self.create_small_town(tiles, 160, 60, "mining")
        
        # Fishing Village (By great lake)
        self.create_small_town(tiles, 130, 170, "fishing")
        
        # Desert Outpost (In desert)
        self.create_small_town(tiles, 35, 165, "desert")
        
        # Forest Hamlet (In enchanted grove)
        self.create_small_town(tiles, 100, 35, "forest")
        
        # ROADS AND PATHS - Connect all major areas
        # Roads to northern settlements
        self.create_stone_path(tiles, 100, 85, 100, 35)  # To forest hamlet
        self.create_stone_path(tiles, 115, 85, 160, 60)  # To mining town
        
        # Roads to southern settlements  
        self.create_stone_path(tiles, 85, 115, 35, 165)  # To desert outpost
        self.create_stone_path(tiles, 115, 115, 130, 170) # To fishing village
        
        # Dirt paths to wilderness areas
        self.create_dirt_path(tiles, 85, 85, 30, 30)     # To dark forest
        self.create_dirt_path(tiles, 115, 85, 140, 30)   # To ancient woods
        self.create_dirt_path(tiles, 85, 115, 15, 80)    # To swamp
        self.create_dirt_path(tiles, 115, 100, 170, 80)  # To crystal caves
        
        # SPECIAL LOCATIONS
        # Ancient Ruins (scattered throughout)
        self.create_ruins(tiles, 50, 60, 8, 6)   # Ruins near village
        self.create_ruins(tiles, 160, 120, 12, 8) # Ruins in east
        self.create_ruins(tiles, 25, 170, 10, 6)  # Desert ruins
        
        # Mysterious Circles (stone circles)
        self.create_stone_circle(tiles, 70, 50)
        self.create_stone_circle(tiles, 130, 130)
        self.create_stone_circle(tiles, 180, 40)
        
        # Ensure player starting area is clear (village center)
        start_x, start_y = 100, 102
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if 0 <= start_x + dx < self.width and 0 <= start_y + dy < self.height:
                    if tiles[start_y + dy][start_x + dx] == self.TILE_WALL:
                        tiles[start_y + dy][start_x + dx] = self.TILE_STONE
        
        return tiles
    
    def create_forest_region(self, tiles, start_x, start_y, width, height, density=0.4, dirt_patches=0.3):
        """Create a forest region with varying density"""
        for y in range(start_y, min(start_y + height, self.height - 1)):
            for x in range(start_x, min(start_x + width, self.width - 1)):
                if random.random() < dirt_patches:
                    tiles[y][x] = self.TILE_DIRT
        
        # Create clearings within forest
        num_clearings = random.randint(2, 4)
        for _ in range(num_clearings):
            clear_x = start_x + random.randint(5, width - 10)
            clear_y = start_y + random.randint(5, height - 10)
            clear_size = random.randint(3, 8)
            
            for dy in range(-clear_size//2, clear_size//2):
                for dx in range(-clear_size//2, clear_size//2):
                    if (0 <= clear_x + dx < self.width and 0 <= clear_y + dy < self.height):
                        if dx*dx + dy*dy <= (clear_size//2)**2:  # Circular clearing
                            tiles[clear_y + dy][clear_x + dx] = self.TILE_DIRT
    
    def create_mountain_region(self, tiles, start_x, start_y, width, height):
        """Create a rocky mountain region"""
        for y in range(start_y, min(start_y + height, self.height - 1)):
            for x in range(start_x, min(start_x + width, self.width - 1)):
                # Create rocky pattern
                if (x + y) % 3 == 0:
                    tiles[y][x] = self.TILE_STONE
                elif (x + y) % 5 == 0:
                    tiles[y][x] = self.TILE_DIRT
        
        # Add some flat areas for building/combat
        num_plateaus = random.randint(1, 3)
        for _ in range(num_plateaus):
            plat_x = start_x + random.randint(5, width - 15)
            plat_y = start_y + random.randint(5, height - 15)
            plat_size = random.randint(8, 15)
            
            for dy in range(plat_size):
                for dx in range(plat_size):
                    if (0 <= plat_x + dx < self.width and 0 <= plat_y + dy < self.height):
                        tiles[plat_y + dy][plat_x + dx] = self.TILE_STONE
    
    def create_desert_region(self, tiles, start_x, start_y, width, height):
        """Create a desert region with sand (dirt) and occasional stone"""
        for y in range(start_y, min(start_y + height, self.height - 1)):
            for x in range(start_x, min(start_x + width, self.width - 1)):
                if random.random() < 0.8:  # 80% dirt (sand)
                    tiles[y][x] = self.TILE_DIRT
                elif random.random() < 0.3:  # Some stone outcroppings
                    tiles[y][x] = self.TILE_STONE
        
        # Create oasis
        oasis_x = start_x + width // 2
        oasis_y = start_y + height // 2
        self.create_lake(tiles, oasis_x, oasis_y, 4)
        
        # Surround oasis with grass
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                if (0 <= oasis_x + dx < self.width and 0 <= oasis_y + dy < self.height):
                    if dx*dx + dy*dy <= 36:  # Circle around oasis
                        if tiles[oasis_y + dy][oasis_x + dx] != self.TILE_WATER:
                            tiles[oasis_y + dy][oasis_x + dx] = self.TILE_GRASS
    
    def create_swamp_region(self, tiles, start_x, start_y, width, height):
        """Create a swamp region with water patches and dirt"""
        for y in range(start_y, min(start_y + height, self.height - 1)):
            for x in range(start_x, min(start_x + width, self.width - 1)):
                rand = random.random()
                if rand < 0.3:  # 30% water
                    tiles[y][x] = self.TILE_WATER
                elif rand < 0.7:  # 40% dirt (muddy ground)
                    tiles[y][x] = self.TILE_DIRT
                # Rest stays grass
    
    def create_small_town(self, tiles, center_x, center_y, town_type):
        """Create a small settlement based on type"""
        # Small town square
        for x in range(center_x - 5, center_x + 6):
            for y in range(center_y - 5, center_y + 6):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = self.TILE_STONE
        
        if town_type == "mining":
            # Mining town buildings
            self.create_building(tiles, center_x - 10, center_y - 8, 12, 8)  # Mine office
            self.create_building(tiles, center_x + 2, center_y - 8, 10, 6)   # Miners' quarters
            self.create_building(tiles, center_x - 8, center_y + 3, 8, 6)    # Supply store
        elif town_type == "fishing":
            # Fishing village buildings
            self.create_building(tiles, center_x - 8, center_y - 6, 10, 6)   # Fish market
            self.create_building(tiles, center_x + 4, center_y - 6, 8, 6)    # Fisherman's hut
            self.create_building(tiles, center_x - 6, center_y + 4, 12, 6)   # Boat house
        elif town_type == "desert":
            # Desert outpost buildings
            self.create_building(tiles, center_x - 6, center_y - 4, 8, 6)    # Trading post
            self.create_building(tiles, center_x + 4, center_y - 4, 6, 6)    # Water storage
            self.create_building(tiles, center_x - 2, center_y + 4, 10, 6)   # Caravan rest
        elif town_type == "forest":
            # Forest hamlet buildings
            self.create_building(tiles, center_x - 6, center_y - 6, 8, 6)    # Ranger station
            self.create_building(tiles, center_x + 4, center_y - 6, 6, 6)    # Herbalist hut
            self.create_building(tiles, center_x - 4, center_y + 4, 10, 6)   # Hunter's lodge
    
    def create_ruins(self, tiles, start_x, start_y, width, height):
        """Create ancient ruins with broken walls"""
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Outer walls (partially broken)
                    if (x == start_x or x == start_x + width - 1 or 
                        y == start_y or y == start_y + height - 1):
                        if random.random() < 0.7:  # 70% chance for wall piece
                            tiles[y][x] = self.TILE_WALL
                    # Interior floor
                    elif random.random() < 0.6:  # 60% chance for stone floor
                        tiles[y][x] = self.TILE_STONE
                    elif random.random() < 0.3:  # Some dirt patches
                        tiles[y][x] = self.TILE_DIRT
    
    def create_stone_circle(self, tiles, center_x, center_y):
        """Create a mysterious stone circle"""
        radius = 4
        for angle in range(0, 360, 45):  # 8 stones
            x = center_x + int(radius * math.cos(math.radians(angle)))
            y = center_y + int(radius * math.sin(math.radians(angle)))
            if 0 <= x < self.width and 0 <= y < self.height:
                tiles[y][x] = self.TILE_STONE
        
        # Center stone
        if 0 <= center_x < self.width and 0 <= center_y < self.height:
            tiles[center_y][center_x] = self.TILE_STONE
    
    def create_river(self, tiles, start_x, start_y, end_x, end_y):
        """Create a winding river between two points"""
        current_x, current_y = start_x, start_y
        
        while abs(current_x - end_x) > 1 or abs(current_y - end_y) > 1:
            # Create river tile
            if 0 <= current_x < self.width and 0 <= current_y < self.height:
                tiles[current_y][current_x] = self.TILE_WATER
                # Add banks
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        bank_x, bank_y = current_x + dx, current_y + dy
                        if (0 <= bank_x < self.width and 0 <= bank_y < self.height and
                            tiles[bank_y][bank_x] == self.TILE_GRASS):
                            if random.random() < 0.3:  # 30% chance for dirt bank
                                tiles[bank_y][bank_x] = self.TILE_DIRT
            
            # Move toward target with some randomness for winding
            if current_x < end_x:
                current_x += 1
            elif current_x > end_x:
                current_x -= 1
            
            if current_y < end_y:
                current_y += 1
            elif current_y > end_y:
                current_y -= 1
            
            # Add some random winding
            if random.random() < 0.3:
                current_x += random.choice([-1, 1])
            if random.random() < 0.3:
                current_y += random.choice([-1, 1])
            
            # Keep in bounds
            current_x = max(1, min(self.width - 2, current_x))
            current_y = max(1, min(self.height - 2, current_y))
    
    def create_stone_path(self, tiles, start_x, start_y, end_x, end_y):
        """Create a stone road between two points"""
        current_x, current_y = start_x, start_y
        
        while abs(current_x - end_x) > 1 or abs(current_y - end_y) > 1:
            # Create 2-wide stone path
            for dx in [0, 1]:
                for dy in [0, 1]:
                    path_x, path_y = current_x + dx, current_y + dy
                    if 0 <= path_x < self.width and 0 <= path_y < self.height:
                        tiles[path_y][path_x] = self.TILE_STONE
            
            # Move toward target
            if current_x < end_x:
                current_x += 1
            elif current_x > end_x:
                current_x -= 1
            
            if current_y < end_y:
                current_y += 1
            elif current_y > end_y:
                current_y -= 1
    
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
            self.load_corner_wall_sprites()
            self.load_directional_wall_sprites()
            self.load_window_wall_sprites()
            
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
            door_sprite = self.create_enhanced_door_sprite()
            self.tile_sprites[self.TILE_DOOR] = door_sprite
    
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
    
    def create_enhanced_door_sprite(self):
        """Create an enhanced door sprite that renders properly"""
        # Create a door sprite that looks like a proper isometric door
        door_width = self.tile_width
        door_height = self.tile_height + 32
        
        surface = pygame.Surface((door_width, door_height), pygame.SRCALPHA)
        
        # Door colors
        door_color = (139, 69, 19)      # Brown door
        frame_color = (100, 50, 10)     # Darker brown frame
        handle_color = (255, 215, 0)    # Gold handle
        
        # Calculate door rectangle dimensions
        door_rect_width = door_width // 2
        door_rect_height = door_height - self.tile_height // 2
        door_x = (door_width - door_rect_width) // 2
        door_y = self.tile_height // 4
        
        # Draw door frame (slightly larger rectangle)
        frame_rect = pygame.Rect(door_x - 2, door_y - 2, door_rect_width + 4, door_rect_height + 4)
        pygame.draw.rect(surface, frame_color, frame_rect)
        
        # Draw main door
        door_rect = pygame.Rect(door_x, door_y, door_rect_width, door_rect_height)
        pygame.draw.rect(surface, door_color, door_rect)
        
        # Add door handle
        handle_x = door_x + door_rect_width - 6
        handle_y = door_y + door_rect_height // 2
        pygame.draw.circle(surface, handle_color, (handle_x, handle_y), 2)
        
        # Add door panels for detail
        panel_margin = 3
        panel_width = door_rect_width - panel_margin * 2
        panel_height = (door_rect_height - panel_margin * 3) // 2
        
        # Top panel outline
        top_panel_rect = pygame.Rect(door_x + panel_margin, door_y + panel_margin, panel_width, panel_height)
        pygame.draw.rect(surface, frame_color, top_panel_rect, 1)
        
        # Bottom panel outline
        bottom_panel_rect = pygame.Rect(door_x + panel_margin, door_y + panel_margin * 2 + panel_height, panel_width, panel_height)
        pygame.draw.rect(surface, frame_color, bottom_panel_rect, 1)
        
        return surface
    
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
        
        # Load horizontal window wall - note the typo in the asset filename
        h_window_image = self.asset_loader.get_image("wall_window_horizonal")  # Asset has typo
        if h_window_image:
            scaled_h_window = pygame.transform.scale(h_window_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = scaled_h_window
            # Also use as generic window wall for backward compatibility
            self.tile_sprites[self.TILE_WALL_WINDOW] = scaled_h_window
        else:
            # Fallback to programmatically created window wall
            if self.TILE_WALL in self.tile_sprites:
                self.create_wall_window_sprite(self.tile_sprites[self.TILE_WALL])
                # Ensure horizontal window wall has a sprite
                if self.TILE_WALL_WINDOW in self.tile_sprites:
                    self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = self.tile_sprites[self.TILE_WALL_WINDOW]
        
        # Load vertical window wall
        v_window_image = self.asset_loader.get_image("wall_window_vertical")
        if v_window_image:
            scaled_v_window = pygame.transform.scale(v_window_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = scaled_v_window
        else:
            # Fallback to horizontal window wall or programmatic creation
            if self.TILE_WALL_WINDOW_HORIZONTAL in self.tile_sprites:
                self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL]
            elif self.TILE_WALL_WINDOW in self.tile_sprites:
                self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL_WINDOW]
            else:
                # Last resort - use regular wall
                if self.TILE_WALL in self.tile_sprites:
                    self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL]
    
    def load_corner_wall_sprites(self):
        """Load dedicated corner wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Try improved isometric assets first, then fall back to original assets
        corner_assets = {
            self.TILE_WALL_CORNER_TL: ["wall_corner_tl_isometric", "wall_corner_tl"],
            self.TILE_WALL_CORNER_TR: ["wall_corner_tr_isometric", "wall_corner_tr"], 
            self.TILE_WALL_CORNER_BL: ["wall_corner_bl_isometric", "wall_corner_bl"],
            self.TILE_WALL_CORNER_BR: ["wall_corner_br_isometric", "wall_corner_br"]
        }
        
        # Track if any corner assets fail to load
        failed_corners = []
        
        for tile_type, asset_names in corner_assets.items():
            corner_image = None
            # Try each asset name in order
            for asset_name in asset_names:
                corner_image = self.asset_loader.get_image(asset_name)
                if corner_image:
                    break
            
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
        
        # Try improved isometric assets first, then fall back to original assets
        # Load horizontal wall
        h_wall_image = self.asset_loader.get_image("wall_horizontal_isometric")
        if not h_wall_image:
            h_wall_image = self.asset_loader.get_image("wall_horizontal")
        
        if h_wall_image:
            scaled_h_wall = pygame.transform.scale(h_wall_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_HORIZONTAL] = scaled_h_wall
        else:
            # Fallback to programmatically created horizontal wall
            print("Warning: wall_horizontal asset not found, using programmatic fallback")
            self.create_wall_directional_sprites(self.tile_sprites[self.TILE_WALL])
        
        # Load vertical wall
        v_wall_image = self.asset_loader.get_image("wall_vertical_isometric")
        if not v_wall_image:
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
        """Spawn enemies in specific story locations across the expanded world"""
        # Dark Forest Goblins (North-West)
        dark_forest_positions = [
            (35, 35), (40, 38), (45, 40), (38, 45), (42, 42),
            (30, 40), (45, 35), (35, 45), (40, 30), (50, 45),
            (32, 50), (48, 32), (55, 38), (38, 55), (42, 48)
        ]
        
        for x, y in dark_forest_positions:
            if self.is_valid_story_position(x, y):
                goblin = Enemy(x, y, "Forest Goblin", health=45, damage=9, experience=30, asset_loader=self.asset_loader)
                self.enemies.append(goblin)
        
        # Enchanted Grove - Magical creatures
        grove_positions = [
            (85, 30), (90, 35), (95, 32), (88, 40), (92, 45),
            (100, 30), (105, 35), (110, 32), (95, 45), (102, 40)
        ]
        
        for x, y in grove_positions:
            if self.is_valid_story_position(x, y):
                sprite_enemy = Enemy(x, y, "Forest Sprite", health=35, damage=12, experience=40, asset_loader=self.asset_loader)
                self.enemies.append(sprite_enemy)
        
        # Ancient Woods - Undead guardians
        ancient_positions = [
            (145, 35), (150, 40), (155, 35), (148, 50), (152, 45),
            (160, 40), (165, 45), (170, 38), (155, 55), (162, 50),
            (175, 42), (168, 35), (158, 60), (172, 55), (165, 32)
        ]
        
        for x, y in ancient_positions:
            if self.is_valid_story_position(x, y):
                skeleton = Enemy(x, y, "Ancient Guardian", health=60, damage=15, experience=50, asset_loader=self.asset_loader)
                self.enemies.append(skeleton)
        
        # Orc Stronghold (Far North-East) - Multiple bosses and minions
        stronghold_positions = [
            (165, 25), (170, 30), (175, 25), (168, 35), (172, 32),
            (180, 28), (175, 35), (185, 30), (178, 40), (182, 35)
        ]
        
        for i, (x, y) in enumerate(stronghold_positions):
            if self.is_valid_story_position(x, y):
                if i == 0:  # First one is the boss
                    orc_chief = Enemy(x, y, "Orc Warlord", 
                                    health=400, damage=30, experience=300, 
                                    is_boss=True, asset_loader=self.asset_loader)
                    self.enemies.append(orc_chief)
                else:
                    orc = Enemy(x, y, "Orc Warrior", health=80, damage=18, experience=60, asset_loader=self.asset_loader)
                    self.enemies.append(orc)
        
        # Dragon's Peak - Dragon and minions
        dragon_positions = [
            (25, 25), (30, 28), (35, 25), (28, 32), (32, 30)
        ]
        
        for i, (x, y) in enumerate(dragon_positions):
            if self.is_valid_story_position(x, y):
                if i == 0:  # Dragon boss
                    dragon = Enemy(x, y, "Ancient Dragon", 
                                 health=800, damage=50, experience=500, 
                                 is_boss=True, asset_loader=self.asset_loader)
                    self.enemies.append(dragon)
                else:
                    drake = Enemy(x, y, "Fire Drake", health=120, damage=25, experience=80, asset_loader=self.asset_loader)
                    self.enemies.append(drake)
        
        # Crystal Caves - Crystal elementals
        crystal_positions = [
            (175, 85), (180, 90), (185, 85), (178, 95), (182, 100),
            (175, 105), (180, 110), (185, 105), (188, 95), (192, 88)
        ]
        
        for x, y in crystal_positions:
            if self.is_valid_story_position(x, y):
                elemental = Enemy(x, y, "Crystal Elemental", health=70, damage=20, experience=65, asset_loader=self.asset_loader)
                self.enemies.append(elemental)
        
        # Desert enemies
        desert_positions = [
            (25, 150), (35, 155), (45, 160), (30, 165), (40, 170),
            (50, 155), (55, 165), (60, 150), (65, 160), (70, 155)
        ]
        
        for x, y in desert_positions:
            if self.is_valid_story_position(x, y):
                scorpion = Enemy(x, y, "Giant Scorpion", health=55, damage=16, experience=45, asset_loader=self.asset_loader)
                self.enemies.append(scorpion)
        
        # Swamp enemies
        swamp_positions = [
            (25, 90), (30, 95), (35, 100), (40, 105), (45, 110),
            (25, 115), (30, 120), (35, 125), (40, 115), (45, 120)
        ]
        
        for x, y in swamp_positions:
            if self.is_valid_story_position(x, y):
                troll = Enemy(x, y, "Swamp Troll", health=90, damage=22, experience=70, asset_loader=self.asset_loader)
                self.enemies.append(troll)
        
        # Village area patrol enemies (easier for new players)
        village_patrol_positions = [
            (70, 70), (130, 70), (70, 130), (130, 130),
            (60, 100), (140, 100), (100, 60), (100, 140)
        ]
        
        for x, y in village_patrol_positions:
            if self.is_valid_story_position(x, y):
                bandit = Enemy(x, y, "Bandit Scout", health=35, damage=8, experience=20, asset_loader=self.asset_loader)
                self.enemies.append(bandit)
    
    def spawn_story_npcs(self):
        """Spawn NPCs across the expanded world"""
        # MAIN VILLAGE NPCs
        # Shopkeeper in the large store
        shopkeeper_x, shopkeeper_y = 77, 85  # Inside large shop building
        shopkeeper = NPC(shopkeeper_x, shopkeeper_y, "Master Merchant", 
                        dialog=[
                            "Welcome to the finest shop in all the lands!",
                            "I have goods from every corner of the realm!",
                            "The roads are dangerous, but profitable for traders.",
                            "I hear the ancient ruins hold great treasures..."
                        ], 
                        asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(shopkeeper)
        
        # Village Elder in his house
        elder_x, elder_y = 122, 85  # Inside elder's house
        elder = NPC(elder_x, elder_y, "Village Elder", 
                   dialog=[
                       "Welcome, brave adventurer!",
                       "Our peaceful village sits at the crossroads of many realms.",
                       "To the north lie ancient forests filled with danger.",
                       "The mountains hold both treasure and terror.",
                       "The desert sands conceal forgotten secrets.",
                       "May your journey bring you wisdom and fortune!"
                   ], 
                   asset_loader=self.asset_loader)
        self.npcs.append(elder)
        
        # Blacksmith
        blacksmith_x, blacksmith_y = 76, 109  # Inside blacksmith
        blacksmith = NPC(blacksmith_x, blacksmith_y, "Master Smith", 
                        dialog=[
                            "The forge burns hot today!",
                            "I craft the finest weapons and armor.",
                            "Bring me rare metals and I'll make you legendary gear!",
                            "The crystal caves have materials I need..."
                        ], 
                        asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(blacksmith)
        
        # Innkeeper
        innkeeper_x, innkeeper_y = 121, 109  # Inside inn
        innkeeper = NPC(innkeeper_x, innkeeper_y, "Innkeeper", 
                       dialog=[
                           "Welcome to the Crossroads Inn!",
                           "Travelers from all lands rest here.",
                           "I've heard tales of dragons in the northern peaks.",
                           "The swamp folk speak of ancient magic.",
                           "Rest well, the roads are perilous."
                       ], 
                       asset_loader=self.asset_loader)
        self.npcs.append(innkeeper)
        
        # Temple Priest
        priest_x, priest_y = 100, 70  # Inside temple
        priest = NPC(priest_x, priest_y, "High Priest", 
                    dialog=[
                        "The light guides all who seek it.",
                        "Ancient evils stir in the forgotten places.",
                        "The stone circles hold power beyond understanding.",
                        "May the divine protect you on your journey."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(priest)
        
        # Village Guard Captain
        guard_x, guard_y = 65, 97  # In guard house
        guard = NPC(guard_x, guard_y, "Guard Captain", 
                   dialog=[
                       "I keep watch over our village.",
                       "Bandits have been spotted on the roads.",
                       "The northern forests grow more dangerous each day.",
                       "If you're heading out, be well armed!",
                       "Report any suspicious activity to me."
                   ], 
                   asset_loader=self.asset_loader)
        self.npcs.append(guard)
        
        # MINING TOWN NPCs
        # Mine Foreman
        foreman_x, foreman_y = 155, 57  # In mine office
        foreman = NPC(foreman_x, foreman_y, "Mine Foreman", 
                     dialog=[
                         "The mines run deep into the mountain.",
                         "We've found strange crystals in the lower tunnels.",
                         "Some miners speak of hearing voices in the dark.",
                         "The work is hard but the pay is good."
                     ], 
                     asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(foreman)
        
        # FISHING VILLAGE NPCs
        # Harbor Master
        harbor_x, harbor_y = 125, 167  # In fish market
        harbor = NPC(harbor_x, harbor_y, "Harbor Master", 
                    dialog=[
                        "The great lake provides for our village.",
                        "Strange lights have been seen beneath the waters.",
                        "The fish have been acting oddly lately.",
                        "Ancient ruins lie submerged in the deep parts."
                    ], 
                    asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(harbor)
        
        # DESERT OUTPOST NPCs
        # Caravan Leader
        caravan_x, caravan_y = 32, 162  # In trading post
        caravan = NPC(caravan_x, caravan_y, "Caravan Master", 
                     dialog=[
                         "The desert trade routes are treacherous.",
                         "Sandstorms hide ancient ruins from view.",
                         "The oasis is sacred to the desert dwellers.",
                         "Scorpions grow large in these parts."
                     ], 
                     asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(caravan)
        
        # FOREST HAMLET NPCs
        # Ranger
        ranger_x, ranger_y = 97, 32  # In ranger station
        ranger = NPC(ranger_x, ranger_y, "Forest Ranger", 
                    dialog=[
                        "The ancient woods hold many secrets.",
                        "Spirits of the old world still walk these paths.",
                        "The stone circles are gathering points for magic.",
                        "Beware the guardians of the ruins."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(ranger)
        
        # Herbalist
        herbalist_x, herbalist_y = 107, 32  # In herbalist hut
        herbalist = NPC(herbalist_x, herbalist_y, "Master Herbalist", 
                       dialog=[
                           "The forest provides all manner of healing herbs.",
                           "Magical plants grow near the stone circles.",
                           "The swamp has rare ingredients, but it's dangerous.",
                           "I can brew potions from the right materials."
                       ], 
                       asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(herbalist)
        
        # MYSTERIOUS WANDERERS (scattered around the world)
        # Mysterious Wizard near stone circle
        wizard_x, wizard_y = 70, 52
        wizard = NPC(wizard_x, wizard_y, "Mysterious Wizard", 
                    dialog=[
                        "The ancient magics still flow through these stones...",
                        "Power calls to power, young one.",
                        "The circles are older than any kingdom.",
                        "Seek the truth in the forgotten places."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(wizard)
        
        # Hermit near ruins
        hermit_x, hermit_y = 52, 62
        hermit = NPC(hermit_x, hermit_y, "Old Hermit", 
                    dialog=[
                        "I've lived here since before the village grew large.",
                        "These ruins... they're older than you think.",
                        "Sometimes I hear whispers from the stones.",
                        "The past has a way of returning."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(hermit)
    
    def spawn_story_objects(self):
        """Spawn environmental objects across the expanded world"""
        # Dense forests in multiple regions
        # Dark Forest (North-West)
        dark_forest_trees = []
        for y in range(25, 65):
            for x in range(25, 65):
                if random.random() < 0.4 and self.is_valid_tree_terrain(x, y):
                    # Avoid clearings and paths
                    if not (35 <= x <= 45 and 35 <= y <= 45):  # Main clearing
                        dark_forest_trees.append((x, y))
        
        for x, y in dark_forest_trees:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Enchanted Grove (North-Center)
        grove_trees = []
        for y in range(20, 50):
            for x in range(75, 115):
                if random.random() < 0.3 and self.is_valid_tree_terrain(x, y):
                    grove_trees.append((x, y))
        
        for x, y in grove_trees:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Ancient Woods (North-East)
        ancient_trees = []
        for y in range(25, 65):
            for x in range(135, 185):
                if random.random() < 0.5 and self.is_valid_tree_terrain(x, y):
                    ancient_trees.append((x, y))
        
        for x, y in ancient_trees:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Scattered trees around settlements
        settlement_tree_positions = [
            # Around main village
            (55, 75), (145, 75), (55, 125), (145, 125),
            (75, 55), (125, 55), (75, 145), (125, 145),
            # Around other settlements
            (140, 45), (180, 75), (45, 125), (75, 175),
            (25, 45), (175, 125), (125, 25), (175, 175)
        ]
        
        for x, y in settlement_tree_positions:
            if self.is_valid_tree_terrain(x, y) and self.is_valid_story_position(x, y):
                tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(tree)
        
        # Rocks in mountain regions
        # Dragon's Peak rocks
        dragon_peak_rocks = [
            (20, 20), (25, 18), (30, 22), (35, 19), (40, 25),
            (18, 30), (22, 35), (28, 38), (35, 40), (42, 35)
        ]
        
        for x, y in dragon_peak_rocks:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Orc Stronghold rocks
        stronghold_rocks = [
            (162, 18), (168, 16), (175, 20), (185, 25), (192, 28),
            (160, 25), (170, 30), (180, 35), (190, 32), (185, 18)
        ]
        
        for x, y in stronghold_rocks:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Crystal Caves rocks
        crystal_rocks = [
            (172, 82), (178, 88), (185, 92), (192, 85), (188, 95),
            (175, 100), (182, 105), (190, 110), (185, 115), (178, 118)
        ]
        
        for x, y in crystal_rocks:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Decorative rocks around all lakes
        lake_positions = [(150, 150), (40, 140), (60, 155), (100, 40)]
        for lake_x, lake_y in lake_positions:
            for i in range(8):  # 8 rocks around each lake
                angle = i * 45  # Every 45 degrees
                distance = random.randint(25, 35)
                rock_x = lake_x + int(distance * math.cos(math.radians(angle)))
                rock_y = lake_y + int(distance * math.sin(math.radians(angle)))
                
                if self.is_valid_story_position(rock_x, rock_y):
                    rock = Entity(rock_x, rock_y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                    self.objects.append(rock)
    
    def spawn_chests(self):
        """Spawn treasure chests across the expanded world"""
        # Wooden chests - common, scattered in safe-ish areas
        wooden_chest_positions = [
            # Near main village
            (75, 65), (125, 65), (75, 135), (125, 135),
            # Near settlements
            (140, 50), (110, 45), (45, 175), (175, 175),
            # In forests (clearings)
            (45, 45), (95, 35), (155, 45),
            # Near ruins
            (55, 65), (165, 125), (30, 175)
        ]
        
        for x, y in wooden_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "wooden", self.asset_loader)
                self.chests.append(chest)
        
        # Iron chests - better loot, in more dangerous areas
        iron_chest_positions = [
            # Deep in forests
            (35, 55), (105, 25), (165, 55),
            # Mountain areas
            (25, 35), (175, 35), (185, 95),
            # Desert and swamp edges
            (55, 145), (35, 105),
            # Near lakes
            (125, 175), (65, 145), (115, 45)
        ]
        
        for x, y in iron_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "iron", self.asset_loader)
                self.chests.append(chest)
        
        # Gold chests - high-value loot, hidden/dangerous locations
        gold_chest_positions = [
            # Boss areas
            (175, 25),  # Near Orc Stronghold
            (30, 25),   # Near Dragon's Peak
            (185, 85),  # In Crystal Caves
            # Deep wilderness
            (45, 165),  # Deep desert
            (35, 115),  # Deep swamp
            # Ancient ruins
            (165, 120), (25, 170)
        ]
        
        for x, y in gold_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "gold", self.asset_loader)
                self.chests.append(chest)
        
        # Magical chests - rare, powerful items in special locations
        magical_chest_positions = [
            # Stone circles
            (70, 50), (130, 130), (180, 40),
            # Hidden corners
            (15, 15), (185, 185), (15, 185), (185, 15),
            # Boss lairs (after defeating bosses)
            (25, 25),   # Dragon's treasure
            (175, 25),  # Orc warlord's hoard
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
        
        # Check if tile is walkable (using numeric walkable grid)
        if self.walkable[y][x] <= 0:
            return False
        
        # Don't place entities too close to player starting position
        start_x, start_y = 100, 102  # Updated to match new village center
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
        
        # Check if tile is walkable (using numeric walkable grid)
        if self.walkable[y][x] <= 0:
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
        """Check collision with level geometry and entities - improved precision with enhanced door handling"""
        # Check if the position is within level bounds with proper margin
        margin = size + 0.1
        if x < margin or x >= self.width - margin or y < margin or y >= self.height - margin:
            return True
        
        # Enhanced door area detection
        tile_x = int(x)
        tile_y = int(y)
        door_context = self.analyze_door_context(tile_x, tile_y, x, y)
        
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
    
    def analyze_door_context(self, tile_x, tile_y, world_x, world_y):
        """Analyze the door context around a position for better collision handling"""
        context = {
            'is_door_area': False,
            'is_double_door': False,
            'door_orientation': None,
            'distance_to_door': float('inf')
        }
        
        # Check current tile and surrounding area for doors
        check_radius = 2  # Check 2 tiles around
        doors_found = []
        
        for dy in range(-check_radius, check_radius + 1):
            for dx in range(-check_radius, check_radius + 1):
                check_x = tile_x + dx
                check_y = tile_y + dy
                
                if (0 <= check_x < self.width and 0 <= check_y < self.height):
                    if self.tiles[check_y][check_x] == self.TILE_DOOR:
                        door_distance = math.sqrt(dx*dx + dy*dy)
                        doors_found.append({
                            'pos': (check_x, check_y),
                            'distance': door_distance,
                            'world_pos': (check_x + 0.5, check_y + 0.5)
                        })
        
        if doors_found:
            # Find closest door
            closest_door = min(doors_found, key=lambda d: d['distance'])
            context['distance_to_door'] = closest_door['distance']
            
            # Consider it a door area if we're close enough
            if closest_door['distance'] <= 1.5:
                context['is_door_area'] = True
                
                # Check for double doors (adjacent door tiles)
                door_x, door_y = closest_door['pos']
                adjacent_doors = 0
                
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_x, adj_y = door_x + dx, door_y + dy
                    if (0 <= adj_x < self.width and 0 <= adj_y < self.height):
                        if self.tiles[adj_y][adj_x] == self.TILE_DOOR:
                            adjacent_doors += 1
                
                context['is_double_door'] = adjacent_doors > 0
                context['door_orientation'] = self.get_door_orientation(door_x, door_y)
        
        return context
    
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
        enhanced_path = self.enhance_door_pathfinding(smoothed_path, entity_size)
        
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
    
    def enhance_door_pathfinding(self, path, entity_size):
        """Add special handling for door navigation with improved doorway handling"""
        if len(path) < 2:
            return path
        
        enhanced_path = []
        i = 0
        
        while i < len(path):
            current_point = path[i]
            enhanced_path.append(current_point)
            
            # Look ahead for door navigation opportunities
            if i < len(path) - 1:
                next_point = path[i + 1]
                
                # Check if we're approaching a door or door area
                door_waypoints = self.generate_improved_door_waypoints(current_point, next_point, entity_size)
                
                if door_waypoints:
                    enhanced_path.extend(door_waypoints)
                    # Skip ahead if we've handled multiple points
                    if len(door_waypoints) > 2:
                        i += min(2, len(path) - i - 1)  # Skip some intermediate points
            
            i += 1
        
        return enhanced_path
    
    def generate_improved_door_waypoints(self, current, next_point, entity_size):
        """Generate improved intermediate waypoints for door navigation"""
        waypoints = []
        
        # Check if path crosses a door or door area
        doors_info = self.find_doors_with_context(current, next_point)
        
        for door_info in doors_info:
            door_pos = door_info['position']
            door_orientation = door_info['orientation']
            approach_side = door_info['approach_side']
            
            # Create more precise approach and exit points
            approach_point = self.calculate_precise_door_approach(door_pos, door_orientation, approach_side, entity_size)
            exit_point = self.calculate_precise_door_exit(door_pos, door_orientation, approach_side, entity_size)
            
            # Add alignment waypoint before door if needed
            if self.needs_door_alignment(current, door_pos, door_orientation):
                align_point = self.calculate_door_alignment_point(door_pos, door_orientation, current, entity_size)
                waypoints.append(align_point)
            
            # Add the main door navigation waypoints
            waypoints.extend([approach_point, door_pos, exit_point])
        
        return waypoints
    
    def find_doors_with_context(self, start, end):
        """Find doors between points with additional context information"""
        doors_info = []
        
        # Sample points along the line between start and end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return doors_info
        
        steps = max(int(distance * 3), 3)  # More sampling for better detection
        
        for i in range(steps + 1):
            t = i / steps
            x = start[0] + dx * t
            y = start[1] + dy * t
            
            tile_x, tile_y = int(x), int(y)
            if (0 <= tile_x < self.width and 0 <= tile_y < self.height and
                self.tiles[tile_y][tile_x] == self.TILE_DOOR):
                
                door_pos = (tile_x + 0.5, tile_y + 0.5)
                
                # Check if we already found this door
                already_found = any(info['position'] == door_pos for info in doors_info)
                if not already_found:
                    orientation = self.get_door_orientation(tile_x, tile_y)
                    approach_side = self.determine_approach_side(start, door_pos, orientation)
                    
                    doors_info.append({
                        'position': door_pos,
                        'orientation': orientation,
                        'approach_side': approach_side,
                        'tile_pos': (tile_x, tile_y)
                    })
        
        return doors_info
    
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
    
    def calculate_precise_door_approach(self, door_pos, orientation, approach_side, entity_size):
        """Calculate precise approach point for door based on orientation and approach side"""
        # Use larger clearance for approach to avoid getting stuck
        clearance = max(0.7, entity_size + 0.3)
        
        if orientation == "horizontal":
            if approach_side == "north":
                return (door_pos[0], door_pos[1] - clearance)
            else:  # south
                return (door_pos[0], door_pos[1] + clearance)
        else:  # vertical
            if approach_side == "west":
                return (door_pos[0] - clearance, door_pos[1])
            else:  # east
                return (door_pos[0] + clearance, door_pos[1])
    
    def calculate_precise_door_exit(self, door_pos, orientation, approach_side, entity_size):
        """Calculate precise exit point from door"""
        # Use larger clearance for exit to ensure we're fully through
        clearance = max(0.8, entity_size + 0.4)
        
        if orientation == "horizontal":
            if approach_side == "north":
                return (door_pos[0], door_pos[1] + clearance)  # Exit to south
            else:  # south
                return (door_pos[0], door_pos[1] - clearance)  # Exit to north
        else:  # vertical
            if approach_side == "west":
                return (door_pos[0] + clearance, door_pos[1])  # Exit to east
            else:  # east
                return (door_pos[0] - clearance, door_pos[1])  # Exit to west
    
    def needs_door_alignment(self, current_pos, door_pos, orientation):
        """Check if we need an alignment waypoint before approaching the door"""
        dx = abs(current_pos[0] - door_pos[0])
        dy = abs(current_pos[1] - door_pos[1])
        
        # If we're not well-aligned with the door, we need an alignment point
        if orientation == "horizontal":
            return dx > 0.3  # Not aligned horizontally
        else:
            return dy > 0.3  # Not aligned vertically
    
    def calculate_door_alignment_point(self, door_pos, orientation, current_pos, entity_size):
        """Calculate alignment point to approach door straight-on"""
        clearance = max(1.0, entity_size + 0.6)  # Extra clearance for alignment
        
        if orientation == "horizontal":
            # Align horizontally, maintain vertical distance
            align_y = current_pos[1]
            if align_y < door_pos[1]:
                align_y = door_pos[1] - clearance
            else:
                align_y = door_pos[1] + clearance
            return (door_pos[0], align_y)
        else:  # vertical
            # Align vertically, maintain horizontal distance
            align_x = current_pos[0]
            if align_x < door_pos[0]:
                align_x = door_pos[0] - clearance
            else:
                align_x = door_pos[0] + clearance
            return (align_x, door_pos[1])
    
    def generate_door_waypoints(self, current, next_point, entity_size):
        """Generate intermediate waypoints for door navigation (legacy method)"""
        waypoints = []
        
        # Check if path crosses a door
        door_positions = self.find_doors_between_points(current, next_point)
        
        for door_pos in door_positions:
            # Create approach waypoint (align with door)
            approach_point = self.calculate_door_approach_point(door_pos, current, entity_size)
            
            # Create exit waypoint (clear of door)
            exit_point = self.calculate_door_exit_point(door_pos, next_point, entity_size)
            
            waypoints.extend([approach_point, door_pos, exit_point])
        
        return waypoints
    
    def find_doors_between_points(self, start, end):
        """Find door tiles between two points"""
        doors = []
        
        # Sample points along the line between start and end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return doors
        
        steps = max(int(distance * 2), 2)
        
        for i in range(steps + 1):
            t = i / steps
            x = start[0] + dx * t
            y = start[1] + dy * t
            
            tile_x, tile_y = int(x), int(y)
            if (0 <= tile_x < self.width and 0 <= tile_y < self.height and
                self.tiles[tile_y][tile_x] == self.TILE_DOOR):
                door_pos = (tile_x + 0.5, tile_y + 0.5)
                if door_pos not in doors:
                    doors.append(door_pos)
        
        return doors
    
    def calculate_door_approach_point(self, door_pos, from_point, entity_size):
        """Calculate optimal approach point for door"""
        door_x, door_y = int(door_pos[0]), int(door_pos[1])
        
        # Find door orientation
        door_orientation = self.get_door_orientation(door_x, door_y)
        
        if door_orientation == "horizontal":
            # Approach from north or south
            if from_point[1] < door_y:
                return (door_pos[0], door_pos[1] - 0.6)  # Approach from north
            else:
                return (door_pos[0], door_pos[1] + 0.6)  # Approach from south
        else:
            # Approach from east or west
            if from_point[0] < door_x:
                return (door_pos[0] - 0.6, door_pos[1])  # Approach from west
            else:
                return (door_pos[0] + 0.6, door_pos[1])  # Approach from east
    
    def calculate_door_exit_point(self, door_pos, to_point, entity_size):
        """Calculate optimal exit point from door"""
        door_x, door_y = int(door_pos[0]), int(door_pos[1])
        
        # Find door orientation
        door_orientation = self.get_door_orientation(door_x, door_y)
        
        if door_orientation == "horizontal":
            # Exit to north or south
            if to_point[1] < door_y:
                return (door_pos[0], door_pos[1] - 0.6)  # Exit to north
            else:
                return (door_pos[0], door_pos[1] + 0.6)  # Exit to south
        else:
            # Exit to east or west
            if to_point[0] < door_x:
                return (door_pos[0] - 0.6, door_pos[1])  # Exit to west
            else:
                return (door_pos[0] + 0.6, door_pos[1])  # Exit to east
    
    def get_door_orientation(self, door_x, door_y):
        """Determine if door is horizontal or vertical based on surrounding walls"""
        # Check adjacent tiles to determine orientation
        horizontal_walls = 0
        vertical_walls = 0
        
        # Check north and south
        if (door_y > 0 and self.is_wall_tile(self.tiles[door_y - 1][door_x])):
            horizontal_walls += 1
        if (door_y < self.height - 1 and self.is_wall_tile(self.tiles[door_y + 1][door_x])):
            horizontal_walls += 1
        
        # Check east and west
        if (door_x > 0 and self.is_wall_tile(self.tiles[door_y][door_x - 1])):
            vertical_walls += 1
        if (door_x < self.width - 1 and self.is_wall_tile(self.tiles[door_y][door_x + 1])):
            vertical_walls += 1
        
        # If more walls on horizontal sides, door is horizontal
        return "horizontal" if horizontal_walls >= vertical_walls else "vertical"
    
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
        if self.is_wall_tile(tile_type):
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
        if self.is_wall_tile(tile_type):
            self.render_flat_wall(surface, screen_x, screen_y, tile_type, x, y)
        elif tile_type == self.TILE_DOOR:
            self.render_door_tile(surface, screen_x, screen_y, tile_type)
    
    def render_flat_wall(self, surface, screen_x, screen_y, tile_type, world_x, world_y):
        """Render walls using flat isometric surfaces with texture support"""
        # Wall height in pixels
        wall_height = 48
        
        # Load wall textures if not already loaded
        if not hasattr(self, 'wall_texture'):
            wall_texture_image = self.asset_loader.get_image("wall_texture")
            if wall_texture_image:
                self.wall_texture = wall_texture_image
            else:
                self.wall_texture = None
        
        # Load window wall texture if not already loaded
        if not hasattr(self, 'wall_texture_window'):
            window_texture_image = self.asset_loader.get_image("wall_texture_window")
            if window_texture_image:
                self.wall_texture_window = window_texture_image
            else:
                self.wall_texture_window = None
        
        # Base wall colors (fallback if no texture)
        wall_color = (180, 180, 180)  # Light gray
        shadow_color = (120, 120, 120)  # Darker gray for shadows
        highlight_color = (220, 220, 220)  # Lighter gray for highlights
        
        # Check adjacent tiles to determine which faces to draw
        # Swapped the directions to match isometric orientation
        north_wall = self.has_wall_at(world_x - 1, world_y)  # Actually west in world coords
        south_wall = self.has_wall_at(world_x + 1, world_y)  # Actually east in world coords  
        east_wall = self.has_wall_at(world_x, world_y + 1)   # Actually south in world coords
        west_wall = self.has_wall_at(world_x, world_y - 1)   # Actually north in world coords
        
        # Special handling for corner walls - they should only show outer faces
        is_corner = self.is_corner_wall(tile_type)
        
        # Calculate isometric wall face points
        tile_width = self.tile_width
        tile_height = self.tile_height
        
        # Different positioning for corners vs regular walls
        if is_corner:
            # Corners use original positioning (they were working correctly before)
            floor_y = screen_y  # Original position for corners
        else:
            # Regular walls use adjusted positioning to sit on floor properly
            floor_y = screen_y + tile_height // 2  # Move walls down to sit on the floor properly
        
        # Base diamond points (floor level)
        top_point = (screen_x, floor_y - tile_height // 2)
        right_point = (screen_x + tile_width // 2, floor_y)
        bottom_point = (screen_x, floor_y + tile_height // 2)
        left_point = (screen_x - tile_width // 2, floor_y)
        
        # Top diamond points (wall height) - walls extend upward from floor level
        top_top = (screen_x, floor_y - tile_height // 2 - wall_height)
        right_top = (screen_x + tile_width // 2, floor_y - wall_height)
        bottom_top = (screen_x, floor_y + tile_height // 2 - wall_height)
        left_top = (screen_x - tile_width // 2, floor_y - wall_height)
        
        # Draw wall faces based on adjacent walls and corner type
        if is_corner:
            # Corner walls render ALL faces for a complete 3D look
            # Always render all 4 side faces for corners
            self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
            self.render_textured_wall_face(surface, [top_point, right_point, right_top, top_top], "east", tile_type)
            self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
            self.render_textured_wall_face(surface, [left_point, bottom_point, bottom_top, left_top], "west", tile_type)
        else:
            # Regular wall rendering - show all exposed faces
            # North face (top-left edge in isometric view)
            if not north_wall:
                self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
            
            # East face (top-right edge in isometric view)  
            if not east_wall:
                self.render_textured_wall_face(surface, [top_point, right_point, right_top, top_top], "east", tile_type)
            
            # South face (bottom-right edge in isometric view)
            if not south_wall:
                self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
            
            # West face (bottom-left edge in isometric view)
            if not west_wall:
                self.render_textured_wall_face(surface, [left_point, bottom_point, bottom_top, left_top], "west", tile_type)
        
        # Always draw the top face with texture
        self.render_textured_wall_face(surface, [top_top, right_top, bottom_top, left_top], "top", tile_type)
        
        # Add window details for window walls (only if not using window texture)
        if (tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL] and
            not self.wall_texture_window):
            self.render_window_on_wall(surface, screen_x, screen_y, wall_height, not north_wall, not east_wall, not south_wall, not west_wall)
    
    def render_textured_wall_face(self, surface, face_points, face_direction, tile_type=None):
        """Render a single wall face with texture or fallback color"""
        # Determine which texture to use based on tile type
        is_window_wall = tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL] if tile_type else False
        current_texture = self.wall_texture_window if (is_window_wall and self.wall_texture_window) else self.wall_texture
        
        if current_texture and len(face_points) == 4:
            # Create a temporary surface for the face
            min_x = min(p[0] for p in face_points)
            max_x = max(p[0] for p in face_points)
            min_y = min(p[1] for p in face_points)
            max_y = max(p[1] for p in face_points)
            
            face_width = int(max_x - min_x) + 1
            face_height = int(max_y - min_y) + 1
            
            if face_width > 0 and face_height > 0:
                # Create face surface
                face_surface = pygame.Surface((face_width, face_height), pygame.SRCALPHA)
                
                # Scale texture to fit the face
                scaled_texture = pygame.transform.scale(current_texture, (face_width, face_height))
                
                # Apply lighting based on face direction
                if face_direction == "north":
                    # Brightest face (highlight)
                    tinted_texture = self.apply_tint_to_surface(scaled_texture, (255, 255, 255), 1.2)
                elif face_direction == "east":
                    # Normal lighting
                    tinted_texture = scaled_texture
                elif face_direction in ["south", "west"]:
                    # Darker faces (shadow)
                    tinted_texture = self.apply_tint_to_surface(scaled_texture, (180, 180, 180), 0.8)
                else:  # top
                    # Top face - normal lighting
                    tinted_texture = scaled_texture
                
                face_surface.blit(tinted_texture, (0, 0))
                
                # Create a mask for the face shape
                adjusted_points = [(p[0] - min_x, p[1] - min_y) for p in face_points]
                
                # Create mask surface
                mask_surface = pygame.Surface((face_width, face_height), pygame.SRCALPHA)
                pygame.draw.polygon(mask_surface, (255, 255, 255, 255), adjusted_points)
                
                # Apply mask to textured surface
                face_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Blit the textured face to the main surface
                surface.blit(face_surface, (min_x, min_y))
                
                # Draw border
                pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
        else:
            # Fallback to solid color rendering
            if face_direction == "north":
                color = (220, 220, 220)  # Highlight
            elif face_direction == "east":
                color = (180, 180, 180)  # Normal
            elif face_direction in ["south", "west"]:
                color = (120, 120, 120)  # Shadow
            else:  # top
                color = (180, 180, 180)  # Normal
            
            pygame.draw.polygon(surface, color, face_points)
            pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
    
    def apply_tint_to_surface(self, surface, tint_color, intensity=1.0):
        """Apply a tint to a surface for lighting effects"""
        tinted_surface = surface.copy()
        
        # Create tint overlay
        tint_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Adjust tint color by intensity
        adjusted_tint = (
            min(255, int(tint_color[0] * intensity)),
            min(255, int(tint_color[1] * intensity)),
            min(255, int(tint_color[2] * intensity))
        )
        
        tint_overlay.fill(adjusted_tint)
        
        # Apply tint using multiply blend mode
        tinted_surface.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_surface
    
    def is_corner_wall(self, tile_type):
        """Check if a tile type is a corner wall"""
        corner_types = [
            self.TILE_WALL_CORNER_TL, self.TILE_WALL_CORNER_TR,
            self.TILE_WALL_CORNER_BL, self.TILE_WALL_CORNER_BR
        ]
        return tile_type in corner_types
    
    def render_window_on_wall(self, surface, screen_x, screen_y, wall_height, show_north, show_east, show_south, show_west):
        """Render window details on exposed wall faces"""
        window_color = (150, 200, 255)  # Light blue for glass
        frame_color = (80, 60, 40)      # Brown for window frame
        
        window_size = 16
        window_height = 12
        
        # Render windows on exposed faces
        if show_north:  # North face window
            window_center_x = screen_x - self.tile_width // 4
            window_center_y = screen_y - wall_height // 2
            window_rect = pygame.Rect(window_center_x - window_size//2, window_center_y - window_height//2, window_size, window_height)
            pygame.draw.rect(surface, frame_color, window_rect)
            pygame.draw.rect(surface, window_color, (window_rect.x + 2, window_rect.y + 2, window_rect.width - 4, window_rect.height - 4))
        
        if show_east:   # East face window
            window_center_x = screen_x + self.tile_width // 4
            window_center_y = screen_y - wall_height // 2
            window_rect = pygame.Rect(window_center_x - window_size//2, window_center_y - window_height//2, window_size, window_height)
            pygame.draw.rect(surface, frame_color, window_rect)
            pygame.draw.rect(surface, window_color, (window_rect.x + 2, window_rect.y + 2, window_rect.width - 4, window_rect.height - 4))
    
    def has_wall_at(self, x, y):
        """Check if there's a wall at the given coordinates"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True  # Treat out-of-bounds as walls
        
        return self.is_wall_tile(self.tiles[y][x])
    
    def is_wall_tile(self, tile_type):
        """Check if a tile type is any kind of wall"""
        wall_types = [
            self.TILE_WALL, self.TILE_WALL_CORNER_TL, self.TILE_WALL_CORNER_TR,
            self.TILE_WALL_CORNER_BL, self.TILE_WALL_CORNER_BR,
            self.TILE_WALL_HORIZONTAL, self.TILE_WALL_VERTICAL, self.TILE_WALL_WINDOW,
            self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL
        ]
        return tile_type in wall_types
    
    def render_door_tile(self, surface, screen_x, screen_y, tile_type):
        """Render door exactly like walls but with rounded front face"""
        # Door height in pixels (same as walls)
        door_height = 48
        
        # Door colors
        door_color = (139, 69, 19)      # Brown door
        door_shadow = (100, 50, 10)     # Darker brown for shadows
        door_highlight = (180, 90, 30)  # Lighter brown for highlights
        
        # Get world coordinates for adjacency checking
        # Convert screen coordinates back to world coordinates using the isometric renderer
        world_x, world_y = self.iso_renderer.screen_to_world(screen_x, screen_y, self.camera_x, self.camera_y)
        world_x = int(world_x)
        world_y = int(world_y)
        
        # Check adjacent tiles to determine which faces to draw (same logic as walls)
        north_wall = self.has_wall_or_door_at(world_x - 1, world_y)
        south_wall = self.has_wall_or_door_at(world_x + 1, world_y)  
        east_wall = self.has_wall_or_door_at(world_x, world_y + 1)
        west_wall = self.has_wall_or_door_at(world_x, world_y - 1)
        
        # Calculate isometric door face points (same as walls)
        tile_width = self.tile_width
        tile_height = self.tile_height
        
        # Use same positioning as the original door code (which was correct)
        floor_y = screen_y + tile_height // 4
        
        # Base diamond points (floor level)
        top_point = (screen_x, floor_y - tile_height // 2)
        right_point = (screen_x + tile_width // 2, floor_y)
        bottom_point = (screen_x, floor_y + tile_height // 2)
        left_point = (screen_x - tile_width // 2, floor_y)
        
        # Top diamond points (door height)
        top_top = (screen_x, floor_y - tile_height // 2 - door_height)
        right_top = (screen_x + tile_width // 2, floor_y - door_height)
        bottom_top = (screen_x, floor_y + tile_height // 2 - door_height)
        left_top = (screen_x - tile_width // 2, floor_y - door_height)
        
        # Render door faces exactly like walls (show all exposed faces)
        
        # North face (top-left edge in isometric view)
        if not north_wall:
            north_face = [left_point, top_point, top_top, left_top]
            pygame.draw.polygon(surface, door_highlight, north_face)
            pygame.draw.polygon(surface, (60, 30, 5), north_face, 1)  # Dark border
        
        # East face (top-right edge in isometric view)  
        if not east_wall:
            east_face = [right_point, top_point, top_top, right_top]
            pygame.draw.polygon(surface, door_color, east_face)
            pygame.draw.polygon(surface, (60, 30, 5), east_face, 1)  # Dark border
        
        # South face (bottom-right edge in isometric view) - THE ROUNDED FRONT FACE
        if not south_wall:
            # Instead of a flat polygon, render a rounded face
            self.render_rounded_door_face(surface, bottom_point, right_point, right_top, bottom_top, door_shadow)
        
        # West face (bottom-left edge in isometric view)
        if not west_wall:
            west_face = [left_point, bottom_point, bottom_top, left_top]
            pygame.draw.polygon(surface, door_shadow, west_face)
            pygame.draw.polygon(surface, (60, 30, 5), west_face, 1)  # Dark border
        
        # Always draw the top face (same as walls) - but make it transparent
        # Skip drawing the top face to make it transparent
        # top_face = [top_top, right_top, bottom_top, left_top]
        # pygame.draw.polygon(surface, door_color, top_face)
        # pygame.draw.polygon(surface, (60, 30, 5), top_face, 1)  # Dark border
        
        # Add door handle on the front (south) face if it's visible
        if not south_wall:
            handle_x = screen_x + tile_width // 3
            handle_y = floor_y - door_height // 2
            pygame.draw.circle(surface, (255, 215, 0), (handle_x, handle_y), 3)  # Gold handle
            pygame.draw.circle(surface, (200, 160, 0), (handle_x, handle_y), 3, 1)  # Handle border
    
    def has_wall_or_door_at(self, x, y):
        """Check if there's a wall or door at the given coordinates"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True  # Treat out of bounds as walls
        
        tile = self.tiles[y][x]
        return self.is_wall_tile(tile) or tile == self.TILE_DOOR
    
    def render_rounded_door_face(self, surface, bottom_point, right_point, right_top, bottom_top, color):
        """Render a rounded door face using the door texture"""
        # Get the door texture from assets
        door_texture = self.asset_loader.get_image("door")
        
        print(f"DEBUG: Door texture loaded: {door_texture is not None}")
        if door_texture:
            print(f"DEBUG: Door texture size: {door_texture.get_size()}")
        
        if door_texture:
            # For simplicity, let's just render the texture as a flat face first
            # Calculate the face rectangle
            face_left = min(bottom_point[0], right_point[0], bottom_top[0], right_top[0])
            face_top = min(bottom_point[1], right_point[1], bottom_top[1], right_top[1])
            face_width = max(bottom_point[0], right_point[0], bottom_top[0], right_top[0]) - face_left
            face_height = max(bottom_point[1], right_point[1], bottom_top[1], right_top[1]) - face_top
            
            print(f"DEBUG: Face dimensions: {face_width}x{face_height}")
            
            if face_width > 0 and face_height > 0:
                # Scale the door texture to fit the face
                scaled_door = pygame.transform.scale(door_texture, (int(face_width), int(face_height)))
                
                # Create a surface for the door face
                face_surface = pygame.Surface((int(face_width), int(face_height)), pygame.SRCALPHA)
                
                # Draw the door face shape as a mask
                face_points = [
                    (bottom_point[0] - face_left, bottom_point[1] - face_top),
                    (right_point[0] - face_left, right_point[1] - face_top),
                    (right_top[0] - face_left, right_top[1] - face_top),
                    (bottom_top[0] - face_left, bottom_top[1] - face_top)
                ]
                
                # First, blit the texture
                face_surface.blit(scaled_door, (0, 0))
                
                # Create a mask surface
                mask_surface = pygame.Surface((int(face_width), int(face_height)), pygame.SRCALPHA)
                pygame.draw.polygon(mask_surface, (255, 255, 255, 255), face_points)
                
                # Apply the mask to the texture
                face_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
                
                # Blit the final textured face to the main surface
                surface.blit(face_surface, (face_left, face_top))
                
                # Draw border
                actual_face_points = [bottom_point, right_point, right_top, bottom_top]
                pygame.draw.polygon(surface, (60, 30, 5), actual_face_points, 2)
                
                print("DEBUG: Successfully rendered textured door face")
            else:
                print("DEBUG: Face dimensions invalid, using fallback")
                # Fallback to solid color
                self.render_rounded_door_face_fallback(surface, bottom_point, right_point, right_top, bottom_top, color)
        else:
            print("DEBUG: No door texture found, using fallback")
            # Fallback to solid color if no texture
            self.render_rounded_door_face_fallback(surface, bottom_point, right_point, right_top, bottom_top, color)
    
    def render_rounded_door_face_fallback(self, surface, bottom_point, right_point, right_top, bottom_top, color):
        """Fallback method for rounded door face with solid color"""
        # Calculate the center line of the face
        center_bottom_x = (bottom_point[0] + right_point[0]) // 2
        center_bottom_y = (bottom_point[1] + right_point[1]) // 2
        center_top_x = (bottom_top[0] + right_top[0]) // 2
        center_top_y = (bottom_top[1] + right_top[1]) // 2
        
        # Create curved segments by offsetting the center outward
        curve_offset = 8  # How much to curve outward
        
        # Calculate the outward direction (perpendicular to the face)
        face_dx = right_point[0] - bottom_point[0]
        face_dy = right_point[1] - bottom_point[1]
        # Rotate 90 degrees to get perpendicular (outward direction)
        outward_dx = -face_dy
        outward_dy = face_dx
        # Normalize
        length = math.sqrt(outward_dx * outward_dx + outward_dy * outward_dy)
        if length > 0:
            outward_dx = outward_dx / length * curve_offset
            outward_dy = outward_dy / length * curve_offset
        
        # Create curved points
        curved_bottom = (center_bottom_x + outward_dx, center_bottom_y + outward_dy)
        curved_top = (center_top_x + outward_dx, center_top_y + outward_dy)
        
        # Draw the curved face as multiple segments
        # Left segment
        left_segment = [bottom_point, curved_bottom, curved_top, bottom_top]
        pygame.draw.polygon(surface, color, left_segment)
        pygame.draw.polygon(surface, (60, 30, 5), left_segment, 1)
        
        # Right segment  
        right_segment = [curved_bottom, right_point, right_top, curved_top]
        pygame.draw.polygon(surface, color, right_segment)
        pygame.draw.polygon(surface, (60, 30, 5), right_segment, 1)
    
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