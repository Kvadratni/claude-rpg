"""
Door pathfinding and navigation system for the RPG
"""

import math


class DoorPathfinder:
    """Handles all door-related pathfinding functionality"""
    
    def __init__(self, level):
        self.level = level
    
    def analyze_door_context(self, tile_x, tile_y, world_x, world_y):
        """Analyze the door context around a position for better collision handling"""
        context = {
            'is_door_area': False,
            'is_double_door': False,
            'door_orientation': None,
            'distance_to_door': float('inf')
        }
        
        # Check current tile and surrounding area for doors
        check_radius = 2  # Check 2 tiles around
        doors_found = []
        
        for dy in range(-check_radius, check_radius + 1):
            for dx in range(-check_radius, check_radius + 1):
                check_x = tile_x + dx
                check_y = tile_y + dy
                
                if (0 <= check_x < self.level.width and 0 <= check_y < self.level.height):
                    if self.level.tiles[check_y][check_x] == self.level.TILE_DOOR:
                        door_distance = math.sqrt(dx*dx + dy*dy)
                        doors_found.append({
                            'pos': (check_x, check_y),
                            'distance': door_distance,
                            'world_pos': (check_x + 0.5, check_y + 0.5)
                        })
        
        if doors_found:
            # Find closest door
            closest_door = min(doors_found, key=lambda d: d['distance'])
            context['distance_to_door'] = closest_door['distance']
            
            # Consider it a door area if we're close enough
            if closest_door['distance'] <= 1.5:
                context['is_door_area'] = True
                
                # Check for double doors (adjacent door tiles)
                door_x, door_y = closest_door['pos']
                adjacent_doors = 0
                
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    adj_x, adj_y = door_x + dx, door_y + dy
                    if (0 <= adj_x < self.level.width and 0 <= adj_y < self.level.height):
                        if self.level.tiles[adj_y][adj_x] == self.level.TILE_DOOR:
                            adjacent_doors += 1
                
                context['is_double_door'] = adjacent_doors > 0
                context['door_orientation'] = self.get_door_orientation(door_x, door_y)
        
        return context
    
    def enhance_door_pathfinding(self, path, entity_size):
        """Add special handling for door navigation with improved doorway handling"""
        if len(path) < 2:
            return path
        
        enhanced_path = []
        i = 0
        
        while i < len(path):
            current_point = path[i]
            enhanced_path.append(current_point)
            
            # Look ahead for door navigation opportunities
            if i < len(path) - 1:
                next_point = path[i + 1]
                
                # Check if we're approaching a door or door area
                door_waypoints = self.generate_improved_door_waypoints(current_point, next_point, entity_size)
                
                if door_waypoints:
                    enhanced_path.extend(door_waypoints)
                    # Skip ahead if we've handled multiple points
                    if len(door_waypoints) > 2:
                        i += min(2, len(path) - i - 1)  # Skip some intermediate points
            
            i += 1
        
        return enhanced_path
    
    def generate_improved_door_waypoints(self, current, next_point, entity_size):
        """Generate improved intermediate waypoints for door navigation"""
        waypoints = []
        
        # Check if path crosses a door or door area
        doors_info = self.find_doors_with_context(current, next_point)
        
        for door_info in doors_info:
            door_pos = door_info['position']
            door_orientation = door_info['orientation']
            approach_side = door_info['approach_side']
            
            # Create more precise approach and exit points
            approach_point = self.calculate_precise_door_approach(door_pos, door_orientation, approach_side, entity_size)
            exit_point = self.calculate_precise_door_exit(door_pos, door_orientation, approach_side, entity_size)
            
            # Add alignment waypoint before door if needed
            if self.needs_door_alignment(current, door_pos, door_orientation):
                align_point = self.calculate_door_alignment_point(door_pos, door_orientation, current, entity_size)
                waypoints.append(align_point)
            
            # Add the main door navigation waypoints
            waypoints.extend([approach_point, door_pos, exit_point])
        
        return waypoints
    
    def find_doors_with_context(self, start, end):
        """Find doors between points with additional context information"""
        doors_info = []
        
        # Sample points along the line between start and end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return doors_info
        
        steps = max(int(distance * 3), 3)  # More sampling for better detection
        
        for i in range(steps + 1):
            t = i / steps
            x = start[0] + dx * t
            y = start[1] + dy * t
            
            tile_x, tile_y = int(x), int(y)
            if (0 <= tile_x < self.level.width and 0 <= tile_y < self.level.height and
                self.level.tiles[tile_y][tile_x] == self.level.TILE_DOOR):
                
                door_pos = (tile_x + 0.5, tile_y + 0.5)
                
                # Check if we already found this door
                already_found = any(info['position'] == door_pos for info in doors_info)
                if not already_found:
                    orientation = self.get_door_orientation(tile_x, tile_y)
                    approach_side = self.determine_approach_side(start, door_pos, orientation)
                    
                    doors_info.append({
                        'position': door_pos,
                        'orientation': orientation,
                        'approach_side': approach_side,
                        'tile_pos': (tile_x, tile_y)
                    })
        
        return doors_info
    
    def determine_approach_side(self, from_point, door_pos, orientation):
        """Determine which side we're approaching the door from"""
        dx = from_point[0] - door_pos[0]
        dy = from_point[1] - door_pos[1]
        
        if orientation == "horizontal":
            # For horizontal doors, check if approaching from north or south
            return "north" if dy < 0 else "south"
        else:
            # For vertical doors, check if approaching from east or west
            return "west" if dx < 0 else "east"
    
    def calculate_precise_door_approach(self, door_pos, orientation, approach_side, entity_size):
        """Calculate precise approach point for door based on orientation and approach side"""
        # Use larger clearance for approach to avoid getting stuck
        clearance = max(0.7, entity_size + 0.3)
        
        if orientation == "horizontal":
            if approach_side == "north":
                return (door_pos[0], door_pos[1] - clearance)
            else:  # south
                return (door_pos[0], door_pos[1] + clearance)
        else:  # vertical
            if approach_side == "west":
                return (door_pos[0] - clearance, door_pos[1])
            else:  # east
                return (door_pos[0] + clearance, door_pos[1])
    
    def calculate_precise_door_exit(self, door_pos, orientation, approach_side, entity_size):
        """Calculate precise exit point from door"""
        # Use larger clearance for exit to ensure we're fully through
        clearance = max(0.8, entity_size + 0.4)
        
        if orientation == "horizontal":
            if approach_side == "north":
                return (door_pos[0], door_pos[1] + clearance)  # Exit to south
            else:  # south
                return (door_pos[0], door_pos[1] - clearance)  # Exit to north
        else:  # vertical
            if approach_side == "west":
                return (door_pos[0] + clearance, door_pos[1])  # Exit to east
            else:  # east
                return (door_pos[0] - clearance, door_pos[1])  # Exit to west
    
    def needs_door_alignment(self, current_pos, door_pos, orientation):
        """Check if we need an alignment waypoint before approaching the door"""
        dx = abs(current_pos[0] - door_pos[0])
        dy = abs(current_pos[1] - door_pos[1])
        
        # If we're not well-aligned with the door, we need an alignment point
        if orientation == "horizontal":
            return dx > 0.3  # Not aligned horizontally
        else:
            return dy > 0.3  # Not aligned vertically
    
    def calculate_door_alignment_point(self, door_pos, orientation, current_pos, entity_size):
        """Calculate alignment point to approach door straight-on"""
        clearance = max(1.0, entity_size + 0.6)  # Extra clearance for alignment
        
        if orientation == "horizontal":
            # Align horizontally, maintain vertical distance
            align_y = current_pos[1]
            if align_y < door_pos[1]:
                align_y = door_pos[1] - clearance
            else:
                align_y = door_pos[1] + clearance
            return (door_pos[0], align_y)
        else:  # vertical
            # Align vertically, maintain horizontal distance
            align_x = current_pos[0]
            if align_x < door_pos[0]:
                align_x = door_pos[0] - clearance
            else:
                align_x = door_pos[0] + clearance
            return (align_x, door_pos[1])
    
    def generate_door_waypoints(self, current, next_point, entity_size):
        """Generate intermediate waypoints for door navigation (legacy method)"""
        waypoints = []
        
        # Check if path crosses a door
        door_positions = self.find_doors_between_points(current, next_point)
        
        for door_pos in door_positions:
            # Create approach waypoint (align with door)
            approach_point = self.calculate_door_approach_point(door_pos, current, entity_size)
            
            # Create exit waypoint (clear of door)
            exit_point = self.calculate_door_exit_point(door_pos, next_point, entity_size)
            
            waypoints.extend([approach_point, door_pos, exit_point])
        
        return waypoints
    
    def find_doors_between_points(self, start, end):
        """Find door tiles between two points"""
        doors = []
        
        # Sample points along the line between start and end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return doors
        
        steps = max(int(distance * 2), 2)
        
        for i in range(steps + 1):
            t = i / steps
            x = start[0] + dx * t
            y = start[1] + dy * t
            
            tile_x, tile_y = int(x), int(y)
            if (0 <= tile_x < self.level.width and 0 <= tile_y < self.level.height and
                self.level.tiles[tile_y][tile_x] == self.level.TILE_DOOR):
                door_pos = (tile_x + 0.5, tile_y + 0.5)
                if door_pos not in doors:
                    doors.append(door_pos)
        
        return doors
    
    def calculate_door_approach_point(self, door_pos, from_point, entity_size):
        """Calculate optimal approach point for door"""
        door_x, door_y = int(door_pos[0]), int(door_pos[1])
        
        # Find door orientation
        door_orientation = self.get_door_orientation(door_x, door_y)
        
        if door_orientation == "horizontal":
            # Approach from north or south
            if from_point[1] < door_y:
                return (door_pos[0], door_pos[1] - 0.6)  # Approach from north
            else:
                return (door_pos[0], door_pos[1] + 0.6)  # Approach from south
        else:
            # Approach from east or west
            if from_point[0] < door_x:
                return (door_pos[0] - 0.6, door_pos[1])  # Approach from west
            else:
                return (door_pos[0] + 0.6, door_pos[1])  # Approach from east
    
    def calculate_door_exit_point(self, door_pos, to_point, entity_size):
        """Calculate optimal exit point from door"""
        door_x, door_y = int(door_pos[0]), int(door_pos[1])
        
        # Find door orientation
        door_orientation = self.get_door_orientation(door_x, door_y)
        
        if door_orientation == "horizontal":
            # Exit to north or south
            if to_point[1] < door_y:
                return (door_pos[0], door_pos[1] - 0.6)  # Exit to north
            else:
                return (door_pos[0], door_pos[1] + 0.6)  # Exit to south
        else:
            # Exit to east or west
            if to_point[0] < door_x:
                return (door_pos[0] - 0.6, door_pos[1])  # Exit to west
            else:
                return (door_pos[0] + 0.6, door_pos[1])  # Exit to east
    
    def get_door_orientation(self, door_x, door_y):
        """Determine if door is horizontal or vertical based on surrounding walls"""
        # Check adjacent tiles to determine orientation
        horizontal_walls = 0
        vertical_walls = 0
        
        # Check north and south
        if (door_y > 0 and self.level.wall_renderer.is_wall_tile(self.level.tiles[door_y - 1][door_x])):
            horizontal_walls += 1
        if (door_y < self.level.height - 1 and self.level.wall_renderer.is_wall_tile(self.level.tiles[door_y + 1][door_x])):
            horizontal_walls += 1
        
        # Check east and west
        if (door_x > 0 and self.level.wall_renderer.is_wall_tile(self.level.tiles[door_y][door_x - 1])):
            vertical_walls += 1
        if (door_x < self.level.width - 1 and self.level.wall_renderer.is_wall_tile(self.level.tiles[door_y][door_x + 1])):
            vertical_walls += 1
        
        # If more walls on horizontal sides, door is horizontal
        return "horizontal" if horizontal_walls >= vertical_walls else "vertical"