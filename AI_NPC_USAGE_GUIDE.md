# AI NPC Usage Guide

## Overview
The game now includes AI-powered NPCs that can have dynamic conversations with the player using Goose recipes and GPT-4o-mini (the fastest model from our benchmark).

## AI-Enabled NPCs
The following NPCs have AI capabilities powered by dedicated Goose recipes:
- **Village Elder** - Wise village leader, gives quests and advice
- **Master Merchant** - Shopkeeper with knowledge of goods and trade  
- **Guard Captain** - Village protector, knows about local threats
- **Tavern Keeper** - Friendly innkeeper and information broker
- **Blacksmith** - Master craftsman and weapon/armor expert
- **Healer** - Compassionate medical expert and potion maker

## How It Works

### Goose Recipe System
Each NPC type has a dedicated YAML recipe file in the `recipes/` directory that defines:
- **Character personality and traits**
- **Knowledge areas and expertise**
- **Response guidelines and behavior**
- **Context awareness parameters**

The recipes use Goose's parameter system to inject:
- Player messages (`{{ message }}`)
- Game context (`{{ context }}`)
- Dynamic situational information

### Session Management
The system uses Goose CLI's `--interactive` and `--resume` flags to maintain conversation continuity:
- **`--interactive`**: Enables interactive mode for real-time conversation flow
- **`--resume`**: Maintains session state between interactions, preserving conversation history
- **Session naming**: Each NPC maintains its own session (e.g., `npc_village_elder`) for persistent memory

This ensures that NPCs remember previous parts of the conversation and can reference earlier topics naturally.

### Recipe Files Structure
```yaml
version: 1.0.0
title: Village Elder NPC
author:
  contact: AI NPC System
description: AI recipe for Village Elder NPC - wise keeper of ancient knowledge
instructions: You are an AI assistant that will roleplay as a Village Elder NPC
extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 30
  bundled: true
prompt: |
  [Detailed character description and guidelines]
  
  CURRENT CONTEXT: {{ context }}
  PLAYER SAYS: "{{ message }}"
  
  Respond as the [NPC Type] to the player's message.

parameters:
  - key: message
    input_type: text
    requirement: user_prompt
    description: The player's message to the NPC
  - key: context
    input_type: text
    requirement: optional
    description: Current game context and situation
    default: "Player is in the village"
```

### First Interaction
1. When you first talk to an AI-enabled NPC, the system will:
   - Display: "🤖 [NPC Name] is now AI-powered!" 
   - Load the appropriate Goose recipe for that NPC type
   - Enable AI chat capabilities for that NPC
   - Open an AI chat window instead of the regular dialog

### AI Chat Interface
- **Chat Window**: A centered overlay with conversation history
- **Input Field**: Type your message at the bottom
- **Controls**:
  - Type your message and press **Enter** to send
  - Press **Escape** to close the chat window

### Multi-Tier Fallback System
1. **Primary**: Goose recipe execution with GPT-4o-mini
2. **Secondary**: Direct Goose CLI integration (legacy mode)
3. **Tertiary**: Intelligent local fallback responses tailored to each NPC

The system gracefully handles:
- Network issues or AI service interruptions
- Recipe loading failures
- Goose CLI unavailability

## Available Recipes

### Village Elder (`village_elder.yaml`)
- Wise keeper of ancient knowledge and village history
- Quest giver with knowledge of local threats and legends
- Speaks with formal, archaic language and authority

### Master Merchant (`master_merchant.yaml`)
- Skilled trader in weapons, armor, potions, and rare items
- Business-minded but fair, with knowledge of distant lands
- Enthusiastic about merchandise quality and good deals

### Guard Captain (`guard_captain.yaml`)
- Village security leader with military training
- Authoritative but fair, focused on protection and order
- Knowledgeable about local dangers and patrol routes

### Tavern Keeper (`tavern_keeper.yaml`)
- Friendly innkeeper and social hub of the village
- Well-informed about local gossip, news, and rumors
- Warm and hospitable, enjoys meeting travelers

### Blacksmith (`blacksmith.yaml`)
- Master craftsman specializing in weapons and armor
- Proud of craftsmanship, knowledgeable about metallurgy
- Practical and hardworking, focused on quality equipment

### Healer (`healer.yaml`)
- Compassionate medical expert and herbalist
- Skilled in healing magic and natural remedies
- Gentle and caring, concerned about wellbeing of others

## Example Conversations

### Village Elder
- "Hello, who are you?" → Wise introduction with ancient wisdom
- "Do you have any quests?" → Information about dark forces and ruins
- "Tell me about this place" → Village history and founding stories

### Master Merchant  
- "What do you sell?" → Enthusiastic description of quality goods
- "What's the best weapon?" → Expert recommendations for your needs
- "Any rare items?" → Details about exotic wares from distant lands

### Guard Captain
- "Is it safe here?" → Authoritative assessment of village security
- "Any dangers nearby?" → Military briefing on local threats
- "Can you help me?" → Professional offers of protection and guidance

## Technical Details

### Recipe Execution Flow
1. Player sends message to NPC
2. System identifies NPC type and loads corresponding recipe
3. Game context is gathered (player stats, location, inventory)
4. Goose CLI executes recipe with message and context parameters using `--interactive` and `--resume` flags for session continuity
5. AI response is parsed, cleaned, and displayed
6. Conversation history is maintained for context through persistent sessions

### Model Selection
- **Primary**: GPT-4o-mini via Goose recipes (fastest response time: ~1.9 seconds)
- **Secondary**: Direct GPT-4o-mini integration (legacy mode)
- **Fallback**: Local intelligent responses when AI is unavailable

### Performance
- Response times typically under 3 seconds with recipes
- Graceful degradation through multiple fallback layers
- Conversation history maintained during chat session
- Recipe caching for improved performance

### Context Awareness
The AI knows through context parameters:
- Your current location in the game
- Your player level and health
- Items in your inventory
- Nearby NPCs and enemies
- The NPC's specific role and personality
- Previous conversation history

## Adding New NPC Recipes

To create a new NPC recipe:

1. **Create Recipe File**: Add a new `.yaml` file in the `recipes/` directory
2. **Define Character**: Set personality traits, knowledge areas, and response guidelines
3. **Add Parameters**: Include `message` and `context` parameters
4. **Update Mapping**: Add NPC name to recipe mapping in `recipe_manager.py`
5. **Test Integration**: Verify the recipe loads and executes properly

Example minimal recipe structure:
```yaml
version: 1.0.0
title: [NPC Type] NPC
description: AI recipe for [NPC Type] - [brief description]
prompt: |
  You are [character description].
  
  CURRENT CONTEXT: {{ context }}
  PLAYER SAYS: "{{ message }}"
  
  Respond as [NPC Type] in 1-2 sentences.

parameters:
  - key: message
    input_type: text
    requirement: user_prompt
  - key: context
    input_type: text
    requirement: optional
    default: "Player is in the village"
```

## Tips for Best Experience
1. **Be specific** - Ask detailed questions for better responses
2. **Stay in character** - The NPCs respond as medieval fantasy characters
3. **Use the context** - Ask about the game world, quests, and locations
4. **Try different topics** - Each NPC has unique knowledge and personality
5. **Experiment with recipes** - Modify recipe files to customize NPC behavior

## Troubleshooting
- **Recipe not loading**: Check YAML syntax and file permissions
- **Generic responses**: System may be using fallback mode, check Goose CLI availability
- **Chat window issues**: Press Escape key or restart interaction
- **Performance issues**: Check network connection and Goose CLI installation
- **Recipe errors**: Check console output for detailed error messages

## Development Notes
- Recipe files are hot-reloadable during development
- Console output shows which system (recipe/direct/fallback) is being used
- Each NPC conversation logs its execution path for debugging
- Recipe parameters can be extended for more complex interactions

Enjoy your conversations with the AI-powered NPCs using Goose recipes!
EOF 2>&1
