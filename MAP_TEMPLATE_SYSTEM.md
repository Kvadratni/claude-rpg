# Claude RPG Map Template System

## Overview

The Claude RPG game uses an image-based map template system for deterministic world generation. Instead of procedural generation, maps are designed as PNG images where each pixel color represents different terrain types, spawn points, and game elements.

## How It Works

### 1. Template Structure
- **Format**: PNG images (any size supported)
- **Location**: `assets/maps/` directory
- **Current main template**: `main_world.png` (200x200 pixels)
- **Each pixel** = One game tile in the world

### 2. Color Mapping System

The `MapTemplate` class in `src/map_template.py` defines color-to-terrain mappings:

```python
COLORS = {
    # Terrain types
    'GRASS': (255, 255, 255),      # White - grass areas
    'DIRT': (139, 69, 19),         # Brown - dirt paths  
    'STONE': (128, 128, 128),      # Gray - stone roads
    'WATER': (0, 0, 255),          # Blue - water areas
    'IMPASSABLE': (0, 0, 0),       # Black - walls/impassable
    
    # Special zones
    'FOREST': (0, 128, 0),         # Green - forest areas (trees allowed)
    'BUILDING': (255, 0, 0),       # Red - building locations
    'NPC_SPAWN': (255, 255, 0),    # Yellow - NPC spawn points
    'OBJECT_SPAWN': (128, 0, 128), # Purple - object spawn areas
    'CHEST_SPAWN': (255, 165, 0),  # Orange - chest locations
    'ENEMY_SPAWN': (255, 0, 255),  # Magenta - enemy spawn areas
    
    # Building interiors
    'INTERIOR': (200, 200, 200),   # Light gray - building interiors
    'DOOR': (100, 50, 25),         # Dark brown - door locations
}
```

### 3. Template Processing Pipeline

1. **Image Loading**: PNG loaded using pygame
2. **Pixel Analysis**: Each pixel color mapped to terrain type
3. **Spawn Point Collection**: Special colors collected as entity spawn locations
4. **Tile Generation**: Colors converted to game tile types
5. **Entity Spawning**: NPCs, enemies, objects placed at designated spots

## Current Map Analysis (main_world.png)

### Terrain Distribution
- **White (Grass)**: ~85% - Open areas for movement
- **Gray (Stone)**: ~8% - Roads and village center
- **Green (Forest)**: ~5% - Tree spawn areas
- **Blue (Water)**: ~2% - Lakes and water features

### Entity Spawn Points
- **Red Buildings**: 8 structures (village buildings)
- **Yellow NPCs**: 6 spawn points (shopkeeper, elder, etc.)
- **Purple Objects**: ~50 points (trees and rocks)
- **Orange Chests**: ~12 treasure locations
- **Magenta Enemies**: ~30 spawn areas

### Layout Features
- **Central Village**: Stone plaza with buildings around it
- **Road Network**: Stone paths connecting all areas
- **Forest Regions**: 3 distinct wooded areas
- **Water Bodies**: 4 lakes of varying sizes
- **Defensive Layout**: Village center with patrol areas

## Size Constraints & Flexibility

### **NOT BOUND TO FIXED SIZE** ✅

The system is designed to be completely flexible:

```python
def __init__(self, template_path: str):
    self.template_image = pygame.image.load(template_path)
    self.width = self.template_image.get_width()    # Dynamic width
    self.height = self.template_image.get_height()  # Dynamic height
```

### Supported Sizes
- **Minimum**: 50x50 pixels (very small map)
- **Current**: 200x200 pixels (medium map)
- **Maximum**: Limited only by:
  - Available RAM (larger maps use more memory)
  - Performance (rendering time increases with size)
  - Practical gameplay (too large becomes unwieldy)

### Recommended Sizes
- **Small Maps**: 100x100 to 200x200 (quick gameplay)
- **Medium Maps**: 300x300 to 500x500 (balanced exploration)
- **Large Maps**: 600x600 to 1000x1000 (epic adventures)
- **Massive Maps**: 1000x1000+ (MMO-style worlds)

## Creating New Templates

### 1. Design Process
1. **Plan Layout**: Sketch regions, roads, settlements
2. **Create Base**: Start with white (grass) background
3. **Add Terrain**: Paint roads (gray), water (blue), forests (green)
4. **Place Buildings**: Red pixels for structures
5. **Add Spawn Points**: Yellow (NPCs), Orange (chests), Purple (objects)
6. **Enemy Areas**: Magenta for combat zones

### 2. Tools Recommended
- **GIMP**: Free, precise pixel editing
- **Photoshop**: Professional pixel art tools
- **Aseprite**: Specialized pixel art editor
- **MS Paint**: Simple but effective for basic templates

### 3. Template Guidelines
- **1 pixel = 1 game tile**: Keep this ratio consistent
- **Use exact colors**: RGB values must match the mapping table
- **Avoid anti-aliasing**: Use pure colors, no blending
- **Test frequently**: Load in-game to verify layout
- **Document changes**: Keep notes on custom additions

## Advanced Features

### 1. Procedural Enhancement
Templates can be combined with procedural generation:
- **Base layout** from template
- **Detail generation** (tree placement, rock distribution)
- **Dynamic content** (weather, seasonal changes)

### 2. Multi-Layer Templates
Future enhancement possibilities:
- **Base terrain layer**: Core landscape
- **Object layer**: Trees, rocks, decorations  
- **Entity layer**: NPCs, enemies, chests
- **Event layer**: Triggers, special zones

### 3. Template Validation
The system includes validation:
```python
def validate_template(self) -> List[str]:
    # Check for required spawn types
    # Verify NPC accessibility
    # Ensure balanced distribution
```

## Integration with Game Systems

### 1. Level Generation
```python
# In level.py
template_path = "/path/to/template.png"
if os.path.exists(template_path):
    success = integrate_template_generation(self, template_path)
```

### 2. Entity Spawning
- **NPCs**: Placed at yellow pixels, matched to predefined characters
- **Enemies**: Distributed across magenta areas with type variation
- **Objects**: Trees in forests, rocks in mountains
- **Chests**: Treasure placement based on danger level

### 3. Collision System
- **Walkable tiles**: Grass, dirt, stone, doors, brick interiors
- **Impassable tiles**: Walls, water, building exteriors
- **Special handling**: Doors allow passage, objects block movement

## Performance Considerations

### Memory Usage
- **200x200 map**: ~160KB image + ~800KB game data
- **500x500 map**: ~1MB image + ~5MB game data  
- **1000x1000 map**: ~4MB image + ~20MB game data

### Rendering Performance
- **Culling system**: Only renders visible tiles
- **Entity sorting**: Depth-based rendering for isometric view
- **Caching**: Tile sprites cached for reuse

### Loading Time
- **Template parsing**: O(width × height) - linear with map size
- **Entity generation**: O(spawn_points) - depends on content density
- **Optimization**: Larger maps may need background loading

## File Organization

```
assets/maps/
├── main_world.png          # Current 200x200 template
├── main_world_debug.png    # Debug visualization
├── bigger_world.png        # Your new larger template
├── dungeon_level1.png      # Indoor areas
├── forest_region.png       # Specialized areas
└── world_overview.png      # Massive overworld map
```

## Best Practices

### 1. Design Principles
- **Logical flow**: Roads should connect important areas
- **Balanced distribution**: Mix safe and dangerous zones
- **Visual clarity**: Clear separation between terrain types
- **Gameplay focus**: Design supports intended player experience

### 2. Technical Guidelines
- **Color precision**: Use exact RGB values from the mapping table
- **Edge handling**: Consider map boundaries and player movement
- **Spawn density**: Balance entity count with performance
- **Testing workflow**: Regular in-game testing during design

### 3. Content Guidelines
- **Progressive difficulty**: Easier enemies near starting areas
- **Reward placement**: Better loot in more dangerous areas
- **NPC distribution**: Services accessible but not overwhelming
- **Exploration incentives**: Hidden areas and secret paths

## Extending the System

### 1. Adding New Terrain Types
```python
# In map_template.py, add to COLORS dict:
'SWAMP': (64, 128, 64),     # Dark green - swamp areas
'DESERT': (255, 255, 128),  # Light yellow - desert sand
'MOUNTAIN': (128, 64, 64),  # Dark red - rocky mountains
```

### 2. Custom Entity Types
```python
# In template_level.py, extend spawn_enemies():
elif terrain == 'SWAMP':
    enemy_type = {'name': 'Swamp Troll', 'health': 80, ...}
```

### 3. Dynamic Content
- **Time-based changes**: Day/night cycles affecting spawn rates
- **Player-driven changes**: Buildings constructed, areas cleared
- **Event systems**: Seasonal changes, special encounters

## Conclusion

The map template system provides a powerful, flexible foundation for world design in Claude RPG. It combines the precision of hand-crafted design with the efficiency of automated generation, supporting maps of virtually any size while maintaining excellent performance and gameplay quality.

The system is **not bound to fixed sizes** and can accommodate everything from small dungeon rooms to massive overworld maps, limited primarily by practical considerations rather than technical constraints.