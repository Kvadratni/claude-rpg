"""
Settlement Integration Layer
Connects the enhanced settlement generator with the existing level generation system
"""

import random
from typing import List, Dict, Any, Optional
from .enhanced_settlement_generator import EnhancedSettlementGenerator
from .settlement_manager import ChunkSettlementManager


class SettlementIntegrator:
    """
    Integrates enhanced settlement generation with the existing level system
    """
    
    def __init__(self, width: int, height: int, seed: int = None):
        """Initialize the settlement integrator"""
        self.width = width
        self.height = height
        self.seed = seed
        
        # Initialize both generators
        self.enhanced_generator = EnhancedSettlementGenerator(width, height, seed)
        self.chunk_manager = ChunkSettlementManager(seed or 12345)
        
        print(f"SettlementIntegrator initialized for {width}x{height} world")
    
    def generate_settlements_for_level(self, tiles: List[List[int]], biome_map: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Generate enhanced settlements for a level using the new system
        
        Args:
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            
        Returns:
            List of settlement information dictionaries
        """
        settlements = []
        
        # Define settlement placement strategy
        settlement_configs = [
            {'type': 'VILLAGE', 'count': 2, 'biomes': ['PLAINS', 'FOREST']},
            {'type': 'TOWN', 'count': 1, 'biomes': ['PLAINS', 'FOREST']},
            {'type': 'DESERT_OUTPOST', 'count': 2, 'biomes': ['DESERT']},
            {'type': 'SNOW_SETTLEMENT', 'count': 2, 'biomes': ['SNOW', 'TUNDRA']},
            {'type': 'SWAMP_VILLAGE', 'count': 1, 'biomes': ['SWAMP']},
            {'type': 'FOREST_CAMP', 'count': 1, 'biomes': ['FOREST']},
            {'type': 'MINING_CAMP', 'count': 1, 'biomes': ['MOUNTAIN', 'HILLS']},
            {'type': 'FISHING_VILLAGE', 'count': 1, 'biomes': ['COAST', 'PLAINS']}
        ]
        
        for config in settlement_configs:
            settlement_type = config['type']
            target_count = config['count']
            suitable_biomes = config['biomes']
            
            placed_count = 0
            max_attempts = target_count * 5
            
            print(f"Attempting to place {target_count} {settlement_type} settlements...")
            
            for attempt in range(max_attempts):
                if placed_count >= target_count:
                    break
                
                # Find suitable location
                location = self._find_suitable_location(tiles, biome_map, settlement_type, suitable_biomes)
                
                if location:
                    start_x, start_y, biome = location
                    
                    # Generate enhanced settlement
                    settlement_info = self.enhanced_generator.generate_enhanced_settlement(
                        tiles, start_x, start_y, settlement_type, biome, seed=hash((start_x, start_y, settlement_type)) % (2**31)
                    )
                    
                    if settlement_info:
                        # Add NPCs using chunk manager data
                        settlement_info = self._add_npcs_to_settlement(settlement_info, settlement_type)
                        settlements.append(settlement_info)
                        placed_count += 1
                        
                        print(f"  Successfully placed enhanced {settlement_type} #{placed_count} at ({start_x}, {start_y}) in {biome}")
                    else:
                        print(f"  Failed to generate {settlement_type} at ({start_x}, {start_y})")
                else:
                    print(f"  No suitable location found for {settlement_type} (attempt {attempt + 1})")
            
            print(f"  Final result: {placed_count}/{target_count} {settlement_type} settlements placed")
        
        print(f"Total enhanced settlements placed: {len(settlements)}")
        return settlements
    
    def _find_suitable_location(self, tiles: List[List[int]], biome_map: List[List[str]], 
                               settlement_type: str, suitable_biomes: List[str]) -> Optional[tuple]:
        """
        Find a suitable location for a settlement
        
        Returns:
            Tuple of (x, y, biome) if found, None otherwise
        """
        # Get settlement size requirements
        size_requirements = {
            'VILLAGE': (24, 24),
            'TOWN': (30, 30),
            'DESERT_OUTPOST': (18, 18),
            'SNOW_SETTLEMENT': (16, 16),
            'SWAMP_VILLAGE': (20, 20),
            'FOREST_CAMP': (14, 14),
            'MINING_CAMP': (16, 16),
            'FISHING_VILLAGE': (18, 18)
        }
        
        required_width, required_height = size_requirements.get(settlement_type, (16, 16))
        
        # Try to find suitable locations
        for attempt in range(100):
            # Random position with margins
            x = random.randint(10, self.width - required_width - 10)
            y = random.randint(10, self.height - required_height - 10)
            
            # Check biome compatibility
            center_biome = biome_map[y + required_height // 2][x + required_width // 2]
            if center_biome not in suitable_biomes:
                continue
            
            # Check for water and other obstacles
            if self._is_area_suitable(tiles, x, y, required_width, required_height):
                # Check collision with existing settlements
                if not self._check_settlement_collision(x, y, required_width, required_height):
                    return (x, y, center_biome)
        
        return None
    
    def _is_area_suitable(self, tiles: List[List[int]], x: int, y: int, width: int, height: int) -> bool:
        """Check if an area is suitable for settlement placement"""
        water_count = 0
        total_tiles = width * height
        
        for cy in range(y, y + height):
            for cx in range(x, x + width):
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    if tiles[cy][cx] == 3:  # TILE_WATER
                        water_count += 1
        
        # Allow up to 10% water tiles
        return water_count / total_tiles <= 0.1
    
    def _check_settlement_collision(self, x: int, y: int, width: int, height: int) -> bool:
        """Check if settlement would collide with existing settlements"""
        new_rect = (x, y, width, height)
        
        for existing_rect in self.enhanced_generator.occupied_areas:
            if self._rectangles_overlap(new_rect, existing_rect):
                return True
        
        return False
    
    def _rectangles_overlap(self, rect1: tuple, rect2: tuple) -> bool:
        """Check if two rectangles overlap"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
    
    def _add_npcs_to_settlement(self, settlement_info: Dict[str, Any], settlement_type: str) -> Dict[str, Any]:
        """Add NPC information to settlement using chunk manager data"""
        # Get NPC templates from chunk manager
        settlement_templates = self.chunk_manager.SETTLEMENT_TEMPLATES
        
        if settlement_type in settlement_templates:
            template = settlement_templates[settlement_type]
            npcs = []
            
            # Create NPCs for buildings that should have them
            for i, building in enumerate(settlement_info.get('buildings', [])):
                # Match building with template buildings that have NPCs
                template_buildings = [b for b in template['buildings'] if 'npc' in b]
                
                if i < len(template_buildings):
                    template_building = template_buildings[i]
                    
                    npc_data = {
                        'name': template_building['npc'],
                        'building': template_building['name'],
                        'building_type': building['type'],
                        'has_shop': template_building.get('has_shop', False),
                        'importance': template_building.get('importance', 'medium'),
                        'x': building['x'] + building['width'] // 2,
                        'y': building['y'] + building['height'] // 2,
                        'dialog': self._generate_npc_dialog(template_building['npc'], settlement_type, template_building['name'])
                    }
                    npcs.append(npc_data)
            
            settlement_info['npcs'] = npcs
            settlement_info['total_npcs'] = len(npcs)
            settlement_info['shops'] = len([npc for npc in npcs if npc['has_shop']])
        
        return settlement_info
    
    def _generate_npc_dialog(self, npc_name: str, settlement_type: str, building_name: str) -> List[str]:
        """Generate contextual dialog for NPCs"""
        # Use the chunk manager's dialog generation
        return self.chunk_manager._generate_npc_dialog(npc_name, settlement_type, building_name)


# Monkey patch the existing settlement generator to use enhanced generation
def patch_settlement_system():
    """
    Patch the existing settlement system to use enhanced generation
    This allows the new system to work with existing code
    """
    import sys
    
    # Import the existing settlement generator
    try:
        from src.procedural_generation.src.settlement_generator import SettlementGenerator
        
        # Store original methods
        original_place_settlements = SettlementGenerator.place_settlements
        original_place_settlement_buildings = SettlementGenerator.place_settlement_buildings
        
        def enhanced_place_settlements(self, tiles, biome_map):
            """Enhanced settlement placement using new system"""
            print("Using enhanced settlement generation system...")
            
            # Create integrator
            integrator = SettlementIntegrator(self.width, self.height, self.seed)
            
            # Generate enhanced settlements
            settlements = integrator.generate_settlements_for_level(tiles, biome_map)
            
            # Convert to expected format
            converted_settlements = []
            for settlement in settlements:
                converted_settlement = {
                    'name': settlement['name'],
                    'x': settlement['x'],
                    'y': settlement['y'],
                    'center_x': settlement['center_x'],
                    'center_y': settlement['center_y'],
                    'size': settlement['size'],
                    'buildings': settlement.get('buildings', []),
                    'biome': settlement['biome'],
                    'npcs': settlement.get('npcs', []),
                    'architectural_style': settlement.get('architectural_style', 'Generic')
                }
                converted_settlements.append(converted_settlement)
            
            # Update safe zones
            for settlement in converted_settlements:
                safe_radius = 50  # Default safe radius
                self.settlement_safe_zones.append((settlement['center_x'], settlement['center_y'], safe_radius))
            
            return converted_settlements
        
        # Apply patches
        SettlementGenerator.place_settlements = enhanced_place_settlements
        
        print("Settlement system successfully patched with enhanced generation!")
        return True
        
    except ImportError as e:
        print(f"Could not patch settlement system: {e}")
        return False


# Auto-patch when module is imported
if __name__ != "__main__":
    patch_settlement_system()