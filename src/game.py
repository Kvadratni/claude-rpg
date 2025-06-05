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

# Try to import MCP server, but don't fail if dependencies are missing
try:
    from .mcp_sse_server import MCPSSEServer as GameMCPServer
    MCP_AVAILABLE = True
except ImportError:
    GameMCPServer = None
    MCP_AVAILABLE = False

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
        self.asset_loader = AssetLoader(self.settings)  # Pass settings to asset loader
        self.game_log = GameLog()
        
        # Initialize MCP server
        self.mcp_server = None
        self.start_mcp_server()
        
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
    
    def new_game(self, seed=None):
        """Start a new game with procedural generation"""
        # Always use procedural generation
        level_name = f"Procedural World"
        if seed:
            level_name += f" (Seed: {seed})"
        
        # Create level first to get optimal spawn location
        self.current_level = Level(
            level_name, 
            None,  # Player will be created after we know spawn location
            self.asset_loader, 
            self,
            seed=seed
        )
        
        # Get optimal player spawn location from procedural generation
        if hasattr(self.current_level, 'procedural_info') and 'player_spawn' in self.current_level.procedural_info:
            start_x, start_y = self.current_level.procedural_info['player_spawn']
        else:
            start_x, start_y = 100, 100  # Fallback
        
        # Create player at optimal location
        self.player = Player(start_x, start_y, self.asset_loader, self.game_log)
        self.current_level.player = self.player
        
        # Initialize quest system with level reference
        from .quest_system import QuestManager
        self.quest_manager = QuestManager(self.player, self.game_log, self.current_level)
        
        # Initialize quest log UI
        from .ui.quest_log import QuestLog
        self.quest_log = QuestLog(self.asset_loader)
        self.quest_log.set_quest_manager(self.quest_manager)
        
        # Switch to playing state
        self.state = Game.STATE_PLAYING
        
        # Log game start
        self.game_log.add_message("Welcome to your procedurally generated world!", "system")
        self.game_log.add_message("Explore and discover what awaits you...", "exploration")
        if seed:
            self.game_log.add_message(f"World seed: {seed}", "system")
        self.game_log.add_message(f"You find yourself near a settlement...", "story")
    
    def load_game(self, save_name):
        """Load a saved game with procedural world support"""
        game_data = self.save_system.load_game(save_name)
        if game_data:
            # Create player from saved data
            self.player = Player.from_save_data(game_data["player"], self.asset_loader, self.game_log)
            
            # Check if this is a procedural world
            level_data = game_data["level"]
            procedural_info = level_data.get("procedural_info", {})
            
            if procedural_info.get("is_procedural", False):
                # Regenerate procedural world from seed
                seed = procedural_info.get("seed")
                level_name = f"Procedural World (Seed: {seed})"
                
                print(f"Loading procedural world with seed: {seed}")
                self.current_level = Level(
                    level_name,
                    self.player, 
                    self.asset_loader, 
                    self,
                    seed=seed
                )
                
                self.game_log.add_message(f"Procedural world regenerated from seed: {seed}", "system")
            else:
                # Convert old template saves to procedural worlds
                print("Converting old save to procedural world...")
                self.current_level = Level(
                    "Procedural World (Converted)",
                    self.player, 
                    self.asset_loader, 
                    self,
                    seed=None  # Random seed for converted worlds
                )
                self.game_log.add_message("Old save converted to procedural world", "system")
            
            # Initialize quest system with level reference
            from .quest_system import QuestManager
            self.quest_manager = QuestManager(self.player, self.game_log, self.current_level)
            
            # Initialize quest log UI
            from .ui.quest_log import QuestLog
            self.quest_log = QuestLog(self.asset_loader)
            self.quest_log.set_quest_manager(self.quest_manager)
            
            # Load quest data if available
            if "quests" in game_data:
                self.quest_manager.load_save_data(game_data["quests"])
            
            self.state = Game.STATE_PLAYING
            return True
        return False
    
    def save_game(self, save_name):
        """Save the current game with procedural world support"""
        if self.player and self.current_level:
            game_data = {
                "player": self.player.get_save_data(),
                "level": self.current_level.get_save_data()
            }
            
            # Save quest data if available
            if hasattr(self, 'quest_manager'):
                game_data["quests"] = self.quest_manager.get_save_data()
            
            # Add procedural info if this is a procedural world
            if hasattr(self.current_level, 'is_procedural_level') and self.current_level.is_procedural_level():
                procedural_data = self.current_level.get_procedural_save_data()
                game_data["level"].update(procedural_data)
                
                seed = self.current_level.get_procedural_seed()
                self.game_log.add_message(f"Procedural world saved (Seed: {seed})", "system")
            else:
                self.game_log.add_message(f"Game saved: {save_name}", "system")
            
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
                    ai_event_handled = self.player.current_ai_chat.handle_input(event)
                
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
                    elif event.key == pygame.K_q:
                        # Toggle quest log
                        if hasattr(self, 'quest_log'):
                            self.quest_log.toggle()
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
                    elif event.key == pygame.K_d and (event.mod & pygame.KMOD_META):
                        # Debug info with Cmd+D
                        self.show_debug_info()
                    elif event.key == pygame.K_F5:
                        # Toggle movement mode with F5
                        if self.player and hasattr(self.player, 'movement_system'):
                            # Get audio manager
                            audio = getattr(self.asset_loader, 'audio_manager', None)
                            if audio:
                                audio.play_ui_sound("click")
                            
                            # Toggle movement mode
                            new_mode = self.player.movement_system.toggle_movement_mode()
                            mode_name = "WASD" if new_mode == "wasd" else "Mouse Click"
                            self.game_log.add_message(f"Movement mode switched to: {mode_name}", "system")
                            
                            # Show helpful message
                            if new_mode == "wasd":
                                self.game_log.add_message("Use WASD keys to move around", "system")
                            else:
                                self.game_log.add_message("Click to move and interact", "system")
                    elif event.key == pygame.K_F6:
                        # DEBUG: Refresh current chunk with F6
                        if (self.player and self.current_level and 
                            hasattr(self.current_level, 'chunk_manager')):
                            self.refresh_current_chunk()
                        else:
                            self.game_log.add_message("Chunk refresh only works in procedural worlds", "system")
                else:
                    # Handle quest log input first
                    if hasattr(self, 'quest_log') and self.quest_log.handle_input(event):
                        continue  # Quest log consumed the event
                    
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
    
    def show_debug_info(self):
        """Show debug information about the current game state"""
        if self.current_level and self.player:
            print("\n=== DEBUG INFO ===")
            print(f"Player position: ({self.player.x:.1f}, {self.player.y:.1f})")
            
            if hasattr(self.current_level, 'is_procedural_level') and self.current_level.is_procedural_level():
                seed = self.current_level.get_procedural_seed()
                print(f"Procedural world seed: {seed}")
                
                if hasattr(self.current_level, 'chunk_manager'):
                    chunk_x, chunk_y = self.current_level.chunk_manager.world_to_chunk_coords(self.player.x, self.player.y)
                    print(f"Player chunk: ({chunk_x}, {chunk_y})")
                    
                    # Get current chunk and check for entities
                    chunk = self.current_level.chunk_manager.get_chunk(chunk_x, chunk_y)
                    if chunk:
                        print(f"Current chunk has {len(chunk.entities)} entities")
                        for entity_data in chunk.entities:
                            print(f"  - {entity_data['type']}: {entity_data.get('name', 'Unknown')} at ({entity_data['x']}, {entity_data['y']})")
            
            print(f"Loaded entities:")
            print(f"  NPCs: {len(self.current_level.npcs)}")
            for npc in self.current_level.npcs:
                print(f"    - {npc.name} at ({npc.x:.1f}, {npc.y:.1f})")
            print(f"  Enemies: {len(self.current_level.enemies)}")
            print(f"  Objects: {len(self.current_level.objects)}")
            print("\n=== DEBUG CONTROLS ===")
            print("F5 - Toggle movement mode (WASD/Click)")
            print("F6 - Refresh current chunk")
            print("Scroll Wheel - Scroll game log")
            print("Cmd+D - Show this debug info")
            print("==================\n")
            
            self.game_log.add_message("Debug info printed to console", "system")
    
    def refresh_current_chunk(self):
        """DEBUG: Force refresh the current chunk to test settlement override and enemy persistence"""
        if not (self.player and self.current_level and hasattr(self.current_level, 'chunk_manager')):
            return
        
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None)
        if audio:
            audio.play_ui_sound("click")
        
        # Get current chunk coordinates
        chunk_manager = self.current_level.chunk_manager
        chunk_x, chunk_y = chunk_manager.world_to_chunk_coords(self.player.x, self.player.y)
        
        self.game_log.add_message(f"🔄 DEBUG: Refreshing chunk ({chunk_x}, {chunk_y})...", "system")
        
        # Store current entity counts for comparison
        old_counts = {
            'npcs': len(self.current_level.npcs),
            'enemies': len(self.current_level.enemies),
            'objects': len(self.current_level.objects)
        }
        
        try:
            # CRITICAL: Save current entity states to chunk before refreshing
            chunk_key = (chunk_x, chunk_y)
            if chunk_key in chunk_manager.loaded_chunks:
                current_chunk = chunk_manager.loaded_chunks[chunk_key]
                
                # Update chunk with current entity states
                self._update_chunk_with_current_entities(current_chunk, chunk_x, chunk_y)
                
                # Save the updated chunk
                current_chunk.save_to_file(chunk_manager.world_dir)
                self.game_log.add_message(f"  💾 Saved current entity states to chunk", "system")
                
                # Remove from memory to force reload
                del chunk_manager.loaded_chunks[chunk_key]
                self.game_log.add_message(f"  🗑️ Unloaded chunk from memory", "system")
            
            # Force reload the chunk (with saved entity states)
            reloaded_chunk = chunk_manager.get_chunk(chunk_x, chunk_y)
            self.game_log.add_message(f"  🔄 Reloaded chunk with {len(reloaded_chunk.entities)} entities", "system")
            
            # Update entities from the reloaded chunk
            self.current_level.update_entities_from_chunks()
            
            # Report new entity counts
            new_counts = {
                'npcs': len(self.current_level.npcs),
                'enemies': len(self.current_level.enemies),
                'objects': len(self.current_level.objects)
            }
            
            # Show comparison
            self.game_log.add_message(f"  📊 Entity changes:", "system")
            for entity_type, old_count in old_counts.items():
                new_count = new_counts[entity_type]
                if new_count != old_count:
                    change = new_count - old_count
                    symbol = "+" if change > 0 else ""
                    self.game_log.add_message(f"    {entity_type.capitalize()}: {old_count} → {new_count} ({symbol}{change})", "system")
                else:
                    self.game_log.add_message(f"    {entity_type.capitalize()}: {old_count} (no change)", "system")
            
            # Check for settlements
            npcs_in_chunk = [e for e in reloaded_chunk.entities if e['type'] == 'npc']
            if npcs_in_chunk:
                self.game_log.add_message(f"  🏘️ Settlement detected with {len(npcs_in_chunk)} NPCs", "system")
                for npc_data in npcs_in_chunk:
                    self.game_log.add_message(f"    - {npc_data['name']} ({npc_data.get('building', 'Unknown Building')})", "system")
            else:
                self.game_log.add_message(f"  🌲 Wilderness chunk (no settlement)", "system")
            
            self.game_log.add_message("✅ Chunk refresh complete!", "system")
            
        except Exception as e:
            self.game_log.add_message(f"❌ Chunk refresh failed: {e}", "system")
            print(f"Chunk refresh error: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_chunk_with_current_entities(self, chunk, chunk_x, chunk_y):
        """Update chunk data with current entity states"""
        # Get chunk bounds
        start_x, start_y, end_x, end_y = chunk.get_world_bounds()
        
        # Clear existing entities in chunk
        chunk.entities.clear()
        
        # Add current NPCs to chunk
        for npc in self.current_level.npcs:
            # Check if NPC is in this chunk
            if start_x <= npc.x < end_x and start_y <= npc.y < end_y:
                local_x = npc.x - start_x
                local_y = npc.y - start_y
                
                npc_data = {
                    'type': 'npc',
                    'name': npc.name,
                    'building': getattr(npc, 'building', 'Unknown Building'),
                    'has_shop': getattr(npc, 'has_shop', False),
                    'x': local_x,
                    'y': local_y,
                    'id': f"npc_{npc.name.lower().replace(' ', '_')}_{chunk_x}_{chunk_y}"
                }
                chunk.add_entity(npc_data)
        
        # Add current LIVING enemies to chunk (dead ones are excluded)
        for enemy in self.current_level.enemies:
            # Check if enemy is in this chunk and alive
            if (start_x <= enemy.x < end_x and start_y <= enemy.y < end_y and 
                enemy.health > 0):
                local_x = enemy.x - start_x
                local_y = enemy.y - start_y
                
                enemy_data = {
                    'type': 'enemy',
                    'name': enemy.name,
                    'x': local_x,
                    'y': local_y,
                    'health': enemy.health,
                    'max_health': enemy.max_health,
                    'damage': enemy.damage,
                    'id': getattr(enemy, 'entity_id', f"{enemy.name}_{int(enemy.x)}_{int(enemy.y)}")
                }
                chunk.add_entity(enemy_data)
        
        # Add current objects to chunk
        for obj in self.current_level.objects:
            # Check if object is in this chunk
            if start_x <= obj.x < end_x and start_y <= obj.y < end_y:
                local_x = obj.x - start_x
                local_y = obj.y - start_y
                
                obj_data = {
                    'type': 'object',
                    'name': obj.name,
                    'x': local_x,
                    'y': local_y,
                    'id': f"{obj.name}_{obj.x}_{obj.y}"
                }
                chunk.add_entity(obj_data)
        
        self.game_log.add_message(f"  🔄 Updated chunk with {len(chunk.entities)} current entities", "system")
    
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
            
            # Render compass in top-right corner
            from .ui.compass import Compass
            if not hasattr(self, 'compass'):
                self.compass = Compass(self.asset_loader)
            self.compass.set_position(self.width, self.height)
            self.compass.render(self.screen)
            
            # Render player UI overlays
            self.player.render_inventory(self.screen)
            
            # Render quest log
            if hasattr(self, 'quest_log'):
                self.quest_log.render(self.screen)
            
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
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(60)  # 60 FPS
        finally:
            # Cleanup on exit
            self.stop_mcp_server()
    
    def start_mcp_server(self):
        """Start the MCP server for AI NPC communication"""
        if not MCP_AVAILABLE:
            self.game_log.add_message("⚠️ MCP Server disabled (missing dependencies)", "system")
            print("MCP Server disabled: FastAPI/uvicorn not installed")
            return
            
        try:
            self.mcp_server = GameMCPServer(self, host="localhost", port=39301)
            self.mcp_server.start_server()
            
            server_info = self.mcp_server.get_server_info()
            if server_info:
                self.game_log.add_message("🌐 MCP Server started for AI NPCs", "system")
                self.game_log.add_message(f"📡 Endpoint: {server_info['sse_endpoint']}", "system")
                print(f"MCP Server started: {server_info['sse_endpoint']}")
            else:
                self.game_log.add_message("⚠️ MCP Server started but info unavailable", "system")
                
        except Exception as e:
            self.game_log.add_message(f"❌ MCP Server failed to start: {e}", "system")
            print(f"MCP Server error: {e}")
    
    def stop_mcp_server(self):
        """Stop the MCP server"""
        if self.mcp_server:
            self.mcp_server.stop_server()
            self.game_log.add_message("🔌 MCP Server stopped", "system")
    
    def get_mcp_server_info(self):
        """Get MCP server connection information"""
        if self.mcp_server:
            return self.mcp_server.get_server_info()
        return None
