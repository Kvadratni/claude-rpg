# 🔧 **Fixed Recipe Configuration Issues**

## ✅ **Issues Resolved**

### **1. Extension Type Fixed**
- **Problem**: Used `type: remote` which Goose doesn't recognize
- **Solution**: Changed to `type: sse` for HTTP-based MCP
- **Result**: All 16 recipe files now use correct extension type

### **2. Old MCP Server Still Present**
- **Problem**: Old `rpg-mcp` command still installed at `/Users/mnovich/.local/bin/rpg-mcp`
- **Impact**: Might cause conflicts or confusion
- **Status**: Old server exists but won't interfere with HTTP-based approach

## 📋 **Current Recipe Configuration**

All recipe files now use the correct format:

```yaml
extensions:
- type: builtin
  name: developer
  display_name: Developer
  timeout: 30
  bundled: true
- type: sse  # ✅ Fixed: was 'remote', now 'sse'
  name: rpg-game-server
  display_name: RPG Game Actions
  timeout: 30
  uri: http://localhost:39301/model_context_protocol/2024-11-05/sse  # ✅ HTTP endpoint
```

## 🚀 **How to Test**

### **1. Start the Game (HTTP MCP Server)**
```bash
cd /Users/mnovich/Development/claude-rpg
./launch_game.sh
```
**Expected**: Game starts with message "🌐 MCP Server started for AI NPCs"

### **2. Test Recipe with Goose**
```bash
# Use any updated recipe with proper parameters
goose run --recipe /Users/mnovich/Development/claude-rpg-goose-npcs/recipes/blacksmith.yaml \
  --params context="You are in the village forge" \
  --interactive \
  --name npc_blacksmith

# Or test the innkeeper
goose run --recipe /Users/mnovich/Development/claude-rpg-goose-npcs/recipes/innkeeper.yaml \
  --params context="You are in a fantasy RPG village" \
  --interactive \
  --name npc_innkeeper
```
**Expected**: Should connect to HTTP MCP server without errors

### **3. Verify Connection**
The AI should be able to use these tools:
- `get_player_info` - Check player status
- `open_shop` - Open trading interface
- `give_item` - Give items to player
- `create_quest` - Create new quests
- `get_world_info` - Get world information
- `send_message` - Send messages to game log

## 🧹 **Optional Cleanup**

If you want to remove the old stdio-based MCP server:

```bash
# Remove old global installation
rm /Users/mnovich/.local/bin/rpg-mcp

# Clean up old files (optional)
rm -rf /Users/mnovich/Development/claude-rpg-goose-npcs/rpg_mcp_package
rm /Users/mnovich/Development/claude-rpg-goose-npcs/mcp_game_server.py
rm /Users/mnovich/Development/claude-rpg-goose-npcs/install_mcp.py
```

## ✅ **Ready to Test**

The recipes should now work correctly with the HTTP-based MCP server! The key fixes:

1. ✅ **Extension type**: `remote` → `sse`
2. ✅ **HTTP endpoint**: Points to `http://localhost:39301/model_context_protocol/2024-11-05/sse`
3. ✅ **All 16 recipes updated** and ready to use

### **Test Steps:**
1. **Start the game**: `cd /Users/mnovich/Development/claude-rpg && ./launch_game.sh`
2. **Use a recipe**: 
   ```bash
   goose run --recipe /Users/mnovich/Development/claude-rpg-goose-npcs/recipes/blacksmith.yaml \
     --params context="You are in the village forge" \
     --interactive \
     --name npc_blacksmith
   ```
3. **Verify**: Should connect to HTTP MCP server without the "unknown variant" error