"""
Pathfinding and navigation system
"""

import heapq
import math
import random


class PathfindingMixin:
    """Mixin class for pathfinding functionality"""
    
    def find_path(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Find a path using multi-resolution pathfinding with corner smoothing"""
        # Phase 1: Coarse pathfinding on tile grid
        coarse_path = self.find_coarse_path(start_x, start_y, end_x, end_y, entity_size)
        if not coarse_path:
            return []
        
        # Phase 2: Apply corner detection and smoothing
        smoothed_path = self.apply_corner_smoothing(coarse_path, entity_size)
        
        # Phase 3: Add door navigation waypoints
        enhanced_path = self.door_pathfinder.enhance_door_pathfinding(smoothed_path, entity_size)
        
        # Phase 4: Validate path with entity simulation
        validated_path = self.validate_path_with_entity_simulation(enhanced_path, entity_size)
        
        return validated_path
    
    def find_coarse_path(self, start_x, start_y, end_x, end_y, entity_size=0.4):
        """Find a coarse path using A* algorithm with sub-tile precision"""
        # Convert to grid coordinates but allow sub-tile positioning
        start_grid_x = int(start_x)
        start_grid_y = int(start_y)
        end_grid_x = int(end_x)
        end_grid_y = int(end_y)
        
        # For chunk-based worlds, use different bounds checking
        if hasattr(self, 'is_infinite_world') and self.is_infinite_world:
            # For infinite worlds, we don't have fixed bounds - just check if chunks can be loaded
            # We'll limit the search to a reasonable area around the start point
            max_search_distance = 50  # tiles
            if (abs(end_grid_x - start_grid_x) > max_search_distance or 
                abs(end_grid_y - start_grid_y) > max_search_distance):
                return []  # Too far for pathfinding
        else:
            # Check if start and end are valid for traditional worlds
            if not (0 <= start_grid_x < self.width and 0 <= start_grid_y < self.height):
                return []
            if not (0 <= end_grid_x < self.width and 0 <= end_grid_y < self.height):
                return []
        
        # Check if end position is walkable
        if not self.is_position_walkable_for_pathfinding(end_grid_x, end_grid_y, entity_size):
            end_grid_x, end_grid_y = self.find_nearest_walkable(end_grid_x, end_grid_y, entity_size)
            if end_grid_x is None:
                return []  # No walkable position found
        
        # For very short distances, create direct path with sub-tile precision
        if abs(start_grid_x - end_grid_x) <= 1 and abs(start_grid_y - end_grid_y) <= 1:
            return self.create_direct_sub_tile_path(start_x, start_y, end_x, end_y, entity_size)
        
        # A* algorithm with enhanced walkability scoring
        open_set = []
        heapq.heappush(open_set, (0, start_grid_x, start_grid_y))
        
        came_from = {}
        g_score = {(start_grid_x, start_grid_y): 0}
        f_score = {(start_grid_x, start_grid_y): self.heuristic(start_grid_x, start_grid_y, end_grid_x, end_grid_y)}
        
        visited = set()
        max_iterations = 500
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current_f, current_x, current_y = heapq.heappop(open_set)
            
            if (current_x, current_y) in visited:
                continue
            
            visited.add((current_x, current_y))
            
            # Check if we reached the goal
            if current_x == end_grid_x and current_y == end_grid_y:
                # Reconstruct path with sub-tile precision
                path = []
                while (current_x, current_y) in came_from:
                    # Use sub-tile positioning instead of forcing tile centers
                    path.append(self.calculate_sub_tile_position(current_x, current_y, entity_size))
                    current_x, current_y = came_from[(current_x, current_y)]
                path.reverse()
                
                # Add final destination with sub-tile precision
                path.append(self.calculate_sub_tile_position(end_grid_x, end_grid_y, entity_size))
                
                return path
            
            # Check all 8 neighbors
            neighbors = [
                (current_x + 1, current_y),     # Right
                (current_x - 1, current_y),     # Left
                (current_x, current_y + 1),     # Down
                (current_x, current_y - 1),     # Up
                (current_x + 1, current_y + 1), # Down-Right
                (current_x - 1, current_y + 1), # Down-Left
                (current_x + 1, current_y - 1), # Up-Right
                (current_x - 1, current_y - 1), # Up-Left
            ]
            
            for next_x, next_y in neighbors:
                if (next_x, next_y) in visited:
                    continue
                
                # For chunk-based worlds, check reasonable bounds
                if hasattr(self, 'is_infinite_world') and self.is_infinite_world:
                    # Limit search to reasonable area around start point
                    if (abs(next_x - start_grid_x) > max_search_distance or 
                        abs(next_y - start_grid_y) > max_search_distance):
                        continue
                else:
                    # Check bounds for traditional worlds
                    if not (0 <= next_x < self.width and 0 <= next_y < self.height):
                        continue
                
                # Check if position is walkable
                if not self.is_position_walkable_for_pathfinding(next_x, next_y, entity_size):
                    continue
                
                # Calculate movement cost
                is_diagonal = abs(next_x - current_x) == 1 and abs(next_y - current_y) == 1
                base_cost = 1.414 if is_diagonal else 1.0
                
                # Get walkability score
                walkability_score = self.get_walkability_score(next_x, next_y)
                influence_penalty = (1.0 - walkability_score) * 2.0
                move_cost = base_cost * (1.0 + influence_penalty)
                
                # Favor doors and open areas
                next_tile = self.get_tile(next_x, next_y)
                if next_tile == getattr(self, 'TILE_DOOR', 5):
                    move_cost *= 0.1  # 90% cost reduction for doors
                elif walkability_score > 0.9:
                    move_cost *= 0.8  # Prefer open areas
                
                tentative_g_score = g_score.get((current_x, current_y), float('inf')) + move_cost
                
                if tentative_g_score < g_score.get((next_x, next_y), float('inf')):
                    came_from[(next_x, next_y)] = (current_x, current_y)
                    g_score[(next_x, next_y)] = tentative_g_score
                    f_score[(next_x, next_y)] = tentative_g_score + self.heuristic(next_x, next_y, end_grid_x, end_grid_y)
                    
                    heapq.heappush(open_set, (f_score[(next_x, next_y)], next_x, next_y))
        
        return []  # No path found
    
    def is_position_walkable_for_pathfinding(self, x, y, entity_size=0.4):
        """Check if a position is walkable for pathfinding - works with both chunk and traditional worlds"""
        # For chunk-based worlds, use chunk-based walkability checking
        if hasattr(self, 'is_infinite_world') and self.is_infinite_world:
            if hasattr(self, 'is_position_walkable_chunk'):
                return self.is_position_walkable_chunk(x, y)
            else:
                # Fallback: check if we can get a tile and if it's walkable
                tile = self.get_tile(x, y)
                if tile is None:
                    return True  # Assume unloaded chunks are walkable
                walkable_tiles = [0, 1, 2, 5, 13, 16, 17, 18, 19]  # Common walkable tile types
                return tile in walkable_tiles
        else:
            # Traditional world bounds checking
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
                    
                    collision_distance = entity_size + 0.4
                    if distance < collision_distance:
                        return False
            
            return True
    
    def get_walkability_score(self, x, y):
        """Get walkability score for a position - works with both chunk and traditional worlds"""
        # For chunk-based worlds, return a simple score based on tile type
        if hasattr(self, 'is_infinite_world') and self.is_infinite_world:
            tile = self.get_tile(x, y)
            if tile is None:
                return 0.8  # Moderate score for unloaded chunks
            
            # Score based on tile type
            if tile == getattr(self, 'TILE_DOOR', 5):
                return 1.0  # Doors are fully walkable
            elif tile in [0, 1, 16, 17, 18, 19]:  # Common walkable tiles
                return 0.9  # High walkability
            elif tile in [2, 13]:  # Stone, brick
                return 0.8  # Good walkability
            else:
                return 0.1  # Low walkability for unknown tiles
        else:
            # Traditional world walkability
            if not (0 <= x < self.width and 0 <= y < self.height):
                return 0.0
            return self.walkable[y][x]
    
    def calculate_sub_tile_position(self, grid_x, grid_y, entity_size):
        """Calculate optimal sub-tile position for smoother movement"""
        # Instead of forcing tile center, find the best position within the tile
        base_x = grid_x + 0.5
        base_y = grid_y + 0.5
        
        # Check if we can optimize position based on nearby obstacles
        best_x, best_y = base_x, base_y
        best_score = self.evaluate_position_quality(base_x, base_y, entity_size)
        
        # Try slight offsets to find better positions
        offsets = [(-0.3, 0), (0.3, 0), (0, -0.3), (0, 0.3), (-0.2, -0.2), (0.2, 0.2), (-0.2, 0.2), (0.2, -0.2)]
        
        for dx, dy in offsets:
            test_x = base_x + dx
            test_y = base_y + dy
            
            # Ensure position is still within the tile and valid
            if (grid_x <= test_x < grid_x + 1 and grid_y <= test_y < grid_y + 1 and
                not self.check_collision(test_x, test_y, entity_size)):
                
                score = self.evaluate_position_quality(test_x, test_y, entity_size)
                if score > best_score:
                    best_x, best_y = test_x, test_y
                    best_score = score
        
        return (best_x, best_y)
    
    def evaluate_position_quality(self, x, y, entity_size):
        """Evaluate how good a position is for pathfinding (higher = better)"""
        score = 1.0
        
        # Penalize positions close to obstacles
        for obj in self.objects:
            if obj.blocks_movement:
                distance = math.sqrt((x - obj.x)**2 + (y - obj.y)**2)
                if distance < 1.0:
                    penalty = max(0, 1.0 - distance)
                    score -= penalty * 0.5
        
        # Bonus for positions away from walls
        tile_x, tile_y = int(x), int(y)
        wall_bonus = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x, check_y = tile_x + dx, tile_y + dy
                if (0 <= check_x < self.width and 0 <= check_y < self.height):
                    if self.walkable[check_y][check_x] > 0.5:
                        wall_bonus += 0.1
        
        score += wall_bonus
        return max(0, score)
    
    def create_direct_sub_tile_path(self, start_x, start_y, end_x, end_y, entity_size):
        """Create a direct path with sub-tile precision for short distances"""
        # Check if direct path is clear
        if self.has_line_of_sight((start_x, start_y), (end_x, end_y), entity_size):
            return [(end_x, end_y)]
        
        # If not clear, create intermediate waypoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Find best intermediate position
        best_mid = self.find_best_intermediate_position(start_x, start_y, end_x, end_y, entity_size)
        if best_mid:
            return [best_mid, (end_x, end_y)]
        
        # Fallback to tile center
        return [(int(end_x) + 0.5, int(end_y) + 0.5)]
    
    def find_best_intermediate_position(self, start_x, start_y, end_x, end_y, entity_size):
        """Find the best intermediate position for a short path"""
        # Try positions around the midpoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        candidates = [
            (mid_x, mid_y),
            (mid_x + 0.3, mid_y),
            (mid_x - 0.3, mid_y),
            (mid_x, mid_y + 0.3),
            (mid_x, mid_y - 0.3)
        ]
        
        for pos in candidates:
            if (not self.check_collision(pos[0], pos[1], entity_size) and
                self.has_line_of_sight((start_x, start_y), pos, entity_size) and
                self.has_line_of_sight(pos, (end_x, end_y), entity_size)):
                return pos
        
        return None
    
    def heuristic(self, x1, y1, x2, y2):
        """Heuristic function for A* (Manhattan distance with diagonal movement)"""
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        # Use diagonal distance heuristic
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)
    
    def apply_corner_smoothing(self, path, entity_size):
        """Apply intelligent corner smoothing to the path"""
        if len(path) < 3:
            return path
        
        corners = self.detect_corners_in_path(path)
        if not corners:
            return path
        
        smoothed_path = path.copy()
        
        # Process corners from end to start to maintain indices
        for corner in reversed(corners):
            smoothed_segment = self.create_smooth_corner(
                smoothed_path, 
                corner['index'], 
                corner['severity'],
                entity_size
            )
            
            # Replace sharp corner with smooth curve
            start_idx = max(0, corner['index'] - 1)
            end_idx = min(len(smoothed_path), corner['index'] + 2)
            smoothed_path[start_idx:end_idx] = smoothed_segment
        
        return smoothed_path
    
    def detect_corners_in_path(self, path):
        """Detect corners that need smoothing"""
        corners = []
        
        for i in range(1, len(path) - 1):
            prev_point = path[i - 1]
            current_point = path[i]
            next_point = path[i + 1]
            
            # Calculate angle between segments
            angle = self.calculate_turn_angle(prev_point, current_point, next_point)
            
            # If angle is sharp (> 45 degrees), mark as corner
            if abs(angle) > 45:
                corner_info = {
                    'index': i,
                    'angle': angle,
                    'position': current_point,
                    'severity': min(abs(angle) / 90.0, 1.0)  # 0-1 scale
                }
                corners.append(corner_info)
        
        return corners
    
    def calculate_turn_angle(self, p1, p2, p3):
        """Calculate the turn angle at point p2 between p1->p2 and p2->p3"""
        # Vector from p1 to p2
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        # Vector from p2 to p3
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        # Calculate angle between vectors
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        cross_product = v1[0] * v2[1] - v1[1] * v2[0]
        
        angle = math.degrees(math.atan2(cross_product, dot_product))
        return angle
    
    def create_smooth_corner(self, path, corner_idx, severity, entity_size):
        """Create a smooth curve around a corner"""
        if corner_idx < 1 or corner_idx >= len(path) - 1:
            return [path[corner_idx]]
        
        p0 = path[corner_idx - 1]
        p1 = path[corner_idx]
        p2 = path[corner_idx + 1]
        
        # Calculate curve control points
        curve_distance = 0.2 + (severity * 0.3)  # 0.2 to 0.5 tiles
        
        # Ensure curve doesn't cause collisions
        curve_distance = min(curve_distance, entity_size * 1.5)
        
        # Generate smooth curve points
        curve_points = self.generate_smooth_curve(p0, p1, p2, curve_distance, entity_size)
        
        return curve_points
    
    def generate_smooth_curve(self, p0, p1, p2, curve_distance, entity_size):
        """Generate a smooth curve between three points"""
        # Calculate control points for the curve
        # Direction vectors
        d1 = math.sqrt((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)
        d2 = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        if d1 == 0 or d2 == 0:
            return [p1]
        
        # Normalized direction vectors
        u1 = ((p1[0] - p0[0]) / d1, (p1[1] - p0[1]) / d1)
        u2 = ((p2[0] - p1[0]) / d2, (p2[1] - p1[1]) / d2)
        
        # Control points for the curve
        c1 = (p1[0] - u1[0] * curve_distance, p1[1] - u1[1] * curve_distance)
        c2 = (p1[0] + u2[0] * curve_distance, p1[1] + u2[1] * curve_distance)
        
        # Generate curve points using quadratic Bezier
        curve_points = []
        num_points = max(3, int(curve_distance * 8))  # More points for larger curves
        
        for i in range(num_points + 1):
            t = i / num_points
            # Quadratic Bezier curve: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
            x = (1-t)**2 * c1[0] + 2*(1-t)*t * p1[0] + t**2 * c2[0]
            y = (1-t)**2 * c1[1] + 2*(1-t)*t * p1[1] + t**2 * c2[1]
            
            # Validate curve point for collisions
            if not self.check_collision(x, y, entity_size):
                curve_points.append((x, y))
            else:
                # If curve causes collision, fall back to original point
                curve_points.append(p1)
                break
        
        return curve_points if curve_points else [p1]
    
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
    
    def validate_path_with_entity_simulation(self, path, entity_size):
        """Simulate entity movement along path to detect issues"""
        if len(path) < 2:
            return path
        
        validated_path = [path[0]]  # Always include start
        
        for i in range(1, len(path)):
            current_pos = validated_path[-1]
            target_pos = path[i]
            
            # Simulate movement from current to target
            movement_valid, corrected_pos = self.simulate_movement_step(
                current_pos, target_pos, entity_size
            )
            
            if movement_valid:
                validated_path.append(target_pos)
            else:
                # Find alternative waypoint
                alternative = self.find_alternative_waypoint(
                    current_pos, target_pos, entity_size
                )
                if alternative:
                    validated_path.append(alternative)
                else:
                    # Can't proceed, truncate path
                    break
        
        return validated_path
    
    def simulate_movement_step(self, start, end, entity_size):
        """Simulate movement step and detect collision issues"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return True, end
        
        # Check multiple points along the movement path
        steps = max(int(distance * 4), 3)  # At least 3 steps
        
        for i in range(1, steps + 1):
            t = i / steps
            check_x = start[0] + dx * t
            check_y = start[1] + dy * t
            
            # Use enhanced collision detection
            if self.check_enhanced_collision(check_x, check_y, entity_size):
                # Find the last valid position
                if i == 1:
                    return False, start  # Can't move at all
                else:
                    # Return last valid position
                    valid_t = (i - 1) / steps
                    valid_x = start[0] + dx * valid_t
                    valid_y = start[1] + dy * valid_t
                    return False, (valid_x, valid_y)
        
        return True, end
    
    def find_alternative_waypoint(self, current_pos, target_pos, entity_size):
        """Find an alternative waypoint when direct movement fails"""
        # Try positions around the target
        offsets = [
            (0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3),
            (0.3, 0.3), (-0.3, 0.3), (0.3, -0.3), (-0.3, -0.3)
        ]
        
        for dx, dy in offsets:
            alt_x = target_pos[0] + dx
            alt_y = target_pos[1] + dy
            
            # Check if alternative position is valid and reachable
            if (not self.check_collision(alt_x, alt_y, entity_size) and
                self.has_line_of_sight(current_pos, (alt_x, alt_y), entity_size)):
                return (alt_x, alt_y)
        
        return None
    
    def find_nearest_walkable(self, x, y, entity_size=0.4, max_radius=5):
        """Find the nearest walkable position to the given coordinates"""
        # Check the position itself first
        if self.is_position_walkable_for_pathfinding(x, y, entity_size):
            return x, y
        
        # Search in expanding circles
        for radius in range(1, max_radius + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Only check positions on the edge of the current radius
                    if abs(dx) == radius or abs(dy) == radius:
                        check_x = x + dx
                        check_y = y + dy
                        
                        if self.is_position_walkable_for_pathfinding(check_x, check_y, entity_size):
                            return check_x, check_y
        
        return None, None  # No walkable position found