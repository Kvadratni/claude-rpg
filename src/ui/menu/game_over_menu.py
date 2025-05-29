"""
Game Over Menu - Displayed when player dies
"""

import pygame
from .base_menu import BaseMenu

class GameOverMenu(BaseMenu):
    """Menu displayed when the game is over"""
    
    def __init__(self, game, parent_menu=None):
        super().__init__(game)
        
        self.parent_menu = parent_menu
        self.menu_items = ["New Game", "Load Game", "Main Menu"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.menu_items)
        self.menu_type = "game_over"
    
    def handle_event(self, event):
        """Handle game over menu events"""
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
        """Handle game over menu item selection"""
        if self.selected_item == 0:  # New Game
            self.start_game_music()
            self.game.new_game()
        elif self.selected_item == 1:  # Load Game
            from .load_menu import LoadMenu
            self.game.menu = LoadMenu(self.game, self)
        elif self.selected_item == 2:  # Main Menu
            self.start_menu_music()
            from .main_menu import MainMenu
            self.game.menu = MainMenu(self.game)
            self.game.state = self.game.STATE_MENU
    
    def render(self, screen):
        """Render the game over menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Render background
        self.render_gradient_background(screen, screen_width, screen_height)
        self.render_background_stars(screen)
        self.render_particles(screen)
        
        # Game over title with dramatic effect
        self.render_game_over_title(screen, screen_width, screen_height)
        
        # Render menu items
        self.render_menu_items(screen, screen_width, screen_height)
        
        # Render instructions
        instruction_text = "Choose an option to continue your journey"
        self.render_instructions(screen, screen_width, screen_height, instruction_text)
    
    def render_game_over_title(self, screen, width, height):
        """Render dramatic game over title"""
        # Main "GAME OVER" text
        game_over_text = "GAME OVER"
        
        # Shadow effect
        shadow_surface = self.title_font.render(game_over_text, True, (100, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(width // 2 + 4, height // 4 + 4))
        screen.blit(shadow_surface, shadow_rect)
        
        # Main text with red color
        game_over_surface = self.title_font.render(game_over_text, True, (255, 100, 100))
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 4))
        screen.blit(game_over_surface, game_over_rect)
        
        # Subtitle
        subtitle_text = "Your adventure has ended... for now"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.colors['menu_normal'])
        subtitle_rect = subtitle_surface.get_rect(center=(width // 2, height // 4 + 60))
        screen.blit(subtitle_surface, subtitle_rect)
    
    def render_menu_items(self, screen, width, height):
        """Render game over menu items"""
        # Clear previous rectangles
        self.menu_rects = []
        
        start_y = height // 2
        
        for i, item in enumerate(self.menu_items):
            y_pos = start_y + i * 70
            
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
