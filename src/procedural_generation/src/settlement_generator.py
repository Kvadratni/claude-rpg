"""
Settlement Generation Module for Procedural World Generation
Handles placement of settlements with collision detection and building generation
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any


class SettlementGenerator:
    """
    Generates settlements using templates with collision detection
    """
    
    # Settlement templates
    SETTLEMENT_TEMPLATES = {
        'VILLAGE': {
            'size': (25, 25),
            'buildings': [
                {'name': 'General Store', 'size': (12, 8), 'npc': 'Master Merchant', 'has_shop': True},
                {'name': 'Inn', 'size': (10, 8), 'npc': 'Innkeeper', 'has_shop': False},
                {'name': 'Blacksmith', 'size': (8, 6), 'npc': 'Master Smith', 'has_shop': True},
                {'name': 'Elder House', 'size': (10, 8), 'npc': 'Village Elder', 'has_shop': False},
                {'name': 'Guard House', 'size': (8, 6), 'npc': 'Guard Captain', 'has_shop': False}
            ],
            'biomes': ['PLAINS', 'FOREST'],
            'safe_radius': 20
        },
        'DESERT_OUTPOST': {
            'size': (20, 20),
            'buildings': [
                {'name': 'Trading Post', 'size': (10, 8), 'npc': 'Caravan Master', 'has_shop': True},
                {'name': 'Water Storage', 'size': (6, 6)},
                {'name': 'Caravan Rest', 'size': (10, 6)}
            ],
            'biomes': ['DESERT'],
            'safe_radius': 15
        },
        'SNOW_SETTLEMENT': {
            'size': (18, 18),
            'buildings': [
                {'name': 'Ranger Station', 'size': (8, 6), 'npc': 'Forest Ranger', 'has_shop': False},
                {'name': 'Herbalist Hut', 'size': (8, 6), 'npc': 'Master Herbalist', 'has_shop': True},
                {'name': 'Warm Lodge', 'size': (10, 8)}
            ],
            'biomes': ['SNOW'],
            'safe_radius': 15
        }
    }
    
    def __init__(self, width: int, height: int, seed: int = None):
        """
        Initialize settlement generator
        
        Args:
            width: World width in tiles
            height: World height in tiles
            seed: Random seed for deterministic generation
        """
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 1000000)
        
        # Initialize random with seed
        random.seed(self.seed)
        
        # Track placed objects for collision
        self.occupied_areas = []  # List of (x, y, width, height) rectangles
        self.settlement_safe_zones = []  # List of (center_x, center_y, radius)
        
        print(f"SettlementGenerator initialized with seed: {self.seed}")
    
    def place_settlements(self, tiles: List[List[int]], biome_map: List[List[str]]) -> List[Dict]:
        """
        Place settlements using templates with collision detection
        
        Args:
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            
        Returns:
            List of settlement information dictionaries
        """
        settlements = []
        
        # Try to place one settlement of each type
        for template_name, template_config in self.SETTLEMENT_TEMPLATES.items():
            settlement = self.try_place_settlement(template_name, template_config, tiles, biome_map)
            if settlement:
                settlements.append(settlement)
        
        print(f"Placed {len(settlements)} settlements")
        return settlements
    
    def try_place_settlement(self, template_name: str, template_config: Dict, 
                           tiles: List[List[int]], biome_map: List[List[str]], 
                           max_attempts: int = 50) -> Optional[Dict]:
        """
        Try to place a settlement, return placement info if successful
        
        Args:
            template_name: Name of settlement template
            template_config: Settlement configuration
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            max_attempts: Maximum placement attempts
            
        Returns:
            Settlement info dict if successful, None otherwise
        """
        settlement_width, settlement_height = template_config['size']
        suitable_biomes = template_config['biomes']
        
        # Strategy 1: Strict placement (no water tolerance)
        for _ in range(max_attempts // 2):
            x = random.randint(10, self.width - settlement_width - 10)
            y = random.randint(10, self.height - settlement_height - 10)
            
            # Check if biome is suitable
            center_biome = biome_map[y + settlement_height // 2][x + settlement_width // 2]
            if center_biome not in suitable_biomes:
                continue
            
            # Check for collisions with existing settlements
            if self.check_area_collision(x, y, settlement_width, settlement_height):
                continue
            
            # Strict water check (no water allowed)
            if self.has_water_in_area(tiles, x, y, settlement_width, settlement_height, max_water_tiles=0):
                continue
            
            # Success with strict placement
            return self._finalize_settlement_placement(template_name, template_config, tiles, x, y, center_biome)
        
        # Strategy 2: Relaxed placement (allow some water)
        for _ in range(max_attempts // 2):
            x = random.randint(10, self.width - settlement_width - 10)
            y = random.randint(10, self.height - settlement_height - 10)
            
            # Check if biome is suitable
            center_biome = biome_map[y + settlement_height // 2][x + settlement_width // 2]
            if center_biome not in suitable_biomes:
                continue
            
            # Check for collisions with existing settlements
            if self.check_area_collision(x, y, settlement_width, settlement_height):
                continue
            
            # Relaxed water check (allow small amounts)
            if self.has_water_in_area(tiles, x, y, settlement_width, settlement_height, max_water_tiles=5):
                continue
            
            # Success with relaxed placement
            return self._finalize_settlement_placement(template_name, template_config, tiles, x, y, center_biome)
        
        print(f"Failed to place {template_name} after {max_attempts} attempts")
        return None
    
    def _finalize_settlement_placement(self, template_name: str, template_config: Dict, 
                                     tiles: List[List[int]], x: int, y: int, center_biome: str) -> Dict:
        """
        Finalize settlement placement and return settlement info
        
        Args:
            template_name: Name of settlement template
            template_config: Settlement configuration
            tiles: 2D list of tile types
            x, y: Settlement position
            center_biome: Biome at settlement center
            
        Returns:
            Settlement information dictionary
        """
        settlement_width, settlement_height = template_config['size']
        
        # Place the settlement
        buildings = self.place_settlement_buildings(tiles, x, y, template_config)
        
        # Mark area as occupied
        self.occupied_areas.append((x, y, settlement_width, settlement_height))
        
        # Add safe zone
        safe_radius = template_config.get('safe_radius', 15)
        center_x = x + settlement_width // 2
        center_y = y + settlement_height // 2
        self.settlement_safe_zones.append((center_x, center_y, safe_radius))
        
        settlement_info = {
            'name': template_name,
            'x': x,
            'y': y,
            'center_x': center_x,
            'center_y': center_y,
            'size': template_config['size'],
            'buildings': buildings,
            'biome': center_biome
        }
        
        print(f"Placed {template_name} at ({x}, {y}) in {center_biome} biome")
        return settlement_info
    
    def place_settlement_buildings(self, tiles: List[List[int]], start_x: int, start_y: int, 
                                 template_config: Dict) -> List[Dict]:
        """
        Place buildings for a settlement with improved placement logic
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Settlement starting position
            template_config: Settlement configuration
            
        Returns:
            List of placed building information
        """
        settlement_width, settlement_height = template_config['size']
        
        # Create smaller stone square in center to leave more room for buildings
        center_size = min(settlement_width, settlement_height) // 3  # Reduced from // 2
        center_start_x = start_x + (settlement_width - center_size) // 2
        center_start_y = start_y + (settlement_height - center_size) // 2
        
        for x in range(center_start_x, center_start_x + center_size):
            for y in range(center_start_y, center_start_y + center_size):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = 2  # TILE_STONE
        
        # Place buildings around the center with improved logic
        buildings = template_config['buildings']
        placed_buildings = []
        
        for building in buildings:
            building_width, building_height = building['size']
            
            # Try to find a good spot for this building with more attempts
            for attempt in range(50):  # Increased from 20
                # Random position within settlement bounds with better margins
                margin = 1  # Reduced margin
                bx = start_x + margin + random.randint(0, settlement_width - building_width - margin * 2)
                by = start_y + margin + random.randint(0, settlement_height - building_height - margin * 2)
                
                # Check if building would overlap with center square (with smaller margin)
                if self.building_overlaps_area_relaxed(bx, by, building_width, building_height, 
                                                     center_start_x, center_start_y, center_size, center_size):
                    continue
                
                if any(self.building_overlaps_area_relaxed(bx, by, building_width, building_height,
                                                         pb['x'], pb['y'], pb['width'], pb['height'])
                       for pb in placed_buildings):
                    continue
                
                # Place the building
                self.create_building(tiles, bx, by, building_width, building_height)
                
                placed_buildings.append({
                    'x': bx, 'y': by, 'width': building_width, 'height': building_height,
                    'name': building['name'], 'npc': building.get('npc'),
                    'has_shop': building.get('has_shop', False)
                })
                break
        
        return placed_buildings
    
    def create_building(self, tiles: List[List[int]], start_x: int, start_y: int, 
                       width: int, height: int) -> None:
        """
        Create a building structure using enhanced building system with proper corners
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Building starting position
            width, height: Building dimensions
        """
        # Building interior floor - use brick tiles for more realistic interiors
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = 13  # TILE_BRICK
        
        # Building walls - use enhanced wall system with proper corners
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Skip interior
                    if (x > start_x and x < start_x + width - 1 and 
                        y > start_y and y < start_y + height - 1):
                        continue
                    
                    # Determine wall type based on position
                    is_top_edge = (y == start_y)
                    is_bottom_edge = (y == start_y + height - 1)
                    is_left_edge = (x == start_x)
                    is_right_edge = (x == start_x + width - 1)
                    
                    # Set corner tiles first
                    if is_top_edge and is_left_edge:
                        tiles[y][x] = 6  # TILE_WALL_CORNER_TL
                    elif is_top_edge and is_right_edge:
                        tiles[y][x] = 7  # TILE_WALL_CORNER_TR
                    elif is_bottom_edge and is_left_edge:
                        tiles[y][x] = 8  # TILE_WALL_CORNER_BL
                    elif is_bottom_edge and is_right_edge:
                        tiles[y][x] = 9  # TILE_WALL_CORNER_BR
                    # Then set edge walls (horizontal/vertical)
                    elif is_top_edge or is_bottom_edge:
                        # Horizontal walls (top and bottom edges)
                        if random.random() < 0.2:  # 20% chance for windows
                            tiles[y][x] = 14  # TILE_WALL_WINDOW_HORIZONTAL
                        else:
                            tiles[y][x] = 10  # TILE_WALL_HORIZONTAL
                    elif is_left_edge or is_right_edge:
                        # Vertical walls (left and right edges)
                        if random.random() < 0.15:  # 15% chance for windows
                            tiles[y][x] = 15  # TILE_WALL_WINDOW_VERTICAL
                        else:
                            tiles[y][x] = 11  # TILE_WALL_VERTICAL
                    else:
                        # This shouldn't happen, but fallback to regular wall
                        tiles[y][x] = 4  # TILE_WALL
        
        # Add double doors (2 tiles wide) - replace bottom wall sections
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        
        # Create 2-tile wide door centered on the building
        door_x1 = door_center_x - 1
        door_x2 = door_center_x
        
        # Make sure both door positions are valid and within the building wall
        if (0 <= door_x1 < self.width and 0 <= door_y < self.height and 
            door_x1 > start_x and door_x1 < start_x + width - 1):
            tiles[door_y][door_x1] = 5  # TILE_DOOR
        
        if (0 <= door_x2 < self.width and 0 <= door_y < self.height and 
            door_x2 > start_x and door_x2 < start_x + width - 1):
            tiles[door_y][door_x2] = 5  # TILE_DOOR
    
    # Helper methods
    def check_area_collision(self, x: int, y: int, width: int, height: int) -> bool:
        """
        Check if area collides with existing occupied areas
        
        Args:
            x, y: Area position
            width, height: Area dimensions
            
        Returns:
            True if collision detected
        """
        new_rect = (x, y, width, height)
        for existing_rect in self.occupied_areas:
            if self.rectangles_overlap(new_rect, existing_rect):
                return True
        return False
    
    def rectangles_overlap(self, rect1: Tuple[int, int, int, int], 
                          rect2: Tuple[int, int, int, int]) -> bool:
        """
        Check if two rectangles overlap
        
        Args:
            rect1, rect2: Rectangle tuples (x, y, width, height)
            
        Returns:
            True if rectangles overlap
        """
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
    
    def building_overlaps_area_relaxed(self, bx: int, by: int, bw: int, bh: int, 
                                     ax: int, ay: int, aw: int, ah: int) -> bool:
        """
        Check if building overlaps with an area (with smaller margin)
        
        Args:
            bx, by, bw, bh: Building position and dimensions
            ax, ay, aw, ah: Area position and dimensions
            
        Returns:
            True if overlap detected
        """
        margin = 1  # Reduced from 2
        return not (bx + bw + margin <= ax or ax + aw + margin <= bx or 
                   by + bh + margin <= ay or ay + ah + margin <= by)
    
    def has_water_in_area(self, tiles: List[List[int]], x: int, y: int, 
                         width: int, height: int, max_water_tiles: int = 3) -> bool:
        """
        Check if area contains too many water tiles
        
        Args:
            tiles: 2D list of tile types
            x, y: Area position
            width, height: Area dimensions
            max_water_tiles: Maximum allowed water tiles
            
        Returns:
            True if too much water
        """
        water_count = 0
        
        for cy in range(y, y + height):
            for cx in range(x, x + width):
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    if tiles[cy][cx] == 3:  # TILE_WATER
                        water_count += 1
                        if water_count > max_water_tiles:
                            return True
        
        # Allow small amounts of water (like a pond or stream)
        return False
    
    def is_in_safe_zone(self, x: int, y: int) -> bool:
        """
        Check if position is within any settlement safe zone
        
        Args:
            x, y: Position to check
            
        Returns:
            True if in safe zone
        """
        for center_x, center_y, radius in self.settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < radius:
                return True
        return False
    
    def distance_to_nearest_settlement(self, x: int, y: int) -> float:
        """
        Calculate distance to nearest settlement
        
        Args:
            x, y: Position to check
            
        Returns:
            Distance to nearest settlement
        """
        if not self.settlement_safe_zones:
            return float('inf')
        
        min_distance = float('inf')
        for center_x, center_y, _ in self.settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            min_distance = min(min_distance, distance)
        
        return min_distance