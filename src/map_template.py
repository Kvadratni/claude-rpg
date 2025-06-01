"""
Image-based map template system for deterministic map generation
"""

import pygame
import os
from typing import Dict, List, Tuple, Set, Optional

class MapTemplate:
    """
    Handles image-based map templates for deterministic world generation
    """
    
    # Color definitions for map template pixels
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
    
    # Reverse lookup for colors to names
    COLOR_TO_NAME = {v: k for k, v in COLORS.items()}
    
    def __init__(self, template_path: str):
        """Initialize map template from image file"""
        self.template_path = template_path
        self.template_image = None
        self.width = 0
        self.height = 0
        self.occupied_tiles: Set[Tuple[int, int]] = set()
        self.spawn_points: Dict[str, List[Tuple[int, int]]] = {}
        
        self.load_template()
        self.analyze_template()
    
    def load_template(self):
        """Load the template image"""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Map template not found: {self.template_path}")
        
        self.template_image = pygame.image.load(self.template_path)
        self.width = self.template_image.get_width()
        self.height = self.template_image.get_height()
        
        print(f"Loaded map template: {self.width}x{self.height} from {self.template_path}")
    
    def analyze_template(self):
        """Analyze template to find spawn points and validate colors"""
        self.spawn_points = {
            'NPC_SPAWN': [],
            'OBJECT_SPAWN': [],
            'CHEST_SPAWN': [],
            'ENEMY_SPAWN': [],
            'BUILDING': [],
            'DOOR': [],
        }
        
        unknown_colors = set()
        
        for y in range(self.height):
            for x in range(self.width):
                color = self.get_pixel_color(x, y)
                color_name = self.COLOR_TO_NAME.get(color)
                
                if color_name is None:
                    unknown_colors.add(color)
                    continue
                
                # Collect spawn points
                if color_name in self.spawn_points:
                    self.spawn_points[color_name].append((x, y))
                
                # Mark impassable areas as occupied
                if color_name in ['IMPASSABLE', 'WATER']:
                    self.occupied_tiles.add((x, y))
        
        if unknown_colors:
            print(f"Warning: Found {len(unknown_colors)} unknown colors in template:")
            for color in list(unknown_colors)[:5]:  # Show first 5
                print(f"  RGB{color}")
        
        # Print spawn point summary
        for spawn_type, points in self.spawn_points.items():
            if points:
                print(f"Found {len(points)} {spawn_type} locations")
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get RGB color of pixel at coordinates"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.COLORS['IMPASSABLE']  # Out of bounds = impassable
        
        return self.template_image.get_at((x, y))[:3]  # RGB only, ignore alpha
    
    def get_terrain_type(self, x: int, y: int) -> str:
        """Get terrain type name for coordinates"""
        color = self.get_pixel_color(x, y)
        return self.COLOR_TO_NAME.get(color, 'UNKNOWN')
    
    def is_position_available(self, x: int, y: int, size: int = 1) -> bool:
        """Check if area is available for placement"""
        for dx in range(size):
            for dy in range(size):
                check_x, check_y = x + dx, y + dy
                if (check_x, check_y) in self.occupied_tiles:
                    return False
                if not (0 <= check_x < self.width and 0 <= check_y < self.height):
                    return False
        return True
    
    def mark_occupied(self, x: int, y: int, size: int = 1):
        """Mark area as occupied"""
        for dx in range(size):
            for dy in range(size):
                self.occupied_tiles.add((x + dx, y + dy))
    
    def get_spawn_points(self, spawn_type: str) -> List[Tuple[int, int]]:
        """Get all spawn points of a specific type"""
        return self.spawn_points.get(spawn_type, [])
    
    def find_nearest_spawn_point(self, x: int, y: int, spawn_type: str) -> Optional[Tuple[int, int]]:
        """Find nearest spawn point of given type to coordinates"""
        points = self.get_spawn_points(spawn_type)
        if not points:
            return None
        
        min_dist = float('inf')
        nearest = None
        
        for px, py in points:
            dist = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest = (px, py)
        
        return nearest
    
    def get_area_spawn_points(self, center_x: int, center_y: int, radius: int, spawn_type: str) -> List[Tuple[int, int]]:
        """Get spawn points of type within radius of center"""
        points = self.get_spawn_points(spawn_type)
        nearby = []
        
        for px, py in points:
            dist = ((center_x - px) ** 2 + (center_y - py) ** 2) ** 0.5
            if dist <= radius:
                nearby.append((px, py))
        
        return nearby
    
    def validate_template(self) -> List[str]:
        """Validate template and return list of issues"""
        issues = []
        
        # Check for required spawn types
        required_spawns = ['NPC_SPAWN', 'BUILDING']
        for spawn_type in required_spawns:
            if not self.spawn_points.get(spawn_type):
                issues.append(f"No {spawn_type} points found")
        
        # Check that NPCs have nearby buildings
        npc_points = self.get_spawn_points('NPC_SPAWN')
        building_points = self.get_spawn_points('BUILDING')
        
        for nx, ny in npc_points:
            nearest_building = None
            min_dist = float('inf')
            
            for bx, by in building_points:
                dist = ((nx - bx) ** 2 + (ny - by) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_building = (bx, by)
            
            if min_dist > 20:  # NPCs should be near buildings
                issues.append(f"NPC at ({nx}, {ny}) is far from nearest building")
        
        return issues
    
    def create_debug_image(self, output_path: str):
        """Create a debug image showing spawn points overlaid on template"""
        debug_surface = self.template_image.copy()
        
        # Draw spawn points with different colors
        spawn_colors = {
            'NPC_SPAWN': (255, 255, 0),      # Yellow
            'OBJECT_SPAWN': (128, 0, 128),   # Purple  
            'CHEST_SPAWN': (255, 165, 0),    # Orange
            'ENEMY_SPAWN': (255, 0, 255),    # Magenta
        }
        
        for spawn_type, color in spawn_colors.items():
            points = self.get_spawn_points(spawn_type)
            for x, y in points:
                # Draw a small cross to mark spawn points
                pygame.draw.line(debug_surface, color, (x-2, y), (x+2, y), 1)
                pygame.draw.line(debug_surface, color, (x, y-2), (x, y+2), 1)
        
        pygame.image.save(debug_surface, output_path)
        print(f"Debug image saved to: {output_path}")


def create_default_template(width: int, height: int, output_path: str):
    """Create a default map template based on current hardcoded layout"""
    
    # Create a surface for the template
    template = pygame.Surface((width, height))
    template.fill(MapTemplate.COLORS['GRASS'])  # Fill with grass
    
    # Add borders (impassable)
    for x in range(width):
        template.set_at((x, 0), MapTemplate.COLORS['IMPASSABLE'])
        template.set_at((x, height-1), MapTemplate.COLORS['IMPASSABLE'])
    for y in range(height):
        template.set_at((0, y), MapTemplate.COLORS['IMPASSABLE'])
        template.set_at((width-1, y), MapTemplate.COLORS['IMPASSABLE'])
    
    # Central village stone area (85-115, 85-115)
    for x in range(85, 116):
        for y in range(85, 116):
            if 0 <= x < width and 0 <= y < height:
                template.set_at((x, y), MapTemplate.COLORS['STONE'])
    
    # Main roads
    # East-west highway
    for x in range(10, 190):
        if x < width:
            for road_y in [100, 101]:
                if road_y < height:
                    template.set_at((x, road_y), MapTemplate.COLORS['STONE'])
    
    # North-south highway
    for y in range(10, 190):
        if y < height:
            for road_x in [100, 101]:
                if road_x < width:
                    template.set_at((road_x, y), MapTemplate.COLORS['STONE'])
    
    # Add building locations and track NPC positions
    buildings = [
        (70, 80, 15, 10),   # Large shopkeeper's store
        (115, 80, 15, 10),  # Elder's house
        (85, 120, 20, 12),  # Village hall
        (70, 105, 12, 8),   # Blacksmith
        (115, 105, 12, 8),  # Inn/Tavern
        (92, 65, 16, 10),   # Temple/Church
        (60, 92, 10, 10),   # Guard house
        (130, 92, 10, 10),  # Storage house
    ]
    
    # NPC positions mapped to buildings
    npc_positions = {
        (77, 85): 'shopkeeper',   # Inside shopkeeper's store
        (122, 85): 'elder',       # Inside elder's house
        (76, 109): 'blacksmith',  # Inside blacksmith
        (121, 109): 'innkeeper',  # Inside inn
        (100, 70): 'priest',      # Inside temple
        (65, 97): 'guard',        # Inside guard house
    }
    
    for start_x, start_y, w, h in buildings:
        # Mark building outline
        for x in range(start_x, start_x + w):
            for y in range(start_y, start_y + h):
                if 0 <= x < width and 0 <= y < height:
                    # Walls
                    if (x == start_x or x == start_x + w - 1 or 
                        y == start_y or y == start_y + h - 1):
                        template.set_at((x, y), MapTemplate.COLORS['BUILDING'])
                    # Interior - check if this is an NPC position
                    else:
                        if (x, y) in npc_positions:
                            # Mark as NPC spawn but on interior floor
                            template.set_at((x, y), MapTemplate.COLORS['NPC_SPAWN'])
                        else:
                            template.set_at((x, y), MapTemplate.COLORS['INTERIOR'])
        
        # Add doors (center of bottom wall)
        door_x = start_x + w // 2
        door_y = start_y + h - 1
        if 0 <= door_x < width and 0 <= door_y < height:
            template.set_at((door_x, door_y), MapTemplate.COLORS['DOOR'])
    
    # Add water areas (lakes)
    lakes = [
        (150, 150, 20),  # Great Lake
        (40, 140, 12),   # Twin Lake 1
        (60, 155, 10),   # Twin Lake 2
        (100, 40, 8),    # Mountain Lake
    ]
    
    for center_x, center_y, radius in lakes:
        for y in range(max(1, center_y - radius), min(height - 1, center_y + radius)):
            for x in range(max(1, center_x - radius), min(width - 1, center_x + radius)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance < radius - 2:
                    template.set_at((x, y), MapTemplate.COLORS['WATER'])
                elif distance < radius:
                    template.set_at((x, y), MapTemplate.COLORS['DIRT'])  # Shore
    
    # Add forest areas
    forest_regions = [
        (30, 30, 40, 40),   # Dark Forest
        (80, 25, 40, 30),   # Enchanted Grove
        (140, 30, 50, 40),  # Ancient Woods
    ]
    
    for start_x, start_y, w, h in forest_regions:
        for x in range(start_x, min(start_x + w, width)):
            for y in range(start_y, min(start_y + h, height)):
                current_color = template.get_at((x, y))[:3]
                # Only mark as forest if it's currently grass
                if current_color == MapTemplate.COLORS['GRASS']:
                    template.set_at((x, y), MapTemplate.COLORS['FOREST'])
    
    # Add enemy spawn areas in forests and dangerous areas
    enemy_regions = [
        # Dark Forest area
        (35, 35, 30, 30),
        # Ancient Woods
        (145, 35, 40, 30),
        # Around village (patrol enemies)
        (70, 70, 5, 5), (130, 70, 5, 5), (70, 130, 5, 5), (130, 130, 5, 5),
    ]
    
    for start_x, start_y, w, h in enemy_regions:
        for x in range(start_x, min(start_x + w, width)):
            for y in range(start_y, min(start_y + h, height)):
                current_color = template.get_at((x, y))[:3]
                # Only mark as enemy spawn in forest or grass areas
                if current_color in [MapTemplate.COLORS['FOREST'], MapTemplate.COLORS['GRASS']]:
                    # Sparse enemy spawns
                    if (x + y) % 7 == 0:  # Every 7th position roughly
                        template.set_at((x, y), MapTemplate.COLORS['ENEMY_SPAWN'])
    
    # Add object spawn areas (for trees and rocks)
    # Trees in forest areas
    for start_x, start_y, w, h in forest_regions:
        for x in range(start_x, min(start_x + w, width)):
            for y in range(start_y, min(start_y + h, height)):
                current_color = template.get_at((x, y))[:3]
                if current_color == MapTemplate.COLORS['FOREST']:
                    # Dense tree spawns in forests
                    if (x * 3 + y * 7) % 5 == 0:  # Pseudo-random but deterministic
                        template.set_at((x, y), MapTemplate.COLORS['OBJECT_SPAWN'])
    
    # Add chest spawn points
    chest_spawns = [
        (75, 65), (125, 65), (75, 135), (125, 135),  # Near village
        (45, 45), (95, 35), (155, 45),               # In forests
        (25, 35), (175, 35),                         # Mountain areas
    ]
    
    for x, y in chest_spawns:
        if 0 <= x < width and 0 <= y < height:
            template.set_at((x, y), MapTemplate.COLORS['CHEST_SPAWN'])
    
    # Save the template
    pygame.image.save(template, output_path)
    print(f"Created default map template: {output_path}")
    
    return template


if __name__ == "__main__":
    # Initialize pygame for image operations
    pygame.init()
    
    # Create default template
    template_path = "assets/maps/main_world.png"
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    create_default_template(1000, 1000, template_path)
    
    # Test loading the template
    try:
        template = MapTemplate(template_path)
        issues = template.validate_template()
        
        if issues:
            print("Template validation issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Template validation passed!")
        
        # Create debug image
        debug_path = template_path.replace('.png', '_debug.png')
        template.create_debug_image(debug_path)
        
    except Exception as e:
        print(f"Error testing template: {e}")