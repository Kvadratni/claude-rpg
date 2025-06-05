"""
Modular Procedural World Generator for Goose RPG
Coordinates biome generation, settlement placement, and entity spawning
"""

import random
from typing import List, Dict, Tuple, Optional, Any

from .biome_generator import BiomeGenerator
from .settlement_generator import SettlementGenerator
from .enhanced_entity_spawner import EnhancedEntitySpawner


class ProceduralWorldGenerator:
    """
    Main procedural world generator that coordinates all subsystems
    """
    
    def __init__(self, width: int, height: int, seed: int = None):
        """
        Initialize the procedural world generator
        
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
        
        # Initialize subsystem generators
        self.biome_generator = BiomeGenerator(width, height, self.seed)
        self.settlement_generator = SettlementGenerator(width, height, self.seed)
        
        # Use enhanced entity spawner with AI NPC support
        self.entity_spawner = EnhancedEntitySpawner(width, height, self.seed)
        
        # Generated data
        self.biome_map = None
        self.tiles = None
        self.settlements = None
        
        print(f"ProceduralWorldGenerator initialized with seed: {self.seed}")
    
    def generate_world(self, asset_loader: Any = None) -> Dict[str, Any]:
        """
        Generate a complete procedural world
        
        Args:
            asset_loader: Asset loader for entity sprites (optional for testing)
            
        Returns:
            Dictionary containing all world data
        """
        print("Generating procedural world...")
        
        # Phase 1: Generate biomes and tiles
        print("Phase 1: Generating biomes and tiles...")
        self.biome_map = self.biome_generator.generate_biome_map()
        self.tiles = self.biome_generator.generate_tiles(self.biome_map)
        
        # Phase 2: Place settlements
        print("Phase 2: Placing settlements...")
        self.settlements = self.settlement_generator.place_settlements(self.tiles, self.biome_map)
        
        # Phase 3: Spawn entities (if asset_loader provided)
        npcs = []
        enemies = []
        bosses = []
        objects = []
        chests = []
        
        if asset_loader:
            print("Phase 3: Spawning entities...")
            
            # Get settlement safe zones from settlement generator
            safe_zones = self.settlement_generator.settlement_safe_zones
            
            npcs = self.entity_spawner.spawn_npcs(self.settlements, asset_loader)
            enemies = self.entity_spawner.spawn_enemies(self.tiles, self.biome_map, safe_zones, asset_loader)
            bosses = self.entity_spawner.spawn_bosses(self.tiles, self.biome_map, safe_zones, asset_loader)
            objects = self.entity_spawner.spawn_objects(self.tiles, self.biome_map, safe_zones, asset_loader)
            chests = self.entity_spawner.spawn_chests(self.tiles, self.biome_map, safe_zones, asset_loader)
        else:
            print("Phase 3: Skipped entity spawning (no asset_loader provided)")
        
        # Generate walkable grid
        walkable_grid = self.generate_walkable_grid()
        
        # Find optimal player spawn location (closest settlement)
        player_spawn = self.entity_spawner.find_closest_settlement(self.settlements) if hasattr(self.entity_spawner, 'find_closest_settlement') else (self.width // 2, self.height // 2)
        
        world_data = {
            'seed': self.seed,
            'width': self.width,
            'height': self.height,
            'biome_map': self.biome_map,
            'tiles': self.tiles,
            'settlements': self.settlements,
            'npcs': npcs,
            'enemies': enemies,
            'bosses': bosses,
            'objects': objects,
            'chests': chests,
            'walkable_grid': walkable_grid,
            'safe_zones': self.settlement_generator.settlement_safe_zones,
            'player_spawn': player_spawn  # Add optimal player spawn location
        }
        
        print(f"World generation complete! Generated {len(self.settlements)} settlements")
        return world_data
    
    def generate_biome_map_only(self) -> List[List[str]]:
        """
        Generate only the biome map (for testing)
        
        Returns:
            2D list of biome names
        """
        return self.biome_generator.generate_biome_map()
    
    def generate_tiles_only(self, biome_map: List[List[str]] = None) -> List[List[int]]:
        """
        Generate only the tile map (for testing)
        
        Args:
            biome_map: Optional biome map, will generate if not provided
            
        Returns:
            2D list of tile type integers
        """
        if biome_map is None:
            biome_map = self.generate_biome_map_only()
        
        return self.biome_generator.generate_tiles(biome_map)
    
    def place_settlements_only(self, tiles: List[List[int]] = None, 
                              biome_map: List[List[str]] = None) -> List[Dict]:
        """
        Place only settlements (for testing)
        
        Args:
            tiles: Optional tile map, will generate if not provided
            biome_map: Optional biome map, will generate if not provided
            
        Returns:
            List of settlement information dictionaries
        """
        if biome_map is None:
            biome_map = self.generate_biome_map_only()
        
        if tiles is None:
            tiles = self.generate_tiles_only(biome_map)
        
        return self.settlement_generator.place_settlements(tiles, biome_map)
    
    def generate_walkable_grid(self) -> List[List[float]]:
        """
        Generate walkable grid from tiles
        
        Returns:
            2D list of walkable values (1.0 = walkable, 0.0 = blocked)
        """
        if self.tiles is None:
            raise ValueError("Tiles must be generated before creating walkable grid")
        
        walkable = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_type = self.tiles[y][x]
                # Walkable tiles: grass, dirt, stone, door, brick, sand, snow, forest_floor, swamp
                is_walkable = tile_type in [0, 1, 2, 5, 13, 16, 17, 18, 19]
                row.append(1.0 if is_walkable else 0.0)
            walkable.append(row)
        
        return walkable
    
    def get_world_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the generated world
        
        Returns:
            Dictionary with world statistics
        """
        if self.biome_map is None:
            return {"error": "World not generated yet"}
        
        # Biome statistics
        biome_stats = self.biome_generator.get_biome_stats(self.biome_map)
        
        # Settlement statistics
        settlement_stats = {
            'total_settlements': len(self.settlements) if self.settlements else 0,
            'settlement_types': {}
        }
        
        if self.settlements:
            for settlement in self.settlements:
                settlement_type = settlement['name']
                settlement_stats['settlement_types'][settlement_type] = \
                    settlement_stats['settlement_types'].get(settlement_type, 0) + 1
        
        # Tile statistics
        tile_stats = {}
        if self.tiles:
            tile_counts = {}
            for y in range(self.height):
                for x in range(self.width):
                    tile_type = self.tiles[y][x]
                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
            
            tile_names = {0: 'GRASS', 1: 'DIRT', 2: 'STONE', 3: 'WATER', 4: 'WALL', 
                         5: 'DOOR', 10: 'WALL_HORIZONTAL', 11: 'WALL_VERTICAL', 
                         13: 'BRICK', 14: 'WALL_WINDOW_HORIZONTAL', 15: 'WALL_WINDOW_VERTICAL'}
            
            for tile_type, count in tile_counts.items():
                name = tile_names.get(tile_type, f'UNKNOWN({tile_type})')
                tile_stats[name] = count
        
        return {
            'seed': self.seed,
            'dimensions': f"{self.width}x{self.height}",
            'biome_stats': biome_stats,
            'settlement_stats': settlement_stats,
            'tile_stats': tile_stats
        }
    
    def save_world_data(self, filepath: str) -> None:
        """
        Save world data to a file (for debugging/analysis)
        
        Args:
            filepath: Path to save the world data
        """
        import json
        
        # Create a serializable version of world data
        world_data = {
            'seed': self.seed,
            'width': self.width,
            'height': self.height,
            'biome_map': self.biome_map,
            'tiles': self.tiles,
            'settlements': self.settlements,
            'stats': self.get_world_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(world_data, f, indent=2)
        
        print(f"World data saved to {filepath}")
    
    def load_world_data(self, filepath: str) -> Dict[str, Any]:
        """
        Load world data from a file (for debugging/analysis)
        
        Args:
            filepath: Path to load the world data from
            
        Returns:
            Dictionary containing world data
        """
        import json
        
        with open(filepath, 'r') as f:
            world_data = json.load(f)
        
        # Restore internal state
        self.seed = world_data['seed']
        self.width = world_data['width']
        self.height = world_data['height']
        self.biome_map = world_data['biome_map']
        self.tiles = world_data['tiles']
        self.settlements = world_data['settlements']
        
        print(f"World data loaded from {filepath}")
        return world_data


# Legacy compatibility - create an alias to the old class name
ProceduralGenerator = ProceduralWorldGenerator