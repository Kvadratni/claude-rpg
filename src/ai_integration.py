"""
AI Integration Framework for NPCs
Handles communication with Goose CLI for AI-powered conversations
"""

import subprocess
import json
import re
import os
import pygame
import tempfile
import time
from typing import List, Dict, Optional, Tuple

class GooseRecipeIntegration:
    """Handles communication with Goose CLI via subprocess"""
    
    def __init__(self, npc_name: str):
        self.npc_name = npc_name
        self.conversation_history = []
        self.session_name = f"npc_{npc_name.lower().replace(' ', '_')}"
        
    def send_message(self, message: str, context: str = "") -> str:
        """Send message to AI and get response using session approach"""
        try:
            # Set up environment with GPT-4.1 as the chosen model
            env = os.environ.copy()
            env["GOOSE_MODEL"] = "goose-gpt-4-1"
            
            # Create a comprehensive NPC prompt
            npc_prompt = self._create_npc_prompt(message, context)
            
            # Write prompt to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(npc_prompt)
                temp_file = f.name
            
            try:
                # Use goose run with instructions file
                cmd = [
                    "goose", "run",
                    "--instructions", temp_file,
                    "--no-session"
                ]
                
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    response = self._parse_response(result.stdout)
                    response = self._clean_npc_response(response)
                    self.conversation_history.append({"player": message, "npc": response})
                    return response
                else:
                    print(f"AI Error: {result.stderr}")
                    return self._get_fallback_response(message)
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return f"*{self.npc_name} takes a moment to think*"
        except Exception as e:
            print(f"AI Integration Error: {e}")
            return self._get_fallback_response(message)
    
    def _create_npc_prompt(self, message: str, context: str) -> str:
        """Create a comprehensive NPC prompt"""
        prompt_parts = [
            f"You are {self.npc_name}, an NPC in a fantasy RPG world.",
            "",
            "ROLE GUIDELINES:",
            f"- You are {self.npc_name}",
            "- Stay in character at all times",
            "- Respond naturally and helpfully",
            "- Keep responses concise (1-2 sentences)",
            "- Use medieval fantasy language appropriate for your role",
            "",
        ]
        
        # Add role-specific guidelines
        if "Elder" in self.npc_name:
            prompt_parts.extend([
                "- You are a wise village elder with knowledge of local history",
                "- You give quests and advice to adventurers",
                "- You speak with wisdom and authority",
            ])
        elif "Merchant" in self.npc_name or "Shopkeeper" in self.npc_name:
            prompt_parts.extend([
                "- You are a merchant who sells goods to adventurers",
                "- You are friendly but business-minded",
                "- You often mention your wares and prices",
            ])
        elif "Guard" in self.npc_name:
            prompt_parts.extend([
                "- You are a town guard who protects the village",
                "- You are vigilant and duty-bound",
                "- You provide information about local threats",
            ])
        
        prompt_parts.extend([
            "",
            f"CURRENT CONTEXT: {context}" if context else "CURRENT CONTEXT: Player is in the village",
            "",
            f"PLAYER SAYS: \"{message}\"",
            "",
            f"Respond as {self.npc_name} in character:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _get_fallback_response(self, message: str) -> str:
        """Get a fallback response when AI fails"""
        fallback_responses = {
            "hello": f"Greetings, traveler. I am {self.npc_name}.",
            "who": f"I am {self.npc_name}, at your service.",
            "help": f"How may {self.npc_name} assist you?",
            "bye": f"Farewell, and may your journey be safe.",
        }
        
        message_lower = message.lower()
        for key, response in fallback_responses.items():
            if key in message_lower:
                return response
        
        return f"*{self.npc_name} nods thoughtfully*"
    
    def _clean_npc_response(self, response: str) -> str:
        """Clean up AI response to be more NPC-like"""
        if not response or len(response.strip()) < 3:
            return f"Greetings, I am {self.npc_name}."
        
        # Remove common artifacts
        response = response.strip()
        response = re.sub(r'\*.*?\*', '', response)  # Remove action text
        response = re.sub(r'\[.*?\]', '', response)  # Remove bracketed text
        
        # Remove AI-like phrases
        ai_phrases = [
            "As an AI", "I'm an AI", "I cannot", "I don't have the ability",
            "I'm not able to", "I can't actually", "In this game", "As your"
        ]
        
        for phrase in ai_phrases:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        response = response.strip()
        
        # Ensure it's not empty after cleaning
        if not response or len(response) < 5:
            return f"Greetings, traveler. I am {self.npc_name}."
        
        # Ensure it ends with punctuation
        if not response.endswith(('.', '!', '?')):
            response += "."
        
        return response
    
    def _parse_response(self, output: str) -> str:
        """Extract the actual AI response from goose output"""
        lines = output.strip().split('\n')
        response_lines = []
        
        # Skip system messages
        skip_patterns = [
            r'running without session',
            r'working directory:',
            r'provider:',
            r'model:',
            r'logging to'
        ]
        
        for line in lines:
            if not line.strip():
                continue
                
            # Check if line matches any skip pattern
            should_skip = any(re.search(pattern, line) for pattern in skip_patterns)
            if should_skip:
                continue
                
            # Remove ANSI color codes
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            if clean_line.strip():
                response_lines.append(clean_line.strip())
        
        response = ' '.join(response_lines) if response_lines else ""
        return response


class AIChatWindow:
    """Renders the chat interface overlay"""
    
    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.is_active = False
        self.chat_history = []
        self.input_buffer = ""
        self.font = None
        self.small_font = None
        self.scroll_offset = 0
        self.max_visible_lines = 10  # Increased for better visibility
        
        # Initialize fonts
        self._init_fonts()
        
        # Chat window dimensions
        self.width = 600
        self.height = 450  # Increased height
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
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle keyboard input for chat. Returns message if Enter is pressed."""
        if not self.is_active:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_buffer.strip():
                    message = self.input_buffer.strip()
                    self.input_buffer = ""
                    return message
            elif event.key == pygame.K_BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.is_active = False
            elif event.key == pygame.K_UP:
                # Scroll up
                if self.scroll_offset > 0:
                    self.scroll_offset -= 1
            elif event.key == pygame.K_DOWN:
                # Scroll down
                max_scroll = max(0, len(self.chat_history) - self.max_visible_lines)
                if self.scroll_offset < max_scroll:
                    self.scroll_offset += 1
            elif event.key == pygame.K_PAGEUP:
                # Page up
                self.scroll_offset = max(0, self.scroll_offset - 3)
            elif event.key == pygame.K_PAGEDOWN:
                # Page down
                max_scroll = max(0, len(self.chat_history) - self.max_visible_lines)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 3)
            elif hasattr(event, 'unicode') and event.unicode.isprintable():
                self.input_buffer += event.unicode
        
        return None
    
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
        title_text = self.font.render("AI Chat", True, (255, 255, 255))
        screen.blit(title_text, (x + self.padding, y + 10))
        
        # Draw chat history area
        chat_area_y = y + 50
        chat_area_height = self.height - 120  # Leave space for title and input
        
        # Create a clipping rectangle for the chat area
        chat_rect = pygame.Rect(x + self.padding, chat_area_y, self.width - self.padding * 2 - 20, chat_area_height)
        
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


class GameContext:
    """Provides AI with current game state information"""
    
    def __init__(self, player, level):
        self.player = player
        self.level = level
    
    def get_context(self) -> str:
        """Get formatted context string for AI"""
        context_parts = []
        
        # Player info
        if self.player:
            context_parts.append(f"Player Level: {getattr(self.player, 'level', 1)}")
            context_parts.append(f"Player HP: {getattr(self.player, 'hp', 100)}/{getattr(self.player, 'max_hp', 100)}")
            
            # Player location
            player_x = getattr(self.player, 'x', 0)
            player_y = getattr(self.player, 'y', 0)
            context_parts.append(f"Player Position: ({player_x}, {player_y})")
            
            # Inventory highlights
            if hasattr(self.player, 'inventory') and self.player.inventory:
                # Get inventory item count properly
                if hasattr(self.player.inventory, 'items'):
                    item_count = len(self.player.inventory.items)
                elif hasattr(self.player.inventory, '__len__'):
                    item_count = len(self.player.inventory)
                else:
                    item_count = 0
                    
                if item_count > 0:
                    context_parts.append(f"Player has {item_count} items in inventory")
        
        return " | ".join(context_parts) if context_parts else "Player is exploring the world"


class FallbackAI:
    """Simple fallback AI when external AI is unavailable"""
    
    def __init__(self, npc_name: str):
        self.npc_name = npc_name
        self.conversation_history = []
        
        # Predefined responses based on NPC type and common inputs
        self.responses = {
            "Village Elder": {
                "hello": "Greetings, young adventurer. I am the Village Elder, keeper of ancient wisdom.",
                "who": "I am the Village Elder, guardian of this village's history and traditions.",
                "help": "I offer guidance to brave souls like yourself. What knowledge do you seek?",
                "quest": "Indeed, there are dark forces stirring. Perhaps you could investigate the old ruins?",
                "bye": "May the ancient spirits guide your path, brave one.",
                "default": "The old ways teach us patience and wisdom, traveler."
            },
            "Master Merchant": {
                "hello": "Welcome, welcome! I am the Master Merchant, purveyor of fine goods!",
                "who": "I am the Master Merchant, trader of exotic wares from distant lands.",
                "help": "I have potions, weapons, and rare artifacts! What catches your eye?",
                "buy": "Ah, excellent choice! My prices are fair for such quality goods.",
                "sell": "I might be interested in your wares. What do you have to offer?",
                "bye": "Safe travels, and remember - quality goods at fair prices!",
                "default": "Business is good when adventurers like you visit my shop!"
            },
            "Guard Captain": {
                "hello": "Halt! I am the Guard Captain. State your business in our village.",
                "who": "I am the Guard Captain, protector of this village and its people.",
                "help": "I maintain order here. Is there trouble you wish to report?",
                "danger": "The roads have been perilous lately. Bandits and worse creatures roam.",
                "safe": "This village is under my protection. You may rest safely here.",
                "bye": "Stay vigilant out there, traveler. Danger lurks in dark places.",
                "default": "I keep watch over this village day and night."
            }
        }
    
    def send_message(self, message: str, context: str = "") -> str:
        """Generate a fallback response"""
        message_lower = message.lower()
        npc_responses = self.responses.get(self.npc_name, {})
        
        # Check for specific keywords
        for keyword, response in npc_responses.items():
            if keyword in message_lower and keyword != "default":
                self.conversation_history.append({"player": message, "npc": response})
                return response
        
        # Use default response for this NPC type
        default_response = npc_responses.get("default", f"*{self.npc_name} nods thoughtfully*")
        self.conversation_history.append({"player": message, "npc": default_response})
        return default_response


# Import the new recipe manager
try:
    import sys
    print(f"🔧 [AI_Integration] Python path: {sys.executable}")
    print(f"🔧 [AI_Integration] Python version: {sys.version}")
    print(f"🔧 [AI_Integration] Attempting to import yaml...")
    import yaml
    print(f"✅ [AI_Integration] yaml imported successfully")
    from .recipe_manager import RecipeBasedGooseIntegration
    RECIPES_AVAILABLE = True
    print("✅ [AI_Integration] Recipe manager imported successfully")
except ImportError as e:
    RECIPES_AVAILABLE = False
    print(f"⚠️  [AI_Integration] Recipe manager not available: {e}, using fallback AI integration")
    import traceback
    traceback.print_exc()


# Update GooseRecipeIntegration to use fallback
class EnhancedGooseRecipeIntegration(GooseRecipeIntegration):
    """Enhanced version with recipe support and fallback AI"""
    
    def __init__(self, npc_name: str):
        print(f"🔧 [EnhancedGooseRecipeIntegration] Initializing for {npc_name}")
        print(f"🔧 [EnhancedGooseRecipeIntegration] RECIPES_AVAILABLE: {RECIPES_AVAILABLE}")
        
        super().__init__(npc_name)
        self.fallback_ai = FallbackAI(npc_name)
        self.use_fallback = False
        
        # Try to use recipe-based integration if available
        if RECIPES_AVAILABLE:
            try:
                print(f"🔧 [EnhancedGooseRecipeIntegration] Attempting to create RecipeBasedGooseIntegration")
                self.recipe_integration = RecipeBasedGooseIntegration(npc_name, "recipes")
                self.use_recipes = True
                print(f"✅ [EnhancedGooseRecipeIntegration] Recipe integration created for {npc_name}")
            except Exception as e:
                print(f"⚠️  [EnhancedGooseRecipeIntegration] Failed to create recipe integration: {e}")
                self.recipe_integration = None
                self.use_recipes = False
        else:
            print(f"⚠️  [EnhancedGooseRecipeIntegration] Recipes not available, using fallback")
            self.recipe_integration = None
            self.use_recipes = False
    
    def send_message(self, message: str, context: str = "") -> str:
        """Send message with recipe support and fallback"""
        print(f"🔧 [EnhancedGooseRecipeIntegration] send_message for {self.npc_name}")
        print(f"🔧 [EnhancedGooseRecipeIntegration] use_recipes: {getattr(self, 'use_recipes', False)}")
        print(f"🔧 [EnhancedGooseRecipeIntegration] use_fallback: {self.use_fallback}")
        
        # If we're already using fallback, continue with it
        if self.use_fallback:
            print(f"🔧 [EnhancedGooseRecipeIntegration] Using fallback AI for {self.npc_name}")
            return self.fallback_ai.send_message(message, context)
        
        # Try recipe-based integration first if available
        if getattr(self, 'use_recipes', False) and self.recipe_integration:
            try:
                print(f"🔧 [EnhancedGooseRecipeIntegration] Trying recipe integration for {self.npc_name}")
                response = self.recipe_integration.send_message(message, context)
                print(f"✅ [EnhancedGooseRecipeIntegration] Recipe response: '{response[:50]}...'")
                return response
            except Exception as e:
                print(f"⚠️  [EnhancedGooseRecipeIntegration] Recipe integration failed: {e}")
                # Fall through to try original AI
        
        try:
            # Try the original AI
            print(f"🔧 [EnhancedGooseRecipeIntegration] Trying external AI for {self.npc_name}")
            response = super().send_message(message, context)
            print(f"🔧 [EnhancedGooseRecipeIntegration] External AI response: '{response[:50]}...'")
            
            # If response is too generic or empty, switch to fallback
            if (not response or 
                len(response.strip()) < 10 or 
                "looks confused" in response or
                response.strip() == f"Greetings, I am {self.npc_name}." or
                "seems distracted" in response or
                "takes too long" in response):
                print(f"⚠️  [EnhancedGooseRecipeIntegration] External AI response inadequate, switching {self.npc_name} to fallback AI")
                print(f"⚠️  [EnhancedGooseRecipeIntegration] Response was: '{response}'")
                self.use_fallback = True
                return self.fallback_ai.send_message(message, context)
            
            return response
            
        except Exception as e:
            print(f"⚠️  [EnhancedGooseRecipeIntegration] AI error for {self.npc_name}, using fallback: {e}")
            self.use_fallback = True
            return self.fallback_ai.send_message(message, context)