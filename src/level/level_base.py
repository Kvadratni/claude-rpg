"""
Base Level class with core functionality
"""

import os
import pygame
import random
import math

try:
    from ..core.isometric import IsometricRenderer, sort_by_depth
    from ..entities import Entity, NPC, Enemy, Item
    from ..core.game_log import GameLog
    from ..door_pathfinder import DoorPathfinder
    from ..door_renderer import DoorRenderer
    from ..wall_renderer import WallRenderer
    from ..template_level import integrate_template_generation
    from ..entities.spawning import SpawningMixin
except ImportError:
    # Fallback for direct execution
    from src.core.isometric import IsometricRenderer, sort_by_depth
    from ..entities import Entity, NPC, Enemy, Item
    from src.core.game_log import GameLog
    from src.door_pathfinder import DoorPathfinder
    from src.door_renderer import DoorRenderer
    from src.wall_renderer import WallRenderer
    from src.template_level import integrate_template_generation
    from src.entities.spawning import SpawningMixin


class LevelBase(SpawningMixin):
    """Base Level class with core initialization and constants"""
    
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
    # Biome-specific tiles
    TILE_SAND = 16            # Desert sand
    TILE_SNOW = 17            # Snow/ice
    TILE_FOREST_FLOOR = 18    # Forest floor
    TILE_SWAMP = 19           # Swamp mud
    
    def __init__(self, level_name, player, asset_loader, game=None):
        """Initialize the base level"""
        self.name = level_name
        self.player = player
        self.asset_loader = asset_loader
        self.game = game
        self.width = 1000  # Large procedural world size
        self.height = 1000
        
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
        
        # Combat state tracking
        self.enemies_in_combat = set()  # Track which enemies are in combat
        self.combat_music_timer = 0     # Timer for combat music fade out
        
        # Initialize template-based generation
        self._initialize_template_generation()
        
        # Generate heightmap and walkable grid if not already done
        self._initialize_level_data()
    
    def _initialize_template_generation(self):
        """Initialize template-based level generation"""
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
    
    def _initialize_level_data(self):
        """Initialize heightmap and walkable grid if not already done"""
        if not hasattr(self, 'heightmap') or self.heightmap is None:
            self.heightmap = self.generate_heightmap()
        if not hasattr(self, 'walkable') or self.walkable is None:
            self.walkable = self.generate_walkable_grid()
    
    def generate_heightmap(self):
        """Generate a heightmap for the level"""
        heightmap = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Default height
                height = 0
                
                # Walls are higher
                tile_type = self.get_tile(x, y) if hasattr(self, 'get_tile') else self.tiles[y][x]
                if tile_type == self.TILE_WALL:
                    height = 1
                # Water is lower
                elif tile_type == self.TILE_WATER:
                    height = -0.5
                # Add some random height variations
                elif random.random() < 0.1:
                    height = random.uniform(-0.1, 0.1)
                
                row.append(height)
            heightmap.append(row)
        
        return heightmap
    
    def generate_walkable_grid(self):
        """Generate enhanced walkable grid that includes object influence"""
        walkable = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Start with basic tile walkability
                tile_type = self.get_tile(x, y) if hasattr(self, 'get_tile') else self.tiles[y][x]
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
    
    def update_camera(self, screen_width, screen_height):
        """Update camera to follow player"""
        # Convert player position to isometric coordinates
        player_iso_x, player_iso_y = self.iso_renderer.cart_to_iso(self.player.x, self.player.y)
        
        # Center camera on player
        self.camera_x = player_iso_x - screen_width // 2
        self.camera_y = player_iso_y - screen_height // 2