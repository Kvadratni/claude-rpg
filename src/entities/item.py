"""
Item entities for the RPG
"""

import pygame
import math
import random
from .base import Entity

class Item(Entity):
    """Item entity"""
    
    def __init__(self, x, y, name, item_type="misc", effect=None, value=0, asset_loader=None):
        super().__init__(x, y, name, "item")
        self.item_type = item_type  # weapon, armor, consumable, misc
        self.effect = effect or {}
        self.value = value
        self.asset_loader = asset_loader
        
        # Animation
        self.bob_offset = 0
        self.bob_speed = 0.1
        
        # Create item sprite
        self.create_item_sprite()
    
    def create_item_sprite(self):
        """Create item sprite using individual sprite files"""
        size = 36  # Increased from 24 to 36
        
        # Map item names to sprite names with values
        sprite_mapping = {
            # Weapons
            "Iron Sword": ("iron_sword", 100),
            "Steel Axe": ("steel_axe", 150), 
            "Bronze Mace": ("bronze_mace", 80),
            "Silver Dagger": ("silver_dagger", 120),
            "War Hammer": ("war_hammer", 200),
            "Magic Bow": ("magic_bow", 180),
            "Crystal Staff": ("crystal_staff", 220),
            "Throwing Knife": ("throwing_knife", 90),
            "Crossbow": ("crossbow", 160),
            # Armor
            "Leather Armor": ("leather_armor", 80),
            "Chain Mail": ("chain_mail", 120),
            "Plate Armor": ("plate_armor", 200), 
            "Studded Leather": ("studded_leather", 100),
            "Scale Mail": ("scale_mail", 160),
            "Dragon Scale Armor": ("dragon_scale_armor", 300),
            "Mage Robes": ("mage_robes", 180),
            "Royal Armor": ("royal_armor", 350),
            # Consumables
            "Health Potion": ("health_potion", 25),
            "Stamina Potion": ("stamina_potion", 20),
            "Mana Potion": ("mana_potion", 30),
            "Antidote": ("antidote", 35),
            "Strength Potion": ("strength_potion", 50),
            # Miscellaneous
            "Gold Ring": ("gold_ring", 250),
            "Magic Scroll": ("magic_scroll", 200),
            "Crystal Gem": ("crystal_gem", 150)
        }
        
        # Set item value if not already set
        if self.value == 0 and self.name in sprite_mapping:
            self.value = sprite_mapping[self.name][1]
        
        # Try to use individual sprite files
        if self.asset_loader and self.name in sprite_mapping:
            sprite_name = sprite_mapping[self.name][0]
            item_image = self.asset_loader.get_image(sprite_name)
            if item_image:
                self.sprite = pygame.transform.scale(item_image, (size, size))
                return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different item types
        if self.item_type == "weapon":
            color = (192, 192, 192)  # Silver
            # Draw sword shape
            pygame.draw.rect(self.sprite, color, (size//2 - 3, 6, 6, size - 12))
            pygame.draw.rect(self.sprite, (139, 69, 19), (size//2 - 6, size - 12, 12, 6))
        elif self.item_type == "armor":
            color = (165, 42, 42)  # Brown
            # Draw armor shape
            pygame.draw.ellipse(self.sprite, color, (6, 9, size - 12, size - 15))
        elif self.item_type == "consumable":
            if "Health" in self.name:
                color = (255, 0, 0)  # Red for health
            else:
                color = (0, 0, 255)  # Blue for mana
            # Draw potion shape
            pygame.draw.ellipse(self.sprite, color, (9, 12, size - 18, size - 18))
            pygame.draw.rect(self.sprite, (139, 69, 19), (size//2 - 3, 6, 6, 9))
        else:
            color = (255, 215, 0)  # Gold
            # Draw generic item
            pygame.draw.circle(self.sprite, color, (size//2, size//2), size//3)
        
        # Add border
        pygame.draw.circle(self.sprite, (0, 0, 0), (size//2, size//2), size//3, 3)  # Thicker border
    
    def update(self, level):
        """Update item (bobbing animation)"""
        self.bob_offset += self.bob_speed
        if self.bob_offset > math.pi * 2:
            self.bob_offset = 0
    
    def render(self, screen, camera_x, camera_y, iso_renderer):
        """Render the item with bobbing animation"""
        if self.sprite:
            screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
            
            # Add bobbing effect
            bob_y = math.sin(self.bob_offset) * 3
            
            # Center the sprite
            sprite_rect = self.sprite.get_rect()
            sprite_rect.center = (screen_x, screen_y - 16 + bob_y)
            
            screen.blit(self.sprite, sprite_rect)
            
            # Render item name when close to player
            # This would be better handled by the level or UI system
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "item_type": self.item_type,
            "effect": self.effect,
            "value": self.value
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create item from save data"""
        item = cls(data["x"], data["y"], data["name"], data["item_type"], data["effect"], data["value"], asset_loader)
        return item