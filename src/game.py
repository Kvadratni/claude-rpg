"""
Game class - Main game controller
"""

import pygame
import sys
from .ui.menu import MainMenu, PauseMenu, GameOverMenu
from .level import Level
from .player import Player
from .save_system import SaveSystem
from .core.assets import AssetLoader
from .settings import Settings
from .core.game_log import GameLog

class Game:
    """Main game class that controls the game flow"""
    
    # Game states
    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    STATE_GAME_OVER = 3
    
    def __init__(self):
        """Initialize the game"""
        # Initialize settings first
        self.settings = Settings()
        
        self.width = self.settings.get("window_width")
        self.height = self.settings.get("window_height")
        self.min_width = 800
        self.min_height = 600
        
        flags = pygame.RESIZABLE
        if self.settings.get("fullscreen"):
            flags |= pygame.FULLSCREEN
            
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("Goose RPG")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = Game.STATE_MENU
        
        # Initialize systems
        self.save_system = SaveSystem()
        self.asset_loader = AssetLoader()
        self.game_log = GameLog()
        
        # Initialize AI recipe manager globally
        print("🔧 [Game] Initializing global AI recipe manager...")
        from .recipe_manager import GooseRecipeManager
        self.recipe_manager = GooseRecipeManager("recipes")
        print(f"✅ [Game] Global recipe manager initialized with {len(self.recipe_manager.recipes)} recipes")
        
        # Initialize game components
        self.menu = MainMenu(self)
        self.player = None
        self.current_level = None
        
        # Load resources
        self.load_resources()
        
        # Apply initial settings
        if hasattr(self.asset_loader, 'audio_manager'):
            self.settings.apply_audio_settings(self.asset_loader.audio_manager)
        
        # Welcome message
        self.game_log.add_message("Welcome to Goose RPG!", "system")
    
    def load_resources(self):
        """Load game resources"""
        # This would typically load sprites, sounds, etc.
        pass
    
    def new_game(self):
        """Start a new game"""
        # Create player at the village center (story starting point)
        self.player = Player(100, 102, self.asset_loader, self.game_log)  # Updated to new village center
        
        # Create the first level
        self.current_level = Level("village", self.player, self.asset_loader, self)
        
        # Initialize quest system
        from .quest_system import QuestManager
        self.quest_manager = QuestManager(self.player, self.game_log)
        
        # Start tutorial quest automatically
        self.quest_manager.start_quest("tutorial")
        
        # Switch to playing state
        self.state = Game.STATE_PLAYING
        
        # Log game start with story context
        self.game_log.add_message("Welcome to Eldermoor Village!", "system")
        self.game_log.add_message("The village elder seeks your help...", "story")
    
    def load_game(self, save_name):
        """Load a saved game"""
        game_data = self.save_system.load_game(save_name)
        if game_data:
            # Create player and level from saved data
            self.player = Player.from_save_data(game_data["player"], self.asset_loader, self.game_log)
            self.current_level = Level.from_save_data(game_data["level"], self.player, self.asset_loader, self)
            self.state = Game.STATE_PLAYING
            self.game_log.add_message(f"Game loaded: {save_name}", "system")
            return True
        return False
    
    def save_game(self, save_name):
        """Save the current game"""
        if self.player and self.current_level:
            game_data = {
                "player": self.player.get_save_data(),
                "level": self.current_level.get_save_data()
            }
            return self.save_system.save_game(save_name, game_data)
        return False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.width = max(self.min_width, event.w)
                self.height = max(self.min_height, event.h)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                
                # Update settings
                self.settings.set("window_width", self.width)
                self.settings.set("window_height", self.height)
                self.settings.save_settings()
                
                self.game_log.add_message(f"Window resized to {self.width}x{self.height}", "system")
                
            if self.state == Game.STATE_MENU:
                self.menu.handle_event(event)
            elif self.state == Game.STATE_PLAYING:
                # CRITICAL: Handle AI chat events FIRST with highest priority
                ai_event_handled = False
                if hasattr(self.player, 'current_ai_chat') and self.player.current_ai_chat and self.player.current_ai_chat.is_active:
                    print(f"Game.py handling AI chat event: {event.type}")
                    if event.type == pygame.KEYDOWN:
                        message = self.player.current_ai_chat.handle_input(event)
                        if message:
                            print(f"🔧 Player sent message from game.py: {message}")
                            # Find the NPC that owns this chat and send the message
                            for npc in getattr(self.current_level, 'npcs', []):
                                if hasattr(npc, 'chat_window') and npc.chat_window == self.player.current_ai_chat:
                                    print(f"🔧 Found NPC {npc.name}, sending message to AI from game.py")
                                    npc.chat_window.add_message("Player", message)
                                    # Get AI response
                                    if npc.game_context:
                                        context = npc.game_context.get_context()
                                        ai_response = npc.ai_integration.send_message(message, context)
                                        npc.chat_window.add_message(npc.name, ai_response)
                                        print(f"🔧 AI responded from game.py: {ai_response}")
                                    break
                        ai_event_handled = True  # Mark as handled regardless of whether we got a message
                
                # If AI handled the event, skip other processing
                if ai_event_handled:
                    continue
                
                # Handle inventory events
                if self.player.inventory.show:
                    # Get audio manager
                    audio = getattr(self.asset_loader, 'audio_manager', None)
                    result = self.player.inventory.handle_input(event, audio)
                    if result:
                        action, item = result
                        if action == "use":
                            self.player.use_item(item)
                        elif action == "drop":
                            self.player.remove_item(item)
                            # Add item to level at player position
                            self.current_level.items.append(item)
                            item.x, item.y = self.player.x, self.player.y
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = Game.STATE_PAUSED
                        self.menu = PauseMenu(self)
                        # Pause music when entering pause menu
                        audio = getattr(self.asset_loader, 'audio_manager', None)
                        if audio:
                            audio.pause_music()
                    elif event.key == pygame.K_i:
                        # Get audio manager
                        audio = getattr(self.asset_loader, 'audio_manager', None)
                        
                        # Toggle inventory
                        self.player.inventory.show = not self.player.inventory.show
                        if self.player.inventory.show:
                            if audio:
                                audio.play_ui_sound("inventory_open")
                            self.game_log.add_message("Inventory opened", "system")
                        else:
                            if audio:
                                audio.play_ui_sound("inventory_close")
                            self.game_log.add_message("Inventory closed", "system")
                    elif event.key == pygame.K_f and (event.mod & pygame.KMOD_META) and (event.mod & pygame.KMOD_SHIFT):
                        # Toggle fullscreen with Cmd+Shift+F (Meta is Cmd on Mac)
                        self.toggle_fullscreen()
                else:
                    self.current_level.handle_event(event)
            elif self.state == Game.STATE_PAUSED:
                self.menu.handle_event(event)
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.screen.get_flags() & pygame.FULLSCREEN:
            # Exit fullscreen
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            print("Exited fullscreen")
        else:
            # Enter fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            print("Entered fullscreen")
    
    def apply_settings(self):
        """Apply current settings to the game"""
        # Update window size and fullscreen mode
        new_width = self.settings.get("window_width")
        new_height = self.settings.get("window_height")
        fullscreen = self.settings.get("fullscreen")
        
        # Update stored dimensions
        self.width = new_width
        self.height = new_height
        
        # Apply display settings
        flags = pygame.RESIZABLE
        if fullscreen:
            flags |= pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((0, 0), flags)
        else:
            self.screen = pygame.display.set_mode((new_width, new_height), flags)
        
        # Apply audio settings
        if hasattr(self.asset_loader, 'audio_manager'):
            self.settings.apply_audio_settings(self.asset_loader.audio_manager)
        
        print(f"Settings applied: {new_width}x{new_height}, Fullscreen: {fullscreen}")
    
    def update(self):
        """Update game logic"""
        # Update game log
        self.game_log.update()
        
        if self.state == Game.STATE_MENU:
            self.menu.update()
        elif self.state == Game.STATE_PLAYING:
            self.current_level.update()
            
            # Update quest system
            if hasattr(self, 'quest_manager'):
                # Connect quest manager to player for quest progress tracking
                if not hasattr(self.player, 'game'):
                    self.player.game = self
            
            # Check if player died
            if self.player.health <= 0:
                self.game_over()
        elif self.state == Game.STATE_PAUSED:
            self.menu.update()
        elif self.state == Game.STATE_GAME_OVER:
            self.menu.update()
    
    def game_over(self):
        """Handle player death"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None)
        
        # Play defeat sound
        if audio:
            audio.play_ui_sound("defeat")
        
        # Switch back to menu music for game over screen
        if self.menu and hasattr(self.menu, 'start_menu_music'):
            self.menu.start_menu_music()
        
        self.game_log.add_message("You have been defeated!", "combat")
        self.game_log.add_message("Game Over", "system")
        self.state = Game.STATE_GAME_OVER
        self.menu = GameOverMenu(self)
    
    def render(self):
        """Render the game"""
        self.screen.fill((0, 0, 0))
        
        if self.state == Game.STATE_MENU:
            self.menu.render(self.screen)
        elif self.state == Game.STATE_PLAYING:
            self.current_level.render(self.screen)
            
            # Render player UI overlays
            self.player.render_inventory(self.screen)
            
            # AI chat windows are now rendered in level_renderer.py
            
            # Don't render game log here - it's handled in level UI
        elif self.state == Game.STATE_PAUSED:
            # Render the game in the background
            self.current_level.render(self.screen)
            # Don't render game log here - it's handled in level UI
            # Render pause menu on top
            self.menu.render(self.screen)
        elif self.state == Game.STATE_GAME_OVER:
            # Render the game in the background (darkened)
            self.current_level.render(self.screen)
            # Don't render game log here - it's handled in level UI
            # Dark overlay
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            # Render game over menu
            self.menu.render(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)  # 60 FPS
