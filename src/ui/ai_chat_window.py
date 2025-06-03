"""
AI Chat Window for NPC conversations
"""

import pygame
from typing import List, Dict, Optional


class AIChatWindow:
    """Renders the AI chat interface overlay for NPC conversations"""
    
    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.is_active = False
        self.chat_history: List[Dict[str, str]] = []
        self.input_buffer = ""
        self.font = None
        self.small_font = None
        self.scroll_offset = 0
        self.max_visible_lines = 10
        self.npc_reference = None  # Reference to the NPC we're chatting with
        
        # Initialize fonts
        self._init_fonts()
        
        # Chat window dimensions
        self.width = 600
        self.height = 450
        self.padding = 20
        
    def _init_fonts(self):
        """Initialize fonts for chat display"""
        try:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
        except:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 20)
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat history"""
        self.chat_history.append({"sender": sender, "message": message})
        
        # Auto-scroll to bottom
        if len(self.chat_history) > self.max_visible_lines:
            self.scroll_offset = len(self.chat_history) - self.max_visible_lines
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input for chat. Returns True if event was handled."""
        if not self.is_active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_buffer.strip() and self.npc_reference:
                    message = self.input_buffer.strip()
                    self.input_buffer = ""
                    
                    # Add player message to chat
                    self.add_message("Player", message)
                    
                    # Get AI response from the NPC
                    context = self.npc_reference._get_game_context(
                        getattr(self.npc_reference, 'current_player', None)
                    )
                    ai_response = self.npc_reference.send_ai_message(message, context)
                    self.add_message(self.npc_reference.name, ai_response)
                    
                return True
                
            elif event.key == pygame.K_BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
                return True
                
            elif event.key == pygame.K_ESCAPE:
                self.is_active = False
                return True
                
            elif event.key == pygame.K_UP:
                # Scroll up
                if self.scroll_offset > 0:
                    self.scroll_offset -= 1
                return True
                
            elif event.key == pygame.K_DOWN:
                # Scroll down
                max_scroll = max(0, len(self.chat_history) - self.max_visible_lines)
                if self.scroll_offset < max_scroll:
                    self.scroll_offset += 1
                return True
                
            elif event.key == pygame.K_PAGEUP:
                # Page up
                self.scroll_offset = max(0, self.scroll_offset - 3)
                return True
                
            elif event.key == pygame.K_PAGEDOWN:
                # Page down
                max_scroll = max(0, len(self.chat_history) - self.max_visible_lines)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 3)
                return True
                
            elif hasattr(event, 'unicode') and event.unicode.isprintable():
                self.input_buffer += event.unicode
                return True
        
        return False
    
    def render(self, screen: pygame.Surface):
        """Render the chat window"""
        if not self.is_active:
            return
            
        screen_width, screen_height = screen.get_size()
        
        # Position chat window in center
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        # Draw background with transparency
        chat_surface = pygame.Surface((self.width, self.height))
        chat_surface.set_alpha(220)
        chat_surface.fill((0, 0, 0))
        screen.blit(chat_surface, (x, y))
        
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.width, self.height), 2)
        
        # Draw title
        npc_name = self.npc_reference.name if self.npc_reference else "AI Chat"
        title_text = self.font.render(f"Talking to {npc_name}", True, (255, 255, 255))
        screen.blit(title_text, (x + self.padding, y + 10))
        
        # Draw chat history area
        chat_area_y = y + 50
        chat_area_height = self.height - 120  # Leave space for title and input
        
        # Draw chat messages with proper spacing
        visible_messages = self.chat_history[self.scroll_offset:self.scroll_offset + self.max_visible_lines]
        current_y = chat_area_y
        line_height = 25  # Increased line height to prevent overlap
        
        for i, msg in enumerate(visible_messages):
            if current_y + line_height > chat_area_y + chat_area_height:
                break  # Don't draw beyond the chat area
                
            sender_color = (100, 255, 100) if msg["sender"] == "Player" else (255, 255, 100)
            
            # Render sender name
            sender_text = self.small_font.render(f"{msg['sender']}:", True, sender_color)
            screen.blit(sender_text, (x + self.padding, current_y))
            
            # Render message with word wrapping
            message_lines = self._wrap_text(msg["message"], self.width - self.padding * 2 - 120)
            for j, line in enumerate(message_lines):
                if current_y + (j + 1) * 18 > chat_area_y + chat_area_height:
                    break  # Don't draw beyond the chat area
                msg_text = self.small_font.render(line, True, (255, 255, 255))
                screen.blit(msg_text, (x + self.padding + 100, current_y + j * 18))
            
            # Move to next message position
            current_y += max(line_height, len(message_lines) * 18 + 5)
        
        # Draw scrollbar if needed
        if len(self.chat_history) > self.max_visible_lines:
            self._draw_scrollbar(screen, x + self.width - 15, chat_area_y, 10, chat_area_height)
        
        # Draw input area
        input_y = y + self.height - 60
        input_rect = pygame.Rect(x + self.padding, input_y, self.width - self.padding * 2, 30)
        pygame.draw.rect(screen, (50, 50, 50), input_rect)
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 1)
        
        # Draw input text with cursor
        display_text = self.input_buffer + "|"
        input_text = self.font.render(display_text, True, (255, 255, 255))
        # Clip text if it's too long
        if input_text.get_width() > input_rect.width - 10:
            # Show only the end of the text that fits
            text_surface = pygame.Surface((input_rect.width - 10, input_text.get_height()))
            text_surface.fill((50, 50, 50))
            text_surface.blit(input_text, (input_rect.width - 10 - input_text.get_width(), 0))
            screen.blit(text_surface, (x + self.padding + 5, input_y + 5))
        else:
            screen.blit(input_text, (x + self.padding + 5, input_y + 5))
        
        # Draw instructions
        instruction_text = self.small_font.render("Type message and press Enter. ESC to close. ↑↓ to scroll.", True, (200, 200, 200))
        screen.blit(instruction_text, (x + self.padding, y + self.height - 25))
    
    def _draw_scrollbar(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Draw a scrollbar for the chat window"""
        # Draw scrollbar background
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        
        # Calculate scrollbar thumb position and size
        total_messages = len(self.chat_history)
        visible_ratio = self.max_visible_lines / total_messages
        thumb_height = max(20, int(height * visible_ratio))
        
        scroll_ratio = self.scroll_offset / max(1, total_messages - self.max_visible_lines)
        thumb_y = y + int((height - thumb_height) * scroll_ratio)
        
        # Draw scrollbar thumb
        pygame.draw.rect(screen, (200, 200, 200), (x, thumb_y, width, thumb_height))
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width pixels"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.small_font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]