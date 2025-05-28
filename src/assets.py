"""
Asset loader for the RPG
"""

import pygame
import os

class AssetLoader:
    """Handles loading and managing game assets"""
    
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        self.asset_path = "assets"
        
        # Create asset directories if they don't exist
        os.makedirs(os.path.join(self.asset_path, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.asset_path, "sounds"), exist_ok=True)
        
        # Load all assets
        self.load_images()
        self.load_sounds()
        self.load_fonts()
    
    def load_images(self):
        """Load all image assets"""
        image_path = os.path.join(self.asset_path, "images")
        
        # Define image mappings
        image_files = {
            "grass_tile": "grass_tile.png",
            "stone_tile": "stone_tile.png", 
            "water_tile": "water_tile.png",
            "wall_tile": "wall_tile.png",
            "player_sprite": "player_sprite.png",
            "goblin_sprite": "goblin_sprite.png",
            "orc_boss_sprite": "orc_boss_sprite.png",
            "npc_shopkeeper": "npc_shopkeeper.png",
            "items_spritesheet": "items_spritesheet.png",
            "tree": "tree.png",
            "rock": "rock.png"
        }
        
        for name, filename in image_files.items():
            filepath = os.path.join(image_path, filename)
            if os.path.exists(filepath):
                try:
                    image = pygame.image.load(filepath).convert_alpha()
                    self.images[name] = image
                    print(f"Loaded image: {name}")
                except pygame.error as e:
                    print(f"Failed to load image {name}: {e}")
                    # Create a fallback colored rectangle
                    self.images[name] = self.create_fallback_image(name)
            else:
                print(f"Image not found: {filepath}, creating fallback")
                self.images[name] = self.create_fallback_image(name)
    
    def create_fallback_image(self, name):
        """Create fallback colored rectangles when images aren't available"""
        size = (64, 32) if "tile" in name else (32, 32)
        
        # Color mapping for fallbacks
        colors = {
            "grass_tile": (50, 150, 50),
            "stone_tile": (150, 150, 150),
            "water_tile": (50, 100, 200),
            "wall_tile": (100, 100, 100),
            "player_sprite": (100, 150, 255),
            "goblin_sprite": (0, 100, 0),
            "orc_boss_sprite": (139, 0, 0),
            "npc_shopkeeper": (255, 215, 0),
            "items_spritesheet": (255, 255, 255),
            "tree": (34, 139, 34),
            "rock": (128, 128, 128)
        }
        
        color = colors.get(name, (255, 255, 255))
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        
        # Add border for visibility
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        
        return surface
    
    def load_sounds(self):
        """Load sound assets (placeholder for now)"""
        # For now, we'll skip sound loading as requested
        # but keep the structure for future use
        pass
    
    def load_fonts(self):
        """Load font assets"""
        # Load default fonts
        self.fonts["default"] = pygame.font.Font(None, 24)
        self.fonts["large"] = pygame.font.Font(None, 36)
        self.fonts["title"] = pygame.font.Font(None, 72)
    
    def get_image(self, name):
        """Get an image by name"""
        return self.images.get(name)
    
    def get_sound(self, name):
        """Get a sound by name"""
        return self.sounds.get(name)
    
    def get_font(self, name):
        """Get a font by name"""
        return self.fonts.get(name, self.fonts["default"])
    
    def scale_image(self, image, scale_factor):
        """Scale an image by a factor"""
        if image:
            new_size = (int(image.get_width() * scale_factor), 
                       int(image.get_height() * scale_factor))
            return pygame.transform.scale(image, new_size)
        return None
    
    def extract_sprite_from_sheet(self, sheet_name, x, y, width, height):
        """Extract a sprite from a spritesheet"""
        sheet = self.get_image(sheet_name)
        if sheet:
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), (x, y, width, height))
            return sprite
        return None