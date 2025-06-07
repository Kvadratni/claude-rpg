"""
Asset loader for the RPG
"""

import pygame
import os

class AssetLoader:
    """Handles loading and managing game assets"""
    
    def __init__(self, settings=None):
        self.settings = settings
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
            "wall_tile": "wall_texture.png",
            "wall_texture": "wall_texture.png",  # Added for wall face rendering
            "wall_texture_window": "wall_texture_window.png",  # Added for window wall rendering
            "wall_corner_tl": "wall_texture.png",
            "wall_corner_tr": "wall_texture.png", 
            "wall_corner_bl": "wall_texture.png",
            "wall_corner_br": "wall_texture.png",
            "wall_horizontal": "wall_texture.png",
            "wall_vertical": "wall_texture.png",
            "wall_window_horizontal": "wall_texture_window.png",
            "wall_window_vertical": "wall_texture_window.png",
            "dirt_tile": "dirt_tile.png",  # Added dirt tile
            "door_tile": "door.png",  # Fixed: use door.png instead of door_tile.png
            "door_tile_isometric": "door.png",  # Added for isometric door rendering
            "door": "door.png",  # Added door texture for front face
            "archway_texture": "archway_texture_tall.png",  # Updated to use tall archway texture for better wall face fit
            "wall_door": "wall_door.png",  # Wall texture showing an open door for side/back faces
            "brick_tile": "brick_tile.png",  # Added brick tile for building interiors
            "roof_texture": "roof_texture.png",  # Added roof texture for building roofs
            "sand_tile": "sand_tile.png",
            "snow_tile": "snow_tile.png",
            "forest_floor_tile": "forest_floor_tile.png",
            "swamp_tile": "swamp_tile.png",
            "player_sprite": "player_sprite.png",
            "goblin_sprite": "goblin_sprite.png",
            "orc_boss_sprite": "orc_boss_sprite.png",
            "npc_shopkeeper": "npc_shopkeeper.png",
            "generic_npc": "generic_npc.png",  # Added generic NPC for background NPCs
            "trader": "trader.png",
            "elder_npc": "elder_npc.png",  # Added elder NPC
            "village_guard_sprite": "village_guard_sprite.png",  # Added village guard
            # New NPCs
            "guard_captain": "guard_captain.png",
            "master_smith": "master_smith.png",
            "innkeeper": "innkeeper.png",
            "high_priest": "high_priest.png",
            "mine_foreman": "mine_foreman.png",
            "harbor_master": "harbor_master.png",
            "caravan_master": "caravan_master.png",
            "forest_ranger": "forest_ranger.png",
            "master_herbalist": "master_herbalist.png",
            "mysterious_wizard": "mysterious_wizard.png",
            "old_hermit": "old_hermit.png",
            "stable_master": "stable_master.png",  # Added missing stable master
            "master_fisher": "master_fisher.png",  # Added missing master fisher
            "trade_master": "trade_master.png",    # Added missing trade master
            # Additional NPCs that need new assets
            "mayor": "mayor.png",
            "noble": "noble.png", 
            "banker": "banker.png",
            "librarian": "librarian.png",
            "guild_master": "guild_master.png",
            "barkeeper": "barkeeper.png",
            "craftsman": "craftsman.png",
            "master_woodcutter": "master_woodcutter.png",
            "miller": "miller.png",
            "boat_builder": "boat_builder.png",
            "swamp_witch": "swamp_witch.png",
            "fur_trader": "fur_trader.png",
            "ice_keeper": "ice_keeper.png",
            "water_keeper": "water_keeper.png",
            "mushroom_farmer": "mushroom_farmer.png",
            "assayer": "assayer.png",
            # New Enemies
            "bandit_scout": "bandit_scout.png",
            "forest_sprite": "forest_sprite.png",
            "ancient_guardian": "ancient_guardian.png",
            "orc_warrior": "orc_warrior.png",
            "ancient_dragon": "ancient_dragon.png",
            "fire_drake": "fire_drake.png",
            "crystal_elemental": "crystal_elemental.png",
            "giant_scorpion": "giant_scorpion.png",
            "swamp_troll": "swamp_troll.png",
            # Ranged Enemies
            "goblin_archer": "goblin_archer.png",
            "orc_crossbow": "orc_crossbow.png",
            "skeleton_archer": "skeleton_archer.png",
            "dark_mage": "dark_mage.png",
            "tree": "tree.png",
            "rock": "rock.png",
            # Biome-specific environmental objects
            "cactus_saguaro": "cactus_saguaro.png",
            "cactus_barrel": "cactus_barrel.png",
            "desert_rock": "desert_rock.png",
            "snowy_pine": "snowy_pine.png",
            "ice_block": "ice_block.png",
            "frozen_rock": "frozen_rock.png",
            "dead_tree": "dead_tree.png",
            "swamp_log": "swamp_log.png",
            "swamp_mushroom": "swamp_mushroom.png",
            "pine_tree": "pine_tree.png",
            "oak_tree": "oak_tree.png",
            "fallen_log": "fallen_log.png",
            "menu_background": "menu_background.png",  # Added menu background
            # Individual item sprites
            "iron_sword": "iron_sword.png",
            "steel_axe": "steel_axe.png",
            "bronze_mace": "bronze_mace.png",
            "silver_dagger": "silver_dagger.png",
            "war_hammer": "war_hammer.png",
            # New weapons
            "magic_bow": "magic_bow.png",
            "crystal_staff": "crystal_staff.png",
            "throwing_knife": "throwing_knife.png",
            "crossbow": "crossbow.png",
            # Armor
            "leather_armor": "leather_armor.png",
            "chain_mail": "chain_mail.png",
            "plate_armor": "plate_armor.png",
            "studded_leather": "studded_leather.png",
            "scale_mail": "scale_mail.png",
            # New armor
            "dragon_scale_armor": "dragon_scale_armor.png",
            "mage_robes": "mage_robes.png",
            "royal_armor": "royal_armor.png",
            # Consumables
            "health_potion": "health_potion.png",
            "stamina_potion": "stamina_potion.png",
            # New consumables
            "mana_potion": "mana_potion.png",
            "antidote": "antidote.png",
            "strength_potion": "strength_potion.png",
            # Miscellaneous items
            "coin": "coin.png",
            "gold_ring": "gold_ring.png",
            "magic_scroll": "magic_scroll.png",
            "crystal_gem": "crystal_gem.png",
            # Chest sprites
            "wooden_chest_closed": "wooden_chest_closed.png",
            "wooden_chest_open": "wooden_chest_open.png",
            "iron_chest_closed": "iron_chest_closed.png",
            "iron_chest_open": "iron_chest_open.png",
            "gold_chest_closed": "gold_chest_closed.png",
            "gold_chest_open": "gold_chest_open.png",
            "magical_chest_closed": "magical_chest_closed.png",
            "magical_chest_open": "magical_chest_open.png",
            # Furniture sprites
            "bed": "bed.png",
            "table": "table.png",
            "chair": "chair.png",
            "storage_chest": "storage_chest.png",
            "shelf": "shelf.png",
            "desk": "desk.png",
            "bar": "bar.png",
            "kitchen": "kitchen.png",
            "weapon_rack": "weapon_rack.png",
            "tool_rack": "tool_rack.png",
            "storage": "storage.png",
            "fancy_bed": "fancy_bed.png",
            # Game logos
            "goose_rpg_logo": "goose_rpg_logo.png",
            "goose_rpg_icon": "goose_rpg_icon.png",
            "goose_rpg_icon_bg": "goose_rpg_icon_bg.png",
            "goose_rpg_square_logo": "goose_rpg_square_logo.png"
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
            "wall_texture": (100, 100, 100),  # Added for wall face rendering
            "wall_texture_window": (120, 120, 150),  # Added for window wall rendering
            "wall_corner_tl": (90, 90, 90),    # Slightly darker for corners
            "wall_corner_tr": (90, 90, 90),
            "wall_corner_bl": (90, 90, 90), 
            "wall_corner_br": (90, 90, 90),
            "wall_horizontal": (110, 110, 110), # Slightly lighter for directional walls
            "wall_vertical": (110, 110, 110),
            "wall_window_horizontal": (120, 120, 150),  # Slightly blue-tinted for window walls
            "wall_window_vertical": (120, 120, 150),    # Slightly blue-tinted for window walls
            "dirt_tile": (139, 69, 19),  # Brown for dirt
            "door_tile": (139, 69, 19),  # Brown for door
            "door_tile_isometric": (139, 69, 19),  # Brown for isometric door
            "door": (139, 69, 19),  # Brown for door texture
            "archway_texture": (160, 140, 120),  # Stone archway color
            "wall_door": (120, 100, 80),  # Open door wall color (slightly darker than archway)
            "brick_tile": (150, 80, 60),  # Reddish-brown for brick
            "roof_texture": (60, 40, 20),  # Dark brown for roof
            "sand_tile": (220, 180, 120),  # Sandy beige
            "snow_tile": (240, 240, 255),  # Snowy white
            "forest_floor_tile": (80, 60, 40),  # Dark forest floor
            "swamp_tile": (60, 80, 50),  # Murky swamp color
            "player_sprite": (100, 150, 255),
            "goblin_sprite": (0, 100, 0),
            "orc_boss_sprite": (139, 0, 0),
            "npc_shopkeeper": (255, 215, 0),
            "generic_npc": (180, 180, 180),  # Light gray for generic NPCs
            "trader": (210, 180, 140),  # Tan for simple trader
            "elder_npc": (128, 0, 128),  # Purple for elder
            "village_guard_sprite": (70, 130, 180),  # Steel blue for guard
            # New NPCs
            "guard_captain": (70, 130, 180),  # Steel blue
            "master_smith": (139, 69, 19),  # Brown
            "innkeeper": (160, 82, 45),  # Saddle brown
            "high_priest": (255, 255, 255),  # White
            "mine_foreman": (105, 105, 105),  # Gray
            "harbor_master": (0, 100, 150),  # Navy blue
            "caravan_master": (210, 180, 140),  # Tan
            "forest_ranger": (34, 139, 34),  # Forest green
            "master_herbalist": (50, 205, 50),  # Lime green
            "mysterious_wizard": (75, 0, 130),  # Indigo
            "old_hermit": (160, 160, 160),  # Gray
            "stable_master": (160, 82, 45),  # Saddle brown for stable master
            "master_fisher": (0, 139, 139),  # Dark cyan for fisher
            "trade_master": (255, 140, 0),   # Dark orange for trade master
            # Additional NPCs
            "mayor": (128, 0, 128),  # Purple for authority
            "noble": (255, 215, 0),  # Gold for wealth
            "banker": (0, 100, 0),  # Dark green for money
            "librarian": (139, 69, 19),  # Brown for books
            "guild_master": (70, 130, 180),  # Steel blue for leadership
            "barkeeper": (160, 82, 45),  # Saddle brown
            "craftsman": (139, 69, 19),  # Brown for crafting
            "master_woodcutter": (34, 139, 34),  # Forest green
            "miller": (210, 180, 140),  # Tan for grain
            "boat_builder": (0, 100, 150),  # Navy blue
            "swamp_witch": (85, 107, 47),  # Dark olive green
            "fur_trader": (160, 82, 45),  # Saddle brown
            "ice_keeper": (173, 216, 230),  # Light blue
            "water_keeper": (30, 144, 255),  # Dodger blue
            "mushroom_farmer": (160, 82, 45),  # Saddle brown
            "assayer": (105, 105, 105),  # Gray for minerals
            # New Enemies
            "bandit_scout": (101, 67, 33),  # Brown
            "forest_sprite": (50, 205, 50),  # Lime green
            "ancient_guardian": (245, 245, 220),  # Beige
            "orc_warrior": (139, 69, 19),  # Brown
            "ancient_dragon": (128, 0, 128),  # Purple
            "fire_drake": (255, 69, 0),  # Red-orange
            "crystal_elemental": (173, 216, 230),  # Light blue
            "giant_scorpion": (160, 82, 45),  # Saddle brown
            "swamp_troll": (85, 107, 47),  # Dark olive green
            # Ranged Enemies
            "goblin_archer": (0, 120, 0),  # Dark green
            "orc_crossbow": (139, 69, 19),  # Brown
            "skeleton_archer": (245, 245, 220),  # Beige
            "dark_mage": (75, 0, 130),  # Indigo
            "tree": (34, 139, 34),
            "rock": (128, 128, 128),
            # Biome-specific environmental objects
            "cactus_saguaro": (34, 139, 34),  # Green cactus
            "cactus_barrel": (107, 142, 35),  # Olive green cactus
            "desert_rock": (210, 180, 140),  # Tan desert rock
            "snowy_pine": (25, 100, 25),  # Dark green with snow
            "ice_block": (173, 216, 230),  # Light blue ice
            "frozen_rock": (176, 196, 222),  # Light steel blue
            "dead_tree": (101, 67, 33),  # Saddle brown dead tree
            "swamp_log": (85, 107, 47),  # Dark olive green log
            "swamp_mushroom": (160, 82, 45),  # Saddle brown mushroom
            "pine_tree": (34, 139, 34),  # Forest green pine
            "oak_tree": (107, 142, 35),  # Olive green oak
            "fallen_log": (139, 69, 19),  # Saddle brown fallen log
            # Item colors
            "iron_sword": (192, 192, 192),
            "steel_axe": (169, 169, 169),
            "bronze_mace": (205, 127, 50),
            "silver_dagger": (211, 211, 211),
            "war_hammer": (105, 105, 105),
            # New weapons
            "magic_bow": (255, 215, 0),  # Gold bow
            "crystal_staff": (138, 43, 226),  # Purple staff
            "throwing_knife": (192, 192, 192),  # Silver
            "crossbow": (139, 69, 19),  # Brown wood
            # Armor
            "leather_armor": (139, 69, 19),
            "chain_mail": (128, 128, 128),
            "plate_armor": (192, 192, 192),
            "studded_leather": (160, 82, 45),
            "scale_mail": (105, 105, 105),
            # New armor
            "dragon_scale_armor": (0, 100, 0),  # Dark green
            "mage_robes": (75, 0, 130),  # Indigo
            "royal_armor": (255, 215, 0),  # Gold
            # Consumables
            "health_potion": (255, 0, 0),
            "stamina_potion": (0, 0, 255),
            "mana_potion": (0, 191, 255),  # Deep sky blue
            "antidote": (0, 255, 0),  # Green
            "strength_potion": (255, 165, 0),  # Orange
            # Miscellaneous
            "coin": (255, 215, 0),  # Gold for coin
            "gold_ring": (255, 215, 0),  # Gold
            "magic_scroll": (245, 245, 220),  # Beige
            "crystal_gem": (0, 191, 255),  # Crystal blue
            # Chest colors
            "wooden_chest_closed": (139, 69, 19),  # Brown
            "wooden_chest_open": (139, 69, 19),  # Brown
            "iron_chest_closed": (105, 105, 105),  # Dim gray
            "iron_chest_open": (105, 105, 105),  # Dim gray
            "gold_chest_closed": (255, 215, 0),  # Gold
            "gold_chest_open": (255, 215, 0),  # Gold
            "magical_chest_closed": (138, 43, 226),  # Blue violet
            "magical_chest_open": (138, 43, 226),  # Blue violet
            # Furniture colors
            "bed": (139, 69, 19),  # Brown
            "table": (160, 82, 45),  # Saddle brown
            "chair": (210, 180, 140),  # Tan
            "storage_chest": (101, 67, 33),  # Dark brown
            "shelf": (205, 133, 63),  # Peru
            "desk": (139, 69, 19),  # Brown
            "bar": (160, 82, 45),  # Saddle brown
            "kitchen": (255, 255, 255),  # White
            "weapon_rack": (105, 105, 105),  # Dim gray
            "tool_rack": (169, 169, 169),  # Dark gray
            "storage": (101, 67, 33),  # Dark brown
            "fancy_bed": (128, 0, 128),  # Purple
            # Logo colors
            "goose_rpg_logo": (255, 215, 0),  # Gold
            "goose_rpg_icon": (25, 25, 112),  # Dark blue
            "goose_rpg_square_logo": (255, 215, 0)  # Gold
        }
        
        color = colors.get(name, (255, 255, 255))
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(color)
        
        # Add border for visibility
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        
        return surface
    
    def load_sounds(self):
        """Load sound assets using the audio manager"""
        from .audio import AudioManager
        self.audio_manager = AudioManager()
        print("Audio system integrated into AssetLoader")
    
    def load_fonts(self):
        """Load font assets"""
        # Load default fonts
        self.fonts["default"] = pygame.font.Font(None, 24)
        self.fonts["large"] = pygame.font.Font(None, 36)
        self.fonts["title"] = pygame.font.Font(None, 72)
    
    def get_image(self, name):
        """Get an image by name"""
        image = self.images.get(name)
        if name == 'generic_npc':
            print(f"🖼️  AssetLoader.get_image('{name}') -> {image is not None}")
            if image:
                print(f"   📏 Image size: {image.get_size()}")
            else:
                print(f"   ❌ Image not found in self.images")
                print(f"   🔍 Available images: {list(self.images.keys())[:10]}...")  # Show first 10
        return image
    
    def get_sound(self, name):
        """Get a sound by name - now uses audio manager"""
        return getattr(self, 'audio_manager', None)
    
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