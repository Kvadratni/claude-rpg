# Refactored NPC Design Proposal

## Overview
This document outlines a complete refactor of the NPC system to be more centralized and object-oriented, where each NPC instance has its recipe directly attached and the parent class handles all AI communication.

## Current Problems
1. **External Recipe Loading**: Recipe manager loads recipes separately from NPC instances
2. **Complex Integration**: Multiple classes handle AI communication (GooseRecipeIntegration, RecipeBasedGooseIntegration, etc.)
3. **Scattered Logic**: AI logic spread across multiple files and classes
4. **Name Mapping**: Complex mapping system between NPC names and recipe files

## Proposed Solution

### 1. Recipe-Embedded NPCs
Each NPC instance will have its recipe directly embedded as a class attribute:

```python
class VillageElderNPC(NPC):
    recipe = {
        "version": "1.0.0",
        "title": "Village Elder NPC",
        "prompt": """
        You are a wise Village Elder in a fantasy RPG world.
        You are the keeper of ancient knowledge and village history.
        You give quests and advice to adventurers.
        
        CURRENT CONTEXT: {{ context }}
        PLAYER SAYS: "{{ message }}"
        
        Respond as the Village Elder in 1-2 sentences.
        """,
        "parameters": [
            {"key": "message", "input_type": "text", "requirement": "user_prompt"},
            {"key": "context", "input_type": "text", "requirement": "optional", "default": "Player is in the village"}
        ]
    }
```

### 2. Centralized AI Communication in Parent Class
The base NPC class will handle all AI communication:

```python
class NPC(BaseEntity):
    recipe = None  # Override in subclasses
    
    def __init__(self, x, y, name, dialog=None, **kwargs):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.conversation_history = []
        self.session_name = f"npc_{self.__class__.__name__.lower()}"
        self.ai_enabled = bool(self.recipe)  # Auto-enable if recipe exists
        
    def send_ai_message(self, message: str, context: str = "") -> str:
        """Send message to AI using embedded recipe"""
        if not self.recipe:
            return self._fallback_response(message)
            
        try:
            # Use the embedded recipe to communicate with Goose CLI
            response = self._execute_recipe(message, context)
            self.conversation_history.append({"player": message, "npc": response})
            return response
        except Exception as e:
            print(f"AI Error for {self.name}: {e}")
            return self._fallback_response(message)
    
    def _execute_recipe(self, message: str, context: str) -> str:
        """Execute the embedded recipe with Goose CLI"""
        # Implementation details for subprocess call
        pass
    
    def _fallback_response(self, message: str) -> str:
        """Intelligent fallback based on NPC type"""
        # Implementation for local responses
        pass
```

### 3. Specific NPC Classes
Each NPC type becomes a simple class with its recipe embedded:

```python
class VillageElderNPC(NPC):
    recipe = {
        # Recipe definition here
    }
    
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, "Village Elder", 
                        dialog=["Greetings, young adventurer."], **kwargs)

class MasterMerchantNPC(NPC):
    recipe = {
        # Recipe definition here
    }
    
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, "Master Merchant", 
                        dialog=["Welcome to my shop!"], **kwargs)
```

### 4. Simplified Game Integration
Game code becomes much simpler:

```python
# Create NPCs directly with AI built-in
village_elder = VillageElderNPC(x=10, y=15)
master_merchant = MasterMerchantNPC(x=20, y=25)

# Interact with NPC - AI is automatic
response = village_elder.send_ai_message("Hello, who are you?", game_context)
```

## Benefits

### 1. **Centralized Logic**
- All AI communication logic in the parent NPC class
- No external recipe managers or integration classes needed
- Single point of control for AI behavior

### 2. **Simplified Architecture**
- Each NPC is self-contained with its own recipe
- No complex name-to-recipe mapping systems
- Direct instantiation of specific NPC types

### 3. **Better Encapsulation**
- Recipe is part of the NPC class definition
- AI capabilities are intrinsic to the NPC
- Clear inheritance hierarchy

### 4. **Easier Maintenance**
- Recipe changes only require updating the class definition
- No separate YAML files to manage
- Version control tracks recipe changes with code changes

### 5. **Type Safety**
- Each NPC type is a distinct class
- IDE support for NPC-specific methods and properties
- Clear class hierarchy

## Implementation Plan

### Phase 1: Create New NPC Base Class
1. Create new `BaseAINPC` class with embedded recipe support
2. Implement `send_ai_message()` method with Goose CLI integration
3. Add fallback response system
4. Add conversation history management

### Phase 2: Create Specific NPC Classes
1. Convert existing NPCs to new class structure:
   - `VillageElderNPC`
   - `MasterMerchantNPC`
   - `GuardCaptainNPC`
   - `TavernKeeperNPC`
   - `BlacksmithNPC`
   - `HealerNPC`

### Phase 3: Update Game Integration
1. Update level generation to use new NPC classes
2. Update UI to work with new NPC structure
3. Remove old recipe manager and integration classes
4. Update save/load system for new NPC structure

### Phase 4: Testing and Cleanup
1. Test each NPC type individually
2. Test conversation continuity
3. Remove deprecated files and classes
4. Update documentation

## File Structure Changes

### New Files
```
src/entities/ai_npc_base.py          # New base class for AI NPCs
src/entities/npcs/village_elder.py   # VillageElderNPC class
src/entities/npcs/master_merchant.py # MasterMerchantNPC class
src/entities/npcs/guard_captain.py   # GuardCaptainNPC class
src/entities/npcs/tavern_keeper.py   # TavernKeeperNPC class
src/entities/npcs/blacksmith.py      # BlacksmithNPC class
src/entities/npcs/healer.py          # HealerNPC class
```

### Deprecated Files
```
src/recipe_manager.py                # No longer needed
src/ai_integration.py                # Simplified and moved to base class
recipes/*.yaml                       # Recipes now embedded in classes
```

### Modified Files
```
src/entities/npc.py                  # Updated to use new base class or deprecated
src/level/entity_manager.py          # Updated to use new NPC classes
src/game.py                          # Updated AI event handling
```

## Example Implementation

Here's a concrete example of how the new system would work:

```python
# src/entities/ai_npc_base.py
class BaseAINPC(BaseEntity):
    recipe = None
    
    def __init__(self, x, y, name, dialog=None, **kwargs):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.conversation_history = []
        self.session_name = f"npc_{self.__class__.__name__.lower()}"
        self.ai_enabled = bool(self.recipe)
        
    def send_ai_message(self, message: str, context: str = "") -> str:
        if not self.recipe:
            return self._fallback_response(message)
        
        # Execute recipe with Goose CLI
        prompt = self.recipe["prompt"].replace("{{ message }}", message)
        prompt = prompt.replace("{{ context }}", context)
        
        response = self._execute_goose_command(prompt)
        self.conversation_history.append({"player": message, "npc": response})
        return response

# src/entities/npcs/village_elder.py
class VillageElderNPC(BaseAINPC):
    recipe = {
        "version": "1.0.0",
        "title": "Village Elder NPC",
        "prompt": """You are a wise Village Elder in a fantasy RPG world.
        
CURRENT CONTEXT: {{ context }}
PLAYER SAYS: "{{ message }}"

Respond as the Village Elder in 1-2 sentences."""
    }
    
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, "Village Elder", 
                        dialog=["Greetings, young adventurer."], **kwargs)

# Usage in game
village_elder = VillageElderNPC(x=10, y=15)
response = village_elder.send_ai_message("Hello", "Player is in village center")
```

This refactor eliminates the complexity of external recipe management while making the system more maintainable and easier to understand.