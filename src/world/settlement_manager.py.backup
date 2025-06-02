"""
Settlement manager for chunk-based worlds
Handles settlement placement across infinite worlds with proper density
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any


class ChunkSettlementManager:
    """
    Manages settlements across chunk-based infinite worlds
    """
    
    # Settlement templates with increased spawn chances
    SETTLEMENT_TEMPLATES = {
        'VILLAGE': {
            'size': (25, 25),
            'buildings': [
                {'name': 'General Store', 'size': (12, 8), 'npc': 'Master Merchant', 'has_shop': True},
                {'name': 'Inn', 'size': (10, 8), 'npc': 'Innkeeper', 'has_shop': False},
                {'name': 'Blacksmith', 'size': (8, 6), 'npc': 'Master Smith', 'has_shop': True},
                {'name': 'Elder House', 'size': (10, 8), 'npc': 'Village Elder', 'has_shop': False},
                {'name': 'Guard House', 'size': (8, 6), 'npc': 'Guard Captain', 'has_shop': False},
                {'name': 'Temple', 'size': (12, 10), 'npc': 'High Priest', 'has_shop': False},
                {'name': 'Market Stall', 'size': (6, 4), 'npc': 'Trader', 'has_shop': True}
            ],
            'biomes': ['PLAINS', 'FOREST'],
            'spawn_chance': 0.25,  # 25% chance per suitable chunk
            'min_distance': 5  # Minimum chunks between same type
        },
        'DESERT_OUTPOST': {
            'size': (20, 20),
            'buildings': [
                {'name': 'Trading Post', 'size': (10, 8), 'npc': 'Caravan Master', 'has_shop': True},
                {'name': 'Water Storage', 'size': (6, 6)},
                {'name': 'Caravan Rest', 'size': (10, 6), 'npc': 'Desert Guide', 'has_shop': False},
                {'name': 'Oasis Keeper', 'size': (8, 6), 'npc': 'Oasis Keeper', 'has_shop': True}
            ],
            'biomes': ['DESERT'],
            'spawn_chance': 0.35,  # Higher chance due to rarity of desert
            'min_distance': 3
        },
        'SNOW_SETTLEMENT': {
            'size': (18, 18),
            'buildings': [
                {'name': 'Ranger Station', 'size': (8, 6), 'npc': 'Forest Ranger', 'has_shop': False},
                {'name': 'Herbalist Hut', 'size': (8, 6), 'npc': 'Master Herbalist', 'has_shop': True},
                {'name': 'Warm Lodge', 'size': (10, 8), 'npc': 'Lodge Keeper', 'has_shop': False},
                {'name': 'Hunter Cabin', 'size': (6, 6), 'npc': 'Hunter', 'has_shop': True}
            ],
            'biomes': ['SNOW'],
            'spawn_chance': 0.30,
            'min_distance': 4
        },
        'SWAMP_VILLAGE': {
            'size': (22, 22),
            'buildings': [
                {'name': 'Alchemist Hut', 'size': (10, 8), 'npc': 'Swamp Alchemist', 'has_shop': True},
                {'name': 'Fisherman Dock', 'size': (12, 6), 'npc': 'Fisherman', 'has_shop': False},
                {'name': 'Witch Hut', 'size': (8, 8), 'npc': 'Swamp Witch', 'has_shop': True},
                {'name': 'Boat Builder', 'size': (10, 6), 'npc': 'Boat Builder', 'has_shop': False}
            ],
            'biomes': ['SWAMP'],
            'spawn_chance': 0.20,
            'min_distance': 4
        },
        'FOREST_CAMP': {
            'size': (16, 16),
            'buildings': [
                {'name': 'Woodcutter Lodge', 'size': (8, 6), 'npc': 'Master Woodcutter', 'has_shop': True},
                {'name': 'Druid Circle', 'size': (10, 10), 'npc': 'Forest Druid', 'has_shop': False},
                {'name': 'Scout Post', 'size': (6, 6), 'npc': 'Scout Leader', 'has_shop': False}
            ],
            'biomes': ['FOREST'],
            'spawn_chance': 0.18,
            'min_distance': 3
        }
    }
    
    def __init__(self, world_seed: int):
        """Initialize settlement manager"""
        self.world_seed = world_seed
        self.placed_settlements = {}  # Track settlements by chunk coordinates
        
    def should_generate_settlement(self, chunk_x: int, chunk_y: int, biome_data: Dict[str, int]) -> Optional[str]:
        """
        Determine if a settlement should be generated in this chunk
        
        Args:
            chunk_x, chunk_y: Chunk coordinates
            biome_data: Dictionary of biome -> tile_count in this chunk
            
        Returns:
            Settlement type to generate, or None
        """
        # Create deterministic random for this chunk
        chunk_seed = hash((self.world_seed, chunk_x, chunk_y, "settlement")) % (2**31)
        chunk_random = random.Random(chunk_seed)
        
        # Find dominant biome in chunk
        if not biome_data:
            return None
            
        dominant_biome = max(biome_data.items(), key=lambda x: x[1])[0]
        
        # Check each settlement type for compatibility
        for settlement_type, config in self.SETTLEMENT_TEMPLATES.items():
            if dominant_biome in config['biomes']:
                # Check spawn chance
                if chunk_random.random() < config['spawn_chance']:
                    # Check minimum distance from other settlements of same type
                    if self._check_minimum_distance(chunk_x, chunk_y, settlement_type, config['min_distance']):
                        return settlement_type
        
        return None
    
    def _check_minimum_distance(self, chunk_x: int, chunk_y: int, settlement_type: str, min_distance: int) -> bool:
        """Check if minimum distance requirement is met"""
        for (cx, cy), placed_type in self.placed_settlements.items():
            if placed_type == settlement_type:
                distance = max(abs(cx - chunk_x), abs(cy - chunk_y))
                if distance < min_distance:
                    return False
        return True
    
    def generate_settlement_in_chunk(self, chunk_x: int, chunk_y: int, settlement_type: str) -> Dict[str, Any]:
        """
        Generate a settlement in the specified chunk
        
        Args:
            chunk_x, chunk_y: Chunk coordinates
            settlement_type: Type of settlement to generate
            
        Returns:
            Settlement data dictionary
        """
        config = self.SETTLEMENT_TEMPLATES[settlement_type]
        
        # Create deterministic random for this settlement
        settlement_seed = hash((self.world_seed, chunk_x, chunk_y, settlement_type)) % (2**31)
        settlement_random = random.Random(settlement_seed)
        
        # Calculate world position within chunk (center-ish)
        chunk_size = 64  # From Chunk.CHUNK_SIZE
        world_x = chunk_x * chunk_size + settlement_random.randint(10, chunk_size - config['size'][0] - 10)
        world_y = chunk_y * chunk_size + settlement_random.randint(10, chunk_size - config['size'][1] - 10)
        
        # Generate NPCs for this settlement
        npcs = []
        for building in config['buildings']:
            if 'npc' in building:
                npc_data = {
                    'name': building['npc'],
                    'building': building['name'],
                    'has_shop': building.get('has_shop', False),
                    'x': world_x + settlement_random.randint(2, config['size'][0] - 2),
                    'y': world_y + settlement_random.randint(2, config['size'][1] - 2)
                }
                npcs.append(npc_data)
        
        settlement_data = {
            'type': settlement_type,
            'chunk_x': chunk_x,
            'chunk_y': chunk_y,
            'world_x': world_x,
            'world_y': world_y,
            'size': config['size'],
            'buildings': config['buildings'],
            'npcs': npcs,
            'biomes': config['biomes']
        }
        
        # Record this settlement
        self.placed_settlements[(chunk_x, chunk_y)] = settlement_type
        
        return settlement_data
