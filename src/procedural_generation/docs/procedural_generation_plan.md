# Simplified Procedural Map Generation Plan - Goose RPG

## Overview
A streamlined procedural generation system that creates **4 core biomes** (Desert, Forest, Plains, Snow) using simple noise generation, places settlements from templates, and spawns existing enemies with proper safe zones.

## Key Constraints & Simplifications
- **Only 4 biomes**: Desert, Forest, Plains, Snow (no mountains, swamps, etc.)
- **No temperature/elevation**: Simple noise-based biome distribution
- **Use existing assets**: Work with current enemies, NPCs, and sprites
- **Template-based settlements**: Reuse existing building system to avoid rendering artifacts
- **Collision detection**: Prevent overlapping structures and enforce safe zones

## Current Assets Analysis

### Existing Enemies (from entity.py and level.py)
```
Forest Biome:
- Forest Goblin (health: 45, damage: 9, exp: 30)
- Forest Sprite (health: 35, damage: 12, exp: 40) 
- Ancient Guardian (health: 60, damage: 15, exp: 50)

Desert Biome:
- Giant Scorpion (health: 55, damage: 16, exp: 45)
- Bandit Scout (health: 35, damage: 8, exp: 20)

Plains Biome:
- Bandit Scout (health: 35, damage: 8, exp: 20)
- Orc Warrior (health: 80, damage: 18, exp: 60)

Snow Biome:
- Crystal Elemental (health: 70, damage: 20, exp: 65)
- Ancient Guardian (health: 60, damage: 15, exp: 50)

Bosses:
- Orc Warlord (health: 400, damage: 30, exp: 300) - Plains biome
- Ancient Dragon (health: 800, damage: 50, exp: 500) - Snow biome
```

### Existing NPCs (from entity.py)
```
- Master Merchant (shopkeeper)
- Village Elder 
- Master Smith (shopkeeper)
- Innkeeper
- High Priest
- Guard Captain
- Mine Foreman (shopkeeper)
- Harbor Master (shopkeeper)
- Caravan Master (shopkeeper)
- Forest Ranger
- Master Herbalist (shopkeeper)
- Mysterious Wizard
- Old Hermit
```

## System Architecture

### 1. Core Procedural Generator (`src/procedural_generator.py`)

#### 1.1 Simple Biome Generation
```python
class ProceduralGenerator:
    BIOME_TILES = {
        'PLAINS': {'primary': TILE_GRASS, 'secondary': TILE_DIRT, 'paths': TILE_STONE},
        'FOREST': {'primary': TILE_GRASS, 'secondary': TILE_DIRT, 'paths': TILE_DIRT},
        'DESERT': {'primary': TILE_DIRT, 'secondary': TILE_STONE, 'paths': TILE_STONE},
        'SNOW': {'primary': TILE_GRASS, 'secondary': TILE_STONE, 'paths': TILE_STONE}
    }
```

- Uses simple sine/cosine noise (no complex Perlin noise)
- Biome determination based on single noise value (0-1 range)
- No temperature or elevation calculations

#### 1.2 Settlement Templates
```python
SETTLEMENT_TEMPLATES = {
    'VILLAGE': {
        'size': (25, 25),
        'buildings': [
            {'name': 'General Store', 'npc': 'Master Merchant', 'has_shop': True},
            {'name': 'Inn', 'npc': 'Innkeeper'},
            {'name': 'Blacksmith', 'npc': 'Master Smith', 'has_shop': True},
            {'name': 'Elder House', 'npc': 'Village Elder'},
            {'name': 'Guard House', 'npc': 'Guard Captain'}
        ],
        'biomes': ['PLAINS', 'FOREST'],
        'safe_radius': 20
    },
    'DESERT_OUTPOST': {
        'biomes': ['DESERT'],
        'safe_radius': 15
    },
    'SNOW_SETTLEMENT': {
        'biomes': ['SNOW'], 
        'safe_radius': 15
    }
}
```

### 2. Integration Points

#### 2.1 Level Class Modifications
```python
def __init__(self, level_name, player, asset_loader, use_procedural=False, seed=None):
    # Add procedural option to existing constructor
    if use_procedural:
        self.generate_procedural_level(seed)
    else:
        # Keep existing template system as default
        # Use procedural as fallback if template fails
```

#### 2.2 Game Class Integration
```python
# In game.py - add option to start with procedural world
def start_new_game(self, use_procedural=False, seed=None):
    self.level = Level("Procedural World", self.player, self.asset_loader, 
                      use_procedural=use_procedural, seed=seed)
```

### 3. Key Features Implementation

#### 3.1 Collision Detection System
```python
class PlacementValidator:
    def __init__(self):
        self.occupied_areas = []  # (x, y, width, height) rectangles
        self.settlement_safe_zones = []  # (center_x, center_y, radius)
    
    def can_place_object(self, x, y, width, height):
        # Check overlaps with existing objects
        # Check terrain suitability
        return is_valid
    
    def is_in_safe_zone(self, x, y):
        # Check if position is within settlement safe zone
        # Enemies cannot spawn here
        return in_safe_zone
```

#### 3.2 Enemy Spawning Rules
- **Safe zones**: No enemies within configurable radius of settlements
- **Biome-specific**: Only appropriate enemies spawn in each biome
- **Density control**: Limit total number of enemies per world
- **Terrain validation**: No enemies on water or walls

#### 3.3 Boss Location System
- **Template-based**: Bosses spawn at specific template locations
- **Distance requirements**: Minimum distance from settlements (40+ tiles)
- **Biome restrictions**: Each boss type only spawns in appropriate biome
- **Unique spawning**: Only one boss of each type per world

## Implementation Phases

### Phase 1: Core System (Week 1) ✅ COMPLETED
**Files to create:**
- `src/procedural_generator.py` ✅ (Created)

**Files to modify:**
- `src/level.py` - Add procedural option to constructor
- `src/game.py` - Add menu option for procedural worlds

**Tasks:**
- [x] Create ProceduralGenerator class ✅
- [x] Implement simple biome noise generation ✅
- [x] Add biome-based tile generation ✅
- [x] Test biome map generation ✅

**Test Results:**
- ✅ Biome generation produces 4 distinct biomes (Desert, Plains, Forest, Snow)
- ✅ Noise function generates values in 0-1 range correctly
- ✅ Same seed produces identical maps (deterministic)
- ✅ Different seeds produce different maps (variety)
- ✅ Tile generation works with appropriate biome-based distribution
- ✅ Test script created: `test_procedural_biomes.py`

### Phase 2: Settlement System (Week 2) ✅ COMPLETED
**Tasks:**
- [x] Implement settlement placement with collision detection ✅
- [x] Create building generation using existing building system ✅
- [x] Add NPC spawning in settlements ✅
- [x] Test settlement generation and NPC placement ✅

**Fixes Applied:**
- ✅ Reduced water generation rates (75% reduction) to prevent settlement blocking
- ✅ Improved biome distribution algorithm for better desert/snow coverage
- ✅ Implemented two-strategy placement system (strict + relaxed water tolerance)
- ✅ Added water tolerance system (allows small amounts of water in settlements)
- ✅ Enhanced noise generation for more varied biome distribution
- ✅ Comprehensive collision detection system working correctly
- ✅ Safe zone system functioning properly

**Test Results:**
- ✅ Village placement: 100% success rate across multiple seeds
- ✅ Desert Outpost placement: 40% success rate (depends on biome distribution)
- ✅ Snow Settlement placement: 60% success rate (depends on biome distribution)
- ✅ Average 2.0 settlements per world (target: 1-3 settlements)
- ✅ Performance: <0.1 seconds for 200x200 world (target: <5 seconds)
- ✅ All collision detection and safe zone tests passing
- ✅ Water tolerance system working as designed

**Test Scripts Created:**
- `test_settlement_placement.py` - Basic settlement placement testing
- `debug_settlement_placement.py` - Diagnostic analysis of placement failures
- `test_desert_placement.py` - Specific testing for desert settlement issues
- `test_settlement_fixes.py` - Comprehensive testing of all fixes

### Phase 3: Entity Spawning (Week 3) ✅ COMPLETED
**Tasks:**
- [x] Implement enemy spawning with safe zone restrictions ✅
- [x] Add boss location templates and spawning ✅
- [x] Implement object spawning (trees, rocks) by biome ✅
- [x] Add chest spawning with rarity based on distance from settlements ✅

**Test Results:**
- ✅ Enemy spawning: 40 enemies per 200x200 world with biome restrictions
- ✅ Boss spawning: Orc Warlord (Plains), Ancient Dragon (Snow) placed correctly
- ✅ Object spawning: 5000+ objects with biome-appropriate distribution
- ✅ Chest spawning: 15 chests with distance-based rarity system
- ✅ Safe zone enforcement: No entities spawn within settlement safe zones

### Phase 4: Integration & Polish (Week 4) ❌ NOT COMPLETED
**Current Architecture Integration Points:**

**Files to modify:**
- `src/level/__init__.py` - Add ProceduralGenerationMixin to Level class
- `src/level/level_base.py` - Create procedural generation mixin
- `src/game.py` - Add procedural option to new_game() method
- `src/ui/menu/main_menu.py` - Add procedural world menu option

**Tasks:**
- [ ] Create ProceduralGenerationMixin for the refactored Level system
- [ ] Integrate with the mixin-based Level architecture
- [ ] Add menu option to choose procedural vs template generation
- [ ] Update save/load system to handle procedural worlds (store seed)
- [ ] Add debug visualization for biome maps
- [ ] Performance testing with actual game assets and entity classes

**Integration Pattern:**
```python
# In src/level/procedural_mixin.py (new file)
from procedural_generation import ProceduralWorldGenerator

class ProceduralGenerationMixin:
    def generate_procedural_level(self, seed=None):
        generator = ProceduralWorldGenerator(self.width, self.height, seed)
        world_data = generator.generate_world(self.asset_loader)
        
        # Replace template data with procedural data
        self.tiles = world_data['tiles']
        self.npcs = world_data['npcs']
        self.enemies = world_data['enemies']
        # ... etc

# In src/level/__init__.py
class Level(
    LevelBase,
    ProceduralGenerationMixin,  # Add this mixin
    WorldGenerationMixin,
    CollisionMixin,
    # ... other mixins
):
    def __init__(self, level_name, player, asset_loader, game=None, use_procedural=False, seed=None):
        if use_procedural:
            # Initialize base, then generate procedural world
            super().__init__(level_name, player, asset_loader, game)
            self.generate_procedural_level(seed)
        else:
            # Use existing template system
            super().__init__(level_name, player, asset_loader, game)
```

## Configuration Options

### World Generation Settings
```python
class WorldConfig:
    world_size = (200, 200)
    settlement_count = 3  # One of each type
    enemy_density = 0.001  # 0.1% of tiles
    boss_count = 2  # Orc Warlord + Ancient Dragon
    chest_count = 15
    object_density_by_biome = {
        'FOREST': 0.3,  # Dense trees
        'PLAINS': 0.05,  # Scattered trees
        'DESERT': 0.08,  # Rocks
        'SNOW': 0.1     # Mixed trees/rocks
    }
```

### Safe Zone Rules
```python
SAFE_ZONE_RULES = {
    'settlement_radius': {
        'VILLAGE': 20,
        'DESERT_OUTPOST': 15,
        'SNOW_SETTLEMENT': 15
    },
    'boss_min_distance': 40,
    'settlement_min_distance': 30
}
```

## Testing Strategy

### Unit Tests
- Biome generation consistency (same seed = same map)
- Collision detection accuracy
- Safe zone calculations
- Settlement placement validation

### Integration Tests
- Full world generation without crashes
- NPC spawning in correct locations
- Enemy spawning respects safe zones
- Boss spawning in appropriate biomes

### Performance Tests
- World generation time (target: <5 seconds)
- Memory usage during generation
- Frame rate impact during gameplay

## File Structure (Updated for Refactored Architecture)
```
src/
├── procedural_generation/          # New - Complete modular procedural system
│   ├── __init__.py                # Package interface
│   ├── src/                       # Modular components
│   │   ├── biome_generator.py     # Biome and tile generation
│   │   ├── settlement_generator.py # Settlement placement
│   │   ├── entity_spawner.py      # Entity spawning
│   │   ├── modular_generator.py   # Main coordinator
│   │   └── procedural_generator.py # Legacy monolithic version
│   ├── tests/                     # Comprehensive test suite
│   ├── examples/                  # Integration examples
│   └── docs/                      # Documentation
├── level/                         # Refactored - Mixin-based Level system
│   ├── __init__.py               # Main Level class with mixins
│   ├── level_base.py             # Base Level functionality
│   ├── procedural_mixin.py       # New - Procedural generation mixin
│   └── [other mixins]            # Existing mixins
├── game.py                       # Modified - Add procedural option
├── ui/menu/                      # Modified - Add procedural menu options
│   ├── main_menu.py             # Add procedural world choice
│   └── procedural_menu.py       # New - Procedural world configuration
├── entities/                     # Existing - Compatible with procedural system
├── core/                         # Existing - Asset loading, etc.
└── [other existing files]        # Existing - No changes needed
```

## Success Criteria

### Minimum Viable Product (MVP)
- [x] Generate 4 distinct biomes using simple noise
- [ ] Place 1-3 settlements without overlaps
- [ ] Spawn biome-appropriate enemies outside safe zones
- [ ] Spawn 2 bosses in correct biomes away from settlements
- [ ] Generate playable world in <5 seconds

### Enhanced Features (Post-MVP)
- [ ] Biome transition zones for smoother boundaries
- [ ] Road generation between settlements
- [ ] Special biome features (oases in desert, clearings in forest)
- [ ] Configurable world size and density
- [ ] Multiple world templates/styles

## Risk Mitigation

### Technical Risks
1. **Performance**: Simple noise generation should be fast enough
2. **Collision detection**: Use spatial partitioning if needed
3. **Asset compatibility**: All existing sprites work with new system

### Design Risks
1. **Biome variety**: 4 biomes may feel repetitive
   - *Mitigation*: Add biome-specific features and objects
2. **Settlement placement**: May fail to place all settlements
   - *Mitigation*: Fallback to template system if placement fails
3. **Enemy balance**: Biome-specific enemies may create difficulty spikes
   - *Mitigation*: Use existing enemy stats, add level scaling later

## Future Enhancements

### Phase 2 Features (Post-Launch)
- **Biome variants**: Desert oases, frozen lakes, forest clearings
- **Dynamic weather**: Snow in snow biome, sandstorms in desert
- **Seasonal changes**: Different spawns/appearance by season
- **Player-built structures**: Allow players to build in procedural worlds

### Phase 3 Features (Long-term)
- **Infinite worlds**: Generate chunks as player explores
- **Multiplayer support**: Shared procedural worlds with seeds
- **Mod support**: Allow custom biomes and settlement templates
- **Advanced AI**: Settlements that grow and change over time

## Conclusion

This simplified approach focuses on the core request: **4 biomes with template-based settlements and proper collision/spawning rules**. By leveraging existing assets and building systems, we can create varied, replayable worlds without the complexity of advanced terrain generation systems.

The phased approach allows for iterative development and testing, ensuring each component works before moving to the next. The fallback to the existing template system provides a safety net if procedural generation fails.

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation
3. Set up testing framework for procedural worlds
4. Create development branch for procedural features