"""
Pause Menu - In-game pause menu interface
"""

import pygame
import os
from .base_menu import BaseMenu

class PauseMenu(BaseMenu):
    """Pause menu displayed when game is paused"""
    
    def __init__(self, game, parent_menu=None):
        super().__init__(game)
        
        self.parent_menu = parent_menu
        self.menu_items = ["Resume", "Save Game", "Load Game", "Settings", "Main Menu"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
        self.menu_type = "pause"
    
    def handle_event(self, event):
        """Handle pause menu events"""
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
                # Resume game on escape
                self.resume_game()
            elif event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                self.select_item()
    
    def select_item(self):
        """Handle pause menu item selection"""
        if self.selected_item == 0:  # Resume
            self.resume_game()
        elif self.selected_item == 1:  # Save Game
            save_name = f"save_{len(os.listdir('saves')) if os.path.exists('saves') else 0}"
            if self.game.save_game(save_name):
                print(f"Game saved as: {save_name}")
            else:
                print("Failed to save game")
        elif self.selected_item == 2:  # Load Game
            from .load_menu import LoadMenu
            self.game.menu = LoadMenu(self.game, self)
        elif self.selected_item == 3:  # Settings
            from .settings_menu import SettingsMenu
            self.game.menu = SettingsMenu(self.game, self)
        elif self.selected_item == 4:  # Main Menu
            self.start_menu_music()
            from .main_menu import MainMenu
            self.game.menu = MainMenu(self.game)
            self.game.state = self.game.STATE_MENU
    
    def resume_game(self):
        """Resume the game"""
        if self.audio_manager:
            self.audio_manager.resume_music()
        self.game.state = self.game.STATE_PLAYING
    
    def render(self, screen):
        """Render the pause menu with overlay"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill(self.colors['bg_dark'])
        screen.blit(overlay, (0, 0))
        
        # Render particles for atmosphere
        self.render_particles(screen)
        
        # Pause title
        title_text = "PAUSED"
        title_surface = self.title_font.render(title_text, True, self.colors['title_gold'])
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_surface, title_rect)
        
        # Render menu items
        self.render_menu_items(screen, screen_width, screen_height)
        
        # Render instructions
        instruction_text = "Use Mouse to Navigate • Click to Select • Esc to Resume"
        self.render_instructions(screen, screen_width, screen_height, instruction_text)
    
    def render_menu_items(self, screen, width, height):
        """Render pause menu items"""
        # Clear previous rectangles
        self.menu_rects = []
        
        start_y = height // 2 - 50
        
        for i, item in enumerate(self.menu_items):
            y_pos = start_y + i * 60
            
            # Determine colors based on selection and hover
            if i == self.selected_item or i == self.mouse_hover:
                color = self.colors['menu_selected']
                # Hover effect
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
