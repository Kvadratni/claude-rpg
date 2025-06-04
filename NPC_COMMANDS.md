# 🎮 **Goose RPG NPC Commands Reference**

## 🚀 **Quick Start**

### **1. Start the Game**
```bash
cd /Users/mnovich/Development/claude-rpg
./launch_game.sh
```

### **2. Run AI NPCs with Goose**

## 📋 **Available NPCs and Commands**

### **🔨 Blacksmith**
```bash
goose run --recipe recipes/blacksmith.yaml \
  --params context="You are in the village forge" \
  --interactive \
  --name npc_blacksmith
```

### **🍺 Innkeeper**
```bash
goose run --recipe recipes/innkeeper.yaml \
  --params context="You are in a fantasy RPG village" \
  --interactive \
  --name npc_innkeeper
```

### **🛡️ Guard Captain**
```bash
goose run --recipe recipes/guard_captain.yaml \
  --params context="You are at the village gates" \
  --interactive \
  --name npc_guard_captain
```

### **💰 Master Merchant**
```bash
goose run --recipe recipes/master_merchant.yaml \
  --params context="You are in the marketplace" \
  --interactive \
  --name npc_merchant
```

### **🌿 Master Herbalist**
```bash
goose run --recipe recipes/master_herbalist.yaml \
  --params context="You are in the herbalist's garden" \
  --interactive \
  --name npc_herbalist
```

### **🧙 Mysterious Wizard**
```bash
goose run --recipe recipes/mysterious_wizard.yaml \
  --params context="You are in the wizard's tower" \
  --interactive \
  --name npc_wizard
```

### **👴 Village Elder**
```bash
goose run --recipe recipes/village_elder.yaml \
  --params context="You are in the village center" \
  --interactive \
  --name npc_elder
```

### **🏹 Forest Ranger**
```bash
goose run --recipe recipes/forest_ranger.yaml \
  --params context="You are at the edge of the forest" \
  --interactive \
  --name npc_ranger
```

### **🚛 Caravan Master**
```bash
goose run --recipe recipes/caravan_master.yaml \
  --params context="You are at the caravan camp" \
  --interactive \
  --name npc_caravan_master
```

### **⚕️ Healer**
```bash
goose run --recipe recipes/healer.yaml \
  --params context="You are in the healing temple" \
  --interactive \
  --name npc_healer
```

## 🛠️ **Available MCP Tools**

Each AI NPC can use these game interaction tools:

- **`get_player_info`** - Check player stats, health, inventory
- **`open_shop`** - Open trading interface
- **`give_item`** - Give items to the player
- **`create_quest`** - Create new quests
- **`get_world_info`** - Get current location info
- **`send_message`** - Send messages to game log

## 💡 **Tips**

### **Context Parameters**
Customize the `context` parameter to set the scene:
- `"You are in the village forge"` - For blacksmith
- `"You are in a cozy tavern"` - For innkeeper
- `"You are in a magical shop"` - For wizard
- `"You are in the wilderness"` - For ranger

### **Interactive Mode**
Always use `--interactive` to have real conversations with the NPCs.

### **Naming Convention**
Use descriptive names like `npc_blacksmith`, `npc_wizard` to keep track of different NPC sessions.

## 🎯 **Example Session**

```bash
# 1. Start the game
./launch_game.sh

# 2. Wait for "🌐 MCP Server started for AI NPCs" message

# 3. In another terminal, start an NPC
goose run --recipe recipes/innkeeper.yaml \
  --params context="You are in a cozy village tavern" \
  --interactive \
  --name npc_innkeeper

# 4. Chat with the NPC - they can interact with the game!
```

All NPCs now use the reliable HTTP-based MCP connection! 🎮✨