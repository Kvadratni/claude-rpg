# Procedural Generation Implementation Details

## Implementation Progress

### ✅ Phase 1: Core System (COMPLETED)
- **Biome Generation**: Simple noise-based system generating 4 biomes (Desert, Plains, Forest, Snow)
- **Tile Generation**: Biome-appropriate tile placement with water features
- **Noise Function**: Multi-layered noise for natural-looking biome distribution
- **Test Coverage**: Comprehensive testing with `test_procedural_biomes.py`

### ✅ Phase 2: Settlement System (COMPLETED)
**Major Issues Resolved:**
- **Water Blocking Issue**: Reduced water generation rates by 75% across all biomes
- **Biome Distribution**: Improved algorithm for better desert/snow coverage
- **Settlement Placement**: Two-strategy system (strict + relaxed water tolerance)
- **Collision Detection**: Comprehensive system preventing settlement overlaps
- **Safe Zone System**: Proper safe zone creation and enforcement
- **Building Generation**: Enhanced building system using existing level.py architecture

**Building Generation Features Implemented:**
- **Enhanced Wall System**: Uses specialized wall tiles (horizontal, vertical, window variants)
- **Window Generation**: 20% chance for horizontal windows, 15% for vertical windows
- **Double Door System**: 2-tile wide doors centered on buildings
- **Interior Floors**: Brick tile interiors for realistic building feel
- **Improved Placement Logic**: 
  - Smaller center squares (1/3 instead of 1/2 of settlement size)
  - Reduced overlap margins (1 pixel instead of 2)
  - More placement attempts (50 instead of 20)
  - Better boundary handling

**Building Types Generated:**
- **Villages**: General Store, Inn, Blacksmith, Elder House, Guard House
- **Desert Outposts**: Trading Post, Water Storage, Caravan Rest
- **Snow Settlements**: Ranger Station, Herbalist Hut, Warm Lodge

**Current Performance:**
- Village Placement: **100% success rate** across multiple seeds
- Desert Outpost: **40% success rate** (improved from 0%)
- Snow Settlement: **60% success rate** (improved from ~30%)
- Average: **2.0 settlements per world** (target: 1-3)
- Building Placement: **100% success rate** within settlements
- Generation Time: **<0.1 seconds** for 200x200 world

**Quality Metrics:**
- ✅ **Windows**: 4-7 window tiles per settlement (horizontal + vertical)
- ✅ **Doors**: 2-4 door tiles per settlement (double doors)
- ✅ **Interior Floors**: 24-48 brick tiles per settlement
- ✅ **Wall Variety**: Mix of regular, horizontal, vertical, and window walls
- ✅ **Building Placement**: All 5 village buildings consistently placed

**Test Scripts Created:**
- `test_settlement_placement.py` - Basic settlement placement testing
- `debug_settlement_placement.py` - Diagnostic analysis of placement failures  
- `test_desert_placement.py` - Specific testing for desert settlement issues
- `test_settlement_fixes.py` - Comprehensive testing of all fixes
- `test_enhanced_buildings.py` - Building generation validation
- `debug_buildings.py` - Building system debugging

### 🔄 Phase 3: Entity Spawning (IN PROGRESS)
- [ ] Enemy spawning with safe zone restrictions
- [ ] Boss placement in appropriate biomes
- [ ] Object spawning (trees, rocks) by biome
- [ ] Chest spawning with distance-based rarity

### ⏳ Phase 4: Integration & Polish (PENDING)
- [ ] Level class integration
- [ ] Game menu integration
- [ ] Save/load system updates
- [ ] Debug visualization tools

## Code Changes Required

### 1. New Files to Create

#### `src/procedural_generator.py` ✅ (Already Created)
- Core procedural generation system
- Biome generation using simple noise
- Settlement placement with collision detection
- Enemy/object spawning with safe zone rules

### 2. Files to Modify

#### `src/level.py` - Constructor Changes
```python
# BEFORE:
def __init__(self, level_name, player, asset_loader):

# AFTER:
def __init__(self, level_name, player, asset_loader, use_procedural=False, seed=None):
```

**New method to add:**
```python
def generate_procedural_level(self, seed=None):
    """Generate level using procedural system"""
    from .procedural_generator import ProceduralGenerator
    
    # Initialize procedural generator
    self.procedural_generator = ProceduralGenerator(self.width, self.height, seed)
    
    # Generate tiles from biomes
    self.tiles = self.procedural_generator.generate_tiles()
    
    # Place settlements
    settlements = self.procedural_generator.place_settlements(self.tiles)
    
    # Spawn entities
    self.npcs = self.procedural_generator.spawn_npcs(settlements, self.asset_loader)
    self.enemies = self.procedural_generator.spawn_enemies(self.tiles, self.asset_loader)
    self.enemies.extend(self.procedural_generator.spawn_bosses(self.tiles, self.asset_loader))
    self.objects = self.procedural_generator.spawn_objects(self.tiles, self.asset_loader)
    self.chests = self.procedural_generator.spawn_chests(self.tiles, self.asset_loader)
    self.items = []  # Items come from enemy drops and chests
    
    # Generate walkable grid
    self.walkable = self.procedural_generator.generate_walkable_grid(self.tiles)
    
    print(f"Procedural level generated with seed: {self.procedural_generator.seed}")
```

#### `src/game.py` - Menu Integration
```python
# Add to Game class
def show_world_type_menu(self):
    """Show menu to choose world type"""
    world_options = [
        "Template World (Handcrafted)",
        "Procedural World (Random)", 
        "Procedural World (Custom Seed)",
        "Back"
    ]
    
    selected = 0
    while True:
        # Render menu options
        # Handle input
        if selected == 0:  # Template world
            self.start_new_game(use_procedural=False)
            break
        elif selected == 1:  # Random procedural
            self.start_new_game(use_procedural=True)
            break
        elif selected == 2:  # Custom seed
            seed = self.get_seed_input()
            self.start_new_game(use_procedural=True, seed=seed)
            break
        elif selected == 3:  # Back
            break

def start_new_game(self, use_procedural=False, seed=None):
    """Modified to support procedural generation"""
    # Reset player
    self.player.reset()
    
    # Create level with procedural option
    self.level = Level("New World", self.player, self.asset_loader, 
                      use_procedural=use_procedural, seed=seed)
    
    # Set player position (center of world)
    self.player.x = self.level.width // 2
    self.player.y = self.level.height // 2
    
    # Start game music
    if hasattr(self.asset_loader, 'audio_manager'):
        self.asset_loader.audio_manager.start_game_music()
    
    self.state = self.STATE_PLAYING
```

### 3. Save System Integration

#### `src/save_system.py` - Add Seed Support
```python
# Add to save data
def save_game(self, player, level, filename):
    save_data = {
        "player": player.get_save_data(),
        "level": level.get_save_data(),
        "timestamp": time.time(),
        # NEW: Add procedural generation info
        "procedural_info": {
            "is_procedural": hasattr(level, 'procedural_generator'),
            "seed": getattr(level.procedural_generator, 'seed', None) if hasattr(level, 'procedural_generator') else None
        }
    }

# Add to load data
def load_game(self, filename, player, asset_loader):
    # ... existing load code ...
    
    # NEW: Handle procedural worlds
    procedural_info = data.get("procedural_info", {})
    if procedural_info.get("is_procedural", False):
        seed = procedural_info.get("seed")
        level = Level(level_data["name"], player, asset_loader, 
                     use_procedural=True, seed=seed)
    else:
        level = Level.from_save_data(level_data, player, asset_loader)
```

## Testing Implementation

### 1. Unit Tests
```python
# tests/test_procedural_generator.py
import unittest
from src.procedural_generator import ProceduralGenerator

class TestProceduralGenerator(unittest.TestCase):
    def test_biome_generation_consistency(self):
        """Same seed should generate same biomes"""
        gen1 = ProceduralGenerator(100, 100, seed=12345)
        gen2 = ProceduralGenerator(100, 100, seed=12345)
        
        self.assertEqual(gen1.biome_map, gen2.biome_map)
    
    def test_settlement_placement(self):
        """Settlements should not overlap"""
        gen = ProceduralGenerator(200, 200, seed=54321)
        tiles = gen.generate_tiles()
        settlements = gen.place_settlements(tiles)
        
        # Check no overlapping settlements
        for i, s1 in enumerate(settlements):
            for j, s2 in enumerate(settlements[i+1:], i+1):
                self.assertFalse(self.settlements_overlap(s1, s2))
    
    def test_safe_zone_enforcement(self):
        """Enemies should not spawn in safe zones"""
        gen = ProceduralGenerator(200, 200, seed=99999)
        tiles = gen.generate_tiles()
        settlements = gen.place_settlements(tiles)
        enemies = gen.spawn_enemies(tiles, None)
        
        for enemy in enemies:
            self.assertFalse(gen.is_in_safe_zone(enemy.x, enemy.y))
```

### 2. Integration Tests
```python
# tests/test_level_integration.py
def test_procedural_level_creation(self):
    """Test full procedural level creation"""
    from src.level import Level
    from src.player import Player
    from src.assets import AssetLoader
    
    asset_loader = AssetLoader()
    player = Player(100, 100, asset_loader)
    
    # Test procedural level creation
    level = Level("Test World", player, asset_loader, 
                 use_procedural=True, seed=12345)
    
    # Verify level was created successfully
    self.assertIsNotNone(level.tiles)
    self.assertIsNotNone(level.walkable)
    self.assertGreater(len(level.npcs), 0)
    self.assertGreater(len(level.enemies), 0)
```

## Debug Tools

### 1. Biome Visualization
```python
# Add to ProceduralGenerator class
def create_biome_debug_image(self, output_path):
    """Create debug image showing biome distribution"""
    debug_surface = pygame.Surface((self.width, self.height))
    
    biome_colors = {
        'PLAINS': (144, 238, 144),  # Light green
        'FOREST': (34, 139, 34),    # Forest green
        'DESERT': (238, 203, 173),  # Navajo white
        'SNOW': (255, 250, 250)     # Snow white
    }
    
    for y in range(self.height):
        for x in range(self.width):
            biome = self.biome_map[y][x]
            color = biome_colors.get(biome, (128, 128, 128))
            debug_surface.set_at((x, y), color)
    
    # Mark settlements
    for center_x, center_y, radius in self.settlement_safe_zones:
        pygame.draw.circle(debug_surface, (255, 0, 0), (center_x, center_y), radius, 2)
    
    pygame.image.save(debug_surface, output_path)
```

### 2. Console Commands
```python
# Add to Game class for debugging
def handle_debug_commands(self, command):
    """Handle debug commands during development"""
    if command.startswith("generate_world"):
        parts = command.split()
        seed = int(parts[1]) if len(parts) > 1 else None
        self.start_new_game(use_procedural=True, seed=seed)
        print(f"Generated procedural world with seed: {seed}")
    
    elif command == "show_biomes":
        if hasattr(self.level, 'procedural_generator'):
            debug_path = "debug_biome_map.png"
            self.level.procedural_generator.create_biome_debug_image(debug_path)
            print(f"Biome debug image saved to: {debug_path}")
    
    elif command == "world_info":
        if hasattr(self.level, 'procedural_generator'):
            gen = self.level.procedural_generator
            print(f"World Seed: {gen.seed}")
            print(f"Settlements: {len(gen.settlement_safe_zones)}")
            print(f"NPCs: {len(self.level.npcs)}")
            print(f"Enemies: {len(self.level.enemies)}")
            print(f"Objects: {len(self.level.objects)}")
            print(f"Chests: {len(self.level.chests)}")
```

## Performance Considerations

### 1. Generation Time Optimization
```python
# Optimize biome generation
def generate_biome_map_optimized(self):
    """Optimized biome generation using numpy if available"""
    try:
        import numpy as np
        # Use numpy for faster array operations
        x_coords = np.arange(self.width)
        y_coords = np.arange(self.height)
        X, Y = np.meshgrid(x_coords, y_coords)
        
        # Vectorized noise calculation
        noise_values = (
            np.sin(X * 0.1 + self.seed * 0.001) +
            np.cos(Y * 0.1 + self.seed * 0.002) +
            np.sin((X + Y) * 0.05 + self.seed * 0.003)
        ) / 3.0
        
        # Normalize and convert to biomes
        normalized = (noise_values + 1) / 2
        # Convert to biome indices and map to biome names
        
    except ImportError:
        # Fallback to original method
        return self.generate_biome_map()
```

### 2. Memory Management
```python
# Clear temporary data after generation
def cleanup_generation_data(self):
    """Clean up temporary data after world generation"""
    # Clear large temporary arrays
    self.biome_map = None  # Keep only if needed for debugging
    self.occupied_areas.clear()
    # Keep settlement_safe_zones for gameplay
```

## Error Handling

### 1. Generation Failures
```python
def generate_procedural_level(self, seed=None):
    """Generate level with error handling"""
    try:
        # ... generation code ...
        
    except Exception as e:
        print(f"Procedural generation failed: {e}")
        print("Falling back to template generation...")
        
        # Fallback to template system
        template_path = "assets/maps/main_world.png"
        if os.path.exists(template_path):
            success = integrate_template_generation(self, template_path)
            if not success:
                # Last resort: generate basic fallback level
                self.generate_fallback_level()
        else:
            self.generate_fallback_level()
```

### 2. Asset Loading Failures
```python
def spawn_npcs_safe(self, settlements, asset_loader):
    """Spawn NPCs with error handling for missing assets"""
    npcs = []
    
    for settlement in settlements:
        for building in settlement.get('buildings', []):
            try:
                # ... NPC creation code ...
                npcs.append(npc)
            except Exception as e:
                print(f"Failed to create NPC {building.get('npc', 'Unknown')}: {e}")
                # Continue with other NPCs
                continue
    
    return npcs
```

## Configuration File

### `config/procedural_settings.json`
```json
{
    "world_generation": {
        "default_size": [200, 200],
        "biome_scale": 0.1,
        "settlement_attempts": 50,
        "enemy_density": 0.001,
        "object_density": {
            "FOREST": 0.3,
            "PLAINS": 0.05,
            "DESERT": 0.08,
            "SNOW": 0.1
        }
    },
    "safe_zones": {
        "village_radius": 20,
        "outpost_radius": 15,
        "boss_min_distance": 40,
        "settlement_min_distance": 30
    },
    "debug": {
        "save_biome_maps": false,
        "verbose_logging": false,
        "generation_timing": false
    }
}
```

## Rollback Plan

If procedural generation causes issues:

1. **Immediate**: Set `use_procedural=False` by default
2. **Short-term**: Add config option to disable procedural generation
3. **Long-term**: Fix issues and re-enable

The existing template system remains untouched and serves as a fallback, ensuring the game remains playable even if procedural generation fails.