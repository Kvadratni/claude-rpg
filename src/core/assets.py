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
            "grass_tile": "environment/grass_tile.png",
            "stone_tile": "environment/stone_tile.png", 
            "water_tile": "environment/water_tile.png",
            "wall_tile": "buildings/wall_texture.png",
            "wall_texture": "buildings/wall_texture.png",  # Added for wall face rendering
            "wall_texture_window": "buildings/wall_texture_window.png",  # Added for window wall rendering
            "wall_corner_tl": "buildings/wall_texture.png",
            "wall_corner_tr": "buildings/wall_texture.png", 
            "wall_corner_bl": "buildings/wall_texture.png",
            "wall_corner_br": "buildings/wall_texture.png",
            "wall_horizontal": "buildings/wall_texture.png",
            "wall_vertical": "buildings/wall_texture.png",
            "wall_window_horizontal": "buildings/wall_texture_window.png",
            "wall_window_vertical": "buildings/wall_texture_window.png",
            "dirt_tile": "environment/dirt_tile.png",  # Added dirt tile
            "door_tile": "buildings/door.png",  # Fixed: use door.png instead of door_tile.png
            "door_tile_isometric": "buildings/door.png",  # Added for isometric door rendering
            "door": "buildings/door.png",  # Added door texture for front face
            "archway_texture": "buildings/archway_texture_tall.png",  # Updated to use tall archway texture for better wall face fit
            "wall_door": "buildings/wall_door.png",  # Wall texture showing an open door for side/back faces
            "brick_tile": "environment/brick_tile.png",  # Added brick tile for building interiors
            "roof_texture": "buildings/roof_texture.png",  # Added roof texture for building roofs
            "sand_tile": "environment/sand_tile.png",
            "snow_tile": "environment/snow_tile.png",
            "forest_floor_tile": "environment/forest_floor_tile.png",
            "swamp_tile": "environment/swamp_tile.png",
            "player_sprite": "characters/player_sprite.png",
            "goblin_sprite": "characters/goblin_sprite.png",
            "orc_boss_sprite": "characters/orc_boss_sprite.png",
            "npc_shopkeeper": "characters/npc_shopkeeper.png",
            "generic_npc": "characters/generic_npc.png",  # Added generic NPC for background NPCs
            "generic_villager_1": "characters/generic_villager_1.png",  # New background NPCs
            "generic_villager_2": "characters/generic_villager_2.png",
            "generic_worker": "characters/generic_worker.png",
            "generic_servant": "characters/generic_servant.png",
            "generic_farmer": "characters/generic_farmer.png",
            "generic_citizen": "characters/generic_citizen.png",
            "generic_elder": "characters/generic_elder.png",
            "generic_child": "characters/generic_child.png",
            "generic_merchant_helper": "characters/generic_merchant_helper.png",
            "trader": "characters/trader.png",
            "elder_npc": "characters/elder_npc.png",  # Added elder NPC
            "village_guard_sprite": "characters/village_guard_sprite.png",  # Added village guard
            # New NPCs
            "guard_captain": "characters/guard_captain.png",
            "master_smith": "characters/master_smith.png",
            "innkeeper": "characters/innkeeper.png",
            "high_priest": "characters/high_priest.png",
            "mine_foreman": "characters/mine_foreman.png",
            "harbor_master": "characters/harbor_master.png",
            "caravan_master": "characters/caravan_master.png",
            "forest_ranger": "characters/forest_ranger.png",
            "master_herbalist": "characters/master_herbalist.png",
            "mysterious_wizard": "characters/mysterious_wizard.png",
            "old_hermit": "characters/old_hermit.png",
            "stable_master": "characters/stable_master.png",  # Added missing stable master
            "master_fisher": "characters/master_fisher.png",  # Added missing master fisher
            "trade_master": "characters/trade_master.png",    # Added missing trade master
            # Additional NPCs that need new assets
            "mayor": "characters/mayor.png",
            "noble": "characters/noble.png", 
            "banker": "characters/banker.png",
            "librarian": "characters/librarian.png",
            "guild_master": "characters/guild_master.png",
            "barkeeper": "characters/barkeeper.png",
            "craftsman": "characters/craftsman.png",
            "master_woodcutter": "characters/master_woodcutter.png",
            "miller": "characters/miller.png",
            "boat_builder": "characters/boat_builder.png",
            "swamp_witch": "characters/swamp_witch.png",
            "fur_trader": "characters/fur_trader.png",
            "ice_keeper": "characters/ice_keeper.png",
            "water_keeper": "characters/water_keeper.png",
            "mushroom_farmer": "characters/mushroom_farmer.png",
            "assayer": "characters/assayer.png",
            # Forest Enemies
            "forest_sprite": "characters/forest_sprite.png",
            "elder_forest_sprite": "characters/elder_forest_sprite.png",
            "ancient_guardian": "characters/ancient_guardian.png",
            "goblin_chieftain": "characters/goblin_chieftain.png",
            
            # Plains Enemies
            "bandit_scout": "characters/bandit_scout.png",
            "wild_boar": "characters/wild_boar.png",
            "bandit_raider": "characters/bandit_raider.png",
            "orc_scout": "characters/orc_scout.png",
            "orc_warrior": "characters/orc_warrior.png",
            "bandit_captain": "characters/bandit_captain.png",
            "orc_berserker": "characters/orc_berserker.png",
            
            # Desert Enemies
            "desert_scorpion": "characters/desert_scorpion.png",
            "sand_viper": "characters/sand_viper.png",
            "giant_scorpion": "characters/giant_scorpion.png",
            "desert_nomad": "characters/desert_nomad.png",
            "sand_elemental": "characters/sand_elemental.png",
            "desert_warlord": "characters/desert_warlord.png",
            "ancient_scorpion_king": "characters/ancient_scorpion_king.png",
            
            # Snow Enemies
            "ice_wolf": "characters/ice_wolf.png",
            "frost_sprite": "characters/frost_sprite.png",
            "ice_troll": "characters/ice_troll.png",
            "crystal_elemental": "characters/crystal_elemental.png",
            "frost_mage": "characters/frost_mage.png",
            "frost_giant": "characters/frost_giant.png",
            "ice_dragon": "characters/ice_dragon.png",
            
            # Swamp Enemies
            "swamp_rat": "characters/swamp_rat.png",
            "bog_sprite": "characters/bog_sprite.png",
            "swamp_troll": "characters/swamp_troll.png",
            "poison_archer": "characters/poison_archer.png",
            "bog_witch": "characters/bog_witch.png",
            "swamp_lord": "characters/swamp_lord.png",
            "plague_bearer": "characters/plague_bearer.png",
            "swamp_dragon": "characters/swamp_dragon.png",
            
            # Boss Enemies
            "forest_dragon": "characters/forest_dragon.png",
            "desert_lich": "characters/desert_lich.png",
            "swamp_hydra": "characters/swamp_hydra.png",
            "ancient_dragon": "characters/ancient_dragon.png",
            
            # Ranged Enemies (existing and new)
            "goblin_archer": "characters/goblin_archer.png",
            "orc_crossbow": "characters/orc_crossbow.png",
            "skeleton_archer": "characters/skeleton_archer.png",
            "dark_mage": "characters/dark_mage.png",
            "tree": "environment/tree.png",
            "rock": "environment/rock.png",
            # Biome-specific environmental objects
            "cactus_saguaro": "environment/cactus_saguaro.png",
            "cactus_barrel": "environment/cactus_barrel.png",
            "desert_rock": "environment/desert_rock.png",
            "snowy_pine": "environment/snowy_pine.png",
            "ice_block": "environment/ice_block.png",
            "frozen_rock": "environment/frozen_rock.png",
            "dead_tree": "environment/dead_tree.png",
            "swamp_log": "environment/swamp_log.png",
            "swamp_mushroom": "environment/swamp_mushroom.png",
            "pine_tree": "environment/pine_tree.png",
            "oak_tree": "environment/oak_tree.png",
            "fallen_log": "environment/fallen_log.png",
            "menu_background": "ui/menu_background.png",  # Added menu background
            # Individual item sprites
            "iron_sword": "items/iron_sword.png",
            "steel_axe": "items/steel_axe.png",
            "bronze_mace": "items/bronze_mace.png",
            "silver_dagger": "items/silver_dagger.png",
            "war_hammer": "items/war_hammer.png",
            # New weapons
            "magic_bow": "items/magic_bow.png",
            "crystal_staff": "items/crystal_staff.png",
            "throwing_knife": "items/throwing_knife.png",
            "crossbow": "items/crossbow.png",
            # Armor
            "leather_armor": "items/leather_armor.png",
            "chain_mail": "items/chain_mail.png",
            "plate_armor": "items/plate_armor.png",
            "studded_leather": "items/studded_leather.png",
            "scale_mail": "items/scale_mail.png",
            # New armor
            "dragon_scale_armor": "items/dragon_scale_armor.png",
            "mage_robes": "items/mage_robes.png",
            "royal_armor": "items/royal_armor.png",
            # Consumables
            "health_potion": "items/health_potion.png",
            "stamina_potion": "items/stamina_potion.png",
            # New consumables
            "mana_potion": "items/mana_potion.png",
            "antidote": "items/antidote.png",
            "strength_potion": "items/strength_potion.png",
            # Miscellaneous items
            "coin": "items/coin.png",
            "gold_ring": "items/gold_ring.png",
            "magic_scroll": "items/magic_scroll.png",
            "crystal_gem": "items/crystal_gem.png",
            # Chest sprites
            "wooden_chest_closed": "chests/wooden_chest_closed.png",
            "wooden_chest_open": "chests/wooden_chest_open.png",
            "iron_chest_closed": "chests/iron_chest_closed.png",
            "iron_chest_open": "chests/iron_chest_open.png",
            "gold_chest_closed": "chests/gold_chest_closed.png",
            "gold_chest_open": "chests/gold_chest_open.png",
            "magical_chest_closed": "chests/magical_chest_closed.png",
            "magical_chest_open": "chests/magical_chest_open.png",
            # Furniture sprites
            "bed": "furniture/bed.png",
            "table": "furniture/table.png",
            "chair": "furniture/chair.png",
            "storage_chest": "chests/storage_chest.png",
            "shelf": "furniture/shelf.png",
            "desk": "furniture/desk.png",
            "bar": "furniture/bar.png",
            "kitchen": "furniture/kitchen.png",
            "weapon_rack": "furniture/weapon_rack.png",
            "tool_rack": "furniture/tool_rack.png",
            "storage": "furniture/storage.png",
            "fancy_bed": "furniture/fancy_bed.png",
            # Game logos
            "goose_rpg_logo": "ui/goose_rpg_logo.png",
            "goose_rpg_icon": "ui/goose_rpg_icon.png",
            "goose_rpg_icon_bg": "ui/goose_rpg_icon_bg.png",
            "goose_rpg_square_logo": "ui/goose_rpg_square_logo.png"
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
            "generic_villager_1": (139, 69, 19),  # Brown tunic
            "generic_villager_2": (34, 139, 34),  # Green dress
            "generic_worker": (101, 67, 33),  # Brown leather
            "generic_servant": (128, 128, 128),  # Gray uniform
            "generic_farmer": (210, 180, 140),  # Tan with straw hat
            "generic_citizen": (70, 130, 180),  # Blue tunic
            "generic_elder": (160, 160, 160),  # Gray with walking stick
            "generic_child": (255, 192, 203),  # Pink for child
            "generic_merchant_helper": (160, 82, 45),  # Brown leather vest
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
            # Forest Enemies
            "forest_sprite": (50, 205, 50),  # Lime green
            "elder_forest_sprite": (0, 255, 127),  # Spring green
            "ancient_guardian": (245, 245, 220),  # Beige
            "goblin_chieftain": (0, 100, 0),  # Dark green
            
            # Plains Enemies  
            "bandit_scout": (101, 67, 33),  # Brown
            "wild_boar": (139, 69, 19),  # Saddle brown
            "bandit_raider": (160, 82, 45),  # Saddle brown
            "orc_scout": (105, 105, 105),  # Dim gray
            "orc_warrior": (139, 69, 19),  # Brown
            "bandit_captain": (139, 0, 0),  # Dark red
            "orc_berserker": (178, 34, 34),  # Firebrick
            
            # Desert Enemies
            "desert_scorpion": (210, 180, 140),  # Tan
            "sand_viper": (238, 203, 173),  # Peach puff
            "giant_scorpion": (160, 82, 45),  # Saddle brown
            "desert_nomad": (210, 180, 140),  # Tan
            "sand_elemental": (244, 164, 96),  # Sandy brown
            "desert_warlord": (139, 0, 0),  # Dark red
            "ancient_scorpion_king": (128, 0, 0),  # Maroon
            
            # Snow Enemies
            "ice_wolf": (176, 196, 222),  # Light steel blue
            "frost_sprite": (230, 230, 250),  # Lavender
            "ice_troll": (119, 136, 153),  # Light slate gray
            "crystal_elemental": (173, 216, 230),  # Light blue
            "frost_mage": (75, 0, 130),  # Indigo
            "frost_giant": (105, 105, 105),  # Dim gray
            "ice_dragon": (70, 130, 180),  # Steel blue
            
            # Swamp Enemies
            "swamp_rat": (107, 142, 35),  # Olive drab
            "bog_sprite": (85, 107, 47),  # Dark olive green
            "swamp_troll": (85, 107, 47),  # Dark olive green
            "poison_archer": (107, 142, 35),  # Olive drab
            "bog_witch": (75, 0, 130),  # Indigo
            "swamp_lord": (47, 79, 79),  # Dark slate gray
            "plague_bearer": (128, 128, 0),  # Olive
            "swamp_dragon": (107, 142, 35),  # Olive drab
            
            # Boss Enemies
            "forest_dragon": (34, 139, 34),  # Forest green
            "desert_lich": (25, 25, 112),  # Midnight blue
            "swamp_hydra": (85, 107, 47),  # Dark olive green
            "ancient_dragon": (128, 0, 128),  # Purple
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