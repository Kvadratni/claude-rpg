"""
Procedural World Menu for selecting procedural generation options
"""

import pygame
import random
from .base_menu import BaseMenu


class ProceduralWorldMenu(BaseMenu):
    """Menu for configuring procedural world generation"""
    
    def __init__(self, game):
        super().__init__(game)
        self.title = "Create Procedural World"
        
        # Menu state
        self.seed_input = ""
        self.use_random_seed = True
        self.selected_option = 0
        
        # Menu options
        self.options = [
            "Random Seed",
            "Custom Seed",
            "Generate World",
            "Back to Main Menu"
        ]
        
        # Colors
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        self.input_color = (200, 200, 255)
        self.background_color = (0, 0, 0, 180)
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.input_font = pygame.font.Font(None, 32)
        
    def handle_event(self, event):
        """Handle menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.play_ui_sound("menu_move")
                
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.play_ui_sound("menu_move")
                
            elif event.key == pygame.K_RETURN:
                self.select_option()
                
            elif event.key == pygame.K_ESCAPE:
                self.go_back()
                
            elif self.selected_option == 1:  # Custom seed input
                if event.key == pygame.K_BACKSPACE:
                    self.seed_input = self.seed_input[:-1]
                elif event.unicode.isdigit() and len(self.seed_input) < 10:
                    self.seed_input += event.unicode
    
    def select_option(self):
        """Handle option selection"""
        option = self.options[self.selected_option]
        
        if option == "Random Seed":
            self.use_random_seed = True
            self.seed_input = ""
            self.play_ui_sound("menu_select")
            
        elif option == "Custom Seed":
            self.use_random_seed = False
            self.play_ui_sound("menu_select")
            
        elif option == "Generate World":
            self.generate_world()
            
        elif option == "Back to Main Menu":
            self.go_back()
    
    def generate_world(self):
        """Generate the procedural world"""
        if self.use_random_seed:
            seed = random.randint(1, 999999)
        else:
            if self.seed_input:
                seed = int(self.seed_input)
            else:
                seed = random.randint(1, 999999)
        
        print(f"Generating procedural world with seed: {seed}")
        
        # Play generation sound
        self.play_ui_sound("menu_confirm")
        
        # Start the game with procedural generation
        self.game.new_game(use_procedural=True, seed=seed)
    
    def go_back(self):
        """Return to main menu"""
        self.play_ui_sound("menu_back")
        from .main_menu import MainMenu
        self.game.menu = MainMenu(self.game)
    
    def play_ui_sound(self, sound_name):
        """Play UI sound if audio manager is available"""
        if hasattr(self.game.asset_loader, 'audio_manager'):
            audio = self.game.asset_loader.audio_manager
            if audio:
                audio.play_ui_sound(sound_name)
    
    def update(self):
        """Update menu logic"""
        pass
    
    def render(self, screen):
        """Render the procedural world menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Draw background overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title_surface = self.title_font.render(self.title, True, self.text_color)
        title_rect = title_surface.get_rect(center=(screen_width // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Draw description
        desc_text = "Choose how to generate your world:"
        desc_surface = self.font.render(desc_text, True, self.text_color)
        desc_rect = desc_surface.get_rect(center=(screen_width // 2, 150))
        screen.blit(desc_surface, desc_rect)
        
        # Draw options
        start_y = 220
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.text_color
            
            if option == "Random Seed":
                display_text = f"● {option}" if self.use_random_seed else f"○ {option}"
            elif option == "Custom Seed":
                display_text = f"● {option}" if not self.use_random_seed else f"○ {option}"
            else:
                display_text = option
            
            text_surface = self.font.render(display_text, True, color)
            text_rect = text_surface.get_rect(center=(screen_width // 2, start_y + i * 50))
            screen.blit(text_surface, text_rect)
        
        # Draw seed input field if custom seed is selected
        if not self.use_random_seed:
            input_y = start_y + len(self.options) * 50 + 20
            
            # Input label
            label_text = "Enter Seed (1-9999999999):"
            label_surface = self.input_font.render(label_text, True, self.text_color)
            label_rect = label_surface.get_rect(center=(screen_width // 2, input_y))
            screen.blit(label_surface, label_rect)
            
            # Input field
            input_text = self.seed_input if self.seed_input else "Random"
            input_surface = self.input_font.render(input_text, True, self.input_color)
            input_rect = input_surface.get_rect(center=(screen_width // 2, input_y + 30))
            
            # Draw input background
            bg_rect = input_rect.inflate(20, 10)
            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            pygame.draw.rect(screen, self.input_color, bg_rect, 2)
            
            screen.blit(input_surface, input_rect)
        
        # Draw instructions
        instructions = [
            "↑↓ Navigate   ENTER Select   ESC Back",
            "",
            "Random Seed: Generate a completely random world",
            "Custom Seed: Use a specific number for reproducible worlds",
            "",
            "Same seed = Same world every time!"
        ]
        
        instruction_y = screen_height - 150
        for instruction in instructions:
            if instruction:  # Skip empty lines
                inst_surface = pygame.font.Font(None, 24).render(instruction, True, (180, 180, 180))
                inst_rect = inst_surface.get_rect(center=(screen_width // 2, instruction_y))
                screen.blit(inst_surface, inst_rect)
            instruction_y += 20