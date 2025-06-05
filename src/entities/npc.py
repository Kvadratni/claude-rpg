"""
NPC entities for the RPG
"""

import pygame
import math
import random
from .base import Entity

class NPC(Entity):
    """Non-player character"""
    
    def __init__(self, x, y, name, dialog=None, shop_items=None, asset_loader=None, has_shop=False):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.shop_items = shop_items or []
        self.dialog_index = 0
        self.asset_loader = asset_loader
        self.has_shop = has_shop
        self.shop = None
        
        # Create shop if this NPC is a shopkeeper
        if self.has_shop:
            from ..ui.shop import Shop
            shop_name = f"{self.name}'s Shop"
            self.shop = Shop(shop_name, asset_loader)
        
        # Create NPC sprite
        self.create_npc_sprite()
    
    def create_npc_sprite(self):
        """Create NPC sprite with support for all new NPC types"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            # Map NPC names to sprite assets - EXPANDED MAPPING
            sprite_mappings = {
                # Existing NPCs with dedicated assets
                "Master Merchant": "npc_shopkeeper",
                "Shopkeeper": "npc_shopkeeper", 
                "Trader": "trader",  # Use dedicated trader asset
                "Rich Merchant": "trade_master",
                "Market Master": "trade_master",
                
                "Village Elder": "elder_npc",
                "Elder": "elder_npc",
                
                "Guard Captain": "guard_captain",
                "Guard": "village_guard_sprite",  # Use the village guard sprite
                "Commander": "guard_captain",  # Reuse guard captain
                "Barracks Chief": "guard_captain",
                
                "Master Smith": "master_smith",
                "Blacksmith": "master_smith",
                "Tool Maker": "master_smith",  # Reuse smith for tool maker
                "Weapon Master": "master_smith",
                
                "Innkeeper": "innkeeper",
                "Inn Master": "innkeeper",
                "Lodge Keeper": "innkeeper",  # Reuse innkeeper
                
                "High Priest": "high_priest",
                "Archbishop": "high_priest",  # Reuse priest
                "Forest Priest": "high_priest",
                
                "Mine Foreman": "mine_foreman",
                "Ore Master": "mine_foreman",  # Reuse mine foreman
                "Veteran Miner": "mine_foreman",
                
                "Harbor Master": "harbor_master",
                "Dock Master": "harbor_master",  # Reuse harbor master
                "Fisherman": "master_fisher",
                "Old Fisherman": "master_fisher",
                "Fish Merchant": "master_fisher",
                "Net Weaver": "master_fisher",
                "Smoke Master": "master_fisher",
                "Sailor": "master_fisher",
                
                "Caravan Master": "caravan_master",
                "Desert Guide": "caravan_master",  # Reuse caravan master
                "Desert Nomad": "caravan_master",
                "Oasis Keeper": "caravan_master",
                
                "Forest Ranger": "forest_ranger",
                "Scout Leader": "forest_ranger",  # Reuse ranger
                "Hunter": "forest_ranger",
                "Tree Keeper": "forest_ranger",
                
                "Master Herbalist": "master_herbalist",
                "Herb Gatherer": "master_herbalist",  # Reuse herbalist
                "Forest Druid": "master_herbalist",
                "Swamp Alchemist": "master_herbalist",
                
                "Mysterious Wizard": "mysterious_wizard",
                "Court Wizard": "mysterious_wizard",  # Reuse wizard
                
                "Old Hermit": "old_hermit",
                "Swamp Dweller": "old_hermit",  # Reuse hermit
                "Villager": "old_hermit",
                
                "Stable Master": "stable_master",
                
                # NPCs that need new assets (will use fallback generation)
                "Mayor": "mayor",  # NEW ASSET NEEDED
                "Noble": "noble",  # NEW ASSET NEEDED
                "Banker": "banker",  # NEW ASSET NEEDED
                "Librarian": "librarian",  # NEW ASSET NEEDED
                "Guild Master": "guild_master",  # NEW ASSET NEEDED
                "Barkeeper": "barkeeper",  # NEW ASSET NEEDED
                "Craftsman": "craftsman",  # NEW ASSET NEEDED
                "Master Woodcutter": "master_woodcutter",  # NEW ASSET NEEDED
                "Miller": "miller",  # NEW ASSET NEEDED
                "Boat Builder": "boat_builder",  # NEW ASSET NEEDED
                "Swamp Witch": "swamp_witch",  # NEW ASSET NEEDED
                "Fur Trader": "fur_trader",  # NEW ASSET NEEDED
                "Ice Keeper": "ice_keeper",  # NEW ASSET NEEDED
                "Water Keeper": "water_keeper",  # NEW ASSET NEEDED
                "Mushroom Farmer": "mushroom_farmer",  # NEW ASSET NEEDED
                "Assayer": "assayer",  # NEW ASSET NEEDED
            }
            
            sprite_name = sprite_mappings.get(self.name)
            if sprite_name:
                npc_image = self.asset_loader.get_image(sprite_name)
                if npc_image:
                    # Create base sprite
                    self.sprite = pygame.transform.scale(npc_image, (size, size))
                    # Create direction sprites - mirror for left movement
                    self.direction_sprites = [
                        self.sprite,  # Down (0)
                        pygame.transform.flip(self.sprite, True, False),  # Left (1) - mirrored
                        self.sprite,  # Up (2)
                        self.sprite   # Right (3) - original (facing right)
                    ]
                    return
        
        # Fallback to generated sprite with unique colors for each NPC type
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors and features for different NPCs
        npc_styles = {
            # Existing NPCs
            "Master Merchant": {"color": (255, 215, 0), "feature": "hat", "feature_color": (139, 69, 19)},  # Gold with brown hat
            "Shopkeeper": {"color": (255, 215, 0), "feature": "hat", "feature_color": (139, 69, 19)},
            "Village Elder": {"color": (128, 0, 128), "feature": "beard", "feature_color": (255, 255, 255)},  # Purple with white beard
            "Elder": {"color": (128, 0, 128), "feature": "beard", "feature_color": (255, 255, 255)},
            "Guard Captain": {"color": (70, 130, 180), "feature": "helmet", "feature_color": (105, 105, 105)},  # Steel blue with gray helmet
            "Guard": {"color": (70, 130, 180), "feature": "helmet", "feature_color": (105, 105, 105)},
            "Master Smith": {"color": (139, 69, 19), "feature": "apron", "feature_color": (101, 67, 33)},  # Brown with dark brown apron
            "Blacksmith": {"color": (139, 69, 19), "feature": "apron", "feature_color": (101, 67, 33)},
            "Innkeeper": {"color": (160, 82, 45), "feature": "apron", "feature_color": (255, 255, 255)},  # Saddle brown with white apron
            "High Priest": {"color": (255, 255, 255), "feature": "hood", "feature_color": (200, 200, 200)},  # White with light gray hood
            "Mine Foreman": {"color": (105, 105, 105), "feature": "helmet", "feature_color": (255, 215, 0)},  # Gray with gold helmet
            "Harbor Master": {"color": (0, 100, 150), "feature": "hat", "feature_color": (0, 50, 100)},  # Navy blue with dark blue hat
            "Caravan Master": {"color": (210, 180, 140), "feature": "turban", "feature_color": (255, 215, 0)},  # Tan with gold turban
            "Forest Ranger": {"color": (34, 139, 34), "feature": "hat", "feature_color": (0, 100, 0)},  # Forest green with dark green hat
            "Master Herbalist": {"color": (50, 205, 50), "feature": "hood", "feature_color": (34, 139, 34)},  # Lime green with forest green hood
            "Mysterious Wizard": {"color": (75, 0, 130), "feature": "hat", "feature_color": (25, 25, 112)},  # Indigo with midnight blue hat
            "Old Hermit": {"color": (160, 160, 160), "feature": "beard", "feature_color": (220, 220, 220)},  # Gray with light gray beard
            
            # New NPCs
            "Desert Guide": {"color": (218, 165, 32), "feature": "turban", "feature_color": (184, 134, 11)},  # Goldenrod with darker turban
            "Head Miner": {"color": (85, 85, 85), "feature": "helmet", "feature_color": (169, 169, 169)},  # Dark gray with light gray helmet
            "Master Fisher": {"color": (0, 139, 139), "feature": "hat", "feature_color": (0, 100, 100)},  # Dark cyan with darker hat
            "Trade Master": {"color": (255, 140, 0), "feature": "hat", "feature_color": (205, 102, 0)},  # Dark orange with darker hat
            "Stable Master": {"color": (160, 82, 45), "feature": "hat", "feature_color": (139, 69, 19)},  # Saddle brown with brown hat
            "Water Keeper": {"color": (30, 144, 255), "feature": "hood", "feature_color": (0, 100, 200)},  # Dodger blue with darker hood
            "Lodge Keeper": {"color": (205, 92, 92), "feature": "apron", "feature_color": (255, 255, 255)}  # Indian red with white apron
        }
        
        # Get style for this NPC, default to generic style
        style = npc_styles.get(self.name, {"color": (0, 191, 255), "feature": "none", "feature_color": (255, 255, 255)})
        
        # Draw NPC base
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, style["color"], center, size // 3)
        pygame.draw.circle(self.sprite, (255, 255, 255), center, size // 4)
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Thicker border
        
        # Add distinguishing features
        feature = style["feature"]
        feature_color = style["feature_color"]
        
        if feature == "hat":
            pygame.draw.rect(self.sprite, feature_color, (size//2 - 12, 3, 24, 12))  # Hat
        elif feature == "beard":
            pygame.draw.circle(self.sprite, feature_color, (size//2, size//2 + 8), 9)  # Beard
        elif feature == "helmet":
            pygame.draw.rect(self.sprite, feature_color, (size//2 - 10, 5, 20, 8))  # Helmet
            pygame.draw.rect(self.sprite, (169, 169, 169), (size//2 - 8, 8, 16, 4))   # Helmet detail
        elif feature == "apron":
            pygame.draw.rect(self.sprite, feature_color, (size//2 - 8, size//2 + 5, 16, 12))  # Apron
        elif feature == "hood":
            pygame.draw.ellipse(self.sprite, feature_color, (size//2 - 14, 2, 28, 20))  # Hood
        elif feature == "turban":
            pygame.draw.ellipse(self.sprite, feature_color, (size//2 - 12, 2, 24, 16))  # Turban
        
        # Create direction sprites for generated sprites - mirror for left movement
        self.direction_sprites = [
            self.sprite,  # Down (0)
            pygame.transform.flip(self.sprite, True, False),  # Left (1) - mirrored
            self.sprite,  # Up (2)
            self.sprite   # Right (3) - original
        ]
    
    def interact(self, player):
        """Interact with the NPC"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play dialog sound
        if audio:
            if "Elder" in self.name:
                audio.play_magic_sound("turn_page")  # Use page turn for elder wisdom
            else:
                audio.play_ui_sound("button_click")  # Generic NPC talk sound
        
        # Handle shop interaction
        if self.has_shop and self.shop:
            self.shop.open_shop()
            if player.game_log:
                player.game_log.add_message(f"{self.name}: Welcome to my shop!", "dialog")
            
            # Update quest progress for talking to shopkeeper
            if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                player.game.quest_manager.update_quest_progress("talk", self.name)
        else:
            # Open dialogue window instead of just logging messages
            if self.dialog:
                from ..ui.dialogue import DialogueWindow
                
                # Create dialogue window with all dialogue lines
                dialogue_window = DialogueWindow(self.name, self.dialog, self.asset_loader)
                
                # Store dialogue window in player or level for rendering
                if hasattr(player, 'current_dialogue'):
                    player.current_dialogue = dialogue_window
                
                # Quest giving logic for Village Elder
                if "Elder" in self.name and hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                    quest_manager = player.game.quest_manager
                    
                    # Check if we should offer the main quest
                    if "main_story" not in quest_manager.active_quests and "main_story" not in quest_manager.completed_quests:
                        # Check if tutorial is completed
                        if "tutorial" in quest_manager.completed_quests:
                            quest_manager.start_quest("main_story")
                            if player.game_log:
                                player.game_log.add_message("New Quest: The Orc Threat", "quest")
                
                # Update quest progress for talking to NPCs
                if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                    player.game.quest_manager.update_quest_progress("talk", self.name)
            
            # Handle shop (legacy)
            if self.shop_items:
                if player.game_log:
                    player.game_log.add_message(f"{self.name} has items for sale!", "dialog")
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "dialog": self.dialog,
            "shop_items": self.shop_items,
            "dialog_index": self.dialog_index,
            "has_shop": self.has_shop
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create NPC from save data"""
        npc = cls(data["x"], data["y"], data["name"], data["dialog"], data["shop_items"], 
                 asset_loader, data.get("has_shop", False))
        npc.dialog_index = data["dialog_index"]
        return npc


