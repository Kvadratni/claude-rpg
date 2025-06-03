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
        
        # Initialize quest system
        from .quest_system import QuestManager
        self.quest_manager = QuestManager(self.player, self.game_log)
        
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
                # Handle inventory events first
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
                    # Handle teleport mode keys first
                    if hasattr(self, 'teleport_mode') and self.teleport_mode:
                        if event.key == pygame.K_ESCAPE:
                            # Cancel teleport mode
                            self.teleport_mode = False
                            self.game_log.add_message("🚫 Teleport cancelled", "system")
                        elif event.key == pygame.K_o:
                            # Teleport to origin
                            self.execute_teleport(0, 0)
                        elif event.key >= pygame.K_1 and event.key <= pygame.K_5:
                            # Teleport to settlement shortcut
                            shortcut_key = str(event.key - pygame.K_0)
                            if shortcut_key in self.teleport_shortcuts:
                                target_x, target_y = self.teleport_shortcuts[shortcut_key]
                                self.execute_teleport(target_x, target_y)
                            else:
                                self.game_log.add_message(f"❌ No settlement shortcut {shortcut_key}", "system")
                        return  # Don't process other keys in teleport mode
                    
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
                    elif event.key == pygame.K_F7:
                        # DEBUG: Teleport to coordinates with F7
                        if self.player and self.current_level:
                            self.prompt_teleport()
                        else:
                            self.game_log.add_message("Teleport only works during gameplay", "system")
                    elif event.key == pygame.K_F8:
                        # DEBUG: List all settlements with F8
                        if self.player and self.current_level:
                            self.list_all_settlements()
                        else:
                            self.game_log.add_message("Settlement list only works during gameplay", "system")
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
            print("F7 - Teleport mode (use number keys for settlements)")
            print("F8 - List all settlements")
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
    
    def prompt_teleport(self):
        """DEBUG: Prompt for coordinates and teleport player"""
        try:
            # Get audio manager
            audio = getattr(self.asset_loader, 'audio_manager', None)
            if audio:
                audio.play_ui_sound("click")
            
            # Show current position
            current_x, current_y = self.player.x, self.player.y
            self.game_log.add_message(f"📍 Current position: ({current_x:.1f}, {current_y:.1f})", "system")
            
            # Show teleport options in game log instead of console input
            self.game_log.add_message("🚀 TELEPORT OPTIONS:", "system")
            
            # Show some helpful coordinates
            if hasattr(self.current_level, 'chunk_manager'):
                chunk_x, chunk_y = self.current_level.chunk_manager.world_to_chunk_coords(current_x, current_y)
                self.game_log.add_message(f"Current chunk: ({chunk_x}, {chunk_y})", "system")
                
                # Show nearby settlements with teleport shortcuts
                settlements_found = False
                shortcut_num = 1
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        check_chunk_x, check_chunk_y = chunk_x + dx, chunk_y + dy
                        chunk_key = (check_chunk_x, check_chunk_y)
                        
                        if chunk_key in self.current_level.chunk_manager.loaded_chunks:
                            chunk = self.current_level.chunk_manager.loaded_chunks[chunk_key]
                            npcs_in_chunk = [e for e in chunk.entities if e['type'] == 'npc']
                            if npcs_in_chunk and shortcut_num <= 5:
                                settlements_found = True
                                chunk_center_x = check_chunk_x * 50 + 25
                                chunk_center_y = check_chunk_y * 50 + 25
                                distance = ((chunk_center_x - current_x)**2 + (chunk_center_y - current_y)**2)**0.5
                                self.game_log.add_message(f"{shortcut_num}. Settlement at ({chunk_center_x}, {chunk_center_y}) - {distance:.0f} units", "exploration")
                                shortcut_num += 1
                
                if not settlements_found:
                    self.game_log.add_message("No settlements found nearby", "system")
            
            # Show common teleport destinations
            self.game_log.add_message("📍 Quick destinations:", "system")
            self.game_log.add_message("• World origin: (0, 0)", "system")
            self.game_log.add_message("• Northeast: (200, -200)", "system")
            self.game_log.add_message("• Southeast: (200, 200)", "system")
            self.game_log.add_message("• Southwest: (-200, 200)", "system")
            self.game_log.add_message("• Northwest: (-200, -200)", "system")
            
            self.game_log.add_message("💡 Use number keys 1-5 for quick settlement teleport", "system")
            self.game_log.add_message("💡 Or press O for origin (0,0)", "system")
            
            # Set teleport mode flag for key handling
            if not hasattr(self, 'teleport_mode'):
                self.teleport_mode = False
            self.teleport_mode = True
            self.teleport_shortcuts = {}
            
            # Store settlement shortcuts
            if hasattr(self.current_level, 'chunk_manager'):
                shortcut_num = 1
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        check_chunk_x, check_chunk_y = chunk_x + dx, chunk_y + dy
                        chunk_key = (check_chunk_x, check_chunk_y)
                        
                        if chunk_key in self.current_level.chunk_manager.loaded_chunks and shortcut_num <= 5:
                            chunk = self.current_level.chunk_manager.loaded_chunks[chunk_key]
                            npcs_in_chunk = [e for e in chunk.entities if e['type'] == 'npc']
                            if npcs_in_chunk:
                                chunk_center_x = check_chunk_x * 50 + 25
                                chunk_center_y = check_chunk_y * 50 + 25
                                self.teleport_shortcuts[str(shortcut_num)] = (chunk_center_x, chunk_center_y)
                                shortcut_num += 1
            
            print(f"\n=== TELEPORT MODE ACTIVATED ===")
            print(f"Press number keys 1-5 for settlement shortcuts")
            print(f"Press O for world origin (0,0)")
            print(f"Press ESC to cancel teleport")
            print("================================\n")
            
        except Exception as e:
            self.game_log.add_message(f"❌ Teleport setup failed: {e}", "system")
            print(f"Teleport setup error: {e}")
            import traceback
            traceback.print_exc()
    
    def execute_teleport(self, target_x, target_y):
        """Execute teleport to specified coordinates"""
        try:
            # Get audio manager
            audio = getattr(self.asset_loader, 'audio_manager', None)
            if audio:
                audio.play_ui_sound("menu_confirm")
            
            # Teleport the player
            old_x, old_y = self.player.x, self.player.y
            self.player.x = target_x
            self.player.y = target_y
            
            # Update camera to follow player
            if hasattr(self.current_level, 'camera_x') and hasattr(self.current_level, 'camera_y'):
                # Center camera on player
                screen_width = self.screen.get_width()
                screen_height = self.screen.get_height()
                self.current_level.camera_x = target_x - screen_width // 2
                self.current_level.camera_y = target_y - screen_height // 2
            
            # Generate chunks around new location if needed
            if hasattr(self.current_level, 'chunk_manager'):
                new_chunk_x, new_chunk_y = self.current_level.chunk_manager.world_to_chunk_coords(target_x, target_y)
                
                # Update entities from chunks around new location
                self.current_level.update_entities_from_chunks()
                
                self.game_log.add_message(f"📍 Teleported to ({target_x:.1f}, {target_y:.1f})", "system")
                self.game_log.add_message(f"🗺️ Now in chunk ({new_chunk_x}, {new_chunk_y})", "system")
                
                # Check for settlements at new location
                chunk = self.current_level.chunk_manager.get_chunk(new_chunk_x, new_chunk_y)
                if chunk:
                    npcs_in_chunk = [e for e in chunk.entities if e['type'] == 'npc']
                    if npcs_in_chunk:
                        self.game_log.add_message(f"🏘️ Settlement found with {len(npcs_in_chunk)} NPCs", "system")
                    else:
                        self.game_log.add_message(f"🌲 Wilderness area", "system")
            else:
                self.game_log.add_message(f"📍 Teleported to ({target_x:.1f}, {target_y:.1f})", "system")
            
            # Exit teleport mode
            self.teleport_mode = False
            
            print(f"Teleported from ({old_x:.1f}, {old_y:.1f}) to ({target_x:.1f}, {target_y:.1f})")
            
        except Exception as e:
            self.game_log.add_message(f"❌ Teleport failed: {e}", "system")
            print(f"Teleport error: {e}")
            self.teleport_mode = False
    
    def list_all_settlements(self):
        """DEBUG: List all settlements with their coordinates"""
        try:
            # Get audio manager
            audio = getattr(self.asset_loader, 'audio_manager', None)
            if audio:
                audio.play_ui_sound("click")
            
            self.game_log.add_message("🏘️ Scanning for settlements...", "system")
            
            if not hasattr(self.current_level, 'chunk_manager'):
                self.game_log.add_message("❌ Settlement list only works in procedural worlds", "system")
                return
            
            chunk_manager = self.current_level.chunk_manager
            settlements = []
            
            print(f"\n=== SETTLEMENT LIST ===")
            print(f"Scanning all loaded chunks for settlements...")
            
            # Check all loaded chunks for settlements
            for (chunk_x, chunk_y), chunk in chunk_manager.loaded_chunks.items():
                npcs_in_chunk = [e for e in chunk.entities if e['type'] == 'npc']
                
                if npcs_in_chunk:
                    # Calculate world coordinates for chunk center
                    chunk_center_x = chunk_x * 50 + 25
                    chunk_center_y = chunk_y * 50 + 25
                    
                    # Determine settlement type based on NPCs
                    npc_names = [npc['name'] for npc in npcs_in_chunk]
                    settlement_type = "Village"
                    
                    # Classify settlement based on NPCs
                    if any("Swamp" in name for name in npc_names):
                        settlement_type = "Swamp Village"
                    elif any("Forest" in name or "Druid" in name or "Ranger" in name for name in npc_names):
                        settlement_type = "Forest Camp"
                    elif any("Master" in name or "Captain" in name for name in npc_names):
                        settlement_type = "Town"
                    elif len(npcs_in_chunk) >= 6:
                        settlement_type = "Large Village"
                    elif len(npcs_in_chunk) <= 3:
                        settlement_type = "Small Camp"
                    
                    settlement_info = {
                        'type': settlement_type,
                        'chunk': (chunk_x, chunk_y),
                        'center': (chunk_center_x, chunk_center_y),
                        'npc_count': len(npcs_in_chunk),
                        'npcs': npc_names[:3]  # Show first 3 NPCs
                    }
                    settlements.append(settlement_info)
            
            # Sort settlements by distance from player
            player_x, player_y = self.player.x, self.player.y
            settlements.sort(key=lambda s: ((s['center'][0] - player_x)**2 + (s['center'][1] - player_y)**2)**0.5)
            
            if not settlements:
                self.game_log.add_message("🌲 No settlements found in loaded chunks", "system")
                print("No settlements found in currently loaded chunks.")
                print("Try exploring more areas or use F7 to teleport to distant locations.")
            else:
                self.game_log.add_message(f"📋 Found {len(settlements)} settlements:", "system")
                print(f"\nFound {len(settlements)} settlements:")
                
                for i, settlement in enumerate(settlements, 1):
                    # Calculate distance from player
                    distance = ((settlement['center'][0] - player_x)**2 + (settlement['center'][1] - player_y)**2)**0.5
                    
                    # Format settlement info
                    settlement_line = f"{i}. {settlement['type']} at ({settlement['center'][0]}, {settlement['center'][1]})"
                    detail_line = f"   {settlement['npc_count']} NPCs, {distance:.1f} units away"
                    npc_line = f"   NPCs: {', '.join(settlement['npcs'])}"
                    if settlement['npc_count'] > 3:
                        npc_line += f" (+{settlement['npc_count'] - 3} more)"
                    
                    # Add to game log
                    self.game_log.add_message(settlement_line, "exploration")
                    
                    # Print to console with more detail
                    print(f"\n{settlement_line}")
                    print(detail_line)
                    print(npc_line)
                    print(f"   Chunk: ({settlement['chunk'][0]}, {settlement['chunk'][1]})")
                    print(f"   Teleport command: {settlement['center'][0]},{settlement['center'][1]}")
                
                # Show usage hint
                self.game_log.add_message("💡 Use F7 to teleport to any coordinates", "system")
                print(f"\n=== USAGE ===")
                print(f"• Press F7 and enter coordinates like: 125,-75")
                print(f"• Current position: ({player_x:.1f}, {player_y:.1f})")
                print(f"• Closest settlement: {settlements[0]['type']} at {settlements[0]['center']}")
            
            print("========================\n")
            
        except Exception as e:
            self.game_log.add_message(f"❌ Settlement scan failed: {e}", "system")
            print(f"Settlement scan error: {e}")
            import traceback
            traceback.print_exc()
    
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