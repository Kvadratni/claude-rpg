# Model Context Protocol (MCP) Integration for RPG Game

## 🎯 **Overview**

This implementation adds a sophisticated Model Context Protocol (MCP) server that allows AI NPCs to take real actions within the game world. NPCs can now:

- **Open shop interfaces** when players want to trade
- **Create and assign quests** dynamically based on conversation
- **Give items** directly to players
- **Trigger game events** and cutscenes
- **Spawn entities** (enemies, items, NPCs)
- **Query game state** (player stats, world info, relationships)

## 🏗️ **Architecture**

### **Components:**

1. **MCP Server** (`mcp_game_server.py`) - Standalone server providing game interaction tools
2. **MCP Integration** (`src/mcp_integration.py`) - Game-side handler for processing MCP actions
3. **Updated Recipes** - AI recipes now include MCP server as extension
4. **Enhanced AI NPCs** - NPCs provide context and IDs for MCP tools

### **Communication Flow:**
```
AI NPC ←→ Goose CLI ←→ MCP Server ←→ Action Queue ←→ Game Integration ←→ Game World
```

## 🛠️ **Available MCP Tools**

### **Core Game Actions:**

#### **`open_shop`**
Opens trading interface with specific NPC
```json
{
  "npc_id": "master_merchant_123",
  "shop_type": "general"
}
```

#### **`create_quest`**
Creates and assigns quests to the player
```json
{
  "title": "Gather Forest Herbs",
  "description": "Collect 5 healing herbs from the dark forest",
  "type": "fetch",
  "objectives": ["Collect Healing Herbs x5"],
  "rewards": {"gold": 100, "experience": 200},
  "npc_id": "village_elder_456"
}
```

#### **`give_item`**
Gives items directly to the player
```json
{
  "item_id": "health_potion",
  "item_name": "Health Potion",
  "quantity": 3,
  "npc_id": "healer_789"
}
```

### **Information Queries:**

#### **`get_player_info`**
Retrieves player statistics and status
```json
{
  "type": "general|stats|inventory|equipment|quests"
}
```

#### **`get_world_info`**
Gets information about the game world
```json
{
  "type": "general|locations|npcs|quests",
  "location": "village"
}
```

#### **`get_npc_relationship`**
Checks relationship status between NPCs and player
```json
{
  "npc_id": "village_elder_456",
  "target_id": "player"
}
```

### **Advanced Actions:**

#### **`trigger_event`**
Triggers special game events or cutscenes
```json
{
  "event_type": "cutscene_intro",
  "event_data": {"scene": "village_celebration"},
  "npc_id": "village_elder_456"
}
```

#### **`spawn_entity`**
Spawns entities in the game world
```json
{
  "entity_type": "enemy",
  "entity_id": "goblin_scout",
  "location": "forest_entrance",
  "properties": {"level": 3, "aggressive": true}
}
```

## 🔗 **MCP Resources**

NPCs can also access structured game data through MCP resources:

- **`game://world-state`** - Current world state and conditions
- **`game://player-data`** - Player stats, inventory, and progress
- **`game://quest-templates`** - Available quest types and templates
- **`game://item-database`** - Available items and their properties

## 🎮 **Integration with Game**

### **Game Loop Integration:**
```python
# In main game loop
mcp_handler = MCPActionHandler(game_instance)

# Update world data for MCP server
mcp_handler.update_world_data(player, level, npcs)
mcp_handler.update_game_state(player)

# Process pending MCP actions
mcp_handler.process_pending_actions(player, level)
```

### **Action Processing:**
The MCP integration processes actions through a queue system:

1. **AI NPC uses MCP tool** → Action queued in `mcp_actions_queue.json`
2. **Game loop processes queue** → Actions executed in game world
3. **Results reflected in game** → UI updates, quest notifications, etc.

## 📝 **Recipe Updates**

### **Extension Configuration:**
```yaml
extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 30
  bundled: true
- type: stdio
  name: rpg-game-server
  display_name: RPG Game Actions
  timeout: 30
  bundled: false
  cmd: python3
  args:
    - mcp_game_server.py
```

### **Enhanced Prompts:**
NPCs now have detailed information about available tools and how to use them naturally in conversation.

## 🚀 **Usage Examples**

### **Quest Creation Scenario:**
```
Player: "Do you have any work for me?"
Village Elder: *uses get_player_info to check level*
Village Elder: *uses create_quest to generate appropriate quest*
Village Elder: "Indeed! I need someone to gather herbs from the forest. The reward will be 100 gold."
```

### **Trading Scenario:**
```
Player: "I'd like to buy some equipment."
Master Merchant: *uses get_player_info to check gold*
Master Merchant: *uses open_shop to start trading interface*
Master Merchant: "Excellent! Let me show you my finest wares."
```

### **Dynamic Item Giving:**
```
Player: "I'm running low on health potions."
Healer: *uses get_player_info to check inventory*
Healer: *uses give_item to provide health potions*
Healer: "Here, take these potions. Stay safe out there!"
```

## 🔧 **Technical Implementation**

### **File Structure:**
```
├── mcp_game_server.py          # MCP server implementation
├── src/mcp_integration.py      # Game-side MCP handler
├── recipes/                    # Updated AI recipes with MCP
│   ├── village_elder.yaml
│   ├── master_merchant.yaml
│   └── ...
└── mcp_actions_queue.json      # Action queue (created at runtime)
```

### **Dependencies:**
- `mcp>=1.0.0` - Model Context Protocol library
- `asyncio` - Async support for MCP server
- `json` - Data serialization
- `pathlib` - File path handling

## 🎯 **Benefits**

1. **Dynamic Interactions** - NPCs can take real actions based on conversation
2. **Contextual Awareness** - NPCs know about player state and world conditions
3. **Emergent Gameplay** - Quests and events can be generated dynamically
4. **Seamless Integration** - Actions feel natural and immediate
5. **Extensible System** - Easy to add new tools and capabilities

## 🔮 **Future Enhancements**

- **Relationship System** - NPCs track and respond to player relationships
- **Dynamic Economy** - NPCs adjust prices based on supply/demand
- **Weather/Time Integration** - NPCs react to environmental conditions
- **Cross-NPC Communication** - NPCs can coordinate actions and share information
- **Advanced AI Planning** - NPCs can plan multi-step interactions and quests

This MCP integration transforms static NPCs into dynamic, intelligent agents that can truly interact with and modify the game world in response to player conversations!