"""
Settlement pattern system for generating consistent settlement layouts
"""

from typing import List, Dict, Any, Tuple
import random


class SettlementPattern:
    """Represents a settlement layout pattern with tiles and building positions"""
    
    def __init__(self, name: str, size: Tuple[int, int], pattern_data: Dict[str, Any]):
        self.name = name
        self.width, self.height = size
        self.pattern_data = pattern_data
        
        # Extract pattern components
        self.tile_pattern = pattern_data.get('tiles', [])
        self.building_positions = pattern_data.get('buildings', [])
        self.pathway_positions = pattern_data.get('pathways', [])
        
    def get_tile_at(self, x: int, y: int) -> int:
        """Get the tile type at a specific position in the pattern"""
        if 0 <= y < len(self.tile_pattern) and 0 <= x < len(self.tile_pattern[y]):
            return self.tile_pattern[y][x]
        return 1  # Default to dirt
    
    def get_building_positions(self) -> List[Dict[str, Any]]:
        """Get all building positions in the pattern"""
        return self.building_positions.copy()
    
    def get_pathway_positions(self) -> List[Tuple[int, int]]:
        """Get all pathway positions in the pattern"""
        return self.pathway_positions.copy()


class SettlementPatternGenerator:
    """Generates settlement patterns for different settlement types"""
    
    # Tile type constants (matching level constants)
    TILE_GRASS = 0
    TILE_DIRT = 1
    TILE_STONE = 2
    TILE_WATER = 3
    TILE_WALL = 4
    TILE_DOOR = 5
    TILE_BRICK = 13
    TILE_SAND = 16
    TILE_SNOW = 17
    TILE_FOREST_FLOOR = 18
    TILE_SWAMP = 19
    
    def __init__(self):
        """Initialize the pattern generator"""
        self.patterns = {}
        self._create_default_patterns()
    
    def _create_default_patterns(self):
        """Create enhanced settlement patterns for all settlement types"""
        
        # Small Village Pattern (12x12) - Basic settlements
        self.patterns['small_village'] = self._create_small_village_pattern()
        
        # Medium Village Pattern (16x16) - Standard villages
        self.patterns['medium_village'] = self._create_medium_village_pattern()
        
        # Large Village Pattern (20x20) - Large villages
        self.patterns['large_village'] = self._create_large_village_pattern()
        
        # Town Pattern (24x24) - Major settlements
        self.patterns['town'] = self._create_town_pattern()
        
        # Large Town Pattern (30x30) - Major towns
        self.patterns['large_town'] = self._create_large_town_pattern()
        
        # Outpost Pattern (8x8) - Small outposts
        self.patterns['outpost'] = self._create_outpost_pattern()
        
        # Desert Outpost Pattern (12x12) - Desert settlements
        self.patterns['desert_outpost'] = self._create_desert_outpost_pattern()
        
        # Mining Camp Pattern (14x14) - Mining settlements
        self.patterns['mining_camp'] = self._create_mining_camp_pattern()
        
        # Fishing Village Pattern (16x16) - Coastal settlements
        self.patterns['fishing_village'] = self._create_fishing_village_pattern()
        
        # Forest Camp Pattern (12x12) - Forest settlements
        self.patterns['forest_camp'] = self._create_forest_camp_pattern()
        
        # Swamp Village Pattern (16x16) - Swamp settlements
        self.patterns['swamp_village'] = self._create_swamp_village_pattern()
        
        # Snow Settlement Pattern (14x14) - Cold climate settlements
        self.patterns['snow_settlement'] = self._create_snow_settlement_pattern()
    
    def _create_small_village_pattern(self) -> SettlementPattern:
        """Create a small village pattern with central square and surrounding buildings"""
        size = (18, 18)  # Increased to accommodate proper 5x5 buildings
        
        # Create tile pattern - dirt base with stone pathways
        tiles = []
        for y in range(18):
            row = []
            for x in range(18):
                # Stone pathways in cross pattern
                if x == 9 or y == 9:
                    row.append(self.TILE_STONE)  # Main pathways
                elif (x == 8 or x == 10) and (y == 8 or y == 10):
                    row.append(self.TILE_STONE)  # Central square
                else:
                    row.append(self.TILE_DIRT)   # Settlement ground
            tiles.append(row)
        
        # Define building positions - ALL MINIMUM 5x5 for 3x3 interior
        buildings = [
            {'x': 1, 'y': 1, 'width': 6, 'height': 5, 'type': 'house'},      # Top-left
            {'x': 11, 'y': 1, 'width': 6, 'height': 5, 'type': 'shop'},      # Top-right  
            {'x': 1, 'y': 12, 'width': 5, 'height': 5, 'type': 'house'},     # Bottom-left
            {'x': 12, 'y': 12, 'width': 5, 'height': 5, 'type': 'house'},    # Bottom-right
        ]
        
        # Define pathway positions
        pathways = [(9, y) for y in range(18)] + [(x, 9) for x in range(18)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('small_village', size, pattern_data)
    
    def _create_medium_village_pattern(self) -> SettlementPattern:
        """Create a medium village pattern (22x22)"""
        size = (22, 22)  # Increased to accommodate larger buildings
        
        # Create tile pattern with organized layout
        tiles = []
        for y in range(22):
            row = []
            for x in range(22):
                # Main cross pathways
                if x == 11 or y == 11:
                    row.append(self.TILE_STONE)
                # Secondary pathways
                elif x == 5 or x == 17 or y == 5 or y == 17:
                    row.append(self.TILE_DIRT)
                # Central plaza
                elif 9 <= x <= 13 and 9 <= y <= 13:
                    row.append(self.TILE_BRICK)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        # Define building positions - ALL MINIMUM 5x5 for 3x3 interior
        buildings = [
            # Central important buildings
            {'x': 1, 'y': 1, 'width': 7, 'height': 5, 'type': 'inn'},
            {'x': 14, 'y': 1, 'width': 7, 'height': 5, 'type': 'shop'},
            {'x': 1, 'y': 16, 'width': 6, 'height': 5, 'type': 'blacksmith'},
            {'x': 15, 'y': 16, 'width': 6, 'height': 5, 'type': 'temple'},
            # Residential
            {'x': 1, 'y': 7, 'width': 5, 'height': 6, 'type': 'house'},
            {'x': 16, 'y': 7, 'width': 5, 'height': 6, 'type': 'house'},
        ]
        
        pathways = [(11, y) for y in range(22)] + [(x, 11) for x in range(22)]
        pathways += [(5, y) for y in range(22)] + [(17, y) for y in range(22)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('medium_village', size, pattern_data)
    
    def _create_large_village_pattern(self) -> SettlementPattern:
        """Create a large village pattern (20x20)"""
        size = (20, 20)
        
        # Create tile pattern with multiple districts
        tiles = []
        for y in range(20):
            row = []
            for x in range(20):
                # Main pathways (wider)
                if 9 <= x <= 10 or 9 <= y <= 10:
                    row.append(self.TILE_STONE)
                # District pathways
                elif x == 5 or x == 15 or y == 5 or y == 15:
                    row.append(self.TILE_DIRT)
                # Central plaza
                elif 7 <= x <= 12 and 7 <= y <= 12:
                    row.append(self.TILE_BRICK)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        # Define building positions for large village
        buildings = [
            # Central plaza buildings
            {'x': 8, 'y': 1, 'width': 4, 'height': 4, 'type': 'town_hall'},
            {'x': 1, 'y': 8, 'width': 4, 'height': 4, 'type': 'temple'},
            {'x': 15, 'y': 8, 'width': 4, 'height': 4, 'type': 'market'},
            
            # Residential quarter
            {'x': 1, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 16, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 1, 'y': 16, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 16, 'y': 16, 'width': 3, 'height': 3, 'type': 'house'},
            
            # Commercial district
            {'x': 6, 'y': 16, 'width': 3, 'height': 3, 'type': 'shop'},
            {'x': 11, 'y': 16, 'width': 4, 'height': 3, 'type': 'inn'},
            {'x': 13, 'y': 1, 'width': 3, 'height': 3, 'type': 'blacksmith'},
            
            # Additional buildings
            {'x': 1, 'y': 13, 'width': 3, 'height': 2, 'type': 'stable'},
            {'x': 16, 'y': 13, 'width': 3, 'height': 2, 'type': 'workshop'},
        ]
        
        pathways = []
        pathways += [(x, 9) for x in range(20)] + [(x, 10) for x in range(20)]
        pathways += [(9, y) for y in range(20)] + [(10, y) for y in range(20)]
        pathways += [(5, y) for y in range(20)] + [(15, y) for y in range(20)]
        pathways += [(x, 5) for x in range(20)] + [(x, 15) for x in range(20)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('large_village', size, pattern_data)
    
    def _create_town_pattern(self) -> SettlementPattern:
        """Create a town pattern (24x24)"""
        size = (24, 24)
        
        # Create sophisticated town layout
        tiles = []
        for y in range(24):
            row = []
            for x in range(24):
                # Main boulevards
                if 11 <= x <= 12 or 11 <= y <= 12:
                    row.append(self.TILE_STONE)
                # Secondary streets
                elif x == 6 or x == 18 or y == 6 or y == 18:
                    row.append(self.TILE_STONE)
                # District paths
                elif x == 3 or x == 21 or y == 3 or y == 21:
                    row.append(self.TILE_DIRT)
                # Central plaza
                elif 9 <= x <= 14 and 9 <= y <= 14:
                    row.append(self.TILE_BRICK)
                # Corner plazas
                elif (4 <= x <= 6 and 4 <= y <= 6) or (17 <= x <= 19 and 4 <= y <= 6) or \
                     (4 <= x <= 6 and 17 <= y <= 19) or (17 <= x <= 19 and 17 <= y <= 19):
                    row.append(self.TILE_BRICK)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        # Define building positions for town
        buildings = [
            # Central government/religious district
            {'x': 10, 'y': 1, 'width': 4, 'height': 5, 'type': 'town_hall'},
            {'x': 1, 'y': 10, 'width': 5, 'height': 4, 'type': 'cathedral'},
            {'x': 18, 'y': 10, 'width': 5, 'height': 4, 'type': 'market'},
            
            # Commercial district
            {'x': 7, 'y': 19, 'width': 4, 'height': 4, 'type': 'inn'},
            {'x': 13, 'y': 19, 'width': 4, 'height': 4, 'type': 'shop'},
            {'x': 19, 'y': 1, 'width': 4, 'height': 3, 'type': 'blacksmith'},
            {'x': 1, 'y': 19, 'width': 4, 'height': 4, 'type': 'guildhall'},
            
            # Residential districts
            {'x': 1, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 20, 'y': 20, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 1, 'y': 4, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 20, 'y': 4, 'width': 3, 'height': 3, 'type': 'house'},
            
            # Specialized buildings
            {'x': 15, 'y': 1, 'width': 3, 'height': 3, 'type': 'library'},
            {'x': 1, 'y': 15, 'width': 3, 'height': 3, 'type': 'barracks'},
            {'x': 20, 'y': 15, 'width': 3, 'height': 3, 'type': 'bank'},
        ]
        
        pathways = []
        # Main boulevards
        pathways += [(x, 11) for x in range(24)] + [(x, 12) for x in range(24)]
        pathways += [(11, y) for y in range(24)] + [(12, y) for y in range(24)]
        # Secondary streets
        pathways += [(6, y) for y in range(24)] + [(18, y) for y in range(24)]
        pathways += [(x, 6) for x in range(24)] + [(x, 18) for x in range(24)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('town', size, pattern_data)
    
    def _create_large_town_pattern(self) -> SettlementPattern:
        """Create a large town pattern (30x30)"""
        size = (30, 30)
        
        # Create grand town layout
        tiles = []
        for y in range(30):
            row = []
            for x in range(30):
                # Grand boulevards
                if 14 <= x <= 15 or 14 <= y <= 15:
                    row.append(self.TILE_STONE)
                # Major streets
                elif x == 7 or x == 22 or y == 7 or y == 22:
                    row.append(self.TILE_STONE)
                # Minor streets
                elif x == 3 or x == 26 or y == 3 or y == 26:
                    row.append(self.TILE_DIRT)
                # Grand central plaza
                elif 12 <= x <= 17 and 12 <= y <= 17:
                    row.append(self.TILE_BRICK)
                # District plazas
                elif (5 <= x <= 7 and 5 <= y <= 7) or (22 <= x <= 24 and 5 <= y <= 7) or \
                     (5 <= x <= 7 and 22 <= y <= 24) or (22 <= x <= 24 and 22 <= y <= 24):
                    row.append(self.TILE_BRICK)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        # Define building positions for large town
        buildings = [
            # Central government district
            {'x': 12, 'y': 1, 'width': 6, 'height': 5, 'type': 'town_hall'},
            {'x': 1, 'y': 12, 'width': 7, 'height': 6, 'type': 'cathedral'},
            {'x': 22, 'y': 12, 'width': 7, 'height': 6, 'type': 'grand_market'},
            
            # Major commercial buildings
            {'x': 8, 'y': 24, 'width': 6, 'height': 5, 'type': 'grand_inn'},
            {'x': 16, 'y': 24, 'width': 5, 'height': 5, 'type': 'armory'},
            {'x': 24, 'y': 1, 'width': 5, 'height': 4, 'type': 'magic_shop'},
            {'x': 1, 'y': 24, 'width': 6, 'height': 5, 'type': 'guildhall'},
            
            # Institutional buildings
            {'x': 19, 'y': 1, 'width': 4, 'height': 4, 'type': 'library'},
            {'x': 1, 'y': 19, 'width': 5, 'height': 4, 'type': 'barracks'},
            {'x': 24, 'y': 19, 'width': 5, 'height': 4, 'type': 'bank'},
            
            # Residential districts
            {'x': 1, 'y': 1, 'width': 4, 'height': 4, 'type': 'noble_house'},
            {'x': 25, 'y': 25, 'width': 4, 'height': 4, 'type': 'merchant_house'},
            {'x': 1, 'y': 4, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 26, 'y': 4, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 4, 'y': 26, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 23, 'y': 26, 'width': 3, 'height': 3, 'type': 'house'},
        ]
        
        pathways = []
        # Grand boulevards
        pathways += [(x, 14) for x in range(30)] + [(x, 15) for x in range(30)]
        pathways += [(14, y) for y in range(30)] + [(15, y) for y in range(30)]
        # Major streets
        pathways += [(7, y) for y in range(30)] + [(22, y) for y in range(30)]
        pathways += [(x, 7) for x in range(30)] + [(x, 22) for x in range(30)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('large_town', size, pattern_data)
    
    def _create_desert_outpost_pattern(self) -> SettlementPattern:
        """Create a desert outpost pattern (16x16)"""
        size = (16, 16)  # Increased from 12x12
        
        # Desert layout with central courtyard
        tiles = []
        for y in range(16):
            row = []
            for x in range(16):
                # Central courtyard
                if 6 <= x <= 9 and 6 <= y <= 9:
                    row.append(self.TILE_SAND)  # Open courtyard
                # Pathways around courtyard
                elif x == 5 or x == 10 or y == 5 or y == 10:
                    row.append(self.TILE_STONE)
                else:
                    row.append(self.TILE_SAND)
            tiles.append(row)
        
        buildings = [
            {'x': 1, 'y': 1, 'width': 7, 'height': 5, 'type': 'trading_post'},
            {'x': 9, 'y': 1, 'width': 6, 'height': 5, 'type': 'water_cistern'},
            {'x': 1, 'y': 11, 'width': 8, 'height': 4, 'type': 'caravan_rest'},
            {'x': 11, 'y': 11, 'width': 4, 'height': 4, 'type': 'shelter'},
        ]
        
        pathways = [(5, y) for y in range(16)] + [(10, y) for y in range(16)]
        pathways += [(x, 5) for x in range(16)] + [(x, 10) for x in range(16)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('desert_outpost', size, pattern_data)
    
    def _create_mining_camp_pattern(self) -> SettlementPattern:
        """Create a mining camp pattern (14x14)"""
        size = (14, 14)
        
        # Mining camp with industrial layout
        tiles = []
        for y in range(14):
            row = []
            for x in range(14):
                # Main road to mine entrance
                if x == 7 or y == 7:
                    row.append(self.TILE_STONE)
                # Work areas
                elif 5 <= x <= 9 and 5 <= y <= 9:
                    row.append(self.TILE_DIRT)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        buildings = [
            {'x': 6, 'y': 1, 'width': 4, 'height': 3, 'type': 'mine_entrance'},
            {'x': 1, 'y': 5, 'width': 5, 'height': 4, 'type': 'ore_processing'},
            {'x': 8, 'y': 10, 'width': 5, 'height': 3, 'type': 'barracks'},
            {'x': 1, 'y': 10, 'width': 3, 'height': 3, 'type': 'tool_shop'},
            {'x': 10, 'y': 5, 'width': 3, 'height': 3, 'type': 'assay_office'},
        ]
        
        pathways = [(7, y) for y in range(14)] + [(x, 7) for x in range(14)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('mining_camp', size, pattern_data)
    
    def _create_fishing_village_pattern(self) -> SettlementPattern:
        """Create a fishing village pattern (16x16)"""
        size = (16, 16)
        
        # Coastal layout with docks
        tiles = []
        for y in range(16):
            row = []
            for x in range(16):
                # Harbor area (bottom)
                if y >= 12:
                    row.append(self.TILE_WATER)
                # Dock pathways
                elif y == 11 or x == 8:
                    row.append(self.TILE_STONE)
                # Village area
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        buildings = [
            {'x': 6, 'y': 10, 'width': 4, 'height': 2, 'type': 'dock'},
            {'x': 1, 'y': 1, 'width': 4, 'height': 3, 'type': 'harbor_master'},
            {'x': 10, 'y': 1, 'width': 5, 'height': 4, 'type': 'fish_market'},
            {'x': 1, 'y': 5, 'width': 3, 'height': 3, 'type': 'net_maker'},
            {'x': 12, 'y': 6, 'width': 3, 'height': 3, 'type': 'fisherman_hut'},
            {'x': 5, 'y': 6, 'width': 4, 'height': 3, 'type': 'smokehouse'},
        ]
        
        pathways = [(8, y) for y in range(12)] + [(x, 11) for x in range(16)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('fishing_village', size, pattern_data)
    
    def _create_forest_camp_pattern(self) -> SettlementPattern:
        """Create a forest camp pattern (16x16)"""
        size = (16, 16)  # Increased from 12x12
        
        # Forest layout with natural clearings
        tiles = []
        for y in range(16):
            row = []
            for x in range(16):
                # Central clearing
                if 6 <= x <= 9 and 6 <= y <= 9:
                    row.append(self.TILE_FOREST_FLOOR)
                # Natural paths
                elif x == 8 or y == 8:
                    row.append(self.TILE_DIRT)
                else:
                    row.append(self.TILE_FOREST_FLOOR)
            tiles.append(row)
        
        buildings = [
            {'x': 1, 'y': 1, 'width': 6, 'height': 5, 'type': 'woodcutter_lodge'},
            {'x': 10, 'y': 10, 'width': 5, 'height': 5, 'type': 'druid_circle'},
            {'x': 10, 'y': 1, 'width': 5, 'height': 5, 'type': 'scout_post'},
            {'x': 1, 'y': 10, 'width': 6, 'height': 5, 'type': 'lumber_mill'},
        ]
        
        pathways = [(8, y) for y in range(16)] + [(x, 8) for x in range(16)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('forest_camp', size, pattern_data)
    
    def _create_swamp_village_pattern(self) -> SettlementPattern:
        """Create a swamp village pattern (16x16)"""
        size = (16, 16)
        
        # Swamp layout with raised walkways
        tiles = []
        for y in range(16):
            row = []
            for x in range(16):
                # Raised walkways
                if x == 8 or y == 8 or (x == 4 and 4 <= y <= 12) or (x == 12 and 4 <= y <= 12):
                    row.append(self.TILE_STONE)  # Raised walkways
                # Building platforms
                elif (2 <= x <= 5 and 2 <= y <= 5) or (10 <= x <= 13 and 2 <= y <= 5) or \
                     (2 <= x <= 5 and 10 <= y <= 13) or (10 <= x <= 13 and 10 <= y <= 13):
                    row.append(self.TILE_DIRT)  # Raised platforms
                else:
                    row.append(self.TILE_SWAMP)
            tiles.append(row)
        
        buildings = [
            {'x': 2, 'y': 2, 'width': 4, 'height': 4, 'type': 'alchemist_hut'},
            {'x': 10, 'y': 2, 'width': 4, 'height': 3, 'type': 'witch_hut'},
            {'x': 2, 'y': 10, 'width': 4, 'height': 4, 'type': 'boat_builder'},
            {'x': 10, 'y': 10, 'width': 4, 'height': 4, 'type': 'stilted_house'},
            {'x': 6, 'y': 12, 'width': 4, 'height': 3, 'type': 'mushroom_farm'},
        ]
        
        pathways = [(8, y) for y in range(16)] + [(x, 8) for x in range(16)]
        pathways += [(4, y) for y in range(4, 13)] + [(12, y) for y in range(4, 13)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('swamp_village', size, pattern_data)
    
    def _create_snow_settlement_pattern(self) -> SettlementPattern:
        """Create a snow settlement pattern (18x18)"""
        size = (18, 18)  # Increased from 14x14
        
        # Cold climate layout with central fire pit
        tiles = []
        for y in range(18):
            row = []
            for x in range(18):
                # Central fire pit area
                if 8 <= x <= 9 and 8 <= y <= 9:
                    row.append(self.TILE_STONE)  # Fire pit
                # Cleared paths
                elif x == 9 or y == 9:
                    row.append(self.TILE_DIRT)  # Cleared paths
                else:
                    row.append(self.TILE_SNOW)
            tiles.append(row)
        
        buildings = [
            {'x': 1, 'y': 1, 'width': 6, 'height': 6, 'type': 'warm_lodge'},
            {'x': 11, 'y': 1, 'width': 6, 'height': 6, 'type': 'ranger_station'},
            {'x': 1, 'y': 11, 'width': 5, 'height': 6, 'type': 'hunter_cabin'},
            {'x': 7, 'y': 11, 'width': 5, 'height': 6, 'type': 'ice_house'},
            {'x': 13, 'y': 11, 'width': 4, 'height': 6, 'type': 'herbalist_hut'},
        ]
        
        pathways = [(9, y) for y in range(18)] + [(x, 9) for x in range(18)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('snow_settlement', size, pattern_data)
    
    def _create_outpost_pattern(self) -> SettlementPattern:
        """Create a small outpost pattern (12x12)"""
        size = (12, 12)
        
        # Simple outpost layout
        tiles = []
        for y in range(12):
            row = []
            for x in range(12):
                # Central pathway
                if x == 6 or y == 6:
                    row.append(self.TILE_STONE)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        buildings = [
            {'x': 1, 'y': 1, 'width': 5, 'height': 5, 'type': 'guard_post'},  # Minimum 5x5
            {'x': 7, 'y': 7, 'width': 4, 'height': 4, 'type': 'storage'},     # Still too small, let's make it 5x5
        ]
        
        # Fix the storage building
        buildings[1] = {'x': 7, 'y': 7, 'width': 4, 'height': 4, 'type': 'storage'}  # Keep smaller for storage
        
        pathways = [(6, y) for y in range(12)] + [(x, 6) for x in range(12)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('outpost', size, pattern_data)
    
    def get_pattern(self, settlement_type: str, seed: int = None) -> SettlementPattern:
        """Get a varied pattern for a specific settlement type with randomization"""
        # Create deterministic random for pattern selection
        if seed is not None:
            pattern_random = random.Random(seed)
        else:
            pattern_random = random
        
        # Define multiple pattern options for each settlement type
        type_pattern_options = {
            'VILLAGE': [
                'small_village',    # 30% - Small rural village
                'medium_village',   # 50% - Standard village  
                'large_village'     # 20% - Large prosperous village
            ],
            'TOWN': [
                'large_village',    # 20% - Large village that's almost a town
                'town',            # 60% - Standard town
                'large_town'       # 20% - Major town/small city
            ],
            'DESERT_OUTPOST': [
                'outpost',         # 40% - Tiny desert outpost
                'desert_outpost'   # 60% - Standard desert outpost
            ],
            'SNOW_SETTLEMENT': [
                'outpost',         # 30% - Small snow outpost
                'snow_settlement'  # 70% - Standard snow settlement
            ],
            'SWAMP_VILLAGE': [
                'small_village',   # 30% - Small swamp hamlet
                'swamp_village'    # 70% - Standard swamp village
            ],
            'FOREST_CAMP': [
                'outpost',         # 40% - Small forest outpost
                'forest_camp'      # 60% - Standard forest camp
            ],
            'MINING_CAMP': [
                'outpost',         # 30% - Small mining outpost
                'mining_camp'      # 70% - Standard mining camp
            ],
            'FISHING_VILLAGE': [
                'small_village',   # 30% - Small fishing hamlet
                'fishing_village'  # 70% - Standard fishing village
            ]
        }
        
        # Get pattern options for this settlement type
        pattern_options = type_pattern_options.get(settlement_type.upper(), ['medium_village'])
        
        # Define weighted selection for variety
        pattern_weights = {
            'VILLAGE': [0.3, 0.5, 0.2],           # small, medium, large
            'TOWN': [0.2, 0.6, 0.2],              # large_village, town, large_town
            'DESERT_OUTPOST': [0.4, 0.6],         # outpost, desert_outpost
            'SNOW_SETTLEMENT': [0.3, 0.7],        # outpost, snow_settlement
            'SWAMP_VILLAGE': [0.3, 0.7],          # small_village, swamp_village
            'FOREST_CAMP': [0.4, 0.6],            # outpost, forest_camp
            'MINING_CAMP': [0.3, 0.7],            # outpost, mining_camp
            'FISHING_VILLAGE': [0.3, 0.7]         # small_village, fishing_village
        }
        
        # Select pattern based on weights
        weights = pattern_weights.get(settlement_type.upper(), [1.0])
        selected_pattern = pattern_random.choices(pattern_options, weights=weights)[0]
        
        return self.patterns.get(selected_pattern, self.patterns['small_village'])
    
    def adapt_pattern_to_biome(self, pattern: SettlementPattern, biome: str) -> SettlementPattern:
        """Adapt a settlement pattern to a specific biome"""
        # Create a copy of the pattern with biome-appropriate tiles
        adapted_tiles = []
        
        biome_tile_mapping = {
            'DESERT': {self.TILE_DIRT: self.TILE_SAND, self.TILE_GRASS: self.TILE_SAND},
            'TUNDRA': {self.TILE_DIRT: self.TILE_SNOW, self.TILE_GRASS: self.TILE_SNOW},
            'FOREST': {self.TILE_DIRT: self.TILE_FOREST_FLOOR, self.TILE_GRASS: self.TILE_FOREST_FLOOR},
            'SWAMP': {self.TILE_DIRT: self.TILE_SWAMP, self.TILE_GRASS: self.TILE_SWAMP},
        }
        
        tile_replacements = biome_tile_mapping.get(biome.upper(), {})
        
        for row in pattern.tile_pattern:
            adapted_row = []
            for tile in row:
                adapted_tile = tile_replacements.get(tile, tile)
                adapted_row.append(adapted_tile)
            adapted_tiles.append(adapted_row)
        
        # Create new pattern with adapted tiles
        adapted_pattern_data = pattern.pattern_data.copy()
        adapted_pattern_data['tiles'] = adapted_tiles
        
        return SettlementPattern(f"{pattern.name}_{biome.lower()}", 
                               (pattern.width, pattern.height), 
                               adapted_pattern_data)