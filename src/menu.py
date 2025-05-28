"""
Menu system for the RPG
"""

import pygame
import os

class MainMenu:
    """Main menu class"""
    
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        
        self.menu_items = ["New Game", "Load Game", "Exit"]
        self.selected_item = 0
        self.menu_type = "main"  # "main", "load", "pause", "game_over"
        
        # Colors
        self.white = (255, 255, 255)
        self.gray = (128, 128, 128)
        self.blue = (100, 150, 255)
        self.dark_blue = (50, 75, 150)
        self.red = (255, 100, 100)
        
        # Load menu
        self.load_menu_items = []
        self.load_selected = 0
        self.refresh_save_list()
        
        # Mouse support
        self.mouse_hover = -1
    
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
    
    def show_game_over_menu(self):
        """Show the game over menu"""
        self.menu_type = "game_over"
        self.menu_items = ["New Game", "Load Game", "Main Menu"]
        self.selected_item = 0
    
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
            if event.key == pygame.K_UP:
                if self.menu_type == "load":
                    self.load_selected = (self.load_selected - 1) % len(self.load_menu_items)
                else:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            
            elif event.key == pygame.K_DOWN:
                if self.menu_type == "load":
                    self.load_selected = (self.load_selected + 1) % len(self.load_menu_items)
                else:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.select_item()
            
            elif event.key == pygame.K_ESCAPE:
                if self.menu_type == "load":
                    self.back_to_main()
                elif self.menu_type == "pause":
                    self.game.state = self.game.STATE_PLAYING
    
    def update_mouse_hover(self, mouse_x, mouse_y):
        """Update which menu item the mouse is hovering over"""
        screen_width = 800  # We'll get this from the screen
        screen_height = 600
        
        if self.menu_type == "load":
            items = self.load_menu_items
            start_y = 150
        else:
            items = self.menu_items
            start_y = 200 if self.menu_type == "main" else 150
        
        self.mouse_hover = -1
        
        for i, item in enumerate(items):
            item_y = start_y + i * 50
            item_rect = pygame.Rect(screen_width // 2 - 100, item_y - 25, 200, 50)
            
            if item_rect.collidepoint(mouse_x, mouse_y):
                self.mouse_hover = i
                break
    
    def select_item(self):
        """Handle item selection"""
        if self.menu_type == "main":
            if self.selected_item == 0:  # New Game
                self.game.new_game()
            elif self.selected_item == 1:  # Load Game
                self.menu_type = "load"
                self.refresh_save_list()
            elif self.selected_item == 2:  # Exit
                self.game.running = False
        
        elif self.menu_type == "load":
            if self.load_selected == len(self.load_menu_items) - 1:  # Back
                self.back_to_main()
            elif self.load_menu_items[self.load_selected] != "No saves found":
                save_name = self.load_menu_items[self.load_selected]
                if self.game.load_game(save_name):
                    print(f"Loaded game: {save_name}")
                else:
                    print(f"Failed to load game: {save_name}")
        
        elif self.menu_type == "pause":
            if self.selected_item == 0:  # Resume
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
                self.back_to_main()
                self.game.state = self.game.STATE_MENU
        
        elif self.menu_type == "game_over":
            if self.selected_item == 0:  # New Game
                self.game.new_game()
            elif self.selected_item == 1:  # Load Game
                self.menu_type = "load"
                self.refresh_save_list()
            elif self.selected_item == 2:  # Main Menu
                self.back_to_main()
                self.game.state = self.game.STATE_MENU
    
    def back_to_main(self):
        """Return to main menu"""
        if self.game.state == self.game.STATE_PAUSED:
            self.show_pause_menu()
        else:
            self.menu_type = "main"
            self.menu_items = ["New Game", "Load Game", "Exit"]
            self.selected_item = 0
    
    def update(self):
        """Update menu logic"""
        pass
    
    def render(self, screen):
        """Render the menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        if self.menu_type == "pause":
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        elif self.menu_type == "game_over":
            # Game over title
            game_over_text = self.title_font.render("GAME OVER", True, self.red)
            game_over_rect = game_over_text.get_rect(center=(screen_width // 2, 100))
            screen.blit(game_over_text, game_over_rect)
        
        # Render title for main menu
        if self.menu_type == "main":
            title_text = self.title_font.render("Claude RPG", True, self.white)
            title_rect = title_text.get_rect(center=(screen_width // 2, 100))
            screen.blit(title_text, title_rect)
        
        # Render menu items
        if self.menu_type == "load":
            items = self.load_menu_items
            selected = self.load_selected
        else:
            items = self.menu_items
            selected = self.selected_item
        
        start_y = 200 if self.menu_type == "main" else 150
        if self.menu_type == "game_over":
            start_y = 200
        
        for i, item in enumerate(items):
            # Determine color based on selection and mouse hover
            if i == selected or i == self.mouse_hover:
                color = self.blue
                # Draw highlight background
                item_rect = pygame.Rect(screen_width // 2 - 100, start_y + i * 50 - 25, 200, 50)
                pygame.draw.rect(screen, self.dark_blue, item_rect)
                pygame.draw.rect(screen, self.blue, item_rect, 2)
            else:
                color = self.white
            
            text = self.font.render(item, True, color)
            text_rect = text.get_rect(center=(screen_width // 2, start_y + i * 50))
            screen.blit(text, text_rect)
        
        # Instructions
        if self.menu_type == "main":
            instruction_text = "Use arrow keys or mouse to navigate, Enter/Click to select"
        elif self.menu_type == "game_over":
            instruction_text = "Choose an option to continue"
        else:
            instruction_text = "Use arrow keys or mouse to navigate, Enter/Click to select, Esc to go back"
        
        instruction_surface = pygame.font.Font(None, 24).render(instruction_text, True, self.gray)
        instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height - 50))
        screen.blit(instruction_surface, instruction_rect)