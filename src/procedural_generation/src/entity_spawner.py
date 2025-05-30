"""
Entity Spawning Module for Procedural World Generation
Handles spawning of enemies, bosses, NPCs, objects, and chests
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any


class EntitySpawner:
    """
    Spawns various entities in procedural worlds
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
    
    def __init__(self, width: int, height: int, seed: int = None):
        """
        Initialize entity spawner
        
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
        
        print(f"EntitySpawner initialized with seed: {self.seed}")
    
    def spawn_npcs(self, settlements: List[Dict], asset_loader: Any) -> List[Any]:
        """
        Spawn NPCs in settlements
        
        Args:
            settlements: List of settlement information
            asset_loader: Asset loader for sprites
            
        Returns:
            List of NPC entities
        """
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
                    
                    # Import NPC class dynamically to avoid circular imports
                    try:
                        from ...entities import NPC
                    except ImportError:
                        try:
                            # Alternative import path
                            import sys
                            import os
                            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                            from entities import NPC
                        except ImportError:
                            # Fallback for testing without game dependencies
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
                    
                    print(f"Spawned {npc_name} at ({npc_x}, {npc_y})")
        
        return npcs
    
    def spawn_enemies(self, tiles: List[List[int]], biome_map: List[List[str]], 
                     settlement_safe_zones: List[Tuple[int, int, int]], 
                     asset_loader: Any) -> List[Any]:
        """
        Spawn enemies based on biomes with safe zone restrictions
        
        Args:
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            settlement_safe_zones: List of (center_x, center_y, radius) tuples
            asset_loader: Asset loader for sprites
            
        Returns:
            List of enemy entities
        """
        enemies = []
        
        # Calculate enemy density (fewer enemies than current system)
        total_area = self.width * self.height
        target_enemies = int(total_area * 0.001)  # 0.1% of tiles have enemies
        
        attempts = 0
        max_attempts = target_enemies * 10
        
        while len(enemies) < target_enemies and attempts < max_attempts:
            attempts += 1
            
            # Random position
            x = random.randint(5, self.width - 6)
            y = random.randint(5, self.height - 6)
            
            # Check if position is in safe zone
            if self._is_in_safe_zone(x, y, settlement_safe_zones):
                continue
            
            # Check if terrain is suitable (not water or walls)
            if tiles[y][x] in [3, 4]:  # TILE_WATER or TILE_WALL
                continue
            
            # Get biome and spawn appropriate enemy
            biome = biome_map[y][x]
            enemy_types = self.BIOME_ENEMIES.get(biome, [])
            
            if not enemy_types:
                continue
            
            enemy_config = random.choice(enemy_types)
            
            # Import Enemy class dynamically to avoid circular imports
            try:
                from ...entities import Enemy
            except ImportError:
                try:
                    # Alternative import path
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from entities import Enemy
                except ImportError:
                    # Fallback for testing without game dependencies
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
        
        print(f"Spawned {len(enemies)} enemies")
        return enemies
    
    def spawn_bosses(self, tiles: List[List[int]], biome_map: List[List[str]], 
                    settlement_safe_zones: List[Tuple[int, int, int]], 
                    asset_loader: Any) -> List[Any]:
        """
        Spawn boss enemies in appropriate locations
        
        Args:
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            settlement_safe_zones: List of (center_x, center_y, radius) tuples
            asset_loader: Asset loader for sprites
            
        Returns:
            List of boss entities
        """
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
                
                # Check terrain
                if tiles[y][x] in [3, 4]:  # TILE_WATER or TILE_WALL
                    continue
                
                # Import Enemy class dynamically to avoid circular imports
                try:
                    from ...entities import Enemy
                except ImportError:
                    try:
                        # Alternative import path
                        import sys
                        import os
                        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                        from entities import Enemy
                    except ImportError:
                        # Fallback for testing without game dependencies
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
                
                print(f"Spawned {boss_config['name']} at ({x}, {y}) in {boss_biome}")
                break
        
        return bosses
    
    def spawn_objects(self, tiles: List[List[int]], biome_map: List[List[str]], 
                     settlement_safe_zones: List[Tuple[int, int, int]], 
                     asset_loader: Any) -> List[Any]:
        """
        Spawn environmental objects (trees, rocks) based on biomes
        
        Args:
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            settlement_safe_zones: List of (center_x, center_y, radius) tuples
            asset_loader: Asset loader for sprites
            
        Returns:
            List of object entities
        """
        objects = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Skip if tile is not suitable
                if tiles[y][x] != 0:  # Only spawn on grass
                    continue
                
                # Skip if in safe zone
                if self._is_in_safe_zone(x, y, settlement_safe_zones):
                    continue
                
                biome = biome_map[y][x]
                
                # Biome-specific object spawning
                spawn_chance = 0
                object_type = "Tree"
                
                if biome == 'FOREST':
                    spawn_chance = 0.3  # Dense forests
                    object_type = "Tree"
                elif biome == 'PLAINS':
                    spawn_chance = 0.05  # Scattered trees
                    object_type = "Tree"
                elif biome == 'DESERT':
                    spawn_chance = 0.08  # Rocks and cacti
                    object_type = "Rock"
                elif biome == 'SNOW':
                    spawn_chance = 0.1  # Frozen trees and rocks
                    object_type = random.choice(["Tree", "Rock"])
                
                if random.random() < spawn_chance:
                    # Import Entity class dynamically to avoid circular imports
                    try:
                        from ...entities import Entity
                    except ImportError:
                        try:
                            # Alternative import path
                            import sys
                            import os
                            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                            from entities import Entity
                        except ImportError:
                            # Fallback for testing without game dependencies
                            class MockEntity:
                                def __init__(self, *args, **kwargs):
                                    self.x = args[0] if args else 0
                                    self.y = args[1] if len(args) > 1 else 0
                                    self.name = args[2] if len(args) > 2 else "Object"
                                def update(self, level):
                                    pass
                            Entity = MockEntity
                    
                    obj = Entity(x, y, object_type, entity_type="object", 
                               blocks_movement=True, asset_loader=asset_loader)
                    objects.append(obj)
        
        print(f"Spawned {len(objects)} objects")
        return objects
    
    def spawn_chests(self, tiles: List[List[int]], biome_map: List[List[str]], 
                    settlement_safe_zones: List[Tuple[int, int, int]], 
                    asset_loader: Any) -> List[Any]:
        """
        Spawn treasure chests in appropriate locations
        
        Args:
            tiles: 2D list of tile types
            biome_map: 2D list of biome names
            settlement_safe_zones: List of (center_x, center_y, radius) tuples
            asset_loader: Asset loader for sprites
            
        Returns:
            List of chest entities
        """
        chests = []
        
        # Spawn fewer chests than current system
        target_chests = 15
        
        for _ in range(target_chests * 3):  # Try 3x as many times as target
            x = random.randint(10, self.width - 11)
            y = random.randint(10, self.height - 11)
            
            # Check terrain
            if tiles[y][x] != 0:  # Only on grass
                continue
            
            # Don't spawn in safe zones
            if self._is_in_safe_zone(x, y, settlement_safe_zones):
                continue
            
            # Determine chest type based on distance from settlements
            distance = self._distance_to_nearest_settlement(x, y, settlement_safe_zones)
            
            if distance < 25:
                chest_type = "wooden"
            elif distance < 50:
                chest_type = "iron"
            else:
                chest_type = "gold"
            
            # Import Chest class dynamically to avoid circular imports
            try:
                from ...entities import Chest
            except ImportError:
                try:
                    # Alternative import path
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                    from entities import Chest
                except ImportError:
                    # Fallback for testing without game dependencies
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
            
            if len(chests) >= target_chests:
                break
        
        print(f"Spawned {len(chests)} chests")
        return chests
    
    def get_npc_dialog(self, npc_name: str) -> List[str]:
        """
        Get appropriate dialog for NPC types
        
        Args:
            npc_name: Name of the NPC
            
        Returns:
            List of dialog strings
        """
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
    
    # Helper methods
    def _is_in_safe_zone(self, x: int, y: int, 
                        settlement_safe_zones: List[Tuple[int, int, int]]) -> bool:
        """
        Check if position is within any settlement safe zone
        
        Args:
            x, y: Position to check
            settlement_safe_zones: List of (center_x, center_y, radius) tuples
            
        Returns:
            True if in safe zone
        """
        for center_x, center_y, radius in settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < radius:
                return True
        return False
    
    def _distance_to_nearest_settlement(self, x: int, y: int, 
                                      settlement_safe_zones: List[Tuple[int, int, int]]) -> float:
        """
        Calculate distance to nearest settlement
        
        Args:
            x, y: Position to check
            settlement_safe_zones: List of (center_x, center_y, radius) tuples
            
        Returns:
            Distance to nearest settlement
        """
        if not settlement_safe_zones:
            return float('inf')
        
        min_distance = float('inf')
        for center_x, center_y, _ in settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            min_distance = min(min_distance, distance)
        
        return min_distance