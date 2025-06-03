"""
NPC entities for the RPG
"""

import pygame
import math
import random
from .base import Entity

class NPC(Entity):
    """Non-player character with optional AI support"""
    
    def __init__(self, x, y, name, dialog=None, shop_items=None, asset_loader=None, has_shop=False):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.shop_items = shop_items or []
        self.dialog_index = 0
        self.asset_loader = asset_loader
        self.has_shop = has_shop
        self.shop = None
        
        # AI Integration
        self.ai_integration = None
        self.chat_window = None
        self.is_ai_enabled = False
        self.player_ref = None
        self.game_context = None
        
        # Create shop if this NPC is a shopkeeper
        if self.has_shop:
            from ..ui.shop import Shop
            shop_name = f"{self.name}'s Shop"
            self.shop = Shop(shop_name, asset_loader)
        
        # Create NPC sprite
        self.create_npc_sprite()
    
    def enable_ai(self, player_ref, game_context):
        """Enable AI for this NPC"""
        print(f"🔧 [NPC] enable_ai called for {self.name}")
        try:
            from ..ai_integration import EnhancedGooseRecipeIntegration, AIChatWindow
            print(f"🔧 [NPC] Successfully imported AI classes")
            
            # Get global recipe manager from game
            game_recipe_manager = None
            if hasattr(player_ref, 'game') and hasattr(player_ref.game, 'recipe_manager'):
                game_recipe_manager = player_ref.game.recipe_manager
                print(f"🔧 [NPC] Using global recipe manager from game")
            else:
                print(f"⚠️  [NPC] No global recipe manager found, will create new one")
            
            self.ai_integration = EnhancedGooseRecipeIntegration(self.name, game_recipe_manager=game_recipe_manager)
            print(f"🔧 [NPC] Created EnhancedGooseRecipeIntegration for {self.name}")
            
            self.chat_window = AIChatWindow(self.asset_loader)
            print(f"🔧 [NPC] Created AIChatWindow")
            
            self.player_ref = player_ref
            self.game_context = game_context
            self.is_ai_enabled = True
            print(f"✅ [NPC] AI enabled for {self.name}")
        except ImportError as e:
            print(f"❌ [NPC] Failed to enable AI for {self.name}: {e}")
            import traceback
            traceback.print_exc()
            self.is_ai_enabled = False
    
    def start_ai_chat(self):
        """Start AI conversation"""
        print(f"🔧 start_ai_chat called for {self.name}")
        print(f"🔧 is_ai_enabled: {self.is_ai_enabled}")
        print(f"🔧 chat_window exists: {self.chat_window is not None}")
        
        if self.is_ai_enabled and self.chat_window:
            print(f"🔧 Activating chat window for {self.name}")
            self.chat_window.is_active = True
            self.chat_window.add_message("System", f"Started conversation with {self.name}")
            
            # Store the chat window in the player for rendering (like regular dialogue)
            if self.player_ref and hasattr(self.player_ref, 'current_ai_chat'):
                self.player_ref.current_ai_chat = self.chat_window
                print(f"🔧 Stored chat window in player.current_ai_chat")
            
            # Send initial context to AI
            if self.game_context:
                print(f"🔧 Sending initial greeting to AI")
                context = self.game_context.get_context()
                initial_greeting = self.ai_integration.send_message("Hello", context)
                self.chat_window.add_message(self.name, initial_greeting)
                print(f"🔧 AI responded: {initial_greeting}")
            else:
                print(f"⚠️  No game_context available")
        else:
            print(f"⚠️  Cannot start AI chat - is_ai_enabled: {self.is_ai_enabled}, chat_window: {self.chat_window is not None}")
    
    def handle_ai_input(self, event):
        """Handle input for AI chat"""
        if not self.is_ai_enabled or not self.chat_window:
            return False
            
        if self.chat_window.is_active:
            message = self.chat_window.handle_input(event)
            if message:
                # Add player message to chat
                self.chat_window.add_message("Player", message)
                
                # Get AI response
                context = self.game_context.get_context() if self.game_context else ""
                ai_response = self.ai_integration.send_message(message, context)
                self.chat_window.add_message(self.name, ai_response)
            
            return True  # Event was handled
        
        return False
    
    def render_ai_chat(self, screen):
        """Render AI chat window if active"""
        if self.is_ai_enabled and self.chat_window:
            self.chat_window.render(screen)
        elif self.is_ai_enabled:
            print(f"⚠️  AI enabled but no chat_window for {self.name}")
    
    def create_npc_sprite(self):
        """Create NPC sprite with support for all new NPC types"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            # Map NPC names to sprite assets
            sprite_mappings = {
                "Master Merchant": "npc_shopkeeper",
                "Shopkeeper": "npc_shopkeeper", 
                "Village Elder": "elder_npc",
                "Elder": "elder_npc",
                "Guard Captain": "guard_captain",
                "Guard": "village_guard_sprite",
                "Master Smith": "master_smith",
                "Blacksmith": "master_smith",
                "Innkeeper": "innkeeper",
                "High Priest": "high_priest",
                "Mine Foreman": "mine_foreman",
                "Harbor Master": "harbor_master",
                "Caravan Master": "caravan_master",
                "Forest Ranger": "forest_ranger",
                "Master Herbalist": "master_herbalist",
                "Mysterious Wizard": "mysterious_wizard",
                "Old Hermit": "old_hermit"
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
        print(f"🔧 [NPC] interact() called for {self.name}")
        print(f"🔧 [NPC] has ai_ready attribute: {hasattr(self, 'ai_ready')}")
        print(f"🔧 [NPC] ai_ready value: {getattr(self, 'ai_ready', 'NOT SET')}")
        print(f"🔧 [NPC] is_ai_enabled: {self.is_ai_enabled}")
        
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play dialog sound
        if audio:
            if "Elder" in self.name:
                audio.play_magic_sound("turn_page")  # Use page turn for elder wisdom
            else:
                audio.play_ui_sound("button_click")  # Generic NPC talk sound
        
        # Check if this NPC is AI-ready and enable AI on first interaction
        if hasattr(self, 'ai_ready') and self.ai_ready and not self.is_ai_enabled:
            print(f"🔧 [NPC] NPC is AI-ready and not yet enabled, calling enable_ai_on_interaction")
            self.enable_ai_on_interaction(player)
        elif self.is_ai_enabled:
            print(f"🔧 [NPC] AI already enabled for {self.name}")
        else:
            print(f"🔧 [NPC] NPC not AI-ready or already enabled")
        
        # Check if AI is enabled - if so, start AI chat instead of regular dialog
        if self.is_ai_enabled:
            print(f"🔧 [NPC] AI is enabled, starting AI chat")
            self.start_ai_chat()
            return
        else:
            print(f"🔧 [NPC] AI not enabled, using regular dialog")
        
        # Handle shop interaction
        if self.has_shop and self.shop:
            print(f"🔧 [NPC] Opening shop for {self.name}")
            self.shop.open_shop()
            if player.game_log:
                player.game_log.add_message(f"{self.name}: Welcome to my shop!", "dialog")
            
            # Update quest progress for talking to shopkeeper
            if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                player.game.quest_manager.update_quest_progress("talk", self.name)
        else:
            print(f"🔧 [NPC] Opening regular dialog for {self.name}")
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
    

    def enable_ai_on_interaction(self, player):
        """Enable AI when player first interacts with an AI-ready NPC"""
        print(f"🔧 [NPC] enable_ai_on_interaction called for {self.name}")
        print(f"🔧 [NPC] ai_ready: {getattr(self, 'ai_ready', 'NOT SET')}")
        print(f"🔧 [NPC] is_ai_enabled: {self.is_ai_enabled}")
        
        try:
            from ..ai_integration import GameContext
            print(f"🔧 [NPC] Successfully imported GameContext")
            
            # Get the current level from the player's game
            current_level = None
            if hasattr(player, 'game') and hasattr(player.game, 'current_level'):
                current_level = player.game.current_level
                print(f"🔧 [NPC] Got current_level: {type(current_level)}")
            else:
                print(f"⚠️  [NPC] Could not get current_level from player")
            
            # Create game context
            game_context = GameContext(player, current_level)
            print(f"🔧 [NPC] Created GameContext")
            
            # Enable AI for this NPC
            self.enable_ai(player, game_context)
            print(f"🔧 [NPC] Called enable_ai")
            
            if player.game_log:
                player.game_log.add_message(f"🤖 {self.name} is now AI-powered!", "system")
                print(f"🔧 [NPC] Added AI-powered message to game log")
            
        except Exception as e:
            print(f"⚠️  [NPC] Failed to enable AI for {self.name}: {e}")
            import traceback
            traceback.print_exc()
            # Fall back to regular dialog
            self.ai_ready = False

    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "dialog": self.dialog,
            "shop_items": self.shop_items,
            "dialog_index": self.dialog_index,
            "has_shop": self.has_shop,
            "is_ai_enabled": self.is_ai_enabled
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create NPC from save data"""
        npc = cls(data["x"], data["y"], data["name"], data["dialog"], data["shop_items"], 
                 asset_loader, data.get("has_shop", False))
        npc.dialog_index = data["dialog_index"]
        npc.is_ai_enabled = data.get("is_ai_enabled", False)
        return npc
