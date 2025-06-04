"""
Compass UI component for the RPG
"""

import pygame
import math


class Compass:
    """Compass UI component showing cardinal directions"""
    
    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.size = 80
        self.position = (0, 0)  # Will be set to top-right corner
        
        # Colors
        self.bg_color = (40, 40, 40)
        self.border_color = (120, 120, 120)
        self.needle_color = (255, 50, 50)
        self.text_color = (255, 255, 255)
        self.tick_color = (200, 200, 200)
        
        # Initialize font
        try:
            self.font = pygame.font.Font(None, 16)
        except:
            self.font = pygame.font.Font(None, 16)
    
    def set_position(self, screen_width, screen_height):
        """Set compass position to top-right corner"""
        margin = 20
        self.position = (screen_width - self.size - margin, margin)
    
    def render(self, screen: pygame.Surface, player_direction=0):
        """Render the compass
        
        Args:
            screen: Surface to render on
            player_direction: Player's facing direction in degrees (0 = North, 90 = East, etc.)
        """
        x, y = self.position
        center_x = x + self.size // 2
        center_y = y + self.size // 2
        radius = self.size // 2 - 5
        
        # Draw background circle
        pygame.draw.circle(screen, self.bg_color, (center_x, center_y), radius)
        pygame.draw.circle(screen, self.border_color, (center_x, center_y), radius, 2)
        
        # Draw cardinal direction markers
        directions = [
            (0, "N", (255, 255, 255)),    # North - White
            (90, "E", (200, 200, 200)),   # East - Light Gray
            (180, "S", (200, 200, 200)),  # South - Light Gray
            (270, "W", (200, 200, 200))   # West - Light Gray
        ]
        
        for angle, label, color in directions:
            # Calculate position for direction marker
            rad = math.radians(angle - 90)  # -90 to make 0 degrees point up (North)
            marker_x = center_x + (radius - 15) * math.cos(rad)
            marker_y = center_y + (radius - 15) * math.sin(rad)
            
            # Draw direction label
            text_surface = self.font.render(label, True, color)
            text_rect = text_surface.get_rect(center=(marker_x, marker_y))
            screen.blit(text_surface, text_rect)
            
            # Draw tick marks
            tick_start_x = center_x + (radius - 8) * math.cos(rad)
            tick_start_y = center_y + (radius - 8) * math.sin(rad)
            tick_end_x = center_x + (radius - 3) * math.cos(rad)
            tick_end_y = center_y + (radius - 3) * math.sin(rad)
            
            pygame.draw.line(screen, self.tick_color, 
                           (tick_start_x, tick_start_y), 
                           (tick_end_x, tick_end_y), 2)
        
        # Draw intermediate tick marks (NE, SE, SW, NW)
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle - 90)
            tick_start_x = center_x + (radius - 6) * math.cos(rad)
            tick_start_y = center_y + (radius - 6) * math.sin(rad)
            tick_end_x = center_x + (radius - 2) * math.cos(rad)
            tick_end_y = center_y + (radius - 2) * math.sin(rad)
            
            pygame.draw.line(screen, self.tick_color, 
                           (tick_start_x, tick_start_y), 
                           (tick_end_x, tick_end_y), 1)
        
        # Draw north needle (always points up)
        needle_length = radius - 20
        north_rad = math.radians(-90)  # Always point up (North)
        
        # North needle (red)
        needle_tip_x = center_x + needle_length * math.cos(north_rad)
        needle_tip_y = center_y + needle_length * math.sin(north_rad)
        
        # Draw needle as a triangle
        needle_points = [
            (needle_tip_x, needle_tip_y),  # Tip
            (center_x - 3, center_y + 3),  # Left base
            (center_x + 3, center_y + 3)   # Right base
        ]
        pygame.draw.polygon(screen, self.needle_color, needle_points)
        
        # Draw center dot
        pygame.draw.circle(screen, self.text_color, (center_x, center_y), 3)
        
        # Optional: Draw player direction indicator
        if player_direction != 0:
            self._draw_player_direction(screen, center_x, center_y, radius, player_direction)
    
    def _draw_player_direction(self, screen, center_x, center_y, radius, direction):
        """Draw a small indicator showing player's facing direction"""
        # Convert direction to radians (0 = North, clockwise)
        rad = math.radians(direction - 90)
        
        # Draw a small arrow showing player direction
        arrow_length = radius - 25
        arrow_tip_x = center_x + arrow_length * math.cos(rad)
        arrow_tip_y = center_y + arrow_length * math.sin(rad)
        
        # Draw a small blue arrow
        arrow_color = (100, 150, 255)
        pygame.draw.circle(screen, arrow_color, (int(arrow_tip_x), int(arrow_tip_y)), 3)
        pygame.draw.line(screen, arrow_color, (center_x, center_y), (arrow_tip_x, arrow_tip_y), 1)


class DirectionHelper:
    """Helper class for calculating directions and spawning locations"""
    
    @staticmethod
    def get_direction_name(angle):
        """Convert angle to direction name"""
        # Normalize angle to 0-360
        angle = angle % 360
        
        if angle < 22.5 or angle >= 337.5:
            return "North"
        elif angle < 67.5:
            return "Northeast"
        elif angle < 112.5:
            return "East"
        elif angle < 157.5:
            return "Southeast"
        elif angle < 202.5:
            return "South"
        elif angle < 247.5:
            return "Southwest"
        elif angle < 292.5:
            return "West"
        else:
            return "Northwest"
    
    @staticmethod
    def get_direction_vector(direction_name):
        """Get x,y vector for a direction name"""
        direction_vectors = {
            "North": (0, -1),
            "Northeast": (1, -1),
            "East": (1, 0),
            "Southeast": (1, 1),
            "South": (0, 1),
            "Southwest": (-1, 1),
            "West": (-1, 0),
            "Northwest": (-1, -1)
        }
        return direction_vectors.get(direction_name, (0, -1))
    
    @staticmethod
    def find_spawn_location(player_x, player_y, direction_name, distance_range=(20, 40), level_bounds=None):
        """Find a suitable spawn location in the given direction
        
        Args:
            player_x, player_y: Player's current position
            direction_name: Direction to spawn (e.g., "North", "Northeast")
            distance_range: Tuple of (min_distance, max_distance) from player
            level_bounds: Tuple of (width, height) for level boundaries
            
        Returns:
            Tuple of (x, y) spawn coordinates
        """
        import random
        
        dx, dy = DirectionHelper.get_direction_vector(direction_name)
        min_dist, max_dist = distance_range
        
        # Random distance within range
        distance = random.randint(min_dist, max_dist)
        
        # Calculate base position
        spawn_x = player_x + dx * distance
        spawn_y = player_y + dy * distance
        
        # Add some randomness to avoid exact straight lines
        spawn_x += random.randint(-5, 5)
        spawn_y += random.randint(-5, 5)
        
        # Clamp to level bounds if provided
        if level_bounds:
            width, height = level_bounds
            spawn_x = max(5, min(width - 5, spawn_x))
            spawn_y = max(5, min(height - 5, spawn_y))
        
        return int(spawn_x), int(spawn_y)
    
    @staticmethod
    def calculate_angle_to_target(from_x, from_y, to_x, to_y):
        """Calculate angle from one point to another (in degrees)"""
        dx = to_x - from_x
        dy = to_y - from_y
        angle = math.degrees(math.atan2(dy, dx))
        # Convert to compass bearing (0 = North, clockwise)
        compass_angle = (angle + 90) % 360
        return compass_angle