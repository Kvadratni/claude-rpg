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
from .ui_renderer import UIRendererMixin


class Level(
    LevelBase,
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
    
    def __init__(self, level_name, player, asset_loader):
        """Initialize the level with all functionality"""
        # Initialize the base class
        super().__init__(level_name, player, asset_loader)
        
        # Create tile sprites after initialization
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