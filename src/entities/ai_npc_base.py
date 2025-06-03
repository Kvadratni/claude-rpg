"""
Base AI NPC class with embedded recipes and centralized AI communication
"""

import subprocess
import os
import tempfile
import re
import pygame
from typing import Dict, List, Optional, Any
from .base import Entity


class BaseAINPC(Entity):
    """Base class for AI-powered NPCs with embedded recipes"""
    
    # Override this in subclasses with the specific recipe
    recipe: Optional[Dict[str, Any]] = None
    
    def __init__(self, x: int, y: int, name: str, dialog: Optional[List[str]] = None, 
                 asset_loader=None, **kwargs):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.asset_loader = asset_loader
        self.conversation_history: List[Dict[str, str]] = []
        self.session_name = f"npc_{self.__class__.__name__.lower()}"
        self.ai_enabled = bool(self.recipe)
        self.use_fallback = False
        
        # Session management
        self.goose_process = None
        self.session_initialized = False
        self.first_interaction = True  # Track if this is the first interaction
        
        # MCP integration
        self.npc_id = f"{self.name.lower().replace(' ', '_')}_{id(self)}"
        
        # Create NPC sprite
        self.create_npc_sprite()
    
    def send_ai_message(self, message: str, context: str = "") -> str:
        """Send message to AI using embedded recipe"""
        print(f"🔧 [BaseAINPC] send_ai_message for {self.name}: '{message}'")
        
        if not self.recipe or self.use_fallback:
            return self._fallback_response(message)
        
        try:
            response = self._execute_recipe(message, context)
            
            # Handle first interaction specially - allow empty response and show "looks at you" message
            if self.first_interaction:
                self.first_interaction = False
                if not response or len(response.strip()) < 1:
                    # Return a "looks at you" message for first interaction
                    return f"*{self.name} looks at you thoughtfully*"
                else:
                    # We got a good response on first try
                    self.conversation_history.append({"player": message, "npc": response})
                    print(f"✅ [BaseAINPC] AI response for {self.name}: '{response[:50]}...'")
                    return response
            
            # For subsequent interactions, require a proper response
            if response and len(response.strip()) > 0:
                self.conversation_history.append({"player": message, "npc": response})
                print(f"✅ [BaseAINPC] AI response for {self.name}: '{response[:50]}...'")
                return response
            else:
                # Only switch to fallback after first interaction if response is inadequate
                print(f"⚠️  [BaseAINPC] AI response inadequate, switching to fallback")
                self.use_fallback = True
                return self._fallback_response(message)
                
        except Exception as e:
            print(f"❌ [BaseAINPC] AI error for {self.name}: {e}")
            if self.first_interaction:
                self.first_interaction = False
                return f"*{self.name} looks at you with interest*"
            else:
                self.use_fallback = True
                return self._fallback_response(message)
    
    def _execute_recipe(self, message: str, context: str) -> str:
        """Execute the embedded recipe with Goose CLI using persistent session"""
        print(f"🔧 [BaseAINPC] _execute_recipe for {self.name}")
        
        if not self.recipe:
            print(f"❌ [BaseAINPC] No recipe available for {self.name}")
            return ""
        
        # Initialize session if not already done
        if not self.session_initialized:
            if not self._initialize_session():
                return ""
        
        # Send message to existing session
        return self._send_message_to_session(message, context)
    
    def _initialize_session(self) -> bool:
        """Initialize the Goose session for this NPC"""
        print(f"🔧 [BaseAINPC] Initializing session for {self.name}")
        
        # Map NPC names to existing recipe files
        recipe_file_map = {
            "Village Elder": "recipes/village_elder.yaml",
            "Master Merchant": "recipes/master_merchant.yaml", 
            "Guard Captain": "recipes/guard_captain.yaml",
            "Blacksmith": "recipes/blacksmith.yaml",
            "Healer": "recipes/healer.yaml",
            "Tavern Keeper": "recipes/tavern_keeper.yaml"
        }
        
        recipe_file = recipe_file_map.get(self.name)
        if not recipe_file or not os.path.exists(recipe_file):
            print(f"❌ [BaseAINPC] Recipe file not found for {self.name}")
            return False
        
        try:
            # Start Goose process with recipe - provide default context parameter only
            cmd = [
                "goose", "run",
                "--recipe", recipe_file,
                "--params", "context=You are in a fantasy RPG village",  # Provide default context
                "--interactive",
                "--name", self.session_name
            ]
            
            print(f"🔧 [BaseAINPC] Starting session: {' '.join(cmd)}")
            
            # Set up environment
            env = os.environ.copy()
            
            # Get AI model from settings if available
            ai_model = "gpt-4o"  # Default fallback
            if self.asset_loader and hasattr(self.asset_loader, 'settings'):
                ai_model = self.asset_loader.settings.get_ai_model()
            
            env["GOOSE_MODEL"] = ai_model
            print(f"🔧 [BaseAINPC] Using AI model: {ai_model}")
            
            # Start the process
            self.goose_process = subprocess.Popen(
                cmd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Wait for initialization and check if process is still running
            import time
            time.sleep(3)  # Give it more time to start
            
            if self.goose_process.poll() is not None:
                # Process has terminated
                stdout, stderr = self.goose_process.communicate()
                print(f"❌ [BaseAINPC] Session failed to start. Stderr: {stderr[:200]}")
                return False
            
            self.session_initialized = True
            print(f"✅ [BaseAINPC] Session initialized for {self.name}")
            return True
            
        except Exception as e:
            print(f"❌ [BaseAINPC] Failed to initialize session: {e}")
            return False
    
    def _send_message_to_session(self, message: str, context: str) -> str:
        """Send a message to the existing Goose session"""
        if not self.goose_process or self.goose_process.poll() is not None:
            print(f"❌ [BaseAINPC] Session is not active, reinitializing")
            self.session_initialized = False
            if not self._initialize_session():
                return ""
        
        try:
            # Send the message
            full_message = f"{message}\n"
            print(f"🔧 [BaseAINPC] Sending to session: '{message}'")
            
            self.goose_process.stdin.write(full_message)
            self.goose_process.stdin.flush()
            
            # Read response (this is tricky with interactive processes)
            # We'll read until we get a response or timeout
            import select
            import time
            
            response_lines = []
            start_time = time.time()
            timeout = 10  # 10 second timeout
            
            while time.time() - start_time < timeout:
                # Check if there's data to read
                if select.select([self.goose_process.stdout], [], [], 0.1)[0]:
                    line = self.goose_process.stdout.readline()
                    if line:
                        response_lines.append(line.strip())
                        # Look for end of response (you might need to adjust this)
                        if len(response_lines) > 5:  # Assume response is complete after several lines
                            break
                else:
                    time.sleep(0.1)
            
            # Parse the response
            full_output = '\n'.join(response_lines)
            response = self._parse_goose_output(full_output)
            cleaned = self._clean_response(response)
            
            print(f"🔧 [BaseAINPC] Session response: '{cleaned}'")
            return cleaned
            
        except Exception as e:
            print(f"❌ [BaseAINPC] Error sending message to session: {e}")
            return ""
    
    def cleanup_session(self):
        """Clean up the Goose session"""
        if self.goose_process:
            try:
                self.goose_process.stdin.write("exit\n")
                self.goose_process.stdin.flush()
                self.goose_process.wait(timeout=5)
            except:
                self.goose_process.terminate()
            finally:
                self.goose_process = None
                self.session_initialized = False
                print(f"🔧 [BaseAINPC] Session cleaned up for {self.name}")
    
    def _parse_goose_output(self, output: str) -> str:
        """Parse Goose CLI output to extract the AI response"""
        print(f"🔧 [BaseAINPC] Raw goose output:\n{output}")
        
        # Remove ANSI color codes
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)
        
        lines = clean_output.strip().split('\n')
        response_lines = []
        
        # Skip system messages and find the actual AI response
        skip_patterns = [
            r'Loading recipe:',
            r'Description:',
            r'Parameters used to load this recipe:',
            r'recipe_dir \(built-in\):',
            r'running without session',
            r'working directory:',
            r'provider:',
            r'model:',
            r'logging to',
            r'context:',
            r'message:',
            r'Goose is running',
            r'Enter your instructions',
            r'Closing session\. Recorded to',  # Filter out session closing messages
            r'Session recorded to',            # Alternative session message format
            r'\.jsonl\.$'                      # Lines ending with .jsonl
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches any skip pattern
            should_skip = any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns)
            if should_skip:
                continue
            
            # Skip action text (lines that start and end with *)
            if line.startswith('*') and line.endswith('*'):
                continue
                
            # This looks like actual AI response content
            if line and len(line) > 5:
                response_lines.append(line)
        
        response = ' '.join(response_lines) if response_lines else ""
        print(f"🔧 [BaseAINPC] Extracted response: '{response}'")
        return response
    
    def _clean_response(self, response: str) -> str:
        """Clean up AI response to be more NPC-like"""
        if not response or len(response.strip()) < 1:
            return ""
        
        # Remove common artifacts
        response = response.strip()
        response = re.sub(r'\*.*?\*', '', response)  # Remove action text
        response = re.sub(r'\[.*?\]', '', response)  # Remove bracketed text
        
        # Fix character encoding issues that cause broken display in UI
        # Replace various dash characters with regular hyphens
        response = response.replace('–', '-')  # en dash
        response = response.replace('—', '-')  # em dash
        response = response.replace('−', '-')  # minus sign
        response = response.replace(''', "'")  # left single quote
        response = response.replace(''', "'")  # right single quote
        response = response.replace('"', '"')  # left double quote
        response = response.replace('"', '"')  # right double quote
        response = response.replace('…', '...')  # ellipsis
        
        # Remove AI-like phrases
        ai_phrases = [
            "As an AI", "I'm an AI", "I cannot", "I don't have the ability",
            "I'm not able to", "I can't actually", "In this game", "As your"
        ]
        
        for phrase in ai_phrases:
            response = re.sub(phrase, "", response, flags=re.IGNORECASE)
        
        response = response.strip()
        
        # Ensure it's not empty after cleaning
        if not response or len(response) < 1:
            return ""
        
        # Ensure it ends with punctuation (but don't require it for very short responses)
        if len(response) > 3 and not response.endswith(('.', '!', '?')):
            response += "."
        
        return response
    
    def _fallback_response(self, message: str) -> str:
        """Generate intelligent fallback response based on NPC type and message"""
        message_lower = message.lower()
        
        # Get NPC-specific responses
        npc_responses = self._get_npc_specific_responses()
        
        # Check for specific keywords
        for keyword, response in npc_responses.items():
            if keyword in message_lower and keyword != "default":
                return response
        
        # Use default response for this NPC type
        return npc_responses.get("default", f"*{self.name} nods thoughtfully*")
    
    def _get_npc_specific_responses(self) -> Dict[str, str]:
        """Override in subclasses to provide NPC-specific fallback responses"""
        return {
            "hello": f"Greetings, traveler. I am {self.name}.",
            "who": f"I am {self.name}, at your service.",
            "help": f"How may I assist you?",
            "bye": f"Farewell, and safe travels.",
            "default": f"*{self.name} nods thoughtfully*"
        }
    
    def interact(self, player):
        """Handle interaction with the player"""
        print(f"🔧 [BaseAINPC] interact() called for {self.name}")
        print(f"🔧 [BaseAINPC] AI enabled: {self.ai_enabled}")
        
        # Play interaction sound
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        if audio:
            audio.play_ui_sound("button_click")
        
        # If AI is enabled, start AI chat
        if self.ai_enabled:
            self.start_ai_chat(player)
        else:
            # Fall back to regular dialog
            self._start_regular_dialog(player)
    
    def start_ai_chat(self, player):
        """Start AI conversation with the player"""
        print(f"🔧 [BaseAINPC] start_ai_chat for {self.name}")
        
        # Import and create chat window
        try:
            from ..ui.ai_chat_window import AIChatWindow
            chat_window = AIChatWindow(self.asset_loader)
            chat_window.is_active = True
            chat_window.npc_reference = self  # Store reference to this NPC
            
            # Store chat window in player for rendering
            if hasattr(player, 'current_ai_chat'):
                player.current_ai_chat = chat_window
                print(f"✅ [BaseAINPC] AI chat started for {self.name}")
                
                # Send initial greeting
                context = self._get_game_context(player)
                greeting = self.send_ai_message("Hello", context)
                chat_window.add_message(self.name, greeting)
            else:
                print(f"❌ [BaseAINPC] Player has no current_ai_chat attribute")
                
        except ImportError as e:
            print(f"❌ [BaseAINPC] Could not import AIChatWindow: {e}")
            self._start_regular_dialog(player)
    
    def _start_regular_dialog(self, player):
        """Start regular dialog as fallback"""
        try:
            from ..ui.dialogue import DialogueWindow
            dialogue_window = DialogueWindow(self.name, self.dialog, self.asset_loader)
            
            if hasattr(player, 'current_dialogue'):
                player.current_dialogue = dialogue_window
        except ImportError:
            pass
    
    def _get_game_context(self, player) -> str:
        """Get current game context for AI"""
        context_parts = []
        
        # Add NPC ID for MCP tools
        context_parts.append(f"NPC ID: {self.npc_id}")
        
        if player:
            context_parts.append(f"Player Level: {getattr(player, 'level', 1)}")
            context_parts.append(f"Player HP: {getattr(player, 'hp', 100)}/{getattr(player, 'max_hp', 100)}")
            
            # Player location
            player_x = getattr(player, 'x', 0)
            player_y = getattr(player, 'y', 0)
            context_parts.append(f"Player Position: ({player_x}, {player_y})")
            
            # Inventory info
            if hasattr(player, 'inventory') and player.inventory:
                if hasattr(player.inventory, 'items'):
                    item_count = len(player.inventory.items)
                elif hasattr(player.inventory, '__len__'):
                    item_count = len(player.inventory)
                else:
                    item_count = 0
                    
                if item_count > 0:
                    context_parts.append(f"Player has {item_count} items in inventory")
        
        return " | ".join(context_parts) if context_parts else f"NPC ID: {self.npc_id} | Player is exploring the world"
    
    def create_npc_sprite(self):
        """Create NPC sprite - override in subclasses for specific appearances"""
        size = 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            sprite_name = self._get_sprite_name()
            if sprite_name:
                npc_image = self.asset_loader.get_image(sprite_name)
                if npc_image:
                    self.sprite = pygame.transform.scale(npc_image, (size, size))
                    self.direction_sprites = [
                        self.sprite,  # Down (0)
                        pygame.transform.flip(self.sprite, True, False),  # Left (1)
                        self.sprite,  # Up (2)
                        self.sprite   # Right (3)
                    ]
                    return
        
        # Fallback to generated sprite
        self._create_generated_sprite(size)
    
    def _get_sprite_name(self) -> Optional[str]:
        """Override in subclasses to specify sprite name"""
        return None
    
    def _create_generated_sprite(self, size: int):
        """Create a generated sprite - override in subclasses for specific styles"""
        import pygame
        
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Default NPC appearance
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, (0, 191, 255), center, size // 3)
        pygame.draw.circle(self.sprite, (255, 255, 255), center, size // 4)
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)
        
        # Create direction sprites
        self.direction_sprites = [
            self.sprite,  # Down (0)
            pygame.transform.flip(self.sprite, True, False),  # Left (1)
            self.sprite,  # Up (2)
            self.sprite   # Right (3)
        ]
    
    def get_save_data(self):
        """Get data for saving"""
        # Clean up session before saving
        self.cleanup_session()
        
        data = super().get_save_data()
        data.update({
            "dialog": self.dialog,
            "ai_enabled": self.ai_enabled,
            "conversation_history": self.conversation_history,
            "use_fallback": self.use_fallback,
            "first_interaction": self.first_interaction
        })
        return data
    
    def __del__(self):
        """Cleanup when NPC is destroyed"""
        self.cleanup_session()
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create NPC from save data"""
        npc = cls(data["x"], data["y"], asset_loader=asset_loader)
        npc.dialog = data.get("dialog", npc.dialog)
        npc.ai_enabled = data.get("ai_enabled", npc.ai_enabled)
        npc.conversation_history = data.get("conversation_history", [])
        npc.use_fallback = data.get("use_fallback", False)
        npc.first_interaction = data.get("first_interaction", True)
        return npc