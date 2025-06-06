"""
Furniture entity system for the RPG game
Handles furniture objects that can be placed in buildings
"""

import pygame
from typing import Optional, Dict, Any
from .base import Entity


class Furniture(Entity):
    """Furniture entity that can be placed in buildings"""
    
    # Furniture types and their properties
    FURNITURE_TYPES = {
        'bed': {
            'name': 'Bed',
            'description': 'A comfortable bed for resting',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'bed',
            'width': 1,
            'height': 1
        },
        'table': {
            'name': 'Table',
            'description': 'A wooden table',
            'blocks_movement': True,
            'interactable': False,
            'sprite_name': 'table',
            'width': 1,
            'height': 1
        },
        'chair': {
            'name': 'Chair',
            'description': 'A wooden chair',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'chair',
            'width': 1,
            'height': 1
        },
        'chest': {
            'name': 'Storage Chest',
            'description': 'A chest for storing items',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'storage_chest',
            'width': 1,
            'height': 1
        },
        'shelf': {
            'name': 'Shelf',
            'description': 'A wooden shelf',
            'blocks_movement': True,
            'interactable': False,
            'sprite_name': 'shelf',
            'width': 1,
            'height': 1
        },
        'desk': {
            'name': 'Desk',
            'description': 'A writing desk',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'desk',
            'width': 1,
            'height': 1
        },
        'bar': {
            'name': 'Bar Counter',
            'description': 'A bar counter for serving drinks',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'bar',
            'width': 2,
            'height': 1
        },
        'kitchen': {
            'name': 'Kitchen Counter',
            'description': 'A kitchen counter for food preparation',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'kitchen',
            'width': 2,
            'height': 1
        },
        'weapon_rack': {
            'name': 'Weapon Rack',
            'description': 'A rack for displaying weapons',
            'blocks_movement': True,
            'interactable': False,
            'sprite_name': 'weapon_rack',
            'width': 1,
            'height': 1
        },
        'tool_rack': {
            'name': 'Tool Rack',
            'description': 'A rack for storing tools',
            'blocks_movement': True,
            'interactable': False,
            'sprite_name': 'tool_rack',
            'width': 1,
            'height': 1
        },
        'storage': {
            'name': 'Storage Container',
            'description': 'A container for storing various items',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'storage',
            'width': 1,
            'height': 1
        },
        'fancy_bed': {
            'name': 'Fancy Bed',
            'description': 'An ornate bed fit for nobility',
            'blocks_movement': True,
            'interactable': True,
            'sprite_name': 'fancy_bed',
            'width': 2,
            'height': 1
        }
    }
    
    def __init__(self, x: float, y: float, furniture_type: str, asset_loader=None):
        """Initialize furniture entity"""
        if furniture_type not in self.FURNITURE_TYPES:
            raise ValueError(f"Unknown furniture type: {furniture_type}")
        
        self.furniture_type = furniture_type
        self.properties = self.FURNITURE_TYPES[furniture_type].copy()
        
        # Initialize base entity
        super().__init__(x, y, self.properties['name'], "furniture", self.properties['blocks_movement'], asset_loader)
        
        # Set entity properties based on furniture type
        self.name = self.properties['name']
        self.description = self.properties['description']
        self.blocks_movement = self.properties['blocks_movement']
        self.interactable = self.properties['interactable']
        self.width = self.properties['width']
        self.height = self.properties['height']
        
        # Load sprite
        self._load_sprite()
        
        # Furniture-specific properties
        self.inventory = []  # Some furniture can store items
        self.max_inventory_size = 0
        
        # Set inventory size for storage furniture
        if furniture_type in ['chest', 'storage', 'desk']:
            self.max_inventory_size = 10
        elif furniture_type in ['bar', 'kitchen']:
            self.max_inventory_size = 5
    
    def _load_sprite(self):
        """Load the furniture sprite"""
        if self.asset_loader:
            sprite_name = self.properties['sprite_name']
            self.sprite = self.asset_loader.get_image(sprite_name)
            
            # Fallback to placeholder if sprite not found
            if not self.sprite:
                self.sprite = self._create_placeholder_sprite()
        else:
            self.sprite = self._create_placeholder_sprite()
    
    def _create_placeholder_sprite(self):
        """Create a placeholder sprite for furniture"""
        # Create a colored rectangle as placeholder
        color_map = {
            'bed': (139, 69, 19),      # Brown
            'table': (160, 82, 45),    # Saddle brown
            'chair': (210, 180, 140),  # Tan
            'chest': (101, 67, 33),    # Dark brown
            'shelf': (205, 133, 63),   # Peru
            'desk': (139, 69, 19),     # Brown
            'bar': (160, 82, 45),      # Saddle brown
            'kitchen': (255, 255, 255), # White
            'weapon_rack': (105, 105, 105), # Dim gray
            'tool_rack': (169, 169, 169),   # Dark gray
            'storage': (101, 67, 33),       # Dark brown
            'fancy_bed': (128, 0, 128)      # Purple
        }
        
        color = color_map.get(self.furniture_type, (128, 128, 128))
        width = 32 * self.width
        height = 32 * self.height
        
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color)
        
        # Add a border
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        
        return surface
    
    def interact(self, player):
        """Handle player interaction with furniture"""
        if not self.interactable:
            return False
        
        if self.furniture_type == 'bed':
            return self._interact_bed(player)
        elif self.furniture_type == 'chair':
            return self._interact_chair(player)
        elif self.furniture_type in ['chest', 'storage', 'desk']:
            return self._interact_storage(player)
        elif self.furniture_type in ['bar', 'kitchen']:
            return self._interact_counter(player)
        
        return False
    
    def _interact_bed(self, player):
        """Handle bed interaction - restore health"""
        if player.health < player.max_health:
            heal_amount = min(20, player.max_health - player.health)
            player.health += heal_amount
            if hasattr(player, 'game_log'):
                player.game_log.add_message(f"You rest on the {self.name} and recover {heal_amount} health.")
            return True
        else:
            if hasattr(player, 'game_log'):
                player.game_log.add_message("You are already at full health.")
            return False
    
    def _interact_chair(self, player):
        """Handle chair interaction - brief rest"""
        if hasattr(player, 'game_log'):
            player.game_log.add_message("You sit on the chair for a moment.")
        return True
    
    def _interact_storage(self, player):
        """Handle storage furniture interaction"""
        if hasattr(player, 'game_log'):
            if len(self.inventory) > 0:
                player.game_log.add_message(f"The {self.name} contains {len(self.inventory)} items.")
            else:
                player.game_log.add_message(f"The {self.name} is empty.")
        # TODO: Implement storage UI
        return True
    
    def _interact_counter(self, player):
        """Handle counter interaction"""
        if hasattr(player, 'game_log'):
            player.game_log.add_message(f"You examine the {self.name}.")
        return True
    
    def add_item(self, item):
        """Add item to furniture inventory"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_item(self, item):
        """Remove item from furniture inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def get_interaction_text(self):
        """Get text to display when player can interact"""
        interaction_map = {
            'bed': "Press E to rest",
            'chair': "Press E to sit",
            'chest': "Press E to open chest",
            'storage': "Press E to open storage",
            'desk': "Press E to examine desk",
            'bar': "Press E to examine bar",
            'kitchen': "Press E to examine kitchen"
        }
        return interaction_map.get(self.furniture_type, "Press E to interact")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert furniture to dictionary for saving"""
        data = super().to_dict()
        data.update({
            'furniture_type': self.furniture_type,
            'inventory': [item.to_dict() if hasattr(item, 'to_dict') else str(item) for item in self.inventory]
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], asset_loader=None):
        """Create furniture from dictionary"""
        furniture = cls(data['x'], data['y'], data['furniture_type'], asset_loader)
        
        # Restore inventory if present
        if 'inventory' in data:
            # TODO: Properly restore item objects from dict
            furniture.inventory = data['inventory']
        
        return furniture
    
    def update(self, dt):
        """Update furniture (most furniture is static)"""
        pass
    
    def render(self, surface, camera_x, camera_y, iso_renderer):
        """Render furniture using isometric projection with same scaling as other entities"""
        if not self.sprite:
            return
        
        # Convert world coordinates to screen coordinates
        screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
        
        # Use the same scaling approach as other entities (base.py)
        # Scale to a fixed size while maintaining aspect ratio
        base_size = 48  # Same as other entities
        
        # For multi-tile furniture, scale proportionally
        scaled_size = base_size * max(self.width, self.height)
        
        # Scale the sprite maintaining aspect ratio
        original_rect = self.sprite.get_rect()
        if original_rect.width > original_rect.height:
            # Wide sprite
            new_width = scaled_size
            new_height = int(scaled_size * original_rect.height / original_rect.width)
        else:
            # Tall or square sprite
            new_height = scaled_size
            new_width = int(scaled_size * original_rect.width / original_rect.height)
        
        scaled_sprite = pygame.transform.scale(self.sprite, (new_width, new_height))
        
        # Center the sprite
        sprite_rect = scaled_sprite.get_rect()
        sprite_rect.center = (screen_x, screen_y)
        
        # Render the scaled sprite
        surface.blit(scaled_sprite, sprite_rect)
        
        # Render interaction prompt if player is nearby
        if hasattr(self, '_show_interaction_prompt') and self._show_interaction_prompt:
            self._render_interaction_prompt(surface, screen_x, screen_y - 30)
    
    def _render_interaction_prompt(self, surface, x, y):
        """Render interaction prompt above furniture"""
        if not hasattr(self, '_interaction_font'):
            self._interaction_font = pygame.font.Font(None, 20)
        
        text = self.get_interaction_text()
        text_surface = self._interaction_font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Draw background
        bg_rect = text_rect.inflate(10, 4)
        pygame.draw.rect(surface, (0, 0, 0, 128), bg_rect)
        
        # Draw text
        surface.blit(text_surface, text_rect)
    
    def check_player_proximity(self, player, interaction_distance=1.5):
        """Check if player is close enough to interact"""
        distance = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5
        self._show_interaction_prompt = distance <= interaction_distance and self.interactable
        return self._show_interaction_prompt