"""
Base Entity class for the RPG
"""

import pygame
import math
import random

class Entity:
    """Base entity class"""
    
    def __init__(self, x, y, name, entity_type="entity", blocks_movement=False, asset_loader=None):
        self.x = x
        self.y = y
        self.name = name
        self.entity_type = entity_type
        self.blocks_movement = blocks_movement
        self.asset_loader = asset_loader
        self.sprite = None
        self.size = 0.4
        
        # Create basic sprite
        self.create_sprite()
    
    def create_sprite(self):
        """Create a basic sprite"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded assets first
        if self.asset_loader and self.entity_type == "object":
            # First try to load by exact name (for biome-specific objects)
            object_image = self.asset_loader.get_image(self.name.lower())
            if object_image:
                self.sprite = pygame.transform.scale(object_image, (size, size))
                return
            
            # Fallback to generic types for backwards compatibility
            if "tree" in self.name.lower():
                tree_image = self.asset_loader.get_image("tree")
                if tree_image:
                    self.sprite = pygame.transform.scale(tree_image, (size, size))
                    return
            elif "rock" in self.name.lower():
                rock_image = self.asset_loader.get_image("rock")
                if rock_image:
                    self.sprite = pygame.transform.scale(rock_image, (size, size))
                    return
            elif "cactus" in self.name.lower():
                # Try specific cactus first, fallback to generic tree
                tree_image = self.asset_loader.get_image("tree")
                if tree_image:
                    self.sprite = pygame.transform.scale(tree_image, (size, size))
                    return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Default color based on entity type
        if self.entity_type == "object":
            if "Tree" in self.name:
                color = (34, 139, 34)  # Forest green
            elif "Rock" in self.name:
                color = (128, 128, 128)  # Gray
            else:
                color = (139, 69, 19)  # Brown
        elif self.entity_type == "npc":
            color = (0, 0, 255)  # Blue
        elif self.entity_type == "enemy":
            color = (255, 0, 0)  # Red
        elif self.entity_type == "item":
            color = (255, 255, 0)  # Yellow
        elif self.entity_type == "chest":
            color = (139, 69, 19)  # Brown
        else:
            color = (128, 128, 128)  # Gray
        
        pygame.draw.circle(self.sprite, color, (size//2, size//2), size//2 - 2)
        
        # Add border
        pygame.draw.circle(self.sprite, (0, 0, 0), (size//2, size//2), size//2 - 2, 2)
    
    def update(self, level):
        """Update entity state"""
        pass
    
    def render(self, screen, camera_x, camera_y, isometric_renderer):
        """Render the entity"""
        if self.sprite:
            # Convert world coordinates to isometric screen coordinates
            screen_x, screen_y = isometric_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
            
            
            # Center the sprite
            sprite_rect = self.sprite.get_rect()
            sprite_rect.center = (screen_x, screen_y)
            
            screen.blit(self.sprite, sprite_rect)
    
    def get_distance_to(self, other_entity):
        """Calculate distance to another entity"""
        dx = self.x - other_entity.x
        dy = self.y - other_entity.y
        return math.sqrt(dx * dx + dy * dy)
    
    def is_adjacent_to(self, other_entity, threshold=1.5):
        """Check if this entity is adjacent to another entity"""
        return self.get_distance_to(other_entity) <= threshold
    
    def get_save_data(self):
        """Get basic entity data for saving"""
        return {
            "x": self.x,
            "y": self.y,
            "name": self.name,
            "entity_type": self.entity_type,
            "blocks_movement": self.blocks_movement
        }
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create entity from save data"""
        entity = cls(
            x=data["x"],
            y=data["y"],
            name=data["name"],
            entity_type=data.get("entity_type", "entity"),
            blocks_movement=data.get("blocks_movement", False),
            asset_loader=asset_loader
        )
        return entity
