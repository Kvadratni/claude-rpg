"""
Load Menu - Game loading interface
"""

import pygame
import os
from .base_menu import BaseMenu

class LoadMenu(BaseMenu):
    """Menu for loading saved games"""
    
    def __init__(self, game, parent_menu=None):
        super().__init__(game)
        
        self.parent_menu = parent_menu
        self.menu_type = "load"
        self.selected_item = 0
        
        # Load save files
        self.refresh_save_list()
        self.menu_hover_time = [0] * len(self.load_menu_items)
    
    def refresh_save_list(self):
        """Refresh the list of save files"""
        save_dir = "saves"
        if os.path.exists(save_dir):
            saves = [f[:-5] for f in os.listdir(save_dir) if f.endswith('.json')]
            self.load_menu_items = saves + ["Back"]
        else:
            self.load_menu_items = ["No saves found", "Back"]
        
        if self.selected_item >= len(self.load_menu_items):
            self.selected_item = len(self.load_menu_items) - 1
    
    def handle_event(self, event):
        """Handle load menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.update_mouse_hover(mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.mouse_hover >= 0:
                    self.selected_item = self.mouse_hover
                    self.select_item()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.back_to_parent()
            elif event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.load_menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.load_menu_items)
            elif event.key == pygame.K_RETURN:
                self.select_item()
    
    def select_item(self):
        """Handle load menu item selection"""
        if self.selected_item == len(self.load_menu_items) - 1:  # Back
            self.back_to_parent()
        elif self.load_menu_items[self.selected_item] != "No saves found":
            save_name = self.load_menu_items[self.selected_item]
            if self.game.load_game(save_name):
                self.start_game_music()
                print(f"Loaded game: {save_name}")
            else:
                print(f"Failed to load game: {save_name}")
    
    def back_to_parent(self):
        """Return to parent menu"""
        if self.parent_menu:
            self.game.menu = self.parent_menu
        else:
            from .main_menu import MainMenu
            self.game.menu = MainMenu(self.game)
    
    def render(self, screen):
        """Render the load menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Render background
        if hasattr(self.parent_menu, 'menu_type') and self.parent_menu.menu_type == "pause":
            # Semi-transparent overlay for pause menu
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(180)
            overlay.fill(self.colors['bg_dark'])
            screen.blit(overlay, (0, 0))
        else:
            # Full background for main menu
            self.render_gradient_background(screen, screen_width, screen_height)
            self.render_background_stars(screen)
        
        # Render particles
        self.render_particles(screen)
        
        # Load menu title
        title_text = "LOAD GAME"
        title_surface = self.title_font.render(title_text, True, self.colors['title_gold'])
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_surface, title_rect)
        
        # Render save list
        self.render_save_list(screen, screen_width, screen_height)
        
        # Render instructions
        instruction_text = "Use Mouse to Navigate • Click to Select • Esc to Go Back"
        self.render_instructions(screen, screen_width, screen_height, instruction_text)
    
    def render_save_list(self, screen, width, height):
        """Render the list of save files"""
        # Clear previous rectangles
        self.menu_rects = []
        
        start_y = height // 2 - 50
        
        for i, save_name in enumerate(self.load_menu_items):
            y_pos = start_y + i * 60
            
            # Determine colors based on selection and hover
            if i == self.selected_item or i == self.mouse_hover:
                color = self.colors['menu_selected']
                # Hover effect
                glow_surface = self.menu_font.render(save_name, True, self.colors['accent_blue'])
                glow_rect = glow_surface.get_rect(center=(width // 2 + 2, y_pos + 2))
                glow_surface.set_alpha(100)
                screen.blit(glow_surface, glow_rect)
            else:
                color = self.colors['menu_normal']
            
            # Special styling for "No saves found"
            if save_name == "No saves found":
                color = self.colors['accent_purple']
            
            # Main text
            text_surface = self.menu_font.render(save_name, True, color)
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
