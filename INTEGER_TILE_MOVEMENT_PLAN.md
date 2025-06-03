# Integer-Based Tile Movement System - Implementation Plan

## Current Issues
1. **Mixed coordinate systems**: Decimal positions (0.2, 0.5) mixed with integer tiles
2. **Complex pathfinding**: Sub-tile precision creates unnecessary complexity
3. **Navigation confusion**: Entities can be "between tiles" making collision detection complex
4. **Performance overhead**: Floating-point calculations for simple tile movement

## Proposed Solution: Integer Tile-Based System

### Core Principles
1. **One entity per tile**: Each entity occupies exactly one tile position
2. **Integer coordinates**: All positions are integers (0, 1, 2, etc.)
3. **Tile center positioning**: Entities are always centered on their tile
4. **Simple movement**: Move from tile to tile in discrete steps
5. **Clear collision**: If tile is walkable (1), entity can move there; if not (0), blocked

### Implementation Changes

#### 1. Player Position System
```python
# OLD: Decimal positions
self.x = 5.7
self.y = 3.2
self.speed = 0.2

# NEW: Integer tile positions
self.tile_x = 5
self.tile_y = 3
self.moving = False
self.move_direction = None
```

#### 2. Movement System
```python
# OLD: Smooth decimal movement
new_x = self.x + move_x * self.speed
new_y = self.y + move_y * self.speed

# NEW: Discrete tile movement
target_tile_x = self.tile_x + move_direction_x
target_tile_y = self.tile_y + move_direction_y
if level.is_tile_walkable(target_tile_x, target_tile_y):
    self.tile_x = target_tile_x
    self.tile_y = target_tile_y
```

#### 3. Pathfinding System
```python
# OLD: Complex sub-tile pathfinding with smoothing
path = [(5.3, 3.7), (6.1, 4.2), (7.8, 4.9)]

# NEW: Simple tile-to-tile pathfinding
path = [(5, 3), (6, 4), (7, 4)]
```

#### 4. Collision Detection
```python
# OLD: Complex entity size and floating-point collision
def check_collision(self, x, y, entity_size):
    # Complex calculations...

# NEW: Simple tile-based collision
def is_tile_walkable(self, tile_x, tile_y):
    if not (0 <= tile_x < width and 0 <= tile_y < height):
        return False
    return self.walkable[tile_y][tile_x] > 0
```

#### 5. Rendering System
```python
# OLD: Direct position rendering
screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)

# NEW: Tile-centered rendering
world_x = self.tile_x + 0.5  # Center of tile for rendering
world_y = self.tile_y + 0.5
screen_x, screen_y = iso_renderer.world_to_screen(world_x, world_y, camera_x, camera_y)
```

### Benefits
1. **Simplified Logic**: No more complex sub-tile calculations
2. **Better Performance**: Integer operations are faster
3. **Clearer Navigation**: Always know exactly which tile an entity occupies
4. **Easier Debugging**: Positions are always clear integers
5. **Consistent Behavior**: Predictable movement and collision
6. **Chunk Compatibility**: Works perfectly with integer-based chunk systems

### Migration Strategy
1. **Phase 1**: Update Player class to use tile-based positioning
2. **Phase 2**: Simplify movement system to discrete tile movement
3. **Phase 3**: Replace complex pathfinding with simple tile pathfinding
4. **Phase 4**: Update all entities (NPCs, enemies, items) to tile positions
5. **Phase 5**: Update collision detection to tile-based system
6. **Phase 6**: Test and validate all systems work correctly

This will make the game much more predictable and easier to work with!