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
        self.menu_items = ["Resume", "Save Game", "Load Game", "Main Menu"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
    
    def show_game_over_menu(self):
        """Show the game over menu"""
        self.menu_type = "game_over"
        self.menu_items = ["New Game", "Load Game", "Main Menu"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
    
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.MOUSEMOTION:
            # Handle mouse hover
            mouse_x, mouse_y = event.pos
            self.update_mouse_hover(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.mouse_hover >= 0:
                    if self.menu_type == "load":
                        self.load_selected = self.mouse_hover
                    else:
                        self.selected_item = self.mouse_hover
                    self.select_item()
        elif event.type == pygame.KEYDOWN:
            # Only handle Escape key for going back
            if event.key == pygame.K_ESCAPE:
                if self.menu_type == "load":
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
                self.menu_type = "settings"
                # TODO: Implement settings menu
                print("Settings menu not yet implemented")
                self.back_to_main()
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
            elif self.selected_item == 3:  # Main Menu
                self.start_menu_music()  # Return to menu music
                self.back_to_main()
                self.game.state = self.game.STATE_MENU
        
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
        title_text = "CLAUDE RPG"
        
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
            
            # Determine colors and effects based on hover state only (no keyboard selection visuals)
            is_hovered = (i == self.mouse_hover)
            hover_amount = self.menu_hover_time[i] if i < len(self.menu_hover_time) else 0
            
            # Store the text rectangle with some padding for mouse interaction (calculate first)
            temp_text_surface = self.menu_font.render(item, True, self.colors['menu_normal'])
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
            text_surface = self.menu_font.render(item, True, text_color)
            screen.blit(text_surface, text_rect)
    
    def render_instructions(self, screen, width, height):
        """Render instructions with better styling"""
        if self.menu_type == "main":
            instruction_text = "Use Mouse to Navigate • Click to Select"
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