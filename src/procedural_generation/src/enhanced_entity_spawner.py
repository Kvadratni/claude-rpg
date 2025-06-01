"""
Enhanced Entity Spawner with Logical Rules
Improved spawning logic with collision detection and terrain validation
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any


class EnhancedEntitySpawner:
    """
    Enhanced entity spawner with logical rules and collision detection
    """
    
    # Existing enemies mapped to biomes
    BIOME_ENEMIES = {
        'FOREST': [
            {'name': 'Forest Goblin', 'health': 45, 'damage': 9, 'experience': 30},
            {'name': 'Forest Sprite', 'health': 35, 'damage': 12, 'experience': 40},
            {'name': 'Ancient Guardian', 'health': 60, 'damage': 15, 'experience': 50}
        ],
        'DESERT': [
            {'name': 'Giant Scorpion', 'health': 55, 'damage': 16, 'experience': 45},
            {'name': 'Bandit Scout', 'health': 35, 'damage': 8, 'experience': 20}
        ],
        'PLAINS': [
            {'name': 'Bandit Scout', 'health': 35, 'damage': 8, 'experience': 20},
            {'name': 'Orc Warrior', 'health': 80, 'damage': 18, 'experience': 60}
        ],
        'SNOW': [
            {'name': 'Crystal Elemental', 'health': 70, 'damage': 20, 'experience': 65},
            {'name': 'Ancient Guardian', 'health': 60, 'damage': 15, 'experience': 50}
        ]
    }
    
    # Boss locations for each biome
    BOSS_LOCATIONS = [
        {'name': 'Orc Warlord', 'health': 400, 'damage': 30, 'experience': 300, 'biome': 'PLAINS'},
        {'name': 'Ancient Dragon', 'health': 800, 'damage': 50, 'experience': 500, 'biome': 'SNOW'}
    ]
    
    # Tile type constants
    TILE_GRASS = 0
    TILE_DIRT = 1
    TILE_STONE = 2
    TILE_WATER = 3
    TILE_WALL = 4
    TILE_DOOR = 5
    # Biome-specific tiles
    TILE_SAND = 16
    TILE_SNOW = 17
    TILE_FOREST_FLOOR = 18
    TILE_SWAMP = 19
    TILE_BRICK = 13
    
    def __init__(self, width: int, height: int, seed: int = None):
        """
        Initialize enhanced entity spawner
        
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
        
        # Track occupied positions for collision detection
        self.occupied_positions = set()  # Set of (x, y) tuples
        
        print(f"EnhancedEntitySpawner initialized with seed: {self.seed}")
    
    def is_position_valid_for_entity(self, x: int, y: int, tiles: List[List[int]], 
                                   biome_map: List[List[str]], entity_type: str = "generic") -> bool:
        """
        Check if a position is valid for spawning an entity with enhanced rules
        
        Args:
            x, y: Position to check
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            entity_type: Type of entity ("enemy", "object", "chest", "boss")
            
        Returns:
            True if position is valid for the entity type
        """
        # Bounds check
        if x < 1 or x >= self.width - 1 or y < 1 or y >= self.height - 1:
            return False
        
        # Check if position is already occupied
        if (x, y) in self.occupied_positions:
            return False
        
        # Get tile type at position
        tile_type = tiles[y][x]
        biome = biome_map[y][x]
        
        # Basic tile validation - no spawning on walls, water, doors, or building interiors
        if tile_type in [self.TILE_WALL, self.TILE_WATER, self.TILE_DOOR, self.TILE_BRICK]:
            return False
        
        # Entity-specific validation
        if entity_type == "object":
            # Trees can only spawn on grass or dirt
            if tile_type not in [self.TILE_GRASS, self.TILE_DIRT]:
                return False
            
            # Check for nearby walls/buildings (objects shouldn't spawn too close to structures)
            if self._has_nearby_walls(x, y, tiles, radius=2):
                return False
        
        elif entity_type in ["enemy", "boss"]:
            # Enemies need walkable terrain
            if tile_type not in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE]:
                return False
            
            # Enemies shouldn't spawn too close to walls (need movement space)
            if self._has_nearby_walls(x, y, tiles, radius=1):
                return False
        
        elif entity_type == "chest":
            # Chests can spawn on grass, dirt, or stone
            if tile_type not in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE]:
                return False
            
            # Chests shouldn't be completely surrounded by walls
            if self._is_surrounded_by_walls(x, y, tiles):
                return False
        
        # Check for entity clustering (prevent too many entities in one area)
        if self._is_area_overcrowded(x, y, radius=3):
            return False
        
        return True
    
    def _has_nearby_walls(self, x: int, y: int, tiles: List[List[int]], radius: int = 1) -> bool:
        """Check if there are walls within a certain radius"""
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                check_x, check_y = x + dx, y + dy
                if (0 <= check_x < self.width and 0 <= check_y < self.height):
                    if tiles[check_y][check_x] in [self.TILE_WALL, self.TILE_DOOR]:
                        return True
        return False
    
    def _is_surrounded_by_walls(self, x: int, y: int, tiles: List[List[int]]) -> bool:
        """Check if position is completely surrounded by walls"""
        wall_count = 0
        total_positions = 0
        
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                check_x, check_y = x + dx, y + dy
                if 0 <= check_x < self.width and 0 <= check_y < self.height:
                    total_positions += 1
                    if tiles[check_y][check_x] in [self.TILE_WALL, self.TILE_DOOR]:
                        wall_count += 1
        
        # If more than 75% of surrounding tiles are walls, consider it surrounded
        return wall_count > (total_positions * 0.75)
    
    def _is_area_overcrowded(self, x: int, y: int, radius: int = 3) -> bool:
        """Check if area has too many entities already"""
        entity_count = 0
        total_positions = 0
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                check_x, check_y = x + dx, y + dy
                if 0 <= check_x < self.width and 0 <= check_y < self.height:
                    total_positions += 1
                    if (check_x, check_y) in self.occupied_positions:
                        entity_count += 1
        
        # If more than 20% of area is occupied, consider it overcrowded
        return entity_count > (total_positions * 0.2)
    
    def mark_position_occupied(self, x: int, y: int):
        """Mark a position as occupied"""
        self.occupied_positions.add((x, y))
    
    def spawn_enemies(self, tiles: List[List[int]], biome_map: List[List[str]], 
                     settlement_safe_zones: List[Tuple[int, int, int]], 
                     asset_loader: Any) -> List[Any]:
        """
        Spawn enemies with enhanced collision detection and terrain validation
        """
        enemies = []
        
        # Calculate enemy density
        total_area = self.width * self.height
        target_enemies = int(total_area * 0.001)  # 0.1% of tiles have enemies
        
        attempts = 0
        max_attempts = target_enemies * 20  # Increased attempts for better placement
        
        while len(enemies) < target_enemies and attempts < max_attempts:
            attempts += 1
            
            # Random position
            x = random.randint(5, self.width - 6)
            y = random.randint(5, self.height - 6)
            
            # Check if position is in safe zone
            if self._is_in_safe_zone(x, y, settlement_safe_zones):
                continue
            
            # Enhanced position validation
            if not self.is_position_valid_for_entity(x, y, tiles, biome_map, "enemy"):
                continue
            
            # Get biome and spawn appropriate enemy
            biome = biome_map[y][x]
            enemy_types = self.BIOME_ENEMIES.get(biome, [])
            
            if not enemy_types:
                continue
            
            enemy_config = random.choice(enemy_types)
            
            # Import Enemy class
            try:
                from ...entities import Enemy
            except ImportError:
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from entities import Enemy
                except ImportError:
                    class MockEnemy:
                        def __init__(self, *args, **kwargs):
                            self.x = args[0] if args else 0
                            self.y = args[1] if len(args) > 1 else 0
                            self.name = args[2] if len(args) > 2 else "Enemy"
                        def update(self, level):
                            pass
                    Enemy = MockEnemy
            
            enemy = Enemy(x, y, enemy_config['name'],
                         health=enemy_config['health'],
                         damage=enemy_config['damage'],
                         experience=enemy_config['experience'],
                         asset_loader=asset_loader)
            enemies.append(enemy)
            
            # Mark position as occupied
            self.mark_position_occupied(x, y)
        
        print(f"Spawned {len(enemies)} enemies with enhanced placement")
        return enemies
    
    def spawn_objects(self, tiles: List[List[int]], biome_map: List[List[str]], 
                     settlement_safe_zones: List[Tuple[int, int, int]], 
                     asset_loader: Any) -> List[Any]:
        """
        Spawn environmental objects with enhanced terrain validation
        """
        objects = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Skip if in safe zone
                if self._is_in_safe_zone(x, y, settlement_safe_zones):
                    continue
                
                # Enhanced position validation for objects
                if not self.is_position_valid_for_entity(x, y, tiles, biome_map, "object"):
                    continue
                
                biome = biome_map[y][x]
                
                # Biome-specific object spawning with terrain validation and variants
                spawn_chance = 0
                object_variants = []
                
                if biome == 'FOREST':
                    # Trees only on grass/dirt/forest_floor, higher density in forests
                    if tiles[y][x] in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_FOREST_FLOOR]:  # 18 = TILE_FOREST_FLOOR
                        spawn_chance = 0.25  # Dense forest coverage
                        object_variants = ["pine_tree", "oak_tree", "fallen_log"]
                elif biome == 'PLAINS':
                    # Scattered trees only on grass/dirt
                    if tiles[y][x] in [self.TILE_GRASS, self.TILE_DIRT]:
                        spawn_chance = 0.03  # Sparse coverage
                        object_variants = ["oak_tree", "Tree"]  # Mix of new and old
                elif biome == 'DESERT':
                    # Desert objects on sand/dirt/stone
                    if tiles[y][x] in [self.TILE_SAND, self.TILE_DIRT, self.TILE_STONE]:  # 16 = TILE_SAND
                        spawn_chance = 0.08  # Moderate coverage
                        object_variants = ["cactus_saguaro", "cactus_barrel", "desert_rock"]
                elif biome == 'SNOW':
                    # Winter objects with terrain restrictions
                    if tiles[y][x] in [self.TILE_SNOW, self.TILE_STONE]:  # 17 = TILE_SNOW
                        spawn_chance = 0.10  # Good coverage
                        object_variants = ["snowy_pine", "ice_block", "frozen_rock"]
                elif biome == 'SWAMP':
                    # Swamp objects on swamp/water tiles
                    if tiles[y][x] in [self.TILE_SWAMP, self.TILE_DIRT]:  # 19 = TILE_SWAMP
                        spawn_chance = 0.12  # Dense swamp coverage
                        object_variants = ["dead_tree", "swamp_log", "swamp_mushroom"]
                
                if random.random() < spawn_chance and object_variants:
                    # Import Entity class
                    try:
                        from ...entities import Entity
                    except ImportError:
                        try:
                            import sys
                            import os
                            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                            from entities import Entity
                        except ImportError:
                            class MockEntity:
                                def __init__(self, *args, **kwargs):
                                    self.x = args[0] if args else 0
                                    self.y = args[1] if len(args) > 1 else 0
                                    self.name = args[2] if len(args) > 2 else "Object"
                                def update(self, level):
                                    pass
                            Entity = MockEntity
                    
                    # Choose random variant from biome-appropriate options
                    chosen_variant = random.choice(object_variants)
                    
                    # Create object with biome-specific sprite
                    obj = Entity(x, y, chosen_variant, entity_type="object", 
                               blocks_movement=True, asset_loader=asset_loader)
                    objects.append(obj)
                    
                    # Mark position as occupied
                    self.mark_position_occupied(x, y)
        
        print(f"Spawned {len(objects)} objects with terrain validation")
        return objects
    
    def spawn_chests(self, tiles: List[List[int]], biome_map: List[List[str]], 
                    settlement_safe_zones: List[Tuple[int, int, int]], 
                    asset_loader: Any) -> List[Any]:
        """
        Spawn treasure chests with enhanced placement logic
        """
        chests = []
        target_chests = 15
        
        for _ in range(target_chests * 5):  # More attempts for better placement
            x = random.randint(10, self.width - 11)
            y = random.randint(10, self.height - 11)
            
            # Don't spawn in safe zones
            if self._is_in_safe_zone(x, y, settlement_safe_zones):
                continue
            
            # Enhanced position validation
            if not self.is_position_valid_for_entity(x, y, tiles, biome_map, "chest"):
                continue
            
            # Determine chest type based on distance from settlements
            distance = self._distance_to_nearest_settlement(x, y, settlement_safe_zones)
            
            if distance < 25:
                chest_type = "wooden"
            elif distance < 50:
                chest_type = "iron"
            else:
                chest_type = "gold"
            
            # Import Chest class
            try:
                from ...entities import Chest
            except ImportError:
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from entities import Chest
                except ImportError:
                    class MockChest:
                        def __init__(self, *args, **kwargs):
                            self.x = args[0] if args else 0
                            self.y = args[1] if len(args) > 1 else 0
                            self.chest_type = args[2] if len(args) > 2 else "wooden"
                        def update(self, level):
                            pass
                    Chest = MockChest
            
            chest = Chest(x, y, chest_type, asset_loader)
            chests.append(chest)
            
            # Mark position as occupied
            self.mark_position_occupied(x, y)
            
            if len(chests) >= target_chests:
                break
        
        print(f"Spawned {len(chests)} chests with enhanced placement")
        return chests
    
    def find_closest_settlement(self, settlements: List[Dict]) -> Tuple[int, int]:
        """
        Find the closest settlement to the center of the world for player spawn
        
        Args:
            settlements: List of settlement information
            
        Returns:
            (x, y) coordinates of the closest settlement center
        """
        if not settlements:
            # Fallback to world center if no settlements
            return (self.width // 2, self.height // 2)
        
        world_center_x = self.width // 2
        world_center_y = self.height // 2
        
        closest_settlement = None
        min_distance = float('inf')
        
        for settlement in settlements:
            settlement_x = settlement['center_x']
            settlement_y = settlement['center_y']
            
            # Calculate distance from world center
            distance = math.sqrt(
                (settlement_x - world_center_x) ** 2 + 
                (settlement_y - world_center_y) ** 2
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_settlement = settlement
        
        if closest_settlement:
            # Return position near the settlement center but not exactly on it
            spawn_x = closest_settlement['center_x'] + random.randint(-3, 3)
            spawn_y = closest_settlement['center_y'] + random.randint(-3, 3)
            
            # Ensure spawn position is within world bounds
            spawn_x = max(5, min(self.width - 5, spawn_x))
            spawn_y = max(5, min(self.height - 5, spawn_y))
            
            print(f"Player spawn near {closest_settlement['name']} at ({spawn_x}, {spawn_y})")
            return (spawn_x, spawn_y)
        
        return (world_center_x, world_center_y)
    
    # Keep existing helper methods
    def _is_in_safe_zone(self, x: int, y: int, 
                        settlement_safe_zones: List[Tuple[int, int, int]]) -> bool:
        """Check if position is within any settlement safe zone"""
        for center_x, center_y, radius in settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < radius:
                return True
        return False
    
    def _distance_to_nearest_settlement(self, x: int, y: int, 
                                      settlement_safe_zones: List[Tuple[int, int, int]]) -> float:
        """Calculate distance to nearest settlement"""
        if not settlement_safe_zones:
            return float('inf')
        
        min_distance = float('inf')
        for center_x, center_y, _ in settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    # Keep existing NPC and boss spawning methods (they already work well)
    def spawn_npcs(self, settlements: List[Dict], asset_loader: Any) -> List[Any]:
        """Spawn NPCs in settlements (existing implementation)"""
        npcs = []
        
        for settlement in settlements:
            for building in settlement.get('buildings', []):
                if 'npc' in building and building['npc']:
                    # Find interior position for NPC
                    bx, by = building['x'], building['y']
                    bw, bh = building['width'], building['height']
                    
                    # Place NPC in center of building
                    npc_x = bx + bw // 2
                    npc_y = by + bh // 2
                    
                    # Create NPC with appropriate dialog
                    npc_name = building['npc']
                    has_shop = building.get('has_shop', False)
                    
                    # Get appropriate dialog for NPC type
                    dialog = self.get_npc_dialog(npc_name)
                    
                    # Import NPC class
                    try:
                        from ...entities import NPC
                    except ImportError:
                        try:
                            import sys
                            import os
                            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                            from entities import NPC
                        except ImportError:
                            class MockNPC:
                                def __init__(self, *args, **kwargs):
                                    self.x = args[0] if args else 0
                                    self.y = args[1] if len(args) > 1 else 0
                                    self.name = args[2] if len(args) > 2 else "NPC"
                                def update(self, level):
                                    pass
                            NPC = MockNPC
                    
                    npc = NPC(npc_x, npc_y, npc_name, dialog=dialog, 
                             asset_loader=asset_loader, has_shop=has_shop)
                    npcs.append(npc)
                    
                    # Mark NPC position as occupied
                    self.mark_position_occupied(npc_x, npc_y)
                    
                    print(f"Spawned {npc_name} at ({npc_x}, {npc_y})")
        
        return npcs
    
    def spawn_bosses(self, tiles: List[List[int]], biome_map: List[List[str]], 
                    settlement_safe_zones: List[Tuple[int, int, int]], 
                    asset_loader: Any) -> List[Any]:
        """Spawn boss enemies with enhanced validation"""
        bosses = []
        
        for boss_config in self.BOSS_LOCATIONS:
            boss_biome = boss_config['biome']
            
            # Find suitable location in the specified biome
            for attempt in range(100):
                x = random.randint(20, self.width - 21)
                y = random.randint(20, self.height - 21)
                
                # Check biome
                if biome_map[y][x] != boss_biome:
                    continue
                
                # Check if far from settlements
                if (self._is_in_safe_zone(x, y, settlement_safe_zones) or 
                    self._distance_to_nearest_settlement(x, y, settlement_safe_zones) < 40):
                    continue
                
                # Enhanced position validation for bosses
                if not self.is_position_valid_for_entity(x, y, tiles, biome_map, "boss"):
                    continue
                
                # Import Enemy class
                try:
                    from ...entities import Enemy
                except ImportError:
                    try:
                        import sys
                        import os
                        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                        from entities import Enemy
                    except ImportError:
                        class MockEnemy:
                            def __init__(self, *args, **kwargs):
                                self.x = args[0] if args else 0
                                self.y = args[1] if len(args) > 1 else 0
                                self.name = args[2] if len(args) > 2 else "Boss"
                            def update(self, level):
                                pass
                        Enemy = MockEnemy
                
                # Spawn boss
                boss = Enemy(x, y, boss_config['name'],
                           health=boss_config['health'],
                           damage=boss_config['damage'],
                           experience=boss_config['experience'],
                           is_boss=True,
                           asset_loader=asset_loader)
                bosses.append(boss)
                
                # Mark position as occupied
                self.mark_position_occupied(x, y)
                
                print(f"Spawned {boss_config['name']} at ({x}, {y}) in {boss_biome}")
                break
        
        return bosses
    
    def get_npc_dialog(self, npc_name: str) -> List[str]:
        """Get appropriate dialog for NPC types"""
        dialogs = {
            'Master Merchant': [
                "Welcome to my shop!",
                "I have the finest goods in the land!",
                "Trade routes are dangerous these days."
            ],
            'Village Elder': [
                "Welcome, traveler!",
                "Our village is peaceful, but dangers lurk beyond.",
                "May your journey be safe."
            ],
            'Master Smith': [
                "The forge burns hot today!",
                "I craft the finest weapons and armor.",
                "Bring me materials and I'll make you legendary gear!"
            ],
            'Innkeeper': [
                "Welcome to my inn!",
                "Rest here and recover your strength.",
                "I hear tales from many travelers."
            ],
            'Guard Captain': [
                "I keep watch over our settlement.",
                "Report any dangers you encounter.",
                "Stay vigilant out there."
            ],
            'Caravan Master': [
                "The desert trade routes are treacherous.",
                "I deal in rare goods from distant lands.",
                "Water is more precious than gold here."
            ],
            'Forest Ranger': [
                "I know these lands well.",
                "The wilderness holds many secrets.",
                "Beware the ancient guardians."
            ],
            'Master Herbalist': [
                "I brew potions from rare herbs.",
                "Nature provides all we need for healing.",
                "My remedies are the finest you'll find."
            ]
        }
        
        return dialogs.get(npc_name, ["Hello, traveler!"])