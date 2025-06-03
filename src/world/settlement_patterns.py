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
        """Create default settlement patterns"""
        
        # Small Village Pattern (12x12)
        self.patterns['small_village'] = self._create_small_village_pattern()
        
        # Medium Town Pattern (16x16) 
        self.patterns['medium_town'] = self._create_medium_town_pattern()
        
        # Large Settlement Pattern (20x20)
        self.patterns['large_settlement'] = self._create_large_settlement_pattern()
        
        # Outpost Pattern (8x8)
        self.patterns['outpost'] = self._create_outpost_pattern()
    
    def _create_small_village_pattern(self) -> SettlementPattern:
        """Create a small village pattern with central square and surrounding buildings"""
        size = (12, 12)
        
        # Create tile pattern - dirt base with stone pathways
        tiles = []
        for y in range(12):
            row = []
            for x in range(12):
                # Stone pathways in cross pattern
                if x == 6 or y == 6:
                    row.append(self.TILE_STONE)  # Main pathways
                elif (x == 5 or x == 7) and (y == 5 or y == 7):
                    row.append(self.TILE_STONE)  # Central square
                else:
                    row.append(self.TILE_DIRT)   # Settlement ground
            tiles.append(row)
        
        # Define building positions
        buildings = [
            {'x': 2, 'y': 2, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 8, 'y': 2, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 2, 'y': 8, 'width': 3, 'height': 3, 'type': 'shop'},
            {'x': 8, 'y': 8, 'width': 3, 'height': 3, 'type': 'house'},
        ]
        
        # Define pathway positions (already in tiles but listed for reference)
        pathways = [(6, y) for y in range(12)] + [(x, 6) for x in range(12)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('small_village', size, pattern_data)
    
    def _create_medium_town_pattern(self) -> SettlementPattern:
        """Create a medium town pattern with multiple districts"""
        size = (16, 16)
        
        # Create tile pattern - more complex layout
        tiles = []
        for y in range(16):
            row = []
            for x in range(16):
                # Main cross pathways
                if x == 8 or y == 8:
                    row.append(self.TILE_STONE)
                # Secondary pathways
                elif x == 4 or x == 12 or y == 4 or y == 12:
                    row.append(self.TILE_DIRT)
                # Central plaza area
                elif 6 <= x <= 10 and 6 <= y <= 10:
                    row.append(self.TILE_BRICK)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        # Define building positions
        buildings = [
            # North district
            {'x': 1, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 5, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 10, 'y': 1, 'width': 4, 'height': 3, 'type': 'inn'},
            
            # South district  
            {'x': 1, 'y': 13, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 5, 'y': 13, 'width': 4, 'height': 3, 'type': 'shop'},
            {'x': 10, 'y': 13, 'width': 4, 'height': 3, 'type': 'blacksmith'},
            
            # East/West districts
            {'x': 13, 'y': 5, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 1, 'y': 5, 'width': 3, 'height': 3, 'type': 'house'},
        ]
        
        pathways = [(8, y) for y in range(16)] + [(x, 8) for x in range(16)]
        pathways += [(4, y) for y in range(16)] + [(12, y) for y in range(16)]
        pathways += [(x, 4) for x in range(16)] + [(x, 12) for x in range(16)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('medium_town', size, pattern_data)
    
    def _create_large_settlement_pattern(self) -> SettlementPattern:
        """Create a large settlement pattern with organized districts"""
        size = (20, 20)
        
        # Create tile pattern
        tiles = []
        for y in range(20):
            row = []
            for x in range(20):
                # Main cross pathways (wider)
                if 9 <= x <= 10 or 9 <= y <= 10:
                    row.append(self.TILE_STONE)
                # District pathways
                elif x == 5 or x == 15 or y == 5 or y == 15:
                    row.append(self.TILE_DIRT)
                # Central plaza
                elif 7 <= x <= 12 and 7 <= y <= 12:
                    row.append(self.TILE_BRICK)
                # Corner plazas
                elif (2 <= x <= 4 and 2 <= y <= 4) or (15 <= x <= 17 and 2 <= y <= 4) or \
                     (2 <= x <= 4 and 15 <= y <= 17) or (15 <= x <= 17 and 15 <= y <= 17):
                    row.append(self.TILE_STONE)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        # Define building positions - more organized layout
        buildings = [
            # Central important buildings
            {'x': 8, 'y': 1, 'width': 4, 'height': 4, 'type': 'town_hall'},
            {'x': 1, 'y': 8, 'width': 4, 'height': 4, 'type': 'temple'},
            {'x': 15, 'y': 8, 'width': 4, 'height': 4, 'type': 'market'},
            
            # Residential areas
            {'x': 1, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 16, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 1, 'y': 16, 'width': 3, 'height': 3, 'type': 'house'},
            {'x': 16, 'y': 16, 'width': 3, 'height': 3, 'type': 'house'},
            
            # Commercial district
            {'x': 6, 'y': 16, 'width': 3, 'height': 3, 'type': 'shop'},
            {'x': 11, 'y': 16, 'width': 3, 'height': 3, 'type': 'inn'},
            {'x': 13, 'y': 1, 'width': 3, 'height': 3, 'type': 'blacksmith'},
        ]
        
        pathways = []
        # Main pathways
        pathways += [(x, 9) for x in range(20)] + [(x, 10) for x in range(20)]
        pathways += [(9, y) for y in range(20)] + [(10, y) for y in range(20)]
        # District pathways
        pathways += [(5, y) for y in range(20)] + [(15, y) for y in range(20)]
        pathways += [(x, 5) for x in range(20)] + [(x, 15) for x in range(20)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('large_settlement', size, pattern_data)
    
    def _create_outpost_pattern(self) -> SettlementPattern:
        """Create a small outpost pattern"""
        size = (8, 8)
        
        # Simple outpost layout
        tiles = []
        for y in range(8):
            row = []
            for x in range(8):
                # Central pathway
                if x == 4 or y == 4:
                    row.append(self.TILE_STONE)
                else:
                    row.append(self.TILE_DIRT)
            tiles.append(row)
        
        buildings = [
            {'x': 1, 'y': 1, 'width': 3, 'height': 3, 'type': 'guard_post'},
            {'x': 5, 'y': 5, 'width': 3, 'height': 3, 'type': 'storage'},
        ]
        
        pathways = [(4, y) for y in range(8)] + [(x, 4) for x in range(8)]
        
        pattern_data = {
            'tiles': tiles,
            'buildings': buildings,
            'pathways': pathways
        }
        
        return SettlementPattern('outpost', size, pattern_data)
    
    def get_pattern(self, settlement_type: str) -> SettlementPattern:
        """Get a pattern for a specific settlement type"""
        # Map settlement types to patterns
        type_mapping = {
            'village': 'small_village',
            'town': 'medium_town', 
            'city': 'large_settlement',
            'outpost': 'outpost',
            'hamlet': 'small_village',
            'settlement': 'medium_town'
        }
        
        pattern_name = type_mapping.get(settlement_type.lower(), 'small_village')
        return self.patterns.get(pattern_name, self.patterns['small_village'])
    
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