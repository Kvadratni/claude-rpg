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
    
    # Settlement templates - FIXED: Larger settlements and smaller buildings
    SETTLEMENT_TEMPLATES = {
        'VILLAGE': {
            'size': (35, 35),  # Increased from 25x25
            'buildings': [
                {'name': 'General Store', 'size': (8, 6), 'npc': 'Master Merchant', 'has_shop': True},  # Reduced from 12x8
                {'name': 'Inn', 'size': (8, 6), 'npc': 'Innkeeper', 'has_shop': False},  # Reduced from 10x8
                {'name': 'Blacksmith', 'size': (6, 5), 'npc': 'Master Smith', 'has_shop': True},  # Reduced from 8x6
                {'name': 'Elder House', 'size': (7, 6), 'npc': 'Village Elder', 'has_shop': False},  # Reduced from 10x8
                {'name': 'Guard House', 'size': (6, 5), 'npc': 'Guard Captain', 'has_shop': False}  # Reduced from 8x6
            ],
            'biomes': ['PLAINS', 'FOREST'],
            'safe_radius': 100  # Increased from 70 - much larger safe zone for main village
        },
        'DESERT_OUTPOST': {
            'size': (28, 28),  # Increased from 20x20
            'buildings': [
                {'name': 'Trading Post', 'size': (7, 6), 'npc': 'Caravan Master', 'has_shop': True},  # Reduced from 10x8
                {'name': 'Water Storage', 'size': (5, 5), 'npc': 'Water Keeper', 'has_shop': False},  # Added NPC
                {'name': 'Caravan Rest', 'size': (8, 5), 'npc': 'Desert Guide', 'has_shop': False}  # Reduced from 10x6
            ],
            'biomes': ['DESERT'],
            'safe_radius': 80  # Increased from 56 - larger safe zone for desert outpost
        },
        'SNOW_SETTLEMENT': {
            'size': (25, 25),  # Increased from 18x18
            'buildings': [
                {'name': 'Ranger Station', 'size': (6, 5), 'npc': 'Forest Ranger', 'has_shop': False},  # Reduced from 8x6
                {'name': 'Herbalist Hut', 'size': (6, 5), 'npc': 'Master Herbalist', 'has_shop': True},  # Reduced from 8x6
                {'name': 'Warm Lodge', 'size': (7, 6), 'npc': 'Lodge Keeper', 'has_shop': False}  # Reduced from 10x8
            ],
            'biomes': ['SNOW'],
            'safe_radius': 75  # Increased from 50 - larger safe zone for snow settlement
        },
        'TRADING_POST': {
            'size': (22, 22),  # Increased from 15x15
            'buildings': [
                {'name': 'Trade Hall', 'size': (7, 5), 'npc': 'Trade Master', 'has_shop': True},  # Reduced from 10x6
                {'name': 'Storage', 'size': (5, 5)},  # Reduced from 6x6
                {'name': 'Stable', 'size': (6, 5), 'npc': 'Stable Master', 'has_shop': False}  # Reduced from 8x6
            ],
            'biomes': ['PLAINS', 'FOREST', 'DESERT'],
            'safe_radius': 70  # Increased from 44 - larger safe zone for trading post
        },
        'MINING_CAMP': {
            'size': (30, 30),  # Increased from 20x20
            'buildings': [
                {'name': 'Mine Office', 'size': (6, 5), 'npc': 'Mine Foreman', 'has_shop': True},  # Reduced from 8x6
                {'name': 'Miners Lodge', 'size': (7, 6), 'npc': 'Head Miner', 'has_shop': False},  # Reduced from 10x8
                {'name': 'Tool Shed', 'size': (5, 4)},  # Reduced from 6x6
                {'name': 'Ore Storage', 'size': (6, 5)}  # Reduced from 8x6
            ],
            'biomes': ['SNOW', 'DESERT'],
            'safe_radius': 90  # Increased from 60 - larger safe zone for mining camp
        },
        'FISHING_VILLAGE': {
            'size': (30, 30),  # Increased from 22x22
            'buildings': [
                {'name': 'Fish Market', 'size': (7, 6), 'npc': 'Harbor Master', 'has_shop': True},  # Reduced from 10x8
                {'name': 'Fisherman Hut', 'size': (6, 5), 'npc': 'Master Fisher', 'has_shop': False},  # Reduced from 8x6
                {'name': 'Boat House', 'size': (8, 5)},  # Reduced from 12x6
                {'name': 'Net Storage', 'size': (5, 4)}  # Reduced from 6x6
            ],
            'biomes': ['PLAINS', 'FOREST'],  # Near water areas
            'safe_radius': 85  # Increased from 60 - larger safe zone for fishing village
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
        
        # Try to place multiple settlements of each type for better coverage
        settlement_targets = {
            'VILLAGE': 2,        # Place 2 villages
            'DESERT_OUTPOST': 2, # Place 2 desert outposts  
            'SNOW_SETTLEMENT': 2, # Place 2 snow settlements
            'TRADING_POST': 3,   # Place 3 trading posts (smaller, more common)
            'MINING_CAMP': 1,    # Place 1 mining camp
            'FISHING_VILLAGE': 1 # Place 1 fishing village
        }
        
        for template_name, template_config in self.SETTLEMENT_TEMPLATES.items():
            target_count = settlement_targets.get(template_name, 1)
            placed_count = 0
            
            print(f"Attempting to place {target_count} {template_name} settlements...")
            
            # Try to place multiple settlements of this type
            for attempt in range(target_count * 3):  # 3x attempts per target
                settlement = self.try_place_settlement(template_name, template_config, tiles, biome_map)
                if settlement:
                    settlements.append(settlement)
                    placed_count += 1
                    print(f"  Successfully placed {template_name} #{placed_count} at ({settlement['x']}, {settlement['y']})")
                    
                    if placed_count >= target_count:
                        break
                else:
                    print(f"  Failed to place {template_name} (attempt {attempt + 1})")
            
            print(f"  Final result: {placed_count}/{target_count} {template_name} settlements placed")
        
        print(f"Total settlements placed: {len(settlements)}")
        
        # Debug: Count expected NPCs
        total_expected_npcs = 0
        for settlement in settlements:
            npc_count = sum(1 for building in settlement.get('buildings', []) if building.get('npc'))
            total_expected_npcs += npc_count
            print(f"  {settlement['name']} at ({settlement['x']}, {settlement['y']}): {npc_count} NPCs expected")
        
        print(f"Total NPCs expected from all settlements: {total_expected_npcs}")
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
        
        # Add template name to config for helper methods
        template_config_with_name = template_config.copy()
        template_config_with_name['name'] = template_name
        
        # Place the settlement
        buildings = self.place_settlement_buildings(tiles, x, y, template_config_with_name)
        
        # Mark area as occupied
        self.occupied_areas.append((x, y, settlement_width, settlement_height))
        
        # Add safe zone with much larger radius for better enemy exclusion
        safe_radius = template_config.get('safe_radius', 60)  # Increased from 35 to 60
        center_x = x + settlement_width // 2
        center_y = y + settlement_height // 2
        self.settlement_safe_zones.append((center_x, center_y, safe_radius))
        
        print(f"  Safe zone established: center=({center_x}, {center_y}), radius={safe_radius} tiles")
        
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
        Place buildings for a settlement with proper ground preparation and pathways
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Settlement starting position
            template_config: Settlement configuration
            
        Returns:
            List of placed building information
        """
        settlement_width, settlement_height = template_config['size']
        
        # Step 1: Prepare the settlement ground with biome-appropriate tiles
        self._prepare_settlement_ground(tiles, start_x, start_y, settlement_width, settlement_height, template_config)
        
        # Step 2: Create central feature (plaza, well, market, etc.)
        center_size = min(settlement_width, settlement_height) // 4
        center_start_x = start_x + (settlement_width - center_size) // 2
        center_start_y = start_y + (settlement_height - center_size) // 2
        
        self._create_central_feature(tiles, center_start_x, center_start_y, center_size, template_config)
        
        # Step 3: Place buildings around the center with improved logic
        buildings = template_config['buildings']
        placed_buildings = []
        
        print(f"    Attempting to place {len(buildings)} buildings in settlement...")
        
        for i, building in enumerate(buildings):
            building_width, building_height = building['size']
            building_name = building['name']
            has_npc = 'npc' in building and building['npc']
            
            print(f"      Building {i+1}/{len(buildings)}: {building_name} ({building_width}x{building_height}) - NPC: {has_npc}")
            
            placed = False
            # Try to find a good spot for this building with more attempts
            for attempt in range(100):  # Increased attempts significantly
                # Random position within settlement bounds with minimal margins
                margin = 0  # No margin - use full settlement area
                max_x = settlement_width - building_width - margin * 2
                max_y = settlement_height - building_height - margin * 2
                
                if max_x <= 0 or max_y <= 0:
                    print(f"        Building too large for settlement! Skipping...")
                    break
                
                bx = start_x + margin + random.randint(0, max_x)
                by = start_y + margin + random.randint(0, max_y)
                
                # Check if building would overlap with center square (with smaller margin)
                if self.building_overlaps_area_relaxed(bx, by, building_width, building_height, 
                                                     center_start_x, center_start_y, center_size, center_size):
                    continue
                
                # Check overlap with existing buildings
                overlaps = False
                for pb in placed_buildings:
                    if self.building_overlaps_area_relaxed(bx, by, building_width, building_height,
                                                         pb['x'], pb['y'], pb['width'], pb['height']):
                        overlaps = True
                        break
                
                if overlaps:
                    continue
                
                # Place the building
                self.create_building(tiles, bx, by, building_width, building_height)
                
                placed_buildings.append({
                    'x': bx, 'y': by, 'width': building_width, 'height': building_height,
                    'name': building['name'], 'npc': building.get('npc'),
                    'has_shop': building.get('has_shop', False)
                })
                
                print(f"        Successfully placed {building_name} at ({bx}, {by})")
                placed = True
                break
            
            if not placed:
                print(f"        FAILED to place {building_name} after 100 attempts!")
        
        # Step 4: Create pathways connecting buildings to center
        self._create_pathways(tiles, start_x, start_y, settlement_width, settlement_height, 
                             center_start_x, center_start_y, center_size, placed_buildings, template_config)
        
        # Step 5: Add outdoor furniture and features
        self._add_outdoor_features(tiles, start_x, start_y, settlement_width, settlement_height, 
                                  placed_buildings, template_config)
        
        print(f"    Settlement building placement complete: {len(placed_buildings)}/{len(buildings)} buildings placed")
        npc_buildings = sum(1 for b in placed_buildings if b.get('npc'))
        print(f"    Buildings with NPCs: {npc_buildings}")
        
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
        
        # Add doors with randomized placement on different sides
        self._add_randomized_doors(tiles, start_x, start_y, width, height)
    
    def _add_randomized_doors(self, tiles: List[List[int]], start_x: int, start_y: int, 
                             width: int, height: int) -> None:
        """
        Add doors to buildings with randomized placement on different sides
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Building starting position
            width, height: Building dimensions
        """
        # Define possible door sides with weights
        # Bottom and right are slightly more common (traditional/practical)
        door_sides = ['bottom', 'top', 'left', 'right']
        door_weights = [0.35, 0.2, 0.2, 0.25]  # Bottom slightly favored, but all sides possible
        
        # Choose a random side for the door
        chosen_side = random.choices(door_sides, weights=door_weights)[0]
        
        # Place door based on chosen side
        if chosen_side == 'bottom':
            self._place_door_bottom(tiles, start_x, start_y, width, height)
        elif chosen_side == 'top':
            self._place_door_top(tiles, start_x, start_y, width, height)
        elif chosen_side == 'left':
            self._place_door_left(tiles, start_x, start_y, width, height)
        elif chosen_side == 'right':
            self._place_door_right(tiles, start_x, start_y, width, height)
    
    def _place_door_bottom(self, tiles: List[List[int]], start_x: int, start_y: int, 
                          width: int, height: int) -> None:
        """Place door(s) on the bottom wall of the building"""
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        
        if width >= 6:
            # Double door for larger buildings
            door_x1 = door_center_x - 1
            door_x2 = door_center_x
            
            if (0 <= door_x1 < self.width and 0 <= door_y < self.height and 
                door_x1 > start_x and door_x1 < start_x + width - 1):
                tiles[door_y][door_x1] = 5  # TILE_DOOR
            
            if (0 <= door_x2 < self.width and 0 <= door_y < self.height and 
                door_x2 > start_x and door_x2 < start_x + width - 1):
                tiles[door_y][door_x2] = 5  # TILE_DOOR
        else:
            # Single door for smaller buildings
            if (0 <= door_center_x < self.width and 0 <= door_y < self.height and 
                door_center_x > start_x and door_center_x < start_x + width - 1):
                tiles[door_y][door_center_x] = 5  # TILE_DOOR
    
    def _place_door_top(self, tiles: List[List[int]], start_x: int, start_y: int, 
                       width: int, height: int) -> None:
        """Place door(s) on the top wall of the building"""
        door_center_x = start_x + width // 2
        door_y = start_y
        
        if width >= 6:
            # Double door for larger buildings
            door_x1 = door_center_x - 1
            door_x2 = door_center_x
            
            if (0 <= door_x1 < self.width and 0 <= door_y < self.height and 
                door_x1 > start_x and door_x1 < start_x + width - 1):
                tiles[door_y][door_x1] = 5  # TILE_DOOR
            
            if (0 <= door_x2 < self.width and 0 <= door_y < self.height and 
                door_x2 > start_x and door_x2 < start_x + width - 1):
                tiles[door_y][door_x2] = 5  # TILE_DOOR
        else:
            # Single door for smaller buildings
            if (0 <= door_center_x < self.width and 0 <= door_y < self.height and 
                door_center_x > start_x and door_center_x < start_x + width - 1):
                tiles[door_y][door_center_x] = 5  # TILE_DOOR
    
    def _place_door_left(self, tiles: List[List[int]], start_x: int, start_y: int, 
                        width: int, height: int) -> None:
        """Place door(s) on the left wall of the building"""
        door_x = start_x
        door_center_y = start_y + height // 2
        
        if height >= 6:
            # Double door for taller buildings
            door_y1 = door_center_y - 1
            door_y2 = door_center_y
            
            if (0 <= door_x < self.width and 0 <= door_y1 < self.height and 
                door_y1 > start_y and door_y1 < start_y + height - 1):
                tiles[door_y1][door_x] = 5  # TILE_DOOR
            
            if (0 <= door_x < self.width and 0 <= door_y2 < self.height and 
                door_y2 > start_y and door_y2 < start_y + height - 1):
                tiles[door_y2][door_x] = 5  # TILE_DOOR
        else:
            # Single door for smaller buildings
            if (0 <= door_x < self.width and 0 <= door_center_y < self.height and 
                door_center_y > start_y and door_center_y < start_y + height - 1):
                tiles[door_center_y][door_x] = 5  # TILE_DOOR
    
    def _place_door_right(self, tiles: List[List[int]], start_x: int, start_y: int, 
                         width: int, height: int) -> None:
        """Place door(s) on the right wall of the building"""
        door_x = start_x + width - 1
        door_center_y = start_y + height // 2
        
        if height >= 6:
            # Double door for taller buildings
            door_y1 = door_center_y - 1
            door_y2 = door_center_y
            
            if (0 <= door_x < self.width and 0 <= door_y1 < self.height and 
                door_y1 > start_y and door_y1 < start_y + height - 1):
                tiles[door_y1][door_x] = 5  # TILE_DOOR
            
            if (0 <= door_x < self.width and 0 <= door_y2 < self.height and 
                door_y2 > start_y and door_y2 < start_y + height - 1):
                tiles[door_y2][door_x] = 5  # TILE_DOOR
        else:
            # Single door for smaller buildings
            if (0 <= door_x < self.width and 0 <= door_center_y < self.height and 
                door_center_y > start_y and door_center_y < start_y + height - 1):
                tiles[door_center_y][door_x] = 5  # TILE_DOOR
    
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
        Check if building overlaps with an area (with very small margin for more lenient placement)
        
        Args:
            bx, by, bw, bh: Building position and dimensions
            ax, ay, aw, ah: Area position and dimensions
            
        Returns:
            True if overlap detected
        """
        margin = 0  # No margin - allow buildings to be adjacent
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
    
    def _prepare_settlement_ground(self, tiles: List[List[int]], start_x: int, start_y: int, 
                                  width: int, height: int, template_config: Dict) -> None:
        """
        Prepare settlement ground with biome-appropriate tiles
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Settlement position
            width, height: Settlement dimensions
            template_config: Settlement configuration
        """
        # Determine ground tile based on settlement type and biome
        settlement_name = template_config.get('name', 'VILLAGE')
        biomes = template_config.get('biomes', ['PLAINS'])
        
        # Choose appropriate ground tile
        if 'DESERT' in biomes:
            ground_tile = 16  # TILE_SAND
        elif 'SNOW' in biomes:
            ground_tile = 17  # TILE_SNOW
        elif 'FOREST' in biomes:
            ground_tile = 18  # TILE_FOREST_FLOOR
        else:
            ground_tile = 1   # TILE_DIRT (default for plains settlements)
        
        # Replace all terrain in settlement area with appropriate ground
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Don't replace water tiles
                    if tiles[y][x] != 3:  # TILE_WATER
                        tiles[y][x] = ground_tile
        
        print(f"    Prepared settlement ground with tile type {ground_tile}")
    
    def _create_central_feature(self, tiles: List[List[int]], center_x: int, center_y: int, 
                               size: int, template_config: Dict) -> None:
        """
        Create central feature for settlement (plaza, well, market, etc.)
        
        Args:
            tiles: 2D list of tile types
            center_x, center_y: Center feature position
            size: Size of central feature
            template_config: Settlement configuration
        """
        settlement_name = template_config.get('name', 'VILLAGE')
        
        # Create stone plaza base
        for y in range(center_y, center_y + size):
            for x in range(center_x, center_x + size):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = 2  # TILE_STONE
        
        # Add central feature based on settlement type
        center_center_x = center_x + size // 2
        center_center_y = center_y + size // 2
        
        if settlement_name in ['VILLAGE', 'FISHING_VILLAGE']:
            # Village well (single stone tile in center)
            if 0 <= center_center_x < self.width and 0 <= center_center_y < self.height:
                tiles[center_center_y][center_center_x] = 2  # TILE_STONE (well)
        elif settlement_name == 'TRADING_POST':
            # Market area (larger stone area)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    wx, wy = center_center_x + dx, center_center_y + dy
                    if 0 <= wx < self.width and 0 <= wy < self.height:
                        tiles[wy][wx] = 2  # TILE_STONE
        
        print(f"    Created central feature for {settlement_name}")
    
    def _create_pathways(self, tiles: List[List[int]], start_x: int, start_y: int, 
                        width: int, height: int, center_x: int, center_y: int, center_size: int,
                        buildings: List[Dict], template_config: Dict) -> None:
        """
        Create pathways connecting buildings to the center
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Settlement position
            width, height: Settlement dimensions
            center_x, center_y: Center position
            center_size: Size of central area
            buildings: List of placed buildings
            template_config: Settlement configuration
        """
        # Path tile based on biome
        biomes = template_config.get('biomes', ['PLAINS'])
        if 'DESERT' in biomes:
            path_tile = 2   # TILE_STONE (stone paths in desert)
        elif 'SNOW' in biomes:
            path_tile = 2   # TILE_STONE (stone paths in snow)
        else:
            path_tile = 1   # TILE_DIRT (dirt paths elsewhere)
        
        center_center_x = center_x + center_size // 2
        center_center_y = center_y + center_size // 2
        
        # Create paths from center to each building
        for building in buildings:
            building_center_x = building['x'] + building['width'] // 2
            building_center_y = building['y'] + building['height'] // 2
            
            # Create L-shaped path (horizontal then vertical)
            # Horizontal path
            start_path_x = min(center_center_x, building_center_x)
            end_path_x = max(center_center_x, building_center_x)
            for x in range(start_path_x, end_path_x + 1):
                if 0 <= x < self.width and 0 <= center_center_y < self.height:
                    # Don't overwrite buildings or center
                    if not self._is_building_tile(tiles[center_center_y][x]):
                        tiles[center_center_y][x] = path_tile
            
            # Vertical path
            start_path_y = min(center_center_y, building_center_y)
            end_path_y = max(center_center_y, building_center_y)
            for y in range(start_path_y, end_path_y + 1):
                if 0 <= building_center_x < self.width and 0 <= y < self.height:
                    # Don't overwrite buildings or center
                    if not self._is_building_tile(tiles[y][building_center_x]):
                        tiles[y][building_center_x] = path_tile
        
        print(f"    Created pathways connecting {len(buildings)} buildings")
    
    def _add_outdoor_features(self, tiles: List[List[int]], start_x: int, start_y: int, 
                             width: int, height: int, buildings: List[Dict], 
                             template_config: Dict) -> None:
        """
        Add outdoor furniture and features to settlement
        
        Args:
            tiles: 2D list of tile types
            start_x, start_y: Settlement position
            width, height: Settlement dimensions
            buildings: List of placed buildings
            template_config: Settlement configuration
        """
        # For now, just add some decorative stone tiles around the settlement
        # This could be expanded to include actual outdoor furniture entities
        
        settlement_name = template_config.get('name', 'VILLAGE')
        
        # Add decorative elements based on settlement type
        if settlement_name == 'TRADING_POST':
            # Add some stone markers around the trading post
            for _ in range(3):
                x = start_x + random.randint(2, width - 3)
                y = start_y + random.randint(2, height - 3)
                if (0 <= x < self.width and 0 <= y < self.height and 
                    not self._is_building_tile(tiles[y][x])):
                    tiles[y][x] = 2  # TILE_STONE
        
        print(f"    Added outdoor features for {settlement_name}")
    
    def _is_building_tile(self, tile_type: int) -> bool:
        """
        Check if a tile is part of a building structure
        
        Args:
            tile_type: Tile type to check
            
        Returns:
            True if tile is part of building
        """
        building_tiles = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}  # All wall and door tiles
        return tile_type in building_tiles