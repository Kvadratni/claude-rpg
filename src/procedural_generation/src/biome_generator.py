"""
Biome Generation Module for Procedural World Generation
Handles the creation of biome maps using noise functions
"""

import random
import math
from typing import List, Dict, Tuple


class BiomeGenerator:
    """
    Generates biome maps using simple noise functions
    """
    
    # Biome tile mappings
    BIOME_TILES = {
        'PLAINS': {
            'primary': 0,    # TILE_GRASS
            'secondary': 1,  # TILE_DIRT
            'paths': 2,      # TILE_STONE
            'water_chance': 0.005  # Reduced from 0.02
        },
        'FOREST': {
            'primary': 18,   # TILE_FOREST_FLOOR
            'secondary': 0,  # TILE_GRASS
            'paths': 1,      # TILE_DIRT (forest paths)
            'water_chance': 0.008  # Reduced from 0.03
        },
        'DESERT': {
            'primary': 16,   # TILE_SAND
            'secondary': 2,  # TILE_STONE (rocky outcrops)
            'paths': 2,      # TILE_STONE
            'water_chance': 0.002  # Reduced from 0.005
        },
        'SNOW': {
            'primary': 17,   # TILE_SNOW
            'secondary': 2,  # TILE_STONE (frozen ground)
            'paths': 2,      # TILE_STONE
            'water_chance': 0.003  # Reduced from 0.01
        },
        'SWAMP': {
            'primary': 19,   # TILE_SWAMP
            'secondary': 3,  # TILE_WATER (swamp water)
            'paths': 1,      # TILE_DIRT (muddy paths)
            'water_chance': 0.015  # Higher water chance for swamps
        }
    }
    
    def __init__(self, width: int, height: int, seed: int = None):
        """
        Initialize biome generator
        
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
        
        print(f"BiomeGenerator initialized with seed: {self.seed}")
    
    def generate_biome_map(self) -> List[List[str]]:
        """
        Generate biome map using simple noise
        
        Returns:
            2D list of biome names
        """
        biome_map = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Simple noise based on position and seed
                noise_value = self.simple_noise(x, y)
                
                # Determine biome based on noise value - Balanced distribution with SWAMP
                if noise_value < 0.12:
                    biome = 'DESERT'
                elif noise_value < 0.32:
                    biome = 'PLAINS'
                elif noise_value < 0.52:
                    biome = 'FOREST'
                elif noise_value < 0.72:
                    biome = 'SWAMP'
                else:
                    biome = 'SNOW'
                
                row.append(biome)
            biome_map.append(row)
        
        return biome_map
    
    def simple_noise(self, x: int, y: int) -> float:
        """
        Generate simple pseudo-random noise with better distribution
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Noise value between 0 and 1
        """
        # Use multiple noise layers for more varied distribution
        
        # Large scale features
        large_scale = (
            math.sin(x * 0.05 + self.seed * 0.001) +
            math.cos(y * 0.05 + self.seed * 0.002)
        ) / 2.0
        
        # Medium scale features  
        medium_scale = (
            math.sin(x * 0.1 + y * 0.1 + self.seed * 0.003) +
            math.cos(x * 0.08 - y * 0.12 + self.seed * 0.004)
        ) / 2.0
        
        # Small scale variation
        small_scale = (
            math.sin(x * 0.2 + self.seed * 0.005) +
            math.cos(y * 0.2 + self.seed * 0.006)
        ) / 2.0
        
        # Combine scales with different weights
        combined = (large_scale * 0.6 + medium_scale * 0.3 + small_scale * 0.1)
        
        # Normalize to 0-1 range
        return (combined + 1) / 2
    
    def generate_tiles(self, biome_map: List[List[str]]) -> List[List[int]]:
        """
        Generate tile grid based on biome map
        
        Args:
            biome_map: 2D list of biome names
            
        Returns:
            2D list of tile type integers
        """
        tiles = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                biome = biome_map[y][x]
                biome_config = self.BIOME_TILES[biome]
                
                # Start with primary tile type
                tile_type = biome_config['primary']
                
                # Add some variation with secondary tiles
                if random.random() < 0.15:  # 15% chance for secondary
                    tile_type = biome_config['secondary']
                
                # Add water features
                if random.random() < biome_config['water_chance']:
                    tile_type = 3  # TILE_WATER
                
                row.append(tile_type)
            tiles.append(row)
        
        # Add borders (walls)
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    tiles[y][x] = 4  # TILE_WALL
        
        return tiles
    
    def get_biome_stats(self, biome_map: List[List[str]]) -> Dict[str, int]:
        """
        Get statistics about biome distribution
        
        Args:
            biome_map: 2D list of biome names
            
        Returns:
            Dictionary with biome counts
        """
        biome_counts = {'DESERT': 0, 'PLAINS': 0, 'FOREST': 0, 'SWAMP': 0, 'SNOW': 0}
        
        for y in range(self.height):
            for x in range(self.width):
                biome = biome_map[y][x]
                biome_counts[biome] += 1
        
        return biome_counts
