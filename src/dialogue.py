"""
Dialogue system for NPC interactions
"""

import pygame

class DialogueWindow:
    """Dialogue window for NPC conversations"""
    
    def __init__(self, npc_name, dialogue_lines, asset_loader=None):
        self.npc_name = npc_name
        self.dialogue_lines = dialogue_lines
        self.current_line = 0
        self.asset_loader = asset_loader
        self.show = True
        
        # UI settings
        self.width = 600
        self.height = 200
        self.padding = 20
        self.line_height = 25
        
        # Fonts
        self.title_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 22)
        self.button_font = pygame.font.Font(None, 20)
        
        # Colors
        self.bg_color = (40, 40, 60)
        self.border_color = (120, 120, 140)
        self.text_color = (255, 255, 255)
        self.title_color = (255, 215, 0)  # Gold
        self.button_color = (80, 80, 100)
        self.button_hover_color = (100, 100, 120)
        
        # Button rects (will be set in render)
        self.next_button_rect = None
        self.close_button_rect = None
    
    def handle_click(self, pos):
        """Handle mouse clicks on the dialogue window"""
        if not self.show:
            return False
        
        # Get window position
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        window_x = (screen_width - self.width) // 2
        window_y = (screen_height - self.height) // 2
        
        # Convert to relative position
        rel_x = pos[0] - window_x
        rel_y = pos[1] - window_y
        
        # Check if click is outside window
        if rel_x < 0 or rel_x > self.width or rel_y < 0 or rel_y > self.height:
            self.close()
            return True
        
        # Check next button
        if self.next_button_rect and self.next_button_rect.collidepoint(rel_x, rel_y):
            self.next_line()
            return True
        
        # Check close button
        if self.close_button_rect and self.close_button_rect.collidepoint(rel_x, rel_y):
            self.close()
            return True
        
        return True  # Consumed the click
    
    def next_line(self):
        """Advance to next dialogue line"""
        if self.current_line < len(self.dialogue_lines) - 1:
            self.current_line += 1
        else:
            # End of dialogue
            self.close()
    
    def close(self):
        """Close the dialogue window"""
        self.show = False
    
    def render(self, screen):
        """Render the dialogue window"""
        if not self.show:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate window position (center of screen)
        window_x = (screen_width - self.width) // 2
        window_y = (screen_height - self.height) // 2
        
        # Create dialogue surface
        dialogue_surface = pygame.Surface((self.width, self.height))
        dialogue_surface.fill(self.bg_color)
        
        # Draw border
        pygame.draw.rect(dialogue_surface, self.border_color, (0, 0, self.width, self.height), 3)
        
        # Draw NPC name (title)
        title_text = self.title_font.render(self.npc_name, True, self.title_color)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.width // 2
        title_rect.y = self.padding // 2
        dialogue_surface.blit(title_text, title_rect)
        
        # Draw current dialogue line(s)
        if self.current_line < len(self.dialogue_lines):
            current_text = self.dialogue_lines[self.current_line]
            
            # Word wrap the text
            words = current_text.split(' ')
            lines = []
            current_line_text = ""
            max_width = self.width - (self.padding * 2)
            
            for word in words:
                test_line = current_line_text + (" " if current_line_text else "") + word
                if self.text_font.size(test_line)[0] <= max_width:
                    current_line_text = test_line
                else:
                    if current_line_text:
                        lines.append(current_line_text)
                    current_line_text = word
            
            if current_line_text:
                lines.append(current_line_text)
            
            # Render wrapped lines
            text_start_y = self.padding + 35  # Below title
            for i, line in enumerate(lines):
                if i >= 4:  # Max 4 lines
                    break
                line_surface = self.text_font.render(line, True, self.text_color)
                dialogue_surface.blit(line_surface, (self.padding, text_start_y + i * self.line_height))
        
        # Draw buttons
        button_y = self.height - 40
        button_height = 30
        
        # Next/Continue button
        if self.current_line < len(self.dialogue_lines) - 1:
            button_text = "Next"
        else:
            button_text = "End"
        
        next_button_width = 80
        next_button_x = self.width - next_button_width - self.padding
        self.next_button_rect = pygame.Rect(next_button_x, button_y, next_button_width, button_height)
        
        pygame.draw.rect(dialogue_surface, self.button_color, self.next_button_rect)
        pygame.draw.rect(dialogue_surface, self.border_color, self.next_button_rect, 2)
        
        button_text_surface = self.button_font.render(button_text, True, self.text_color)
        button_text_rect = button_text_surface.get_rect(center=self.next_button_rect.center)
        dialogue_surface.blit(button_text_surface, button_text_rect)
        
        # Close button (X)
        close_button_size = 25
        close_button_x = self.width - close_button_size - 5
        close_button_y = 5
        self.close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
        
        pygame.draw.rect(dialogue_surface, (200, 50, 50), self.close_button_rect)
        pygame.draw.rect(dialogue_surface, self.border_color, self.close_button_rect, 2)
        
        close_text = self.button_font.render("X", True, self.text_color)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        dialogue_surface.blit(close_text, close_text_rect)
        
        # Progress indicator
        if len(self.dialogue_lines) > 1:
            progress_text = f"{self.current_line + 1}/{len(self.dialogue_lines)}"
            progress_surface = self.button_font.render(progress_text, True, (180, 180, 180))
            dialogue_surface.blit(progress_surface, (self.padding, button_y + 5))
        
        # Blit dialogue surface to main screen
        screen.blit(dialogue_surface, (window_x, window_y))