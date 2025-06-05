## Merge Strategy: AI NPCs + Procedural Generation

### Current State Analysis

**Our Branch (merge-ai-and-procedural):**
- ✅ Revolutionary AI NPC System with MCP integration
- ✅ Asset-aware quest generation system  
- ✅ Dynamic quest spawning with directional placement
- ✅ Clean, stable codebase with comprehensive README
- ✅ Item registry system for asset verification

**Target Branch (feature/modular-procedural-generation):**
- ✅ Complete procedural world generation
- ✅ Settlement generation with buildings and NPCs
- ✅ Biome-based terrain generation
- ✅ Enhanced rendering with roofs and improved visuals
- ✅ Chunked world system for large worlds
- ✅ Modular procedural generation architecture

### Key Conflicts to Resolve

#### 1. **NPC System Architecture**
- **Our branch**: AI NPCs with MCP server integration, recipe-based personalities
- **Their branch**: Procedural NPC spawning based on settlements and biomes
- **Solution**: Merge both - procedural spawning + AI personalities

#### 2. **World Generation**
- **Our branch**: Static village-based world
- **Their branch**: Fully procedural world with biomes and settlements
- **Solution**: Adopt procedural world, integrate AI quest spawning

#### 3. **Rendering System**
- **Our branch**: Basic isometric rendering
- **Their branch**: Enhanced rendering with roofs, better building system
- **Solution**: Use enhanced rendering, ensure AI quest objects render correctly

#### 4. **Quest System Integration**
- **Our branch**: AI-generated quests spawn objects in static world
- **Their branch**: Procedural world with different entity management
- **Solution**: Adapt quest spawning to work with procedural world chunks

### Merge Approach

#### Phase 1: Foundation Merge
1. Adopt procedural generation core systems
2. Preserve AI integration files
3. Merge asset systems (combine both asset sets)

#### Phase 2: NPC System Integration  
1. Integrate AI NPC base classes with procedural NPC spawning
2. Ensure AI NPCs can be spawned in procedural settlements
3. Maintain MCP server functionality

#### Phase 3: Quest System Adaptation
1. Adapt AI quest generation to work with chunked world
2. Ensure quest object spawning works with procedural entity management
3. Test directional spawning in procedural world

#### Phase 4: Testing & Polish
1. Verify all AI features work in procedural world
2. Test quest generation and completion
3. Ensure save/load compatibility

### Files Requiring Special Attention

#### Critical AI Files to Preserve:
- `src/ai_integration.py` - Core AI system
- `src/mcp_sse_server.py` - MCP server for AI communication  
- `src/item_registry.py` - Asset-aware quest generation
- `src/quest_system.py` - Quest management
- `recipes/` - AI NPC personalities

#### Critical Procedural Files to Adopt:
- `src/world/` - New world generation system
- `src/procedural_generation/` - Enhanced procedural system
- `src/roof_renderer.py` - Enhanced rendering
- Enhanced asset system with new sprites

#### Files Needing Careful Merge:
- `src/game.py` - Game initialization and loop
- `src/level/` - Level management system
- `src/entities/npc.py` - NPC base class
- `src/core/assets.py` - Asset loading system

### Expected Challenges

1. **Entity Management**: Different approaches to spawning and managing entities
2. **World Coordinates**: Static vs procedural coordinate systems
3. **Save System**: Different world state management
4. **Rendering Pipeline**: Enhanced rendering may affect AI quest object display
5. **Performance**: Ensuring AI features don't impact procedural generation performance

### Success Criteria

✅ AI NPCs spawn and function in procedural settlements
✅ Quest generation works with procedural world chunks  
✅ All existing AI features preserved and functional
✅ Enhanced procedural generation features working
✅ Performance remains acceptable
✅ Save/load system works with combined features