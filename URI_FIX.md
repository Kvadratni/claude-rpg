# ✅ **FIXED: URI Field Issue**

## 🔧 **Issue Resolved**

**Problem**: `Error: extensions: missing field 'uri' at line 9 column 1`

**Root Cause**: The `sse` extension type requires `uri` field, not `url` field.

**Solution**: Updated all 16 recipe files to use `uri` instead of `url`.

## 📋 **Correct Configuration**

```yaml
extensions:
- type: sse
  name: rpg-game-server
  display_name: RPG Game Actions
  timeout: 30
  uri: http://localhost:39301/model_context_protocol/2024-11-05/sse  # ✅ 'uri' not 'url'
```

## 🎯 **Ready to Test**

The recipes should now work without the missing field error:

```bash
# 1. Start the game
cd /Users/mnovich/Development/claude-rpg
./launch_game.sh

# 2. Wait for "🌐 MCP Server started for AI NPCs"

# 3. Test the innkeeper NPC
goose run --recipe recipes/innkeeper.yaml \
  --params context="You are in a fantasy RPG village" \
  --interactive \
  --name npc_innkeeper
```

All recipe files have been updated with the correct `uri` field! 🎮✨