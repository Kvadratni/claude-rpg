# Goose CLI Usage Update for AI NPCs

## Summary of Changes

This document outlines the updated Goose CLI command structure for AI-powered NPCs, specifically the addition of `--interactive` and `--resume` flags for improved conversation continuity.

## Updated Command Structure

### Previous Command (Deprecated)
```bash
goose run --recipe recipes/village_elder.yaml \
  --params "message=Hello" \
  --params "context=test" \
  --no-session
```

### New Command (Current)
```bash
goose run --recipe recipes/village_elder.yaml \
  --params "message=Hello" \
  --params "context=test" \
  --interactive --resume
```

## Key Changes

### Added Flags
- **`--interactive`**: Enables interactive mode for continuous conversation flow
- **`--resume`**: Maintains session continuity between interactions

### Removed Flags
- **`--no-session`**: Replaced with session-based approach for conversation memory

## Benefits of New Approach

### 1. Conversation Continuity
- NPCs remember previous parts of the conversation
- Natural reference to earlier topics and context
- Persistent character memory across interactions

### 2. Improved User Experience
- More natural conversation flow
- Reduced repetition in NPC responses
- Better context awareness over time

### 3. Session Management
- Each NPC maintains its own session (e.g., `npc_village_elder`)
- Isolated conversation histories per character
- Automatic session cleanup and management

## Implementation Details

### Files Updated
1. **`AI_NPC_USAGE_GUIDE.md`**
   - Updated Recipe Execution Flow section
   - Added Session Management section
   - Enhanced technical documentation

2. **`recipes/README.md`**
   - Updated manual testing commands
   - Added explanation of new flags
   - Improved testing documentation

3. **`KNOWN_ISSUES.md`**
   - Updated manual command examples
   - Reflected new flag usage in troubleshooting

4. **`src/recipe_manager.py`**
   - Updated command string generation
   - Added `--interactive` and `--resume` flags
   - Maintained session naming convention

### Session Naming Convention
- Format: `npc_{recipe_name}`
- Examples:
  - Village Elder: `npc_village_elder`
  - Master Merchant: `npc_master_merchant`
  - Guard Captain: `npc_guard_captain`

## Testing the Changes

### Manual Testing
Test the updated commands manually:

```bash
# Test Village Elder
goose run --recipe recipes/village_elder.yaml \
  --params "message=Hello, who are you?" \
  --params "context=Player is in the village center" \
  --interactive --resume

# Test Master Merchant
goose run --recipe recipes/master_merchant.yaml \
  --params "message=What do you sell?" \
  --params "context=Player is looking at shop items" \
  --interactive --resume
```

### Automated Testing
The existing test scripts will automatically use the new command structure through the updated `recipe_manager.py`.

## Migration Notes

### For Developers
- All existing recipe files remain compatible
- No changes needed to YAML recipe structure
- Session management is handled automatically
- Fallback systems remain unchanged

### For Users
- No visible changes to game interface
- Improved conversation quality and continuity
- NPCs will remember previous interactions better
- More natural dialogue flow

## Troubleshooting

### Common Issues
1. **Session conflicts**: Each NPC uses isolated sessions
2. **Flag compatibility**: Ensure Goose CLI version supports these flags
3. **Performance**: Session management may slightly increase response times

### Debug Commands
```bash
# Check Goose CLI version
goose --version

# Test basic recipe functionality
goose run --recipe recipes/village_elder.yaml --help

# Verify session creation
goose sessions list
```

## Future Enhancements

### Planned Improvements
- Session persistence across game restarts
- Cross-NPC conversation references
- Dynamic session cleanup
- Enhanced context sharing between NPCs

### Monitoring
- Track session performance metrics
- Monitor conversation quality improvements
- Analyze user engagement with AI NPCs

---

**Last Updated**: 2025-06-03  
**Version**: 1.0  
**Status**: Active Implementation