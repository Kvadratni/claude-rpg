# AI NPC Implementation Guide

## Overview
This document outlines the essential components needed to implement AI-powered NPCs in the Pygame RPG using Goose CLI recipes. The implementation allows players to have dynamic conversations with NPCs powered by AI.

## Core Architecture

### 1. AI Integration Framework (`src/ai_integration.py`)
The foundation of the AI NPC system consists of three main classes:

#### GooseRecipeIntegration
- Handles communication with Goose CLI via subprocess
- Manages recipe execution and response parsing
- Filters out system messages to keep chat clean
- Key methods: `send_message()`, `_parse_response()`

#### AIChatWindow
- Renders the chat interface overlay
- Manages chat history and input buffer
- Handles text rendering and UI layout
- Key methods: `render()`, `add_message()`, `handle_input()`

#### GameContext
- Provides AI with current game state information
- Includes player stats, location, inventory, nearby entities
- Formats context for AI understanding
- Key method: `get_context()`

### 2. NPC Integration (`src/entities/npc.py`)
Direct integration approach (not mixin):
```python
class NPC(BaseEntity):
    def __init__(self, ...):
        # ... existing init ...
        self.ai_integration = None
        self.chat_window = None
        self.is_ai_enabled = False
    
    def enable_ai(self, player_ref, game_context):
        """Enable AI for this NPC"""
        self.ai_integration = GooseRecipeIntegration(self.name)
        self.chat_window = AIChatWindow()
        self.player_ref = player_ref
        self.game_context = game_context
        self.is_ai_enabled = True
    
    def start_ai_chat(self):
        """Start AI conversation"""
        if self.is_ai_enabled and self.chat_window:
            self.chat_window.is_active = True
            # Send initial context to AI
            context = self.game_context.get_context()
            self.ai_integration.send_message(f"Context: {context}")
```

### 3. Game-Level Event Handling (`src/game.py`)
**CRITICAL**: AI chat events must be handled at the game level BEFORE other event processing:

```python
def handle_events(self):
    for event in pygame.event.get():
        # PRIORITY 1: Handle AI chat events first
        if hasattr(self, 'current_level') and self.current_level:
            ai_handled = self._handle_ai_chat_events(event)
            if ai_handled:
                continue  # Skip other event processing
        
        # PRIORITY 2: Other game events (inventory, movement, etc.)
        # ... rest of event handling ...

def _handle_ai_chat_events(self, event):
    """Handle AI chat events with highest priority"""
    # Find active AI chat window
    active_chat = None
    for entity in self.current_level.entity_manager.npcs:
        if (hasattr(entity, 'chat_window') and 
            entity.chat_window and 
            entity.chat_window.is_active):
            active_chat = entity
            break
    
    if not active_chat:
        return False
    
    # Handle keyboard input for chat
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            active_chat.chat_window.is_active = False
        elif event.key == pygame.K_RETURN:
            # Send message to AI
            message = active_chat.chat_window.input_buffer
            if message.strip():
                active_chat.chat_window.add_message(f"You: {message}")
                response = active_chat.ai_integration.send_message(message)
                active_chat.chat_window.add_message(f"{active_chat.name}: {response}")
                active_chat.chat_window.input_buffer = ""
        elif event.key == pygame.K_BACKSPACE:
            active_chat.chat_window.input_buffer = active_chat.chat_window.input_buffer[:-1]
        else:
            # Add character to input buffer
            if event.unicode.isprintable():
                active_chat.chat_window.input_buffer += event.unicode
        return True
    
    return False
```

### 4. Goose Recipe (`goose_recipe.toml`)
```toml
[recipe]
name = "rpg_npc_chat"
description = "AI-powered NPC for RPG conversations"

[recipe.prompt]
instructions = """
You are {npc_name}, an NPC in a fantasy RPG world. 

Character Guidelines:
- Stay in character as {npc_name}
- Respond naturally to player questions and comments
- Reference the current game context when relevant
- Keep responses concise (1-3 sentences typically)
- Be helpful but maintain your character's personality

Current Context: The player is interacting with you in the game world.
"""
```

### 5. Test Environment (`src/ai_test_world.py`)
Create a simplified test world that bypasses complex template systems:
```python
class AITestWorld:
    def __init__(self, game):
        self.game = game
        # Simple 20x20 world with basic tiles
        self.world_map = [['grass' for _ in range(20)] for _ in range(20)]
        
        # Create test NPC with AI enabled
        test_npc = NPC(x=5, y=5, npc_type="villager", name="TestBot")
        game_context = GameContext(game.player, self)
        test_npc.enable_ai(game.player, game_context)
        
        self.npcs = [test_npc]
```

## Key Implementation Points

### Event Handling Priority
**MOST IMPORTANT**: The main issue we encountered was keyboard input not reaching the AI chat window. This happens because:

1. Game events are processed in order
2. If inventory key ('I') is handled first, it consumes the event
3. AI chat never receives the keyboard input

**Solution**: Handle AI chat events at the game level with highest priority, before any other game systems.

### Testing Approach
1. Create a simple test world that bypasses complex map generation
2. Add a single AI-enabled NPC
3. Test keyboard input capture first
4. Verify AI communication works
5. Then integrate into main game systems

### Common Pitfalls
1. **Event Handling Order**: Always handle AI events first
2. **Message Filtering**: Filter out system messages from AI responses
3. **Context Management**: Provide relevant game context to AI
4. **UI Rendering**: Ensure chat window renders on top of game elements

## Essential Files to Modify

### New Files:
- `src/ai_integration.py` - Core AI framework
- `src/ai_test_world.py` - Test environment
- `goose_recipe.toml` - AI recipe configuration

### Modified Files:
- `src/game.py` - Add game-level AI event handling
- `src/entities/npc.py` - Add AI integration to NPCs
- `src/level/level_renderer.py` - Render AI chat windows

## Launch Script Reminder
**ALWAYS TEST WITH**: `./launch_game.sh` or `uv run goose-rpg`

Many debugging issues were caused by running the game incorrectly, leading to import errors and missing dependencies. The launch script ensures proper environment setup and points to the correct project directory.

## Minimal Implementation Steps
1. Create `src/ai_integration.py` with the three core classes
2. Add AI integration methods to `src/entities/npc.py`
3. Add game-level AI event handling to `src/game.py`
4. Create `goose_recipe.toml` in project root
5. Create test world in `src/ai_test_world.py`
6. Test with launch script

This approach avoids the complexity of mixins, template systems, and other architectural complications while providing a solid foundation for AI NPCs.