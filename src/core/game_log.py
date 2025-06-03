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
        """Render the message log UI - now handled by HUD integration"""
        # This method is now handled by the UI renderer's render_game_log_in_hud method
        # Keep this method for compatibility but don't render anything here
        pass
    
    def clear(self):
        """Clear all messages"""
        self.messages.clear()
    
    def get_recent_messages(self, count=10):
        """Get the most recent messages"""
        return self.messages[-count:] if len(self.messages) >= count else self.messages
    
    def get_message_color(self, msg_type):
        """Get color for a message type"""
        return self.colors.get(msg_type, self.colors["default"])