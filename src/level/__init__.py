"""
Main Level class combining all functionality through mixins
"""

import pygame
from .level_base import LevelBase
from .level_world_gen import WorldGenerationMixin
from .level_collision import CollisionMixin
from .level_pathfinding import PathfindingMixin
from .tile_manager import TileManagerMixin
from .level_events import EventHandlingMixin
from .entity_manager import EntityManagerMixin
from .level_data import LevelDataMixin
from .level_renderer import LevelRendererMixin
from .procedural_mixin import ProceduralGenerationMixin
from ..ui.hud import HUD
from .ui_renderer import UIRendererMixin


class Level(
    LevelBase,
    ProceduralGenerationMixin,  # Add procedural generation capability
    WorldGenerationMixin,
    CollisionMixin,
    PathfindingMixin,
    TileManagerMixin,
    EventHandlingMixin,
    EntityManagerMixin,
    LevelDataMixin,
    LevelRendererMixin,
    UIRendererMixin
):
    """
    Complete Level class combining all functionality through mixins.
    
    This class maintains the same public API as the original monolithic Level class
    while providing a cleaner, more maintainable internal structure.
    """
    
    def __init__(self, level_name, player, asset_loader, game=None, use_procedural=False, seed=None):
        """Initialize the level with all functionality"""
        
        if use_procedural:
            # For procedural levels, initialize base without template generation
            print(f"Creating procedural level: {level_name}")
            
            # Initialize the base class but skip template initialization
            self.name = level_name
            self.player = player
            self.asset_loader = asset_loader
            self.game = game
            self.width = 1000  # Large procedural world size
            self.height = 1000
            
            # Initialize core systems without template loading
            from ..core.isometric import IsometricRenderer
            from ..core.game_log import GameLog
            from ..door_pathfinder import DoorPathfinder
            from ..door_renderer import DoorRenderer
            from ..wall_renderer import WallRenderer
            
            self.iso_renderer = IsometricRenderer(64, 32)
            self.tile_width = self.iso_renderer.tile_width
            self.tile_height = self.iso_renderer.tile_height
            
            self.door_renderer = DoorRenderer(asset_loader, self.iso_renderer)
            self.door_pathfinder = DoorPathfinder(self)
            self.wall_renderer = WallRenderer(self)
            
            self.camera_x = 0
            self.camera_y = 0
            self.template_generator = None
            
            # Combat state tracking
            self.enemies_in_combat = set()
            self.combat_music_timer = 0
            
            # Initialize empty entity lists
            self.npcs = []
            self.enemies = []
            self.objects = []
            self.items = []
            self.chests = []  # Add chests list
            
            # Generate procedural world
            self.generate_procedural_level(seed)
            
        else:
            # Use existing template system
            print(f"Creating template level: {level_name}")
            # Initialize the base class normally
            super().__init__(level_name, player, asset_loader, game)
        
        # Initialize HUD
        self.hud = HUD(self.game)
        
        # Create tile sprites after initialization
        if hasattr(self, 'create_tile_sprites'):
            self.create_tile_sprites()
    
    def update(self):
        """Main update loop - coordinates all subsystems"""
        # Handle player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self)  # Pass level to handle_input
        
        # Update player
        self.player.update(self)
        
        # Update all entities (enemies, NPCs, items)
        self.update_entities()


# For backward compatibility, export Level as the main class
__all__ = ['Level']