# AI NPC Recipes

This directory contains Goose recipe files that power the AI NPCs in the RPG game. Each recipe defines a specific NPC personality, knowledge base, and response patterns.

## Available Recipes

### Core NPCs

- **`village_elder.yaml`** - Wise village leader and guide for adventurers
- **`master_merchant.yaml`** - Skilled trader and shopkeeper  
- **`guard_captain.yaml`** - Village protector and security expert
- **`tavern_keeper.yaml`** - Friendly tavern owner and information source
- **`blacksmith.yaml`** - Village craftsman and weapon/armor expert
- **`healer.yaml`** - Compassionate medical expert and potion maker

### Specialized NPCs

- **`innkeeper.yaml`** - Welcoming host and provider of rest
- **`master_smith.yaml`** - Legendary craftsman with advanced skills
- **`forest_ranger.yaml`** - Wilderness expert and nature guardian
- **`master_herbalist.yaml`** - Expert in plants, potions, and natural magic
- **`caravan_master.yaml`** - Experienced trader and travel coordinator

## Recipe Structure

Each recipe follows the standard Goose recipe format:

```yaml
version: 1.0.0
title: [NPC Type] NPC
author:
  contact: AI NPC System
description: Brief description of the NPC's role
instructions: Instructions for the AI assistant
extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 30
  bundled: true
prompt: |
  Detailed character description and behavior guidelines
  
  CURRENT CONTEXT: {{ context }}
  PLAYER SAYS: "{{ message }}"
  
  Respond as [NPC Type] in character.

parameters:
  - key: message
    input_type: string
    requirement: user_prompt
    description: The player's message to the NPC
  - key: context
    input_type: string
    requirement: optional
    description: Current game context and situation
    default: "Player is in the village"
```

## Testing Recipes

### Manual Testing
Test individual recipes using the Goose CLI:

```bash
goose run --recipe recipes/village_elder.yaml \
  --params "message=Hello, who are you?" \
  --params "context=Player is in the village center" \
  --no-session
```

### Automated Testing
Run the test script to verify all recipes:

```bash
python test_recipes.py
```

## Usage in Game

The recipes are automatically loaded by the `RecipeBasedGooseIntegration` class in `src/recipe_manager.py`. The system:

1. Maps NPC names to recipe files
2. Loads the appropriate recipe when an NPC conversation starts
3. Passes player messages and game context as parameters
4. Returns the AI-generated response in character

## Adding New Recipes

1. Create a new `.yaml` file in this directory
2. Follow the standard recipe structure above
3. Define the NPC's personality, knowledge, and response style
4. Add the NPC name mapping in `src/recipe_manager.py`
5. Test the recipe manually and with the test script

## Character Guidelines

Each recipe should define:

- **Role Characteristics**: What the NPC does and their position in the world
- **Personality Traits**: How they behave and interact with others
- **Knowledge Areas**: What they know about and can discuss
- **Response Guidelines**: Natural conversation style and behavior rules
- **Sample Interactions**: Examples of typical conversations

### Language Style
- Use **natural fantasy English** - avoid overly formal or archaic language
- Keep responses conversational and engaging
- Stay true to each character's personality and role
- Maintain fantasy setting without being pretentious

## Performance Notes

- Recipes typically respond in 1-3 seconds
- The system includes fallback mechanisms for reliability
- Context parameters provide game state awareness
- Conversation history is maintained during chat sessions

## Development Tips

- Keep responses to 1-2 sentences for better gameplay flow
- Use medieval fantasy language appropriate to the setting
- Include specific knowledge areas for each NPC type
- Test recipes with various player input types
- Monitor console output for debugging information