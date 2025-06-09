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
    
    # Rebalanced enemies with tier-based spawning and biome difficulty scaling
    # Tier 1: Near settlements (0-30 tiles) - Beginner enemies
    # Tier 2: Medium distance (30-60 tiles) - Intermediate enemies  
    # Tier 3: Far from settlements (60+ tiles) - Advanced enemies
    BIOME_ENEMIES = {
        'FOREST': {
            'difficulty_modifier': 1.0,  # Easy biome - baseline difficulty
            'tier_1': [
                {'name': 'Forest Goblin', 'health': 50, 'damage': 12, 'experience': 35, 'type': 'melee'},
                {'name': 'Forest Sprite', 'health': 45, 'damage': 10, 'experience': 30, 'type': 'melee'},
            ],
            'tier_2': [
                {'name': 'Goblin Archer', 'health': 55, 'damage': 15, 'experience': 45, 'type': 'ranged', 'weapon': 'bow'},
                {'name': 'Forest Goblin', 'health': 65, 'damage': 16, 'experience': 50, 'type': 'melee'},
                {'name': 'Skeleton Archer', 'health': 60, 'damage': 18, 'experience': 55, 'type': 'ranged', 'weapon': 'bow'}
            ],
            'tier_3': [
                {'name': 'Ancient Guardian', 'health': 85, 'damage': 22, 'experience': 75, 'type': 'melee'},
                {'name': 'Elder Forest Sprite', 'health': 70, 'damage': 20, 'experience': 65, 'type': 'melee'},
                {'name': 'Goblin Chieftain', 'health': 95, 'damage': 24, 'experience': 85, 'type': 'melee'}
            ]
        },
        'PLAINS': {
            'difficulty_modifier': 1.2,  # Medium biome - 20% harder
            'tier_1': [
                {'name': 'Bandit Scout', 'health': 50, 'damage': 14, 'experience': 35, 'type': 'melee'},
                {'name': 'Wild Boar', 'health': 55, 'damage': 12, 'experience': 30, 'type': 'melee'},
            ],
            'tier_2': [
                {'name': 'Bandit Raider', 'health': 70, 'damage': 18, 'experience': 55, 'type': 'melee'},
                {'name': 'Orc Scout', 'health': 75, 'damage': 20, 'experience': 60, 'type': 'melee'},
                {'name': 'Orc Crossbow', 'health': 80, 'damage': 22, 'experience': 70, 'type': 'ranged', 'weapon': 'crossbow'}
            ],
            'tier_3': [
                {'name': 'Orc Warrior', 'health': 110, 'damage': 28, 'experience': 90, 'type': 'melee'},
                {'name': 'Bandit Captain', 'health': 100, 'damage': 26, 'experience': 85, 'type': 'melee'},
                {'name': 'Orc Berserker', 'health': 120, 'damage': 32, 'experience': 100, 'type': 'melee'}
            ]
        },
        'DESERT': {
            'difficulty_modifier': 1.4,  # Hard biome - 40% harder
            'tier_1': [
                {'name': 'Desert Scorpion', 'health': 60, 'damage': 16, 'experience': 40, 'type': 'melee'},
                {'name': 'Sand Viper', 'health': 45, 'damage': 18, 'experience': 45, 'type': 'melee'},
            ],
            'tier_2': [
                {'name': 'Giant Scorpion', 'health': 85, 'damage': 24, 'experience': 70, 'type': 'melee'},
                {'name': 'Desert Nomad', 'health': 75, 'damage': 22, 'experience': 65, 'type': 'ranged', 'weapon': 'bow'},
                {'name': 'Sand Elemental', 'health': 90, 'damage': 20, 'experience': 75, 'type': 'melee'}
            ],
            'tier_3': [
                {'name': 'Dark Mage', 'health': 100, 'damage': 30, 'experience': 110, 'type': 'ranged', 'weapon': 'dark_magic'},
                {'name': 'Desert Warlord', 'health': 130, 'damage': 35, 'experience': 120, 'type': 'melee'},
                {'name': 'Ancient Scorpion King', 'health': 140, 'damage': 32, 'experience': 125, 'type': 'melee'}
            ]
        },
        'SNOW': {
            'difficulty_modifier': 1.5,  # Very hard biome - 50% harder
            'tier_1': [
                {'name': 'Ice Wolf', 'health': 55, 'damage': 18, 'experience': 45, 'type': 'melee'},
                {'name': 'Frost Sprite', 'health': 50, 'damage': 16, 'experience': 40, 'type': 'melee'},
            ],
            'tier_2': [
                {'name': 'Ice Troll', 'health': 95, 'damage': 26, 'experience': 80, 'type': 'melee'},
                {'name': 'Crystal Elemental', 'health': 85, 'damage': 28, 'experience': 85, 'type': 'melee'},
                {'name': 'Frost Mage', 'health': 80, 'damage': 30, 'experience': 90, 'type': 'ranged', 'weapon': 'ice_magic'}
            ],
            'tier_3': [
                {'name': 'Ancient Guardian', 'health': 120, 'damage': 35, 'experience': 130, 'type': 'melee'},
                {'name': 'Frost Giant', 'health': 160, 'damage': 40, 'experience': 150, 'type': 'melee'},
                {'name': 'Ice Dragon Wyrmling', 'health': 140, 'damage': 38, 'experience': 140, 'type': 'melee'}
            ]
        },
        'SWAMP': {
            'difficulty_modifier': 1.6,  # Extremely hard biome - 60% harder
            'tier_1': [
                {'name': 'Swamp Rat', 'health': 50, 'damage': 14, 'experience': 35, 'type': 'melee'},
                {'name': 'Bog Sprite', 'health': 55, 'damage': 16, 'experience': 40, 'type': 'melee'},
            ],
            'tier_2': [
                {'name': 'Swamp Troll', 'health': 100, 'damage': 30, 'experience': 95, 'type': 'melee'},
                {'name': 'Poison Archer', 'health': 75, 'damage': 25, 'experience': 80, 'type': 'ranged', 'weapon': 'poison_bow'},
                {'name': 'Bog Witch', 'health': 85, 'damage': 32, 'experience': 100, 'type': 'ranged', 'weapon': 'dark_magic'}
            ],
            'tier_3': [
                {'name': 'Ancient Swamp Lord', 'health': 150, 'damage': 42, 'experience': 160, 'type': 'melee'},
                {'name': 'Plague Bearer', 'health': 130, 'damage': 38, 'experience': 145, 'type': 'melee'},
                {'name': 'Swamp Dragon', 'health': 170, 'damage': 45, 'experience': 180, 'type': 'melee'}
            ]
        }
    }
    
    # Enhanced boss locations with biome-specific scaling
    BOSS_LOCATIONS = [
        {'name': 'Forest Dragon', 'health': 600, 'damage': 45, 'experience': 400, 'biome': 'FOREST'},
        {'name': 'Orc Warlord', 'health': 800, 'damage': 55, 'experience': 500, 'biome': 'PLAINS'},
        {'name': 'Desert Lich', 'health': 900, 'damage': 65, 'experience': 600, 'biome': 'DESERT'},
        {'name': 'Ancient Dragon', 'health': 1200, 'damage': 75, 'experience': 750, 'biome': 'SNOW'},
        {'name': 'Swamp Hydra', 'health': 1000, 'damage': 70, 'experience': 650, 'biome': 'SWAMP'}
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
            # Objects can spawn on walkable biome-specific tiles
            valid_object_tiles = [
                self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE,
                self.TILE_SAND, self.TILE_SNOW, self.TILE_FOREST_FLOOR, self.TILE_SWAMP
            ]
            if tile_type not in valid_object_tiles:
                return False
            
            # Check for nearby walls/buildings (objects shouldn't spawn too close to structures)
            if self._has_nearby_walls(x, y, tiles, radius=2):
                return False
        
        elif entity_type in ["enemy", "boss"]:
            # Enemies need walkable terrain (including biome-specific tiles)
            valid_enemy_tiles = [
                self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE,
                self.TILE_SAND, self.TILE_SNOW, self.TILE_FOREST_FLOOR, self.TILE_SWAMP
            ]
            if tile_type not in valid_enemy_tiles:
                return False
            
            # Enemies shouldn't spawn too close to walls (need movement space)
            if self._has_nearby_walls(x, y, tiles, radius=1):
                return False
        
        elif entity_type == "chest":
            # Chests can spawn on walkable terrain (including biome-specific tiles)
            valid_chest_tiles = [
                self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE,
                self.TILE_SAND, self.TILE_SNOW, self.TILE_FOREST_FLOOR, self.TILE_SWAMP
            ]
            if tile_type not in valid_chest_tiles:
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
        Spawn enemies with tier-based difficulty scaling and biome modifiers
        """
        enemies = []
        
        # Calculate enemy density with improved scaling
        total_area = self.width * self.height
        target_enemies = int(total_area * 0.0015)  # Reduced from 0.003 to 0.0015 - 0.15% of tiles have enemies
        
        attempts = 0
        max_attempts = target_enemies * 25  # More attempts for better tier-based placement
        
        print(f"🎯 Target enemies: {target_enemies} (0.15% of {total_area} tiles)")
        
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
            
            # Get biome and calculate distance to nearest settlement for tier determination
            biome = biome_map[y][x]
            biome_config = self.BIOME_ENEMIES.get(biome)
            
            if not biome_config:
                continue
            
            # Determine enemy tier based on distance from settlements
            distance_to_settlement = self._distance_to_nearest_settlement(x, y, settlement_safe_zones)
            
            if distance_to_settlement < 30:
                tier = 'tier_1'  # Near settlements - beginner enemies
                tier_name = "Beginner"
            elif distance_to_settlement < 60:
                tier = 'tier_2'  # Medium distance - intermediate enemies
                tier_name = "Intermediate"
            else:
                tier = 'tier_3'  # Far from settlements - advanced enemies
                tier_name = "Advanced"
            
            # Get appropriate enemy types for this tier
            enemy_types = biome_config.get(tier, [])
            if not enemy_types:
                continue
            
            # Choose random enemy from tier
            base_enemy_config = random.choice(enemy_types)
            
            # Apply biome difficulty modifier
            difficulty_modifier = biome_config.get('difficulty_modifier', 1.0)
            
            # Scale enemy stats based on biome difficulty
            enemy_config = {
                'name': base_enemy_config['name'],
                'health': int(base_enemy_config['health'] * difficulty_modifier),
                'damage': int(base_enemy_config['damage'] * difficulty_modifier),
                'experience': int(base_enemy_config['experience'] * difficulty_modifier),
                'type': base_enemy_config['type']
            }
            
            # Add weapon if ranged enemy
            if base_enemy_config.get('weapon'):
                enemy_config['weapon'] = base_enemy_config['weapon']
            
            # Import Enemy and RangedEnemy classes
            try:
                from ...entities import Enemy, RangedEnemy
            except ImportError:
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from entities import Enemy, RangedEnemy
                except ImportError:
                    class MockEnemy:
                        def __init__(self, *args, **kwargs):
                            self.x = args[0] if args else 0
                            self.y = args[1] if len(args) > 1 else 0
                            self.name = args[2] if len(args) > 2 else "Enemy"
                        def update(self, level):
                            pass
                    Enemy = MockEnemy
                    RangedEnemy = MockEnemy
            
            # Create appropriate enemy type
            if enemy_config.get('type') == 'ranged':
                weapon_type = enemy_config.get('weapon', 'bow')
                enemy = RangedEnemy(x, y, enemy_config['name'],
                                  health=enemy_config['health'],
                                  damage=enemy_config['damage'],
                                  experience=enemy_config['experience'],
                                  asset_loader=asset_loader,
                                  weapon_type=weapon_type)
            else:
                enemy = Enemy(x, y, enemy_config['name'],
                             health=enemy_config['health'],
                             damage=enemy_config['damage'],
                             experience=enemy_config['experience'],
                             asset_loader=asset_loader)
            
            enemies.append(enemy)
            
            # Mark position as occupied
            self.mark_position_occupied(x, y)
            
            # Debug info for first few enemies
            if len(enemies) <= 5:
                print(f"  🗡️  {enemy_config['name']} ({tier_name}) in {biome}: "
                      f"HP={enemy_config['health']}, DMG={enemy_config['damage']}, "
                      f"XP={enemy_config['experience']}, Distance={distance_to_settlement:.1f}")
        
        # Count enemies by tier and biome for debugging
        tier_counts = {'Beginner': 0, 'Intermediate': 0, 'Advanced': 0}
        biome_counts = {}
        
        for enemy in enemies:
            # Estimate tier based on stats (rough approximation for debug)
            if enemy.health < 70:
                tier_counts['Beginner'] += 1
            elif enemy.health < 120:
                tier_counts['Intermediate'] += 1
            else:
                tier_counts['Advanced'] += 1
            
            # Count by biome (approximate based on position)
            enemy_biome = biome_map[int(enemy.y)][int(enemy.x)]
            biome_counts[enemy_biome] = biome_counts.get(enemy_biome, 0) + 1
        
        print(f"✅ Spawned {len(enemies)} enemies with tier-based scaling:")
        print(f"   📊 Tiers: Beginner={tier_counts['Beginner']}, "
              f"Intermediate={tier_counts['Intermediate']}, Advanced={tier_counts['Advanced']}")
        print(f"   🌍 Biomes: {biome_counts}")
        
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
                
                biome = biome_map[y][x]
                
                # Enhanced position validation for objects
                if not self.is_position_valid_for_entity(x, y, tiles, biome_map, "object"):
                    continue
                
                
                # Biome-specific object spawning with terrain validation and variants
                spawn_chance = 0
                object_variants = []
                
                if biome == 'FOREST':
                    # Trees only on grass/dirt/forest_floor, higher density in forests
                    if tiles[y][x] in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_FOREST_FLOOR]:  # 18 = TILE_FOREST_FLOOR
                        spawn_chance = 0.06  # Reduced from 0.25 - More reasonable forest coverage
                        object_variants = ["pine_tree", "oak_tree", "fallen_log"]
                elif biome == 'PLAINS':
                    # Scattered trees only on grass/dirt
                    if tiles[y][x] in [self.TILE_GRASS, self.TILE_DIRT]:
                        spawn_chance = 0.015  # Reduced from 0.03 - Sparse coverage
                        object_variants = ["oak_tree", "Tree"]  # Mix of new and old
                elif biome == 'DESERT':
                    # Desert objects on sand/dirt/stone
                    if tiles[y][x] in [self.TILE_SAND, self.TILE_DIRT, self.TILE_STONE]:  # 16 = TILE_SAND
                        spawn_chance = 0.03  # Reduced from 0.08 - Moderate coverage
                        object_variants = ["cactus_saguaro", "cactus_barrel", "desert_rock"]
                elif biome == 'SNOW':
                    # Winter objects with terrain restrictions
                    if tiles[y][x] in [self.TILE_SNOW, self.TILE_STONE]:  # 17 = TILE_SNOW
                        spawn_chance = 0.04  # Reduced from 0.10 - Good coverage
                        object_variants = ["snowy_pine", "ice_block", "frozen_rock"]
                elif biome == 'SWAMP':
                    # Swamp objects on swamp/water tiles
                    if tiles[y][x] in [self.TILE_SWAMP, self.TILE_DIRT]:  # 19 = TILE_SWAMP
                        spawn_chance = 0.05  # Reduced from 0.12 - Dense swamp coverage
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
        Find optimal player spawn location within or near a settlement
        
        Args:
            settlements: List of settlement information
            
        Returns:
            (x, y) coordinates for player spawn within/near settlement
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
            # Try to spawn player within the settlement area first
            settlement_x = closest_settlement['x']
            settlement_y = closest_settlement['y']
            
            # Get settlement buildings to find a good spawn location
            buildings = closest_settlement.get('buildings', [])
            
            if buildings:
                # Try to find a courtyard or open area within the settlement
                for attempt in range(20):  # Multiple attempts to find good spot
                    # Try spawning near buildings but not inside them
                    building = random.choice(buildings)
                    
                    # Spawn near the building entrance or courtyard
                    spawn_options = [
                        # Near building entrance (south side)
                        (building['x'] + building['width'] // 2, building['y'] + building['height'] + 2),
                        # Settlement courtyard areas
                        (building['x'] - 3, building['y'] + building['height'] // 2),
                        (building['x'] + building['width'] + 3, building['y'] + building['height'] // 2),
                        # Near settlement center but offset
                        (closest_settlement['center_x'] + random.randint(-8, 8), 
                         closest_settlement['center_y'] + random.randint(-8, 8))
                    ]
                    
                    for spawn_x, spawn_y in spawn_options:
                        # Ensure spawn position is within world bounds
                        spawn_x = max(5, min(self.width - 5, spawn_x))
                        spawn_y = max(5, min(self.height - 5, spawn_y))
                        
                        # Check if this is a reasonable spawn location
                        # (not inside buildings, not too close to walls)
                        if self._is_good_player_spawn(spawn_x, spawn_y, buildings):
                            print(f"Player spawn within {closest_settlement['name']} at ({spawn_x}, {spawn_y})")
                            return (spawn_x, spawn_y)
            
            # Fallback: spawn at settlement border (safe zone edge)
            center_x = closest_settlement['center_x']
            center_y = closest_settlement['center_y']
            
            # Spawn at the edge of the safe zone (radius ~25-30 tiles from center)
            angle = random.uniform(0, 2 * math.pi)
            spawn_radius = random.uniform(20, 30)  # Between 20-30 tiles from center
            
            spawn_x = int(center_x + spawn_radius * math.cos(angle))
            spawn_y = int(center_y + spawn_radius * math.sin(angle))
            
            # Ensure spawn position is within world bounds
            spawn_x = max(5, min(self.width - 5, spawn_x))
            spawn_y = max(5, min(self.height - 5, spawn_y))
            
            print(f"Player spawn near {closest_settlement['name']} border at ({spawn_x}, {spawn_y})")
            return (spawn_x, spawn_y)
        
        return (world_center_x, world_center_y)
    
    def _is_good_player_spawn(self, x: int, y: int, buildings: List[Dict]) -> bool:
        """
        Check if a position is suitable for player spawning
        
        Args:
            x, y: Position to check
            buildings: List of buildings in the settlement
            
        Returns:
            True if position is good for player spawn
        """
        # Check if spawn position is inside any building
        for building in buildings:
            bx, by = building['x'], building['y']
            bw, bh = building['width'], building['height']
            
            # If player would spawn inside building, reject
            if bx <= x < bx + bw and by <= y < by + bh:
                return False
            
            # If too close to building walls (less than 2 tiles), reject
            if (bx - 2 <= x < bx + bw + 2 and by - 2 <= y < by + bh + 2):
                # But allow if it's near the south entrance area
                if by + bh <= y < by + bh + 3 and bx + 2 <= x < bx + bw - 2:
                    continue  # This is near entrance, allow it
                else:
                    return False
        
        return True
    
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
        """Spawn NPCs in settlements with enhanced debugging"""
        npcs = []
        
        print(f"Starting NPC spawning for {len(settlements)} settlements...")
        
        for settlement_idx, settlement in enumerate(settlements):
            settlement_name = settlement.get('name', 'Unknown')
            print(f"  Settlement {settlement_idx + 1}: {settlement_name}")
            
            buildings = settlement.get('buildings', [])
            print(f"    Buildings in settlement: {len(buildings)}")
            
            for building_idx, building in enumerate(buildings):
                building_name = building.get('name', 'Unknown Building')
                npc_name = building.get('npc')
                
                print(f"      Building {building_idx + 1}: {building_name}")
                print(f"        Has NPC: {npc_name is not None}")
                
                if npc_name:
                    # Find interior position for NPC
                    bx, by = building['x'], building['y']
                    bw, bh = building['width'], building['height']
                    
                    # Place NPC in center of building
                    npc_x = bx + bw // 2
                    npc_y = by + bh // 2
                    
                    # Create NPC with appropriate dialog
                    has_shop = building.get('has_shop', False)
                    
                    # Get appropriate dialog for NPC type
                    dialog = self.get_npc_dialog(npc_name)
                    
                    print(f"        Creating NPC: {npc_name} at ({npc_x}, {npc_y}), has_shop: {has_shop}")
                    
                    # Create AI-powered NPC based on type
                    npc = self.create_ai_npc(npc_name, npc_x, npc_y, dialog, has_shop, asset_loader)
                    if npc:
                        npcs.append(npc)
                        # Mark NPC position as occupied
                        self.mark_position_occupied(npc_x, npc_y)
                        print(f"        ✓ Successfully spawned AI-powered {npc_name}")
                    else:
                        print(f"        ✗ Failed to create AI NPC {npc_name}")
                else:
                    print(f"        No NPC assigned to this building")
        
        print(f"NPC spawning complete: {len(npcs)} NPCs created")
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
            ],
            # New NPCs
            'Desert Guide': [
                "The desert is harsh but I know its ways.",
                "Sandstorms can bury entire caravans.",
                "Follow the stars and you'll find your path."
            ],
            'Lodge Keeper': [
                "Welcome to our warm lodge!",
                "The cold winds can be deadly out there.",
                "Stay as long as you need to recover."
            ],
            'Trade Master': [
                "All roads lead to profit, my friend.",
                "I deal in goods from every corner of the realm.",
                "What do you have to trade today?"
            ],
            'Stable Master': [
                "These are the finest mounts in the land.",
                "A good horse can save your life.",
                "Take care of them and they'll take care of you."
            ],
            'Mine Foreman': [
                "The mines run deep and dangerous.",
                "We've struck rich veins of ore lately.",
                "The deeper we dig, the stranger things get."
            ],
            'Head Miner': [
                "Hard work and strong backs built this camp.",
                "The mountain holds treasures beyond imagination.",
                "But it also holds dangers we don't speak of."
            ],
            'Harbor Master': [
                "The waters provide for our village.",
                "Strange currents have been stirring lately.",
                "The fish know things we don't."
            ],
            'Master Fisher': [
                "I've sailed these waters for thirty years.",
                "The deep holds secrets older than memory.",
                "Respect the water and it will feed you."
            ],
            'Water Keeper': [
                "Water is life in the desert.",
                "Every drop is precious here.",
                "I guard our most valuable resource."
            ]
        }
        
        return dialogs.get(npc_name, ["Hello, traveler!"])
    
    def create_ai_npc(self, npc_name: str, x: int, y: int, dialog: List[str], has_shop: bool, asset_loader: Any):
        """Create appropriate AI-powered NPC based on name"""
        try:
            # Map NPC names to their AI classes
            ai_npc_mappings = {
                'Master Merchant': 'MasterMerchantNPC',
                'Village Elder': 'VillageElderNPC', 
                'Master Smith': 'MasterSmithNPC',
                'Innkeeper': 'InnkeeperNPC',
                'Guard Captain': 'GuardCaptainNPC',
                'Caravan Master': 'CaravanMasterNPC',
                'High Priest': 'HealerNPC',  # Use HealerNPC for priests
                'Mine Foreman': 'BlacksmithNPC',  # Use BlacksmithNPC for miners
                'Harbor Master': 'MasterMerchantNPC',  # Use MasterMerchantNPC for harbor masters
                'Master Herbalist': 'HealerNPC',  # Use HealerNPC for herbalists
            }
            
            ai_class_name = ai_npc_mappings.get(npc_name)
            
            if ai_class_name:
                # Try to import the specific AI NPC class
                try:
                    from ...entities.npcs.master_merchant import MasterMerchantNPC
                    from ...entities.npcs.village_elder import VillageElderNPC
                    from ...entities.npcs.master_smith import MasterSmithNPC
                    from ...entities.npcs.innkeeper import InnkeeperNPC
                    from ...entities.npcs.guard_captain import GuardCaptainNPC
                    from ...entities.npcs.caravan_master import CaravanMasterNPC
                    from ...entities.npcs.healer import HealerNPC
                    from ...entities.npcs.blacksmith import BlacksmithNPC
                    
                    # Get the class by name
                    ai_class = locals()[ai_class_name]
                    
                    # Create AI NPC instance
                    npc = ai_class(x, y, asset_loader=asset_loader)
                    
                    # Override name if needed (for cases like High Priest using HealerNPC)
                    if npc.name != npc_name:
                        npc.name = npc_name
                    
                    print(f"        ✓ Created AI-powered {npc_name} using {ai_class_name}")
                    return npc
                    
                except ImportError as e:
                    print(f"        ⚠️  Failed to import AI NPC class {ai_class_name}: {e}")
                    # Fall back to regular NPC
                    pass
            
            # Fallback: Create regular NPC but mark it as AI-ready
            print(f"        ⚠️  No AI class found for {npc_name}, creating AI-ready regular NPC")
            from ...entities import NPC
            
            npc = NPC(x, y, npc_name, dialog=dialog, 
                     asset_loader=asset_loader, has_shop=has_shop)
            
            # Mark as AI-ready so it will be enabled on first interaction
            npc.ai_ready = True
            
            return npc
            
        except ImportError as e:
            print(f"        ✗ Failed to import NPC classes: {e}")
            # Final fallback - try alternative import path
            try:
                import sys
                import os
                sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                from entities import NPC
                
                npc = NPC(x, y, npc_name, dialog=dialog, 
                         asset_loader=asset_loader, has_shop=has_shop)
                npc.ai_ready = True  # Mark as AI-ready
                return npc
                
            except ImportError:
                print(f"        ✗ All import attempts failed for {npc_name}")
                return None
        
        except Exception as e:
            print(f"        ✗ Unexpected error creating AI NPC {npc_name}: {e}")
            import traceback
            traceback.print_exc()
            return None