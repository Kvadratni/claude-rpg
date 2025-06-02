"""
Collision detection and physics functionality
"""

import math


class CollisionMixin:
    """Mixin class for collision detection functionality"""
    
    def check_collision(self, x, y, size=0.4, exclude_entity=None):
        """Check collision with level geometry and entities - improved precision with enhanced door handling"""
        # Check if the position is within level bounds with proper margin
        margin = size + 0.1
        if x < margin or x >= self.width - margin or y < margin or y >= self.height - margin:
            return True
        
        # Enhanced door area detection
        tile_x = int(x)
        tile_y = int(y)
        door_context = self.door_pathfinder.analyze_door_context(tile_x, tile_y, x, y)
        
        # For door areas, use much more lenient collision
        if door_context['is_door_area']:
            effective_size = size * 0.4  # Very small collision box for doors
            
            # Special handling for multi-tile door areas
            if door_context['is_double_door']:
                effective_size = size * 0.3  # Even smaller for double doors
        else:
            effective_size = size * 0.7  # Normal collision
        
        half_size = effective_size
        
        corners = [
            (x - half_size, y - half_size),  # Top-left
            (x + half_size, y - half_size),  # Top-right
            (x - half_size, y + half_size),  # Bottom-left
            (x + half_size, y + half_size),  # Bottom-right
        ]
        
        # Check each corner against tiles
        for corner_x, corner_y in corners:
            corner_tile_x = int(corner_x)
            corner_tile_y = int(corner_y)
            
            # Ensure tile coordinates are within bounds
            if 0 <= corner_tile_x < self.width and 0 <= corner_tile_y < self.height:
                if self.walkable[corner_tile_y][corner_tile_x] <= 0:
                    # For door areas, be more forgiving about walkability
                    if not door_context['is_door_area']:
                        return True
        
        # Also check center point
        center_tile_x = int(x)
        center_tile_y = int(y)
        if 0 <= center_tile_x < self.width and 0 <= center_tile_y < self.height:
            if self.walkable[center_tile_y][center_tile_x] <= 0:
                if not door_context['is_door_area']:
                    return True
        
        # Skip object collision checking in door areas to allow easier passage
        if door_context['is_door_area']:
            return False
        
        # Check collision with objects using circular collision (only when not in door areas)
        for obj in self.objects:
            if obj.blocks_movement and obj != exclude_entity:
                dist_x = x - obj.x
                dist_y = y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use circular collision for objects
                collision_distance = size + 0.35  # Slightly tighter collision
                if distance < collision_distance:
                    return True
        
        # Check collision with chests using circular collision
        for chest in self.chests:
            if chest.blocks_movement and chest != exclude_entity:
                dist_x = x - chest.x
                dist_y = y - chest.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use circular collision for chests
                collision_distance = size + 0.35  # Same as objects
                if distance < collision_distance:
                    return True
        
        # Check collision with NPCs using circular collision
        for npc in self.npcs:
            if npc != exclude_entity:
                dist_x = x - npc.x
                dist_y = y - npc.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # NPCs have collision
                collision_distance = size + 0.4
                if distance < collision_distance:
                    return True
        
        # Check collision with enemies (prevent stacking)
        for enemy in self.enemies:
            if enemy != exclude_entity:
                dist_x = x - enemy.x
                dist_y = y - enemy.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Enemies should not overlap too much
                collision_distance = size + 0.3
                if distance < collision_distance:
                    return True
        
        return False
    
    def check_enhanced_collision(self, x, y, entity_size):
        """Enhanced collision detection with predictive elements"""
        # Standard collision check
        if self.check_collision(x, y, entity_size):
            return True
        
        # Check for "squeeze" situations
        if self.is_squeeze_situation(x, y, entity_size):
            return True
        
        return False
    
    def is_squeeze_situation(self, x, y, entity_size):
        """Detect if entity would be squeezed between obstacles"""
        # Check if there are obstacles on opposite sides
        check_distance = entity_size + 0.2
        
        # Check cardinal directions for opposing obstacles
        obstacles = {
            'north': self.check_collision(x, y - check_distance, entity_size * 0.5),
            'south': self.check_collision(x, y + check_distance, entity_size * 0.5),
            'east': self.check_collision(x + check_distance, y, entity_size * 0.5),
            'west': self.check_collision(x - check_distance, y, entity_size * 0.5)
        }
        
        # If opposing sides have obstacles, it's a squeeze
        return (obstacles['north'] and obstacles['south']) or (obstacles['east'] and obstacles['west'])
    
    def is_position_walkable(self, x, y, entity_size=0.4):
        """Check if a grid position is walkable for pathfinding"""
        # Check basic tile walkability
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        if self.walkable[y][x] <= 0:
            return False
        
        # Check for objects that block movement
        center_x = x + 0.5
        center_y = y + 0.5
        
        for obj in self.objects:
            if obj.blocks_movement:
                dist_x = center_x - obj.x
                dist_y = center_y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use slightly larger collision for pathfinding to avoid tight squeezes
                collision_distance = entity_size + 0.4
                if distance < collision_distance:
                    return False
        
        return True
    
    def is_position_walkable_lenient(self, x, y, entity_size=0.4):
        """Check if a grid position is walkable for pathfinding with more lenient rules"""
        # Check basic tile walkability
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        if self.walkable[y][x] <= 0:
            return False
        
        # Special handling for doors - be more lenient around door tiles
        current_tile = self.get_tile(x, y) if hasattr(self, 'get_tile') else self.tiles[y][x]
        is_door_area = current_tile == self.TILE_DOOR
        
        # Also check adjacent tiles for doors
        if not is_door_area:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    check_x, check_y = x + dx, y + dy
                    if (0 <= check_x < self.width and 0 <= check_y < self.height):
                        check_tile = self.get_tile(check_x, check_y) if hasattr(self, 'get_tile') else self.tiles[check_y][check_x]
                        if check_tile == self.TILE_DOOR:
                            is_door_area = True
                            break
                if is_door_area:
                    break
        
        # Check for objects that block movement with smaller collision for pathfinding
        center_x = x + 0.5
        center_y = y + 0.5
        
        for obj in self.objects:
            if obj.blocks_movement:
                dist_x = center_x - obj.x
                dist_y = center_y - obj.y
                distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
                
                # Use much smaller collision for door areas, normal for others
                if is_door_area:
                    collision_distance = entity_size + 0.1  # Very lenient for doors
                else:
                    collision_distance = entity_size + 0.2  # Reduced from 0.4
                
                if distance < collision_distance:
                    return False
        
        return True
    
    def is_direct_path_clear(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Check if there's a clear direct path between two points"""
        # Calculate the distance and direction
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return True
        
        # Normalize direction
        step_x = dx / distance
        step_y = dy / distance
        
        # Check points along the path
        steps = int(distance * 4)  # Check every 0.25 units
        for i in range(1, steps + 1):
            check_x = start_x + (step_x * i * 0.25)
            check_y = start_y + (step_y * i * 0.25)
            
            # Check if we're near a door - if so, be more lenient with collision
            tile_x = int(check_x)
            tile_y = int(check_y)
            is_near_door = False
            
            if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
                # Check current tile and adjacent tiles for doors
                for dx_check in [-1, 0, 1]:
                    for dy_check in [-1, 0, 1]:
                        check_tile_x = tile_x + dx_check
                        check_tile_y = tile_y + dy_check
                        if (0 <= check_tile_x < self.width and 0 <= check_tile_y < self.height):
                            check_tile = self.get_tile(check_tile_x, check_tile_y) if hasattr(self, 'get_tile') else self.tiles[check_tile_y][check_tile_x]
                            if check_tile == self.TILE_DOOR:
                                is_near_door = True
                                break
                    if is_near_door:
                        break
            
            # Use more lenient collision checking near doors
            if is_near_door:
                # Use smaller entity size for door areas
                if self.check_collision(check_x, check_y, entity_size * 0.7):
                    return False
            else:
                # Normal collision checking
                if self.check_collision(check_x, check_y, entity_size):
                    return False
        
        return True
    
    def has_line_of_sight(self, start, end, entity_size=0.4):
        """Check if there's a clear line of sight between two points"""
        start_x, start_y = start
        end_x, end_y = end
        
        # Calculate the number of steps to check along the line
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return True
        
        # Check points along the line
        steps = int(distance * 2)  # Check every 0.5 units
        for i in range(1, steps):
            t = i / steps
            check_x = start_x + dx * t
            check_y = start_y + dy * t
            
            # Check if this point is walkable
            grid_x = int(check_x)
            grid_y = int(check_y)
            
            if not (0 <= grid_x < self.width and 0 <= grid_y < self.height):
                return False
            
            if self.walkable[grid_y][grid_x] <= 0:
                return False
            
            # Check for blocking objects
            if self.check_collision(check_x, check_y, entity_size):
                return False
        
        return True