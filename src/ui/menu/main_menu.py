"""
Main Menu - Primary game menu interface
"""

import pygame
import os
from .base_menu import BaseMenu

class MainMenu(BaseMenu):
    """Main menu with New Game, Load Game, Settings, Exit options"""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Main menu items
        self.menu_items = ["New Game", "Load Game", "Settings", "Exit"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
        
        # Current menu type
        self.menu_type = "main"
        
        # Start menu music
        self.start_menu_music()
    
    def handle_event(self, event):
        """Handle main menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.update_mouse_hover(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.mouse_hover >= 0:
                    self.selected_item = self.mouse_hover
                    self.select_item()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                self.select_item()
    
    def select_item(self):
        """Handle main menu item selection"""
        if self.selected_item == 0:  # New Game
            # Switch to procedural world menu for seed selection
            from .procedural_menu import ProceduralWorldMenu
            self.game.menu = ProceduralWorldMenu(self.game)
        elif self.selected_item == 1:  # Load Game
            # Switch to load menu
            from .load_menu import LoadMenu
            self.game.menu = LoadMenu(self.game, self)
        elif self.selected_item == 2:  # Settings
            # Switch to settings menu
            from .settings_menu import SettingsMenu
            self.game.menu = SettingsMenu(self.game, self)
        elif self.selected_item == 3:  # Exit
            self.game.running = False
    
    def render(self, screen):
        """Render the main menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Render background
        self.render_gradient_background(screen, screen_width, screen_height)
        
        # Render background stars and particles
        self.render_background_stars(screen)
        self.render_particles(screen)
        
        # Render main title
        self.render_main_title(screen, screen_width, screen_height)
        
        # Render menu items
        self.render_menu_items(screen, screen_width, screen_height)
        
        # Render instructions
        instruction_text = "Use Mouse to Navigate • Click to Select"
        self.render_instructions(screen, screen_width, screen_height, instruction_text)
    
    def render_main_title(self, screen, width, height):
        """Render the main game title with effects"""
        title_text = "GOOSE RPG"
        
        # Title with pulsing effect
        pulse_scale = 1.0 + self.title_pulse * 0.05
        title_size = int(96 * pulse_scale)
        title_font = pygame.font.Font(None, title_size)
        
        # Shadow effect
        shadow_surface = title_font.render(title_text, True, self.colors['title_shadow'])
        shadow_rect = shadow_surface.get_rect(center=(width // 2 + 3, height // 4 + 3))
        screen.blit(shadow_surface, shadow_rect)
        
        # Main title
        title_surface = title_font.render(title_text, True, self.colors['title_gold'])
        title_rect = title_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "An Epic Adventure Awaits"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.colors['menu_normal'])
        subtitle_rect = subtitle_surface.get_rect(center=(width // 2, height // 4 + 60))
        screen.blit(subtitle_surface, subtitle_rect)
    
    def render_menu_items(self, screen, width, height):
        """Render main menu items with hover effects"""
        # Clear previous rectangles
        self.menu_rects = []
        
        start_y = height // 2
        
        for i, item in enumerate(self.menu_items):
            y_pos = start_y + i * 70
            
            # Determine colors based on selection and hover
            if i == self.selected_item or i == self.mouse_hover:
                color = self.colors['menu_selected']
                # Hover effect - slight glow
                glow_surface = self.menu_font.render(item, True, self.colors['accent_blue'])
                glow_rect = glow_surface.get_rect(center=(width // 2 + 2, y_pos + 2))
                glow_surface.set_alpha(100)
                screen.blit(glow_surface, glow_rect)
            else:
                color = self.colors['menu_normal']
            
            # Main text
            text_surface = self.menu_font.render(item, True, color)
            text_rect = text_surface.get_rect(center=(width // 2, y_pos))
            screen.blit(text_surface, text_rect)
            
            # Store rectangle for mouse collision
            self.menu_rects.append(text_rect)
            
            # Selection indicator
            if i == self.selected_item:
                indicator_x = text_rect.left - 30
                indicator_y = text_rect.centery
                pygame.draw.polygon(screen, self.colors['menu_selected'], [
                    (indicator_x, indicator_y - 8),
                    (indicator_x, indicator_y + 8),
                    (indicator_x + 12, indicator_y)
                ])
