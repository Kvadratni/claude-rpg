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
        
        # Mouse support
        self.mouse_hover = -1
        self.menu_rects = []
        
        # Colors (matching main menu style)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        self.input_color = (200, 200, 255)
        self.background_color = (0, 0, 0, 180)
        
        # Add input font
        self.input_font = pygame.font.Font(None, 32)
        
    def handle_event(self, event):
        """Handle menu events with mouse and keyboard support"""
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.update_mouse_hover(mouse_x, mouse_y)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.mouse_hover >= 0:
                    self.selected_option = self.mouse_hover
                    self.select_option()
                    
        elif event.type == pygame.KEYDOWN:
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
    
    def update_mouse_hover(self, mouse_x, mouse_y):
        """Update mouse hover state"""
        self.mouse_hover = -1
        for i, rect in enumerate(self.menu_rects):
            if rect and rect.collidepoint(mouse_x, mouse_y):
                if self.mouse_hover != i:
                    self.mouse_hover = i
                    self.selected_option = i
                break
    
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
        self.game.new_game(seed=seed)
    
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
        """Render the procedural world menu with main menu styling"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Render background (matching main menu style)
        self.render_gradient_background(screen, screen_width, screen_height)
        self.render_background_stars(screen)
        self.render_particles(screen)
        
        # Draw title with main menu styling
        title_text = "PROCEDURAL WORLD"
        pulse_scale = 1.0 + self.title_pulse * 0.05
        title_size = int(72 * pulse_scale)
        title_font = pygame.font.Font(None, title_size)
        
        # Shadow effect
        shadow_surface = title_font.render(title_text, True, self.colors['title_shadow'])
        shadow_rect = shadow_surface.get_rect(center=(screen_width // 2 + 3, screen_height // 4 + 3))
        screen.blit(shadow_surface, shadow_rect)
        
        # Main title
        title_surface = title_font.render(title_text, True, self.colors['title_gold'])
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle_text = "Create Your Own Adventure"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, self.colors['menu_normal'])
        subtitle_rect = subtitle_surface.get_rect(center=(screen_width // 2, screen_height // 4 + 50))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Clear previous rectangles
        self.menu_rects = []
        
        # Draw options with main menu styling - moved up more to prevent overlap
        start_y = screen_height // 2 - 120  # Moved up more to make room for all content
        for i, option in enumerate(self.options):
            y_pos = start_y + i * 45  # Reduced spacing to 45 to fit more content
            
            # Determine colors based on selection and hover
            if i == self.selected_option or i == self.mouse_hover:
                color = self.colors['menu_selected']
                # Hover effect - slight glow
                glow_surface = self.menu_font.render(option, True, self.colors['accent_blue'])
                glow_rect = glow_surface.get_rect(center=(screen_width // 2 + 2, y_pos + 2))
                glow_surface.set_alpha(100)
                screen.blit(glow_surface, glow_rect)
            else:
                color = self.colors['menu_normal']
            
            # Special formatting for seed options
            if option == "Random Seed":
                display_text = f"● {option}" if self.use_random_seed else f"○ {option}"
            elif option == "Custom Seed":
                display_text = f"● {option}" if not self.use_random_seed else f"○ {option}"
            else:
                display_text = option
            
            # Main text
            text_surface = self.menu_font.render(display_text, True, color)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_pos))
            screen.blit(text_surface, text_rect)
            
            # Store rectangle for mouse collision
            self.menu_rects.append(text_rect)
            
            # Selection indicator (matching main menu style)
            if i == self.selected_option:
                indicator_x = text_rect.left - 30
                indicator_y = text_rect.centery
                pygame.draw.polygon(screen, self.colors['menu_selected'], [
                    (indicator_x, indicator_y - 8),
                    (indicator_x, indicator_y + 8),
                    (indicator_x + 12, indicator_y)
                ])
        
        # Draw seed input field if custom seed is selected
        if not self.use_random_seed:
            input_y = start_y + len(self.options) * 45 + 15  # Adjusted for new spacing and reduced gap
            
            # Input label
            label_text = "Enter Seed (1-9999999999):"
            label_surface = self.input_font.render(label_text, True, self.colors['menu_normal'])
            label_rect = label_surface.get_rect(center=(screen_width // 2, input_y))
            screen.blit(label_surface, label_rect)
            
            # Input field with main menu styling
            input_text = self.seed_input if self.seed_input else "Random"
            input_surface = self.input_font.render(input_text, True, self.colors['accent_blue'])
            input_rect = input_surface.get_rect(center=(screen_width // 2, input_y + 30))
            
            # Draw input background with glow effect
            bg_rect = input_rect.inflate(30, 15)
            pygame.draw.rect(screen, (20, 20, 40), bg_rect)
            pygame.draw.rect(screen, self.colors['accent_blue'], bg_rect, 2)
            
            screen.blit(input_surface, input_rect)
        
        # Instructions (matching main menu style) - moved up more to prevent overlap
        instruction_text = "Use Mouse to Navigate • Click to Select"
        instruction_surface = self.small_font.render(instruction_text, True, self.colors['menu_normal'])
        instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height - 120))  # Moved up more
        
        # Semi-transparent background for instructions
        bg_rect = instruction_rect.inflate(20, 10)
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*self.colors['bg_dark'], 180))
        screen.blit(bg_surface, bg_rect)
        pygame.draw.rect(screen, self.colors['border_color'], bg_rect, 1)
        screen.blit(instruction_surface, instruction_rect)
        
        # Additional info - moved up more and made more compact
        info_y = screen_height - 90  # Moved up more to prevent overlap
        info_lines = [
            "Random: Completely random world • Custom: Reproducible world",
            "Same seed = Same world every time!"
        ]
        
        for i, line in enumerate(info_lines):
            info_surface = pygame.font.Font(None, 18).render(line, True, self.colors['menu_normal'])  # Even smaller font
            info_rect = info_surface.get_rect(center=(screen_width // 2, info_y + i * 18))  # Tighter spacing
            screen.blit(info_surface, info_rect)