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
        
        # Print to console as well for debugging
        print(f"[{msg_type.upper()}] {text}")
    
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
        """Render the message log UI"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Log panel dimensions
        panel_width = screen_width - 20
        panel_height = (self.visible_messages * self.message_height) + 20
        panel_x = 10
        panel_y = screen_height - panel_height - 10
        
        # Draw semi-transparent background
        log_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        log_surface.fill((0, 0, 0, 180))
        
        # Draw border
        pygame.draw.rect(log_surface, (100, 100, 100), log_surface.get_rect(), 2)
        
        # Draw title
        title_text = self.small_font.render("Game Log", True, (200, 200, 200))
        log_surface.blit(title_text, (5, 2))
        
        # Draw messages (most recent at bottom)
        recent_messages = self.messages[-self.visible_messages:]
        
        for i, message in enumerate(recent_messages):
            y_pos = 18 + (i * self.message_height)
            color = self.colors.get(message["type"], self.colors["default"])
            
            # Apply alpha for fading
            if message["alpha"] < 255:
                color = (*color, message["alpha"])
                text_surface = self.font.render(message["text"], True, color)
                text_surface.set_alpha(message["alpha"])
            else:
                text_surface = self.font.render(message["text"], True, color)
            
            # Truncate long messages
            if text_surface.get_width() > panel_width - 10:
                # Find a good truncation point
                truncated_text = message["text"]
                while self.font.size(truncated_text + "...")[0] > panel_width - 10:
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