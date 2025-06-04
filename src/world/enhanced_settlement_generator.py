"""
Enhanced Settlement Generator with varied building shapes, road networks, and biome-specific architecture
Integrates with the existing settlement pattern system for sophisticated town layouts
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any
from .settlement_patterns import SettlementPatternGenerator, SettlementPattern


class EnhancedSettlementGenerator:
    """
    Enhanced settlement generator that creates varied, realistic settlements with:
    - Complex building shapes (L-shaped, T-shaped, courtyards)
    - Road and pathway networks
    - Biome-specific architectural styles
    - District-based layouts
    """
    
    # Tile constants (matching level constants)
    TILE_GRASS = 0
    TILE_DIRT = 1
    TILE_STONE = 2
    TILE_WATER = 3
    TILE_WALL = 4
    TILE_DOOR = 5
    TILE_WALL_CORNER_TL = 6
    TILE_WALL_CORNER_TR = 7
    TILE_WALL_CORNER_BL = 8
    TILE_WALL_CORNER_BR = 9
    TILE_WALL_HORIZONTAL = 10
    TILE_WALL_VERTICAL = 11
    TILE_WALL_WINDOW_HORIZONTAL = 14
    TILE_WALL_WINDOW_VERTICAL = 15
    TILE_BRICK = 13
    TILE_SAND = 16
    TILE_SNOW = 17
    TILE_FOREST_FLOOR = 18
    TILE_SWAMP = 19
    
    # Building shape templates
    BUILDING_SHAPES = {
        'rectangle': {
            'pattern': [(0, 0, 1, 1)],  # Single rectangle
            'door_positions': ['bottom_center']
        },
        'L_shape': {
            'pattern': [
                (0, 0, 0.6, 0.7),  # Main section
                (0.6, 0.3, 0.4, 0.4)  # Extension
            ],
            'door_positions': ['bottom_center', 'right_center']
        },
        'T_shape': {
            'pattern': [
                (0.2, 0, 0.6, 0.7),  # Main vertical section
                (0, 0.5, 1, 0.3)     # Horizontal extension
            ],
            'door_positions': ['bottom_center', 'left_center', 'right_center']
        },
        'courtyard': {
            'pattern': [
                (0, 0, 1, 0.3),      # Top section
                (0, 0.7, 1, 0.3),    # Bottom section
                (0, 0.3, 0.25, 0.4), # Left section
                (0.75, 0.3, 0.25, 0.4) # Right section
            ],
            'door_positions': ['courtyard_entrances']
        },
        'cross': {
            'pattern': [
                (0.3, 0, 0.4, 1),    # Vertical bar
                (0, 0.3, 1, 0.4)     # Horizontal bar
            ],
            'door_positions': ['all_sides']
        }
    }
    
    # Road patterns for different settlement sizes
    ROAD_PATTERNS = {
        'small': {
            'type': 'cross',
            'main_roads': [(0.5, 0, 0.5, 1), (0, 0.5, 1, 0.5)],
            'secondary_roads': []
        },
        'medium': {
            'type': 'grid',
            'main_roads': [(0.5, 0, 0.5, 1), (0, 0.5, 1, 0.5)],
            'secondary_roads': [(0.25, 0, 0.25, 1), (0.75, 0, 0.75, 1), (0, 0.25, 1, 0.25), (0, 0.75, 1, 0.75)]
        },
        'large': {
            'type': 'radial',
            'main_roads': [(0.5, 0, 0.5, 1), (0, 0.5, 1, 0.5)],
            'secondary_roads': [(0.2, 0, 0.2, 1), (0.8, 0, 0.8, 1), (0, 0.2, 1, 0.2), (0, 0.8, 1, 0.8)],
            'diagonal_roads': [(0, 0, 1, 1), (0, 1, 1, 0)]  # Diagonal connections
        }
    }
    
    def __init__(self, width: int, height: int, seed: int = None):
        """Initialize the enhanced settlement generator"""
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 1000000)
        
        # Initialize pattern generator
        self.pattern_generator = SettlementPatternGenerator()
        
        # Track placed objects for collision
        self.occupied_areas = []
        self.settlement_safe_zones = []
        
        print(f"EnhancedSettlementGenerator initialized with seed: {self.seed}")
    
    def generate_enhanced_settlement(self, tiles: List[List[int]], start_x: int, start_y: int, 
                                   settlement_type: str, biome: str, seed: int = None) -> Dict[str, Any]:
        """
        Generate an enhanced settlement with sophisticated layout
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Settlement starting position
            settlement_type: Type of settlement to generate
            biome: Biome for architectural adaptation
            seed: Seed for deterministic generation
            
        Returns:
            Settlement information dictionary
        """
        # Use provided seed or generate one based on position
        if seed is None:
            seed = hash((start_x, start_y, settlement_type, biome)) % (2**31)
        
        # Create deterministic random for this settlement
        settlement_random = random.Random(seed)
        
        # Get appropriate pattern for settlement type with variety
        pattern = self.pattern_generator.get_pattern(settlement_type, seed)
        
        # Adapt pattern to biome
        adapted_pattern = self.pattern_generator.adapt_pattern_to_biome(pattern, biome)
        
        # Apply the pattern to tiles
        self._apply_pattern_to_tiles(tiles, start_x, start_y, adapted_pattern)
        
        # Generate enhanced buildings with varied shapes
        buildings = self._generate_enhanced_buildings(tiles, start_x, start_y, adapted_pattern, biome, settlement_random)
        
        # Create road network
        self._create_road_network(tiles, start_x, start_y, adapted_pattern, biome)
        
        # Add architectural details
        self._add_architectural_details(tiles, start_x, start_y, adapted_pattern, biome, settlement_random)
        
        # Mark area as occupied
        self.occupied_areas.append((start_x, start_y, pattern.width, pattern.height))
        
        settlement_info = {
            'name': settlement_type,
            'x': start_x,
            'y': start_y,
            'center_x': start_x + pattern.width // 2,
            'center_y': start_y + pattern.height // 2,
            'size': (pattern.width, pattern.height),
            'buildings': buildings,
            'biome': biome,
            'pattern_used': pattern.name,
            'architectural_style': self._get_architectural_style(biome),
            'seed': seed
        }
        
        print(f"Generated enhanced {settlement_type} at ({start_x}, {start_y}) in {biome} biome using {pattern.name} pattern")
        return settlement_info
    
    def _apply_pattern_to_tiles(self, tiles: List[List[int]], start_x: int, start_y: int, 
                               pattern: SettlementPattern) -> None:
        """Apply the settlement pattern to the tile grid"""
        for y in range(pattern.height):
            for x in range(pattern.width):
                world_x = start_x + x
                world_y = start_y + y
                
                if 0 <= world_x < self.width and 0 <= world_y < self.height:
                    pattern_tile = pattern.get_tile_at(x, y)
                    tiles[world_y][world_x] = pattern_tile
    
    def _generate_enhanced_buildings(self, tiles: List[List[int]], start_x: int, start_y: int, 
                                   pattern: SettlementPattern, biome: str, settlement_random: random.Random) -> List[Dict[str, Any]]:
        """Generate buildings with varied shapes and architectural styles"""
        buildings = []
        
        for building_info in pattern.get_building_positions():
            building_x = start_x + building_info['x']
            building_y = start_y + building_info['y']
            building_width = building_info['width']
            building_height = building_info['height']
            building_type = building_info['type']
            
            # Choose building shape based on type, size, and randomization
            shape_name = self._choose_building_shape(building_type, building_width, building_height, settlement_random)
            
            # Create the building with chosen shape
            self._create_shaped_building(tiles, building_x, building_y, building_width, 
                                       building_height, shape_name, biome, settlement_random)
            
            buildings.append({
                'x': building_x,
                'y': building_y,
                'width': building_width,
                'height': building_height,
                'type': building_type,
                'shape': shape_name,
                'architectural_style': self._get_architectural_style(biome)
            })
        
        return buildings
    
    def _choose_building_shape(self, building_type: str, width: int, height: int, settlement_random: random.Random) -> str:
        """Choose appropriate building shape based on type, size, and randomization"""
        # Define shape probabilities based on building type and size
        if width >= 6 and height >= 6:
            # Large buildings - can have complex shapes
            if building_type in ['town_hall', 'cathedral', 'grand_market', 'temple', 'church']:
                # Important religious/government buildings favor complex shapes
                shape_options = ['courtyard', 'cross', 'T_shape', 'L_shape', 'rectangle']
                weights = [0.3, 0.25, 0.2, 0.15, 0.1]
            elif building_type in ['inn', 'market', 'guildhall', 'grand_inn', 'armory']:
                # Commercial/social buildings favor practical shapes
                shape_options = ['L_shape', 'T_shape', 'rectangle', 'courtyard']
                weights = [0.35, 0.3, 0.25, 0.1]
            elif building_type in ['noble_house', 'merchant_house', 'warm_lodge']:
                # Residential buildings favor L-shapes and rectangles
                shape_options = ['L_shape', 'rectangle', 'T_shape']
                weights = [0.5, 0.3, 0.2]
            else:
                # Generic large buildings
                shape_options = ['rectangle', 'L_shape', 'T_shape']
                weights = [0.5, 0.3, 0.2]
        elif width >= 4 and height >= 4:
            # Medium buildings - some variety
            if building_type in ['shop', 'blacksmith', 'inn', 'market_stall']:
                # Commercial buildings can be L-shaped
                shape_options = ['rectangle', 'L_shape']
                weights = [0.7, 0.3]
            elif building_type in ['house', 'cottage', 'hut']:
                # Residential buildings mostly rectangular with some L-shapes
                shape_options = ['rectangle', 'L_shape']
                weights = [0.8, 0.2]
            else:
                # Generic medium buildings
                shape_options = ['rectangle', 'L_shape']
                weights = [0.75, 0.25]
        else:
            # Small buildings are always rectangular
            return 'rectangle'
        
        # Select shape based on weights
        return settlement_random.choices(shape_options, weights=weights)[0]
    
    def _create_shaped_building(self, tiles: List[List[int]], start_x: int, start_y: int, 
                               width: int, height: int, shape_name: str, biome: str, settlement_random: random.Random) -> None:
        """Create a building with the specified shape"""
        shape_info = self.BUILDING_SHAPES[shape_name]
        
        # Clear the area first
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = self._get_biome_floor_tile(biome)
        
        # Create each section of the building
        for section in shape_info['pattern']:
            section_x = start_x + int(section[0] * width)
            section_y = start_y + int(section[1] * height)
            section_width = max(1, int(section[2] * width))
            section_height = max(1, int(section[3] * height))
            
            self._create_building_section(tiles, section_x, section_y, section_width, 
                                        section_height, biome, settlement_random)
        
        # Add doors based on shape
        self._add_building_doors(tiles, start_x, start_y, width, height, shape_info, biome)
    
    def _create_building_section(self, tiles: List[List[int]], start_x: int, start_y: int, 
                               width: int, height: int, biome: str, settlement_random: random.Random) -> None:
        """Create a single rectangular section of a building"""
        # Interior floor
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = self._get_biome_interior_tile(biome)
        
        # Walls with proper corners
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Skip interior
                    if (x > start_x and x < start_x + width - 1 and 
                        y > start_y and y < start_y + height - 1):
                        continue
                    
                    # Determine wall type
                    is_top = (y == start_y)
                    is_bottom = (y == start_y + height - 1)
                    is_left = (x == start_x)
                    is_right = (x == start_x + width - 1)
                    
                    # Set appropriate wall tile
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_top or is_bottom:
                        # Add windows to horizontal walls
                        if settlement_random.random() < self._get_window_chance(biome):
                            tiles[y][x] = self.TILE_WALL_WINDOW_HORIZONTAL
                        else:
                            tiles[y][x] = self.TILE_WALL_HORIZONTAL
                    elif is_left or is_right:
                        # Add windows to vertical walls
                        if settlement_random.random() < self._get_window_chance(biome):
                            tiles[y][x] = self.TILE_WALL_WINDOW_VERTICAL
                        else:
                            tiles[y][x] = self.TILE_WALL_VERTICAL
                    else:
                        tiles[y][x] = self.TILE_WALL
    
    def _add_building_doors(self, tiles: List[List[int]], start_x: int, start_y: int, 
                           width: int, height: int, shape_info: Dict, biome: str) -> None:
        """Add doors to the building based on its shape"""
        door_positions = shape_info['door_positions']
        
        for door_pos in door_positions:
            if door_pos == 'bottom_center':
                door_x = start_x + width // 2
                door_y = start_y + height - 1
                if 0 <= door_x < self.width and 0 <= door_y < self.height:
                    tiles[door_y][door_x] = self.TILE_DOOR
            elif door_pos == 'top_center':
                door_x = start_x + width // 2
                door_y = start_y
                if 0 <= door_x < self.width and 0 <= door_y < self.height:
                    tiles[door_y][door_x] = self.TILE_DOOR
            elif door_pos == 'left_center':
                door_x = start_x
                door_y = start_y + height // 2
                if 0 <= door_x < self.width and 0 <= door_y < self.height:
                    tiles[door_y][door_x] = self.TILE_DOOR
            elif door_pos == 'right_center':
                door_x = start_x + width - 1
                door_y = start_y + height // 2
                if 0 <= door_x < self.width and 0 <= door_y < self.height:
                    tiles[door_y][door_x] = self.TILE_DOOR
    
    def _create_road_network(self, tiles: List[List[int]], start_x: int, start_y: int, 
                           pattern: SettlementPattern, biome: str) -> None:
        """Create a road network for the settlement"""
        # Determine road pattern based on settlement size
        if pattern.width <= 12:
            road_pattern = self.ROAD_PATTERNS['small']
        elif pattern.width <= 20:
            road_pattern = self.ROAD_PATTERNS['medium']
        else:
            road_pattern = self.ROAD_PATTERNS['large']
        
        road_tile = self._get_biome_road_tile(biome)
        
        # Create main roads
        for road in road_pattern['main_roads']:
            self._create_road_segment(tiles, start_x, start_y, pattern.width, pattern.height, 
                                    road, road_tile, width=2)
        
        # Create secondary roads
        for road in road_pattern['secondary_roads']:
            self._create_road_segment(tiles, start_x, start_y, pattern.width, pattern.height, 
                                    road, road_tile, width=1)
        
        # Create diagonal roads for large settlements
        if 'diagonal_roads' in road_pattern:
            for road in road_pattern['diagonal_roads']:
                self._create_diagonal_road(tiles, start_x, start_y, pattern.width, pattern.height, 
                                         road, road_tile)
    
    def _create_road_segment(self, tiles: List[List[int]], start_x: int, start_y: int, 
                           settlement_width: int, settlement_height: int, 
                           road_spec: Tuple[float, float, float, float], 
                           road_tile: int, width: int = 1) -> None:
        """Create a road segment"""
        x1 = start_x + int(road_spec[0] * settlement_width)
        y1 = start_y + int(road_spec[1] * settlement_height)
        x2 = start_x + int(road_spec[2] * settlement_width)
        y2 = start_y + int(road_spec[3] * settlement_height)
        
        # Create road line
        if x1 == x2:  # Vertical road
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for offset in range(-width//2, width//2 + 1):
                    road_x = x1 + offset
                    if 0 <= road_x < self.width and 0 <= y < self.height:
                        # Don't overwrite buildings
                        if tiles[y][road_x] not in [self.TILE_WALL, self.TILE_DOOR, self.TILE_BRICK]:
                            tiles[y][road_x] = road_tile
        else:  # Horizontal road
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for offset in range(-width//2, width//2 + 1):
                    road_y = y1 + offset
                    if 0 <= x < self.width and 0 <= road_y < self.height:
                        # Don't overwrite buildings
                        if tiles[road_y][x] not in [self.TILE_WALL, self.TILE_DOOR, self.TILE_BRICK]:
                            tiles[road_y][x] = road_tile
    
    def _create_diagonal_road(self, tiles: List[List[int]], start_x: int, start_y: int, 
                            settlement_width: int, settlement_height: int, 
                            road_spec: Tuple[float, float, float, float], 
                            road_tile: int) -> None:
        """Create a diagonal road"""
        x1 = start_x + int(road_spec[0] * settlement_width)
        y1 = start_y + int(road_spec[1] * settlement_height)
        x2 = start_x + int(road_spec[2] * settlement_width)
        y2 = start_y + int(road_spec[3] * settlement_height)
        
        # Use Bresenham's line algorithm for diagonal roads
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        x, y = x1, y1
        x_inc = 1 if x1 < x2 else -1
        y_inc = 1 if y1 < y2 else -1
        error = dx - dy
        
        while True:
            if 0 <= x < self.width and 0 <= y < self.height:
                # Don't overwrite buildings
                if tiles[y][x] not in [self.TILE_WALL, self.TILE_DOOR, self.TILE_BRICK]:
                    tiles[y][x] = road_tile
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * error
            if e2 > -dy:
                error -= dy
                x += x_inc
            if e2 < dx:
                error += dx
                y += y_inc
    
    def _add_architectural_details(self, tiles: List[List[int]], start_x: int, start_y: int, 
                                 pattern: SettlementPattern, biome: str, settlement_random: random.Random) -> None:
        """Add biome-specific architectural details"""
        # Add fountains, statues, gardens, etc. based on biome
        center_x = start_x + pattern.width // 2
        center_y = start_y + pattern.height // 2
        
        if biome == 'DESERT':
            # Add oasis or water feature
            self._add_water_feature(tiles, center_x, center_y, 2)
        elif biome == 'FOREST':
            # Add garden areas
            self._add_garden_areas(tiles, start_x, start_y, pattern.width, pattern.height, settlement_random)
        elif biome == 'SNOW':
            # Add fire pits or warming areas
            self._add_warming_areas(tiles, center_x, center_y)
        elif biome == 'SWAMP':
            # Add raised walkways
            self._add_raised_walkways(tiles, start_x, start_y, pattern.width, pattern.height, settlement_random)
    
    def _add_water_feature(self, tiles: List[List[int]], center_x: int, center_y: int, radius: int) -> None:
        """Add a water feature like a fountain or oasis"""
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= radius:
                        # Don't overwrite buildings
                        if tiles[y][x] not in [self.TILE_WALL, self.TILE_DOOR, self.TILE_BRICK]:
                            tiles[y][x] = self.TILE_WATER
    
    def _add_garden_areas(self, tiles: List[List[int]], start_x: int, start_y: int, 
                         width: int, height: int, settlement_random: random.Random) -> None:
        """Add small garden areas throughout the settlement"""
        for _ in range(3):  # Add 3 small gardens
            garden_x = start_x + settlement_random.randint(2, width - 4)
            garden_y = start_y + settlement_random.randint(2, height - 4)
            
            for y in range(garden_y, garden_y + 2):
                for x in range(garden_x, garden_x + 2):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        # Don't overwrite buildings or roads
                        if tiles[y][x] == self.TILE_DIRT:
                            tiles[y][x] = self.TILE_GRASS
    
    def _add_warming_areas(self, tiles: List[List[int]], center_x: int, center_y: int) -> None:
        """Add warming areas like fire pits"""
        if 0 <= center_x < self.width and 0 <= center_y < self.height:
            # Don't overwrite buildings
            if tiles[center_y][center_x] not in [self.TILE_WALL, self.TILE_DOOR, self.TILE_BRICK]:
                tiles[center_y][center_x] = self.TILE_STONE  # Fire pit base
    
    def _add_raised_walkways(self, tiles: List[List[int]], start_x: int, start_y: int, 
                           width: int, height: int, settlement_random: random.Random) -> None:
        """Add raised walkways for swamp settlements"""
        # Add some stone pathways
        for _ in range(2):
            path_y = start_y + settlement_random.randint(2, height - 3)
            for x in range(start_x + 1, start_x + width - 1):
                if 0 <= x < self.width and 0 <= path_y < self.height:
                    if tiles[path_y][x] == self.TILE_SWAMP:
                        tiles[path_y][x] = self.TILE_STONE
    
    # Helper methods for biome-specific tiles
    def _get_biome_floor_tile(self, biome: str) -> int:
        """Get appropriate floor tile for biome"""
        biome_floors = {
            'DESERT': self.TILE_SAND,
            'SNOW': self.TILE_SNOW,
            'FOREST': self.TILE_FOREST_FLOOR,
            'SWAMP': self.TILE_SWAMP,
            'PLAINS': self.TILE_DIRT
        }
        return biome_floors.get(biome, self.TILE_DIRT)
    
    def _get_biome_interior_tile(self, biome: str) -> int:
        """Get appropriate interior tile for biome"""
        # Most interiors use brick, but some biomes might differ
        return self.TILE_BRICK
    
    def _get_biome_road_tile(self, biome: str) -> int:
        """Get appropriate road tile for biome"""
        biome_roads = {
            'DESERT': self.TILE_SAND,
            'SNOW': self.TILE_STONE,  # Cleared stone paths in snow
            'FOREST': self.TILE_DIRT,
            'SWAMP': self.TILE_STONE,  # Raised stone walkways
            'PLAINS': self.TILE_STONE
        }
        return biome_roads.get(biome, self.TILE_STONE)
    
    def _get_window_chance(self, biome: str) -> float:
        """Get window probability based on biome"""
        biome_windows = {
            'DESERT': 0.1,   # Fewer windows in desert (heat)
            'SNOW': 0.05,    # Very few windows in cold
            'FOREST': 0.25,  # More windows in pleasant forest
            'SWAMP': 0.15,   # Some windows but not many
            'PLAINS': 0.2    # Standard window rate
        }
        return biome_windows.get(biome, 0.2)
    
    def _get_architectural_style(self, biome: str) -> str:
        """Get architectural style name for biome"""
        styles = {
            'DESERT': 'Adobe Desert Style',
            'SNOW': 'Northern Lodge Style',
            'FOREST': 'Woodland Cottage Style',
            'SWAMP': 'Stilted Marsh Style',
            'PLAINS': 'Classic Village Style'
        }
        return styles.get(biome, 'Generic Style')