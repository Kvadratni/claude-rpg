"""
Enhanced Menu system for the RPG
"""

import pygame
import os
import math
import random

class MainMenu:
    """Enhanced main menu class with visual effects"""
    
    def __init__(self, game):
        self.game = game
        self.asset_loader = game.asset_loader  # Access to asset loader
        
        # Get audio manager for music control
        self.audio_manager = getattr(self.asset_loader, 'audio_manager', None)
        
        # Load custom fonts if available, fallback to system fonts
        try:
            self.title_font = pygame.font.Font(None, 96)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        except:
            self.title_font = pygame.font.Font(None, 96)
            self.menu_font = pygame.font.Font(None, 48)
            self.subtitle_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
        
        # Load background image
        self.background_image = self.asset_loader.get_image("menu_background")
        if self.background_image:
            print("Menu background loaded successfully!")
        else:
            print("Menu background not found, using procedural background")
        
        self.menu_items = ["New Game", "Load Game", "Settings", "Exit"]
        self.selected_item = 0
        self.menu_type = "main"  # "main", "load", "pause", "game_over", "settings"
        
        # Settings menu
        self.settings_items = ["Resolution", "Music Volume", "SFX Volume", "Fullscreen", "Apply", "Back"]
        self.settings_selected = 0
        self.settings_values = {}  # Store temporary settings values
        self.resolution_index = 0  # Current resolution index
        self.resolution_dropdown_open = False  # Track if resolution dropdown is open
        self.dragging_music_slider = False  # Track if dragging music volume slider
        self.dragging_sfx_slider = False    # Track if dragging SFX volume slider
        
        # Start menu music
        self.start_menu_music()
        
        # Enhanced color palette
        self.colors = {
            'bg_dark': (15, 15, 25),
            'bg_medium': (25, 25, 40),
            'title_gold': (255, 215, 0),
            'title_shadow': (180, 150, 0),
            'menu_normal': (200, 200, 220),
            'menu_hover': (255, 255, 255),
            'menu_selected': (255, 215, 0),
            'accent_blue': (100, 150, 255),
            'accent_purple': (150, 100, 255),
            'particle_color': (255, 255, 150),
            'border_color': (100, 100, 150)
        }
        
        # Animation variables
        self.time = 0
        self.title_pulse = 0
        self.menu_hover_time = [0] * len(self.menu_items)
        
        # Particle system for background
        self.particles = []
        self.init_particles()
        
        # Background elements
        self.background_stars = []
        self.init_background_stars()
        
        # Load menu
        self.load_menu_items = []
        self.load_selected = 0
        self.refresh_save_list()
        
        # Mouse support
        self.mouse_hover = -1
        self.menu_rects = []  # Store actual rendered rectangles for mouse collision
    
    def start_menu_music(self):
        """Start playing menu music"""
        if self.audio_manager:
            # Only start menu music if no music is currently playing or if game music is playing
            current_music = self.audio_manager.get_current_music()
            if current_music != 'menu':
                self.audio_manager.play_music('menu', loop=True, fade_in_ms=1000)
    
    def start_game_music(self):
        """Start playing game music"""
        if self.audio_manager:
            # Only start game music if menu music is playing or no music is playing
            current_music = self.audio_manager.get_current_music()
            if current_music != 'game':
                self.audio_manager.play_music('game', loop=True, fade_in_ms=1000)
    
    def init_particles(self):
        """Initialize floating particles for background effect"""
        for _ in range(50):
            particle = {
                'x': random.randint(0, 1200),
                'y': random.randint(0, 800),
                'speed_x': random.uniform(-0.5, 0.5),
                'speed_y': random.uniform(-1, -0.2),
                'size': random.randint(1, 3),
                'alpha': random.randint(50, 150),
                'pulse_speed': random.uniform(0.01, 0.03)
            }
            self.particles.append(particle)
    
    def init_background_stars(self):
        """Initialize background stars"""
        for _ in range(100):
            star = {
                'x': random.randint(0, 1200),
                'y': random.randint(0, 800),
                'brightness': random.randint(50, 200),
                'twinkle_speed': random.uniform(0.005, 0.02)
            }
            self.background_stars.append(star)
    
    def update_particles(self):
        """Update particle positions and properties"""
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Reset particle if it goes off screen
            if particle['y'] < -10:
                particle['y'] = 810
                particle['x'] = random.randint(0, 1200)
            
            if particle['x'] < -10:
                particle['x'] = 1210
            elif particle['x'] > 1210:
                particle['x'] = -10
            
            # Pulse effect
            particle['alpha'] = int(100 + 50 * math.sin(self.time * particle['pulse_speed']))
    
    def update_background_stars(self):
        """Update background star twinkling"""
        for star in self.background_stars:
            star['brightness'] = int(100 + 100 * math.sin(self.time * star['twinkle_speed']))
    
    def refresh_save_list(self):
        """Refresh the list of save files"""
        save_dir = "saves"
        if os.path.exists(save_dir):
            saves = [f[:-5] for f in os.listdir(save_dir) if f.endswith('.json')]
            self.load_menu_items = saves + ["Back"]
        else:
            self.load_menu_items = ["No saves found", "Back"]
        
        if self.load_selected >= len(self.load_menu_items):
            self.load_selected = len(self.load_menu_items) - 1
    
    def show_pause_menu(self):
        """Show the pause menu"""
        self.menu_type = "pause"
        self.menu_items = ["Resume", "Save Game", "Load Game", "Settings", "Main Menu"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
    
    def show_game_over_menu(self):
        """Show the game over menu"""
        self.menu_type = "game_over"
        self.menu_items = ["New Game", "Load Game", "Main Menu"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
    
    def show_settings_menu(self):
        """Show the settings menu"""
        self.menu_type = "settings"
        self.settings_selected = 0
        self.menu_hover_time = [0] * len(self.settings_items)
        
        # Load current settings into temporary values
        settings = self.game.settings
        self.settings_values = {
            "music_volume": settings.get("music_volume"),
            "sfx_volume": settings.get("sfx_volume"),
            "fullscreen": settings.get("fullscreen")
        }
        
        # Find current resolution index
        current_res = settings.get_current_resolution()
        available_res = settings.get_available_resolutions()
        try:
            self.resolution_index = available_res.index(current_res)
        except ValueError:
            self.resolution_index = 1  # Default to 1024x768
    
    def apply_settings(self):
        """Apply the current settings"""
        settings = self.game.settings
        
        # Apply resolution
        available_res = settings.get_available_resolutions()
        if 0 <= self.resolution_index < len(available_res):
            width, height = available_res[self.resolution_index]
            settings.set_resolution(width, height)
            
            # Update the actual screen
            flags = pygame.RESIZABLE
            if self.settings_values.get("fullscreen", False):
                flags |= pygame.FULLSCREEN
            
            self.game.screen = pygame.display.set_mode((width, height), flags)
            self.game.width = width
            self.game.height = height
        
        # Apply audio settings
        settings.set("music_volume", self.settings_values["music_volume"])
        settings.set("sfx_volume", self.settings_values["sfx_volume"])
        settings.set("fullscreen", self.settings_values["fullscreen"])
        
        # Apply to audio manager
        if self.audio_manager:
            settings.apply_audio_settings(self.audio_manager)
        
        # Save settings
        settings.save_settings()
        print("Settings applied successfully!")
    
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.MOUSEMOTION:
            # Handle mouse hover
            mouse_x, mouse_y = event.pos
            self.update_mouse_hover(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.menu_type == "settings":
                    # Handle special settings interactions first
                    if self.handle_settings_click(event.pos):
                        return  # Handled by settings controls
                
                # Handle normal menu selection
                if self.mouse_hover >= 0:
                    if self.menu_type == "load":
                        self.load_selected = self.mouse_hover
                    elif self.menu_type == "settings":
                        self.settings_selected = self.mouse_hover
                    else:
                        self.selected_item = self.mouse_hover
                    self.select_item()
            elif event.button == 3:  # Right click (for settings adjustments)
                if self.menu_type == "settings" and self.mouse_hover >= 0:
                    self.adjust_setting(self.mouse_hover, -1)  # Decrease value
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if self.menu_type == "settings":
                    self.dragging_music_slider = False
                    self.dragging_sfx_slider = False
        elif event.type == pygame.MOUSEMOTION:
            if self.menu_type == "settings":
                # Handle slider dragging
                if self.dragging_music_slider:
                    self.update_volume_from_mouse(event.pos, "music")
                elif self.dragging_sfx_slider:
                    self.update_volume_from_mouse(event.pos, "sfx")
        elif event.type == pygame.KEYDOWN:
            # Only handle Escape key for going back
            if event.key == pygame.K_ESCAPE:
                if self.menu_type == "load":
                    self.back_to_main()
                elif self.menu_type == "settings":
                    self.back_to_main()
                elif self.menu_type == "pause":
                    self.game.state = self.game.STATE_PLAYING
    
    def update_mouse_hover(self, mouse_x, mouse_y):
        """Update which menu item the mouse is hovering over using stored rectangles"""
        self.mouse_hover = -1
        
        # Check collision with stored menu rectangles
        for i, rect in enumerate(self.menu_rects):
            if rect.collidepoint(mouse_x, mouse_y):
                self.mouse_hover = i
                break
    
    def adjust_setting(self, setting_index, direction):
        """Adjust a setting value (direction: 1 for increase, -1 for decrease)"""
        if setting_index == 0:  # Resolution
            available_res = self.game.settings.get_available_resolutions()
            self.resolution_index = (self.resolution_index + direction) % len(available_res)
        elif setting_index == 1:  # Music Volume
            self.settings_values["music_volume"] = max(0.0, min(1.0, 
                self.settings_values["music_volume"] + direction * 0.1))
        elif setting_index == 2:  # SFX Volume
            self.settings_values["sfx_volume"] = max(0.0, min(1.0, 
                self.settings_values["sfx_volume"] + direction * 0.1))
        elif setting_index == 3:  # Fullscreen
            self.settings_values["fullscreen"] = not self.settings_values["fullscreen"]
    
    def handle_settings_click(self, mouse_pos):
        """Handle clicks on settings UI elements. Returns True if handled."""
        mouse_x, mouse_y = mouse_pos
        
        # Check if clicking on resolution dropdown
        if hasattr(self, '_resolution_dropdown_rect') and self._resolution_dropdown_rect.collidepoint(mouse_x, mouse_y):
            self.resolution_dropdown_open = not self.resolution_dropdown_open
            return True
        
        # Check if clicking on dropdown options when open
        if self.resolution_dropdown_open and hasattr(self, '_resolution_option_rects'):
            for i, rect in enumerate(self._resolution_option_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    self.resolution_index = i
                    self.resolution_dropdown_open = False
                    return True
        
        # Check if clicking on volume sliders
        if hasattr(self, '_music_slider_rect') and self._music_slider_rect.collidepoint(mouse_x, mouse_y):
            self.dragging_music_slider = True
            self.update_volume_from_mouse(mouse_pos, "music")
            return True
        
        if hasattr(self, '_sfx_slider_rect') and self._sfx_slider_rect.collidepoint(mouse_x, mouse_y):
            self.dragging_sfx_slider = True
            self.update_volume_from_mouse(mouse_pos, "sfx")
            return True
        
        # Check if clicking on fullscreen toggle
        if hasattr(self, '_fullscreen_toggle_rect') and self._fullscreen_toggle_rect.collidepoint(mouse_x, mouse_y):
            self.settings_values["fullscreen"] = not self.settings_values["fullscreen"]
            return True
        
        return False
    
    def get_resolution_dropdown_rect(self):
        """Get the rectangle for the resolution dropdown button"""
        if not hasattr(self, '_resolution_dropdown_rect'):
            return None
        return self._resolution_dropdown_rect
    
    def get_resolution_option_rects(self):
        """Get rectangles for resolution dropdown options"""
        if not hasattr(self, '_resolution_option_rects'):
            return []
        return self._resolution_option_rects
    
    def get_music_slider_rect(self):
        """Get the rectangle for the music volume slider"""
        if not hasattr(self, '_music_slider_rect'):
            return None
        return self._music_slider_rect
    
    def get_sfx_slider_rect(self):
        """Get the rectangle for the SFX volume slider"""
        if not hasattr(self, '_sfx_slider_rect'):
            return None
        return self._sfx_slider_rect
    
    def update_volume_from_mouse(self, mouse_pos, volume_type):
        """Update volume based on mouse position on slider"""
        mouse_x, mouse_y = mouse_pos
        
        if volume_type == "music":
            slider_rect = self.get_music_slider_rect()
        else:
            slider_rect = self.get_sfx_slider_rect()
        
        if slider_rect:
            # Calculate volume based on mouse X position within slider
            relative_x = mouse_x - slider_rect.x
            slider_width = slider_rect.width
            volume = max(0.0, min(1.0, relative_x / slider_width))
            
            if volume_type == "music":
                self.settings_values["music_volume"] = volume
            else:
                self.settings_values["sfx_volume"] = volume
    
    def select_item(self):
        """Handle item selection"""
        if self.menu_type == "main":
            if self.selected_item == 0:  # New Game
                self.start_game_music()  # Start game music
                self.game.new_game()
            elif self.selected_item == 1:  # Load Game
                self.menu_type = "load"
                self.refresh_save_list()
            elif self.selected_item == 2:  # Settings
                self.show_settings_menu()
            elif self.selected_item == 3:  # Exit
                self.game.running = False
        
        elif self.menu_type == "load":
            if self.load_selected == len(self.load_menu_items) - 1:  # Back
                self.back_to_main()
            elif self.load_menu_items[self.load_selected] != "No saves found":
                save_name = self.load_menu_items[self.load_selected]
                if self.game.load_game(save_name):
                    self.start_game_music()  # Start game music
                    print(f"Loaded game: {save_name}")
                else:
                    print(f"Failed to load game: {save_name}")
        
        elif self.menu_type == "pause":
            if self.selected_item == 0:  # Resume
                # Resume music when returning to game
                if self.audio_manager:
                    self.audio_manager.resume_music()
                self.game.state = self.game.STATE_PLAYING
            elif self.selected_item == 1:  # Save Game
                save_name = f"save_{len(os.listdir('saves')) if os.path.exists('saves') else 0}"
                if self.game.save_game(save_name):
                    print(f"Game saved as: {save_name}")
                else:
                    print("Failed to save game")
            elif self.selected_item == 2:  # Load Game
                self.menu_type = "load"
                self.refresh_save_list()
            elif self.selected_item == 3:  # Settings
                self.show_settings_menu()
            elif self.selected_item == 4:  # Main Menu
                self.start_menu_music()  # Return to menu music
                self.back_to_main()
                self.game.state = self.game.STATE_MENU
        
        elif self.menu_type == "settings":
            if self.settings_selected == 0:  # Resolution
                self.adjust_setting(0, 1)  # Cycle to next resolution
            elif self.settings_selected == 1:  # Music Volume
                self.adjust_setting(1, 1)  # Increase music volume
            elif self.settings_selected == 2:  # SFX Volume
                self.adjust_setting(2, 1)  # Increase SFX volume
            elif self.settings_selected == 3:  # Fullscreen
                self.adjust_setting(3, 1)  # Toggle fullscreen
            elif self.settings_selected == 4:  # Apply
                self.apply_settings()
            elif self.settings_selected == 5:  # Back
                self.back_to_main()
        
        elif self.menu_type == "game_over":
            if self.selected_item == 0:  # New Game
                self.start_game_music()  # Start game music
                self.game.new_game()
            elif self.selected_item == 1:  # Load Game
                self.menu_type = "load"
                self.refresh_save_list()
            elif self.selected_item == 2:  # Main Menu
                self.start_menu_music()  # Return to menu music
                self.back_to_main()
                self.game.state = self.game.STATE_MENU
    
    def back_to_main(self):
        """Return to main menu"""
        if self.game.state == self.game.STATE_PAUSED:
            self.show_pause_menu()
        else:
            self.menu_type = "main"
            self.menu_items = ["New Game", "Load Game", "Settings", "Exit"]
            self.selected_item = 0
            # Reinitialize hover time array for new menu items
            self.menu_hover_time = [0] * len(self.menu_items)
    
    def update(self):
        """Update menu logic and animations"""
        self.time += 0.016  # Approximate 60 FPS
        self.title_pulse = math.sin(self.time * 2) * 0.1 + 1.0
        
        # Update particle effects
        self.update_particles()
        self.update_background_stars()
        
        # Update hover animations
        for i in range(len(self.menu_items)):
            if i == self.selected_item or i == self.mouse_hover:
                self.menu_hover_time[i] = min(1.0, self.menu_hover_time[i] + 0.05)
            else:
                self.menu_hover_time[i] = max(0.0, self.menu_hover_time[i] - 0.05)
    
    def render(self, screen):
        """Render the enhanced menu with visual effects"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Render background (image or procedural)
        if self.background_image:
            # Scale background image to fit screen
            scaled_bg = pygame.transform.scale(self.background_image, (screen_width, screen_height))
            screen.blit(scaled_bg, (0, 0))
            
            # Add a subtle overlay for better text readability
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
        else:
            # Fallback to procedural background
            self.render_gradient_background(screen, screen_width, screen_height)
            # Render background stars
            self.render_background_stars(screen)
        
        # Always render floating particles for extra atmosphere
        self.render_particles(screen)
        
        if self.menu_type == "pause":
            # Semi-transparent overlay for pause menu
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(180)
            overlay.fill(self.colors['bg_dark'])
            screen.blit(overlay, (0, 0))
        elif self.menu_type == "game_over":
            # Game over title with dramatic effect
            self.render_game_over_title(screen, screen_width, screen_height)
        
        # Render main title for main menu
        if self.menu_type == "main":
            self.render_main_title(screen, screen_width, screen_height)
        
        # Render menu items with enhanced styling
        self.render_menu_items(screen, screen_width, screen_height)
        
        # Render dropdown options on top of everything else (for settings menu)
        if self.menu_type == "settings" and self.resolution_dropdown_open:
            self.render_dropdown_overlay(screen)
        
        # Render instructions with better styling
        self.render_instructions(screen, screen_width, screen_height)
    
    def render_gradient_background(self, screen, width, height):
        """Render a gradient background"""
        for y in range(height):
            # Create a vertical gradient from dark blue to dark purple
            ratio = y / height
            r = int(self.colors['bg_dark'][0] + (self.colors['bg_medium'][0] - self.colors['bg_dark'][0]) * ratio)
            g = int(self.colors['bg_dark'][1] + (self.colors['bg_medium'][1] - self.colors['bg_dark'][1]) * ratio)
            b = int(self.colors['bg_dark'][2] + (self.colors['bg_medium'][2] - self.colors['bg_dark'][2]) * ratio)
            
            # Add some color variation
            r += int(10 * math.sin(self.time * 0.5 + y * 0.01))
            b += int(15 * math.sin(self.time * 0.3 + y * 0.008))
            
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            pygame.draw.line(screen, (r, g, b), (0, y), (width, y))
    
    def render_background_stars(self, screen):
        """Render twinkling background stars"""
        for star in self.background_stars:
            if star['x'] < screen.get_width() and star['y'] < screen.get_height():
                brightness = max(0, min(255, star['brightness']))
                color = (brightness, brightness, brightness)
                pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), 1)
    
    def render_particles(self, screen):
        """Render floating particles"""
        for particle in self.particles:
            if (0 <= particle['x'] <= screen.get_width() and 
                0 <= particle['y'] <= screen.get_height()):
                alpha = max(0, min(255, particle['alpha']))
                color = (*self.colors['particle_color'], alpha)
                
                # Create a surface for the particle with alpha
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, 
                                 (particle['size'], particle['size']), particle['size'])
                screen.blit(particle_surface, (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def render_main_title(self, screen, width, height):
        """Render the main game title with effects"""
        # Main title with shadow and glow effect
        title_text = "GOOSE RPG"
        
        # Calculate title size with pulse effect
        pulse_scale = self.title_pulse
        title_size = int(96 * pulse_scale)
        title_font = pygame.font.Font(None, title_size)
        
        # Render title shadow (multiple layers for glow effect)
        for offset in range(5, 0, -1):
            shadow_alpha = 100 - (offset * 15)
            shadow_surface = title_font.render(title_text, True, (*self.colors['title_shadow'], shadow_alpha))
            shadow_rect = shadow_surface.get_rect(center=(width // 2 + offset, height // 4 + offset))
            
            # Create alpha surface
            alpha_surface = pygame.Surface(shadow_surface.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((*self.colors['title_shadow'], shadow_alpha))
            alpha_surface.blit(shadow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(alpha_surface, shadow_rect)
        
        # Main title
        title_surface = title_font.render(title_text, True, self.colors['title_gold'])
        title_rect = title_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "An Epic Adventure Awaits"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.colors['menu_normal'])
        subtitle_rect = subtitle_surface.get_rect(center=(width // 2, height // 4 + 60))
        screen.blit(subtitle_surface, subtitle_rect)
    
    def render_game_over_title(self, screen, width, height):
        """Render dramatic game over title"""
        game_over_text = "GAME OVER"
        
        # Pulsing red effect
        pulse = math.sin(self.time * 4) * 0.3 + 0.7
        red_intensity = int(255 * pulse)
        game_over_color = (red_intensity, 50, 50)
        
        # Shadow effect
        shadow_surface = self.title_font.render(game_over_text, True, (100, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(width // 2 + 3, height // 4 + 3))
        screen.blit(shadow_surface, shadow_rect)
        
        # Main text
        game_over_surface = self.title_font.render(game_over_text, True, game_over_color)
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(game_over_surface, game_over_rect)
    
    def render_menu_items(self, screen, width, height):
        """Render menu items with enhanced styling"""
        if self.menu_type == "load":
            items = self.load_menu_items
            selected = self.load_selected
        elif self.menu_type == "settings":
            # Special rendering for settings menu
            self.render_settings_menu(screen, width, height)
            return
        else:
            items = self.menu_items
            selected = self.selected_item
        
        # Clear previous rectangles
        self.menu_rects = []
        
        start_y = height // 2 if self.menu_type == "main" else height // 2 - 50
        if self.menu_type == "game_over":
            start_y = height // 2
        
        for i, item in enumerate(items):
            y_pos = start_y + i * 70
            
            display_text = item
            
            # Determine colors and effects based on hover state only (no keyboard selection visuals)
            is_hovered = (i == self.mouse_hover)
            hover_amount = self.menu_hover_time[i] if i < len(self.menu_hover_time) else 0
            
            # Store the text rectangle with some padding for mouse interaction (calculate first)
            temp_text_surface = self.menu_font.render(display_text, True, self.colors['menu_normal'])
            text_rect = temp_text_surface.get_rect(center=(width // 2, y_pos))
            padded_rect = text_rect.inflate(40, 20)  # Add padding around text
            self.menu_rects.append(padded_rect)
            
            # Determine text color based on hover state only
            if is_hovered:
                text_color = (0, 0, 0)  # Black for hovered items
            else:
                text_color = self.colors['menu_normal']
            
            if is_hovered:
                # Animated selection background
                bg_width = 300 + int(20 * hover_amount)
                bg_height = 50 + int(10 * hover_amount)
                bg_rect = pygame.Rect(width // 2 - bg_width // 2, y_pos - bg_height // 2, bg_width, bg_height)
                
                # Gradient background for selected item
                bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                for y in range(bg_height):
                    alpha = int(100 + 50 * hover_amount - (y / bg_height) * 50)
                    color = (*self.colors['accent_blue'], alpha)
                    pygame.draw.line(bg_surface, color, (0, y), (bg_width, y))
                
                screen.blit(bg_surface, bg_rect)
                
                # Border effect
                border_color = (*self.colors['menu_selected'], int(200 * hover_amount))
                pygame.draw.rect(screen, border_color, bg_rect, 2)
            
            # Render the text with the correct color
            text_surface = self.menu_font.render(display_text, True, text_color)
            screen.blit(text_surface, text_rect)
    
    def render_settings_menu(self, screen, width, height):
        """Render the settings menu with sliders and dropdown"""
        # Clear and initialize rectangles list
        self.menu_rects = [None] * len(self.settings_items)
        
        start_y = height // 2 - 150
        item_spacing = 80
        
        for i, item in enumerate(self.settings_items):
            y_pos = start_y + i * item_spacing
            
            # Determine if this item is hovered
            is_hovered = (i == self.mouse_hover)
            hover_amount = self.menu_hover_time[i] if i < len(self.menu_hover_time) else 0
            
            # Render label (except for Apply/Back buttons which render their own text)
            if i < 4:  # Only render labels for Resolution, Music Volume, SFX Volume, Fullscreen
                label_color = self.colors['menu_selected'] if is_hovered else self.colors['menu_normal']
                label_surface = self.menu_font.render(item, True, label_color)
                label_rect = label_surface.get_rect()
                label_rect.x = width // 2 - 200
                label_rect.centery = y_pos
                screen.blit(label_surface, label_rect)
            
            # Render control based on item type
            if i == 0:  # Resolution dropdown
                self.render_resolution_dropdown(screen, width // 2 + 50, y_pos, is_hovered)
            elif i == 1:  # Music Volume slider
                self.render_volume_slider(screen, width // 2 + 50, y_pos, "music", is_hovered)
            elif i == 2:  # SFX Volume slider
                self.render_volume_slider(screen, width // 2 + 50, y_pos, "sfx", is_hovered)
            elif i == 3:  # Fullscreen toggle
                self.render_fullscreen_toggle(screen, width // 2 + 50, y_pos, is_hovered)
            elif i == 4 or i == 5:  # Apply/Back buttons
                # Store button rect for clicking
                button_rect = pygame.Rect(width // 2 - 100, y_pos - 25, 200, 50)
                self.menu_rects[i] = button_rect
                
                if is_hovered:
                    # Button background
                    pygame.draw.rect(screen, self.colors['accent_blue'], button_rect)
                    pygame.draw.rect(screen, self.colors['menu_selected'], button_rect, 2)
                    text_color = (255, 255, 255)
                else:
                    pygame.draw.rect(screen, (60, 60, 60), button_rect)
                    pygame.draw.rect(screen, self.colors['border_color'], button_rect, 2)
                    text_color = self.colors['menu_normal']
                
                # Render button text
                button_text = self.menu_font.render(item, True, text_color)
                text_rect = button_text.get_rect(center=button_rect.center)
                screen.blit(button_text, text_rect)
            else:
                # Store a default rect for other items
                default_rect = pygame.Rect(width // 2 - 100, y_pos - 25, 200, 50)
                self.menu_rects[i] = default_rect
    
    def render_resolution_dropdown(self, screen, x, y, is_hovered):
        """Render resolution dropdown"""
        available_res = self.game.settings.get_available_resolutions()
        current_res = available_res[self.resolution_index] if 0 <= self.resolution_index < len(available_res) else (1024, 768)
        
        # Dropdown button
        dropdown_width = 200
        dropdown_height = 40
        dropdown_rect = pygame.Rect(x, y - dropdown_height // 2, dropdown_width, dropdown_height)
        self._resolution_dropdown_rect = dropdown_rect  # Store for click detection
        
        # Button background
        button_color = self.colors['accent_blue'] if is_hovered else (60, 60, 60)
        pygame.draw.rect(screen, button_color, dropdown_rect)
        pygame.draw.rect(screen, self.colors['border_color'], dropdown_rect, 2)
        
        # Current resolution text
        res_text = f"{current_res[0]}x{current_res[1]}"
        text_surface = self.subtitle_font.render(res_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=dropdown_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Dropdown arrow
        arrow_points = [
            (x + dropdown_width - 20, y - 5),
            (x + dropdown_width - 10, y + 5),
            (x + dropdown_width - 30, y + 5)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points)
        
        # Store dropdown rect for menu system (this is what gets clicked)
        self.menu_rects[0] = dropdown_rect  # Replace the first rect with the actual dropdown rect
    
    def render_volume_slider(self, screen, x, y, volume_type, is_hovered):
        """Render volume slider"""
        slider_width = 200
        slider_height = 20
        slider_rect = pygame.Rect(x, y - slider_height // 2, slider_width, slider_height)
        
        # Store slider rect for interaction
        if volume_type == "music":
            self._music_slider_rect = slider_rect
            slider_index = 1  # Music is index 1
        else:
            self._sfx_slider_rect = slider_rect
            slider_index = 2  # SFX is index 2
        
        # Slider background
        pygame.draw.rect(screen, (40, 40, 40), slider_rect)
        pygame.draw.rect(screen, self.colors['border_color'], slider_rect, 2)
        
        # Slider fill
        volume = self.settings_values[f"{volume_type}_volume"]
        fill_width = int(slider_width * volume)
        if fill_width > 0:
            fill_rect = pygame.Rect(x, y - slider_height // 2, fill_width, slider_height)
            color = self.colors['accent_blue'] if is_hovered else (100, 150, 255)
            pygame.draw.rect(screen, color, fill_rect)
        
        # Slider handle
        handle_x = x + fill_width - 5
        handle_rect = pygame.Rect(handle_x, y - 12, 10, 24)
        handle_color = (255, 255, 255) if is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, handle_color, handle_rect)
        pygame.draw.rect(screen, (0, 0, 0), handle_rect, 2)
        
        # Volume percentage text
        volume_text = f"{int(volume * 100)}%"
        text_surface = self.small_font.render(volume_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x = x + slider_width + 10
        text_rect.centery = y
        screen.blit(text_surface, text_rect)
        
        # Store slider rect for menu system (replace the correct index)
        self.menu_rects[slider_index] = slider_rect
    
    def render_fullscreen_toggle(self, screen, x, y, is_hovered):
        """Render fullscreen toggle"""
        toggle_width = 60
        toggle_height = 30
        toggle_rect = pygame.Rect(x, y - toggle_height // 2, toggle_width, toggle_height)
        
        # Toggle background
        is_on = self.settings_values["fullscreen"]
        bg_color = (50, 150, 50) if is_on else (150, 50, 50)
        if is_hovered:
            bg_color = tuple(min(255, c + 30) for c in bg_color)
        
        pygame.draw.rect(screen, bg_color, toggle_rect, border_radius=15)
        pygame.draw.rect(screen, self.colors['border_color'], toggle_rect, 2, border_radius=15)
        
        # Toggle handle
        handle_radius = 12
        handle_x = x + toggle_width - handle_radius - 3 if is_on else x + handle_radius + 3
        handle_center = (handle_x, y)
        pygame.draw.circle(screen, (255, 255, 255), handle_center, handle_radius)
        pygame.draw.circle(screen, (0, 0, 0), handle_center, handle_radius, 2)
        
        # Status text
        status_text = "On" if is_on else "Off"
        text_surface = self.small_font.render(status_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.x = x + toggle_width + 10
        text_rect.centery = y
        screen.blit(text_surface, text_rect)
        
        # Store toggle rect for menu system (replace index 3)
        self.menu_rects[3] = toggle_rect
        self._fullscreen_toggle_rect = toggle_rect  # Also store for click detection
    
    def render_dropdown_overlay(self, screen):
        """Render dropdown options on top of everything else"""
        if not hasattr(self, '_resolution_dropdown_rect'):
            return
            
        dropdown_rect = self._resolution_dropdown_rect
        available_res = self.game.settings.get_available_resolutions()
        
        # Render dropdown options
        self._resolution_option_rects = []
        dropdown_width = dropdown_rect.width
        
        for i, res in enumerate(available_res):
            option_y = dropdown_rect.bottom + i * 35
            option_rect = pygame.Rect(dropdown_rect.x, option_y, dropdown_width, 30)
            self._resolution_option_rects.append(option_rect)
            
            # Option background with shadow
            shadow_rect = pygame.Rect(option_rect.x + 2, option_rect.y + 2, option_rect.width, option_rect.height)
            pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect)
            
            # Option background
            if i == self.resolution_index:
                pygame.draw.rect(screen, self.colors['menu_selected'], option_rect)
            else:
                pygame.draw.rect(screen, (40, 40, 40), option_rect)
            pygame.draw.rect(screen, self.colors['border_color'], option_rect, 1)
            
            # Option text
            option_text = f"{res[0]}x{res[1]}"
            option_surface = self.small_font.render(option_text, True, (255, 255, 255))
            option_text_rect = option_surface.get_rect(center=option_rect.center)
            screen.blit(option_surface, option_text_rect)
    
    def get_settings_display_text(self, index, item):
        """Get display text for settings items with current values"""
        if index == 0:  # Resolution
            available_res = self.game.settings.get_available_resolutions()
            if 0 <= self.resolution_index < len(available_res):
                width, height = available_res[self.resolution_index]
                return f"Resolution: {width}x{height}"
            return "Resolution: Unknown"
        elif index == 1:  # Music Volume
            volume = int(self.settings_values["music_volume"] * 100)
            return f"Music Volume: {volume}%"
        elif index == 2:  # SFX Volume
            volume = int(self.settings_values["sfx_volume"] * 100)
            return f"SFX Volume: {volume}%"
        elif index == 3:  # Fullscreen
            status = "On" if self.settings_values["fullscreen"] else "Off"
            return f"Fullscreen: {status}"
        else:
            return item  # Apply, Back
    
    def render_instructions(self, screen, width, height):
        """Render instructions with better styling"""
        if self.menu_type == "main":
            instruction_text = "Use Mouse to Navigate • Click to Select"
        elif self.menu_type == "settings":
            instruction_text = "Left Click: Increase/Toggle • Right Click: Decrease • Esc to Go Back"
        elif self.menu_type == "game_over":
            instruction_text = "Choose an option to continue your journey"
        else:
            instruction_text = "Use Mouse to Navigate • Click to Select • Esc to Go Back"
        
        # Background for instructions
        instruction_surface = self.small_font.render(instruction_text, True, self.colors['menu_normal'])
        instruction_rect = instruction_surface.get_rect(center=(width // 2, height - 40))
        
        # Semi-transparent background
        bg_rect = instruction_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((*self.colors['bg_dark'], 150))
        screen.blit(bg_surface, bg_rect)
        
        screen.blit(instruction_surface, instruction_rect)