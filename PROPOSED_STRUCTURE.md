# Proposed File Structure Reorganization

## Current Status

### ✅ COMPLETED: Phase 1 - Core Systems Foundation
The core systems have been successfully moved to a dedicated `core/` module:

```
src/core/                      # ✅ COMPLETED
├── __init__.py               # Core module exports
├── assets.py                 # Asset loading (moved from src/assets.py)
├── audio.py                  # Audio management (moved from src/audio.py)
├── isometric.py              # Coordinate conversion (moved from src/isometric.py)
└── game_log.py               # Message logging (moved from src/game_log.py)
```

### ✅ COMPLETED: Phase 2 - Entity System Refactoring
The monolithic entity.py has been successfully broken down into focused modules:

```
src/entities/                  # ✅ COMPLETED
├── __init__.py               # Entity module exports
├── base.py                   # Base Entity class
├── npc.py                    # NPC class and logic
├── enemy.py                  # Enemy class and AI
├── item.py                   # Item class and effects
├── chest.py                  # Chest class and loot
└── spawning.py               # Entity spawning logic
```

### ✅ COMPLETED: Phase 4 - UI System Consolidation
The large menu.py and UI components have been reorganized into a cohesive system:

```
src/ui/                        # ✅ COMPLETED
├── __init__.py               # UI module exports
├── menu/                     # Menu system
│   ├── __init__.py
│   ├── main_menu.py          # Main menu
│   ├── settings_menu.py      # Settings interface
│   ├── pause_menu.py         # Pause menu
│   └── load_menu.py          # Load game menu
├── inventory.py              # Inventory UI
├── dialogue.py               # Dialogue system
├── shop.py                   # Shop interface
└── hud.py                    # In-game HUD elements
```

**Benefits Achieved:**
- Reduced file count in root src/ directory
- Clear separation of fundamental systems
- Improved import organization
- No wrapper files - direct imports to organized modules
- Game functionality fully preserved
- Monolithic files broken down into manageable, focused modules

## Current Issues (Remaining)
1. **Large monolithic files**: `player.py` (915 lines) - remaining to be split
2. **Mixed responsibilities**: Player file handling multiple concerns (movement, combat, inventory)
3. **Scattered world functionality**: World-related systems need consolidation
4. **Systems organization**: Game systems need proper organization

## Proposed Structure

```
src/
├── __init__.py
├── main.py                    # Entry point
├── game.py                    # Main game controller (keep as-is)
├── settings.py                # Configuration (keep as-is)
├── save_system.py             # Save/load system (keep as-is)
│
├── core/                      # ✅ COMPLETED - Core game systems
│   ├── __init__.py
│   ├── assets.py              # Asset loading
│   ├── audio.py               # Audio management
│   ├── isometric.py           # Coordinate conversion
│   └── game_log.py            # Message logging
│
├── entities/                  # All game entities
│   ├── __init__.py
│   ├── base.py                # Base Entity class
│   ├── player.py              # Player class (refactored)
│   ├── npc.py                 # NPC entities
│   ├── enemy.py               # Enemy entities
│   ├── item.py                # Item entities
│   ├── chest.py               # Chest entities
│   └── spawning.py            # Entity spawning logic
│
├── ui/                        # All UI components
│   ├── __init__.py
│   ├── menu/                  # Menu system
│   │   ├── __init__.py
│   │   ├── main_menu.py       # Main menu
│   │   ├── pause_menu.py      # Pause menu
│   │   ├── settings_menu.py   # Settings menu
│   │   └── load_menu.py       # Load game menu
│   ├── inventory.py           # Inventory UI
│   ├── dialogue.py            # Dialogue system
│   ├── shop.py                # Shop interface
│   └── hud.py                 # In-game HUD elements
│
├── world/                     # World and level management
│   ├── __init__.py
│   ├── level/                 # Current level system (keep structure)
│   │   ├── __init__.py
│   │   ├── level_base.py
│   │   ├── level_world_gen.py
│   │   ├── level_collision.py
│   │   ├── level_pathfinding.py
│   │   ├── tile_manager.py
│   │   ├── level_events.py
│   │   ├── entity_manager.py
│   │   ├── level_data.py
│   │   ├── level_renderer.py
│   │   └── ui_renderer.py
│   ├── map_template.py        # Map templates
│   ├── template_level.py      # Template-based levels
│   ├── door_pathfinder.py     # Door pathfinding
│   ├── door_renderer.py       # Door rendering
│   └── wall_renderer.py       # Wall rendering
│
├── systems/                   # Game systems
│   ├── __init__.py
│   ├── quest_system.py        # Quest management
│   ├── combat.py              # Combat system (extracted from player)
│   ├── movement.py            # Movement system (extracted from player)
│   └── pathfinding.py         # General pathfinding utilities
│
└── procedural_generation/     # Keep current structure
    ├── __init__.py
    ├── src/
    ├── tests/
    └── docs/
```

## Detailed Refactoring Plan

### 1. **Break Down Large Files**

#### `entity.py` (1089 lines) → Multiple files:
- `entities/base.py` - Base Entity class (~200 lines)
- `entities/npc.py` - NPC class and logic (~250 lines)
- `entities/enemy.py` - Enemy class and AI (~300 lines)
- `entities/item.py` - Item class and effects (~150 lines)
- `entities/chest.py` - Chest class and loot (~100 lines)

#### `player.py` (915 lines) → Split responsibilities:
- `entities/player.py` - Core player data and basic methods (~400 lines)
- `systems/combat.py` - Combat mechanics (~200 lines)
- `systems/movement.py` - Movement and pathfinding (~200 lines)
- Keep inventory integration in player (~115 lines)

#### `menu.py` (934 lines) → Menu system:
- `ui/menu/main_menu.py` - Main menu (~300 lines)
- `ui/menu/settings_menu.py` - Settings interface (~250 lines)
- `ui/menu/pause_menu.py` - Pause menu (~150 lines)
- `ui/menu/load_menu.py` - Load game menu (~150 lines)
- `ui/menu/__init__.py` - Menu coordinator (~84 lines)

### 2. **Create Logical Groupings**

#### Core Systems (`core/`):
- Move fundamental systems that other modules depend on
- Asset loading, audio, coordinate conversion, logging

#### UI Components (`ui/`):
- Centralize all user interface code
- Menu system, inventory, dialogue, shop, HUD

#### Entity Management (`entities/`):
- All game objects in one place
- Clear inheritance hierarchy
- Shared spawning logic

#### World Management (`world/`):
- Keep the excellent level/ structure
- Add related world systems (doors, walls, templates)

#### Game Systems (`systems/`):
- Extract reusable game mechanics
- Combat, movement, quests, pathfinding

### 3. **Benefits of This Structure**

1. **Reduced File Sizes**: No file over 400 lines
2. **Clear Responsibilities**: Each file has a single, clear purpose
3. **Better Maintainability**: Related code grouped together
4. **Easier Testing**: Smaller, focused modules are easier to test
5. **Improved Reusability**: Systems can be reused across different contexts
6. **Cleaner Dependencies**: Clear import hierarchy

### 4. **Migration Strategy**

1. **Phase 1**: Create new directory structure
2. **Phase 2**: Move and refactor `entity.py` 
3. **Phase 3**: Split `player.py` into player + systems
4. **Phase 4**: Refactor menu system
5. **Phase 5**: Move core systems
6. **Phase 6**: Update all imports and test

### 5. **Backward Compatibility**

Maintain backward compatibility during transition:
```python
# In old locations, provide import redirects
from .entities.player import Player
from .ui.inventory import Inventory
# etc.
```

This structure would make the codebase much more maintainable while preserving all existing functionality.