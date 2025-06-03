"""
Game log system for displaying messages to the player
"""

import pygame
import time

class GameLog:
    """Manages game messages and UI display"""
    
    def __init__(self, max_messages=50):
        self.messages = []
        self.max_messages = max_messages
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Scrolling functionality
        self.scroll_offset = 0  # How many messages to scroll up from the bottom
        self.max_scroll_offset = 0  # Maximum scroll offset based on message count
        
        # Scroll arrow buttons
        self.scroll_up_rect = None
        self.scroll_down_rect = None
        self.arrow_size = 16
        
        # Colors
        self.colors = {
            "default": (255, 255, 255),
            "combat": (255, 100, 100),
            "item": (100, 255, 100),
            "experience": (255, 255, 100),
            "system": (150, 150, 255),
            "dialog": (200, 200, 255),
            "quest": (255, 215, 0),      # Gold for quest messages
            "story": (255, 165, 0),      # Orange for story messages
            "exploration": (100, 255, 255),  # Cyan for exploration
            "reward": (50, 255, 50),     # Bright green for rewards
            "error": (255, 50, 50)
        }
        
        # UI settings
        self.visible_messages = 8
        self.message_height = 22
        self.fade_time = 10.0  # seconds before messages start fading
        
    def add_message(self, text, msg_type="default"):
        """Add a message to the log"""
        timestamp = time.time()
        message = {
            "text": text,
            "type": msg_type,
            "timestamp": timestamp,
            "alpha": 255
        }
        
        self.messages.append(message)
        
        # Remove old messages if we exceed the limit
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
        
        # Update max scroll offset
        self.max_scroll_offset = max(0, len(self.messages) - self.visible_messages)
        
        # Auto-scroll to bottom when new message arrives (unless user is scrolling)
        if self.scroll_offset == 0:
            self.scroll_offset = 0  # Stay at bottom
        
        # Print to console as well for debugging
        print(f"[{msg_type.upper()}] {text}")
    
    def scroll_up(self):
        """Scroll up in the message log"""
        if self.scroll_offset < self.max_scroll_offset:
            self.scroll_offset += 1
            return True
        return False
    
    def scroll_down(self):
        """Scroll down in the message log"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            return True
        return False
    
    def handle_click(self, pos):
        """Handle mouse clicks on scroll arrows"""
        if self.scroll_up_rect and self.scroll_up_rect.collidepoint(pos):
            return self.scroll_up()
        elif self.scroll_down_rect and self.scroll_down_rect.collidepoint(pos):
            return self.scroll_down()
        return False
    
    def handle_scroll(self, scroll_direction):
        """Handle scroll wheel input"""
        if scroll_direction > 0:  # Scroll up
            return self.scroll_up()
        elif scroll_direction < 0:  # Scroll down
            return self.scroll_down()
        return False
    
    def update(self):
        """Update message fading"""
        current_time = time.time()
        
        for message in self.messages:
            age = current_time - message["timestamp"]
            
            if age > self.fade_time:
                # Start fading after fade_time seconds
                fade_duration = 5.0  # 5 seconds to fully fade
                fade_progress = min(1.0, (age - self.fade_time) / fade_duration)
                message["alpha"] = int(255 * (1.0 - fade_progress))
            else:
                message["alpha"] = 255
        
        # Remove fully faded messages
        self.messages = [msg for msg in self.messages if msg["alpha"] > 0]
    
    def render(self, screen):
        """Render the message log UI with scroll arrows"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Log panel dimensions (make room for scroll arrows)
        panel_width = screen_width - 20
        panel_height = (self.visible_messages * self.message_height) + 20
        panel_x = 10
        panel_y = screen_height - panel_height - 10
        
        # Draw semi-transparent background
        log_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        log_surface.fill((0, 0, 0, 180))
        
        # Draw border
        pygame.draw.rect(log_surface, (100, 100, 100), log_surface.get_rect(), 2)
        
        # Draw title with scroll indicator
        title_text = "Game Log"
        if self.scroll_offset > 0:
            title_text += f" (↑{self.scroll_offset})"
        title_surface = self.small_font.render(title_text, True, (200, 200, 200))
        log_surface.blit(title_surface, (5, 2))
        
        # Draw scroll arrows if there are more messages than visible
        if len(self.messages) > self.visible_messages:
            # Calculate arrow positions
            arrow_x = panel_width - 30
            up_arrow_y = 2
            down_arrow_y = panel_height - self.arrow_size - 2
            
            # Update arrow rects for click detection (in screen coordinates)
            self.scroll_up_rect = pygame.Rect(panel_x + arrow_x, panel_y + up_arrow_y, self.arrow_size, self.arrow_size)
            self.scroll_down_rect = pygame.Rect(panel_x + arrow_x, panel_y + down_arrow_y, self.arrow_size, self.arrow_size)
            
            # Draw up arrow (triangle pointing up)
            up_color = (255, 255, 255) if self.scroll_offset < self.max_scroll_offset else (100, 100, 100)
            up_points = [
                (arrow_x + self.arrow_size // 2, up_arrow_y + 2),  # Top point
                (arrow_x + 2, up_arrow_y + self.arrow_size - 2),   # Bottom left
                (arrow_x + self.arrow_size - 2, up_arrow_y + self.arrow_size - 2)  # Bottom right
            ]
            pygame.draw.polygon(log_surface, up_color, up_points)
            
            # Draw down arrow (triangle pointing down)
            down_color = (255, 255, 255) if self.scroll_offset > 0 else (100, 100, 100)
            down_points = [
                (arrow_x + 2, down_arrow_y + 2),  # Top left
                (arrow_x + self.arrow_size - 2, down_arrow_y + 2),  # Top right
                (arrow_x + self.arrow_size // 2, down_arrow_y + self.arrow_size - 2)  # Bottom point
            ]
            pygame.draw.polygon(log_surface, down_color, down_points)
            
            # Show scroll hint
            hint_text = "Scroll or click arrows"
            hint_surface = self.small_font.render(hint_text, True, (150, 150, 150))
            hint_width = hint_surface.get_width()
            log_surface.blit(hint_surface, (panel_width - hint_width - 50, 2))
        else:
            # No scroll arrows needed
            self.scroll_up_rect = None
            self.scroll_down_rect = None
        
        # Calculate which messages to show based on scroll offset
        if len(self.messages) <= self.visible_messages:
            # Show all messages if we have fewer than visible_messages
            messages_to_show = self.messages
        else:
            # Show messages based on scroll position
            start_index = len(self.messages) - self.visible_messages - self.scroll_offset
            end_index = len(self.messages) - self.scroll_offset
            messages_to_show = self.messages[start_index:end_index]
        
        # Draw messages
        for i, message in enumerate(messages_to_show):
            y_pos = 18 + (i * self.message_height)
            color = self.colors.get(message["type"], self.colors["default"])
            
            # Apply alpha for fading (but not when scrolling up)
            if message["alpha"] < 255 and self.scroll_offset == 0:
                color = (*color, message["alpha"])
                text_surface = self.font.render(message["text"], True, color)
                text_surface.set_alpha(message["alpha"])
            else:
                text_surface = self.font.render(message["text"], True, color)
            
            # Truncate long messages (leave room for scroll arrows)
            max_width = panel_width - 60 if len(self.messages) > self.visible_messages else panel_width - 10
            if text_surface.get_width() > max_width:
                # Find a good truncation point
                truncated_text = message["text"]
                while self.font.size(truncated_text + "...")[0] > max_width:
                    truncated_text = truncated_text[:-1]
                text_surface = self.font.render(truncated_text + "...", True, color)
            
            log_surface.blit(text_surface, (5, y_pos))
        
        # Blit the log panel to the screen
        screen.blit(log_surface, (panel_x, panel_y))
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
    
    def get_recent_messages(self, count=10):
        """Get the most recent messages"""
        return self.messages[-count:] if len(self.messages) >= count else self.messages
    
    def get_message_color(self, msg_type):
        """Get color for a message type"""
        return self.colors.get(msg_type, self.colors["default"])