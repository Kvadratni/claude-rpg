"""
Simplified procedural map generation for Goose RPG
Generates 4 biomes (Desert, Forest, Plains, Snow) with template-based settlements
"""

import pygame
import random
import math
from typing import Dict, List, Tuple, Optional
from ..entities import Entity, NPC, Enemy, Item, Chest

class ProceduralGenerator:
    """
    Simple procedural world generator using existing assets
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
            'primary': 0,    # TILE_GRASS
            'secondary': 1,  # TILE_DIRT
            'paths': 1,      # TILE_DIRT (forest paths)
            'water_chance': 0.008  # Reduced from 0.03
        },
        'DESERT': {
            'primary': 1,    # TILE_DIRT (sand)
            'secondary': 2,  # TILE_STONE (rocky outcrops)
            'paths': 2,      # TILE_STONE
            'water_chance': 0.002  # Reduced from 0.005
        },
        'SNOW': {
            'primary': 0,    # TILE_GRASS (snow-covered)
            'secondary': 2,  # TILE_STONE (frozen ground)
            'paths': 2,      # TILE_STONE
            'water_chance': 0.003  # Reduced from 0.01
        }
    }
    
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
    
    # Settlement templates
    SETTLEMENT_TEMPLATES = {
        'VILLAGE': {
            'size': (25, 25),
            'buildings': [
                {'name': 'General Store', 'size': (12, 8), 'npc': 'Master Merchant', 'has_shop': True},
                {'name': 'Inn', 'size': (10, 8), 'npc': 'Innkeeper', 'has_shop': False},
                {'name': 'Blacksmith', 'size': (8, 6), 'npc': 'Master Smith', 'has_shop': True},
                {'name': 'Elder House', 'size': (10, 8), 'npc': 'Village Elder', 'has_shop': False},
                {'name': 'Guard House', 'size': (8, 6), 'npc': 'Guard Captain', 'has_shop': False}
            ],
            'biomes': ['PLAINS', 'FOREST'],
            'safe_radius': 40  # Increased from 20 for better protection
        },
        'DESERT_OUTPOST': {
            'size': (20, 20),
            'buildings': [
                {'name': 'Trading Post', 'size': (10, 8), 'npc': 'Caravan Master', 'has_shop': True},
                {'name': 'Water Storage', 'size': (6, 6)},
                {'name': 'Caravan Rest', 'size': (10, 6)}
            ],
            'biomes': ['DESERT'],
            'safe_radius': 30  # Increased from 15 for better protection
        },
        'SNOW_SETTLEMENT': {
            'size': (18, 18),
            'buildings': [
                {'name': 'Ranger Station', 'size': (8, 6), 'npc': 'Forest Ranger', 'has_shop': False},
                {'name': 'Herbalist Hut', 'size': (8, 6), 'npc': 'Master Herbalist', 'has_shop': True},
                {'name': 'Warm Lodge', 'size': (10, 8)}
            ],
            'biomes': ['SNOW'],
            'safe_radius': 30  # Increased from 15 for better protection
        }
    }
    
    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(0, 1000000)
        
        # Initialize random with seed
        random.seed(self.seed)
        
        # Generate biome map
        self.biome_map = self.generate_biome_map()
        
        # Track placed objects for collision
        self.occupied_areas = []  # List of (x, y, width, height) rectangles
        self.settlement_safe_zones = []  # List of (center_x, center_y, radius)
        
        print(f"Procedural generator initialized with seed: {self.seed}")
    
    def generate_biome_map(self):
        """Generate simple biome map using basic noise"""
        biome_map = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Simple noise based on position and seed
                noise_value = self.simple_noise(x, y)
                
                # Determine biome based on noise value - Balanced distribution
                if noise_value < 0.15:
                    biome = 'DESERT'
                elif noise_value < 0.45:
                    biome = 'PLAINS'
                elif noise_value < 0.75:
                    biome = 'FOREST'
                else:
                    biome = 'SNOW'
                
                row.append(biome)
            biome_map.append(row)
        
        return biome_map
    
    def simple_noise(self, x, y):
        """Generate simple pseudo-random noise with better distribution"""
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
    
    def generate_tiles(self):
        """Generate tile grid based on biome map"""
        tiles = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                biome = self.biome_map[y][x]
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
    
    def place_settlements(self, tiles):
        """Place settlements using templates with collision detection"""
        settlements = []
        
        # Try to place one settlement of each type
        for template_name, template_config in self.SETTLEMENT_TEMPLATES.items():
            settlement = self.try_place_settlement(template_name, template_config, tiles)
            if settlement:
                settlements.append(settlement)
        
        print(f"Placed {len(settlements)} settlements")
        return settlements
    
    def try_place_settlement(self, template_name, template_config, tiles, max_attempts=50):
        """Try to place a settlement, return placement info if successful"""
        settlement_width, settlement_height = template_config['size']
        suitable_biomes = template_config['biomes']
        
        # Strategy 1: Strict placement (no water tolerance)
        for _ in range(max_attempts // 2):
            x = random.randint(10, self.width - settlement_width - 10)
            y = random.randint(10, self.height - settlement_height - 10)
            
            # Check if biome is suitable
            center_biome = self.biome_map[y + settlement_height // 2][x + settlement_width // 2]
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
            center_biome = self.biome_map[y + settlement_height // 2][x + settlement_width // 2]
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
    
    def _finalize_settlement_placement(self, template_name, template_config, tiles, x, y, center_biome):
        """Finalize settlement placement and return settlement info"""
        settlement_width, settlement_height = template_config['size']
        
        # Place the settlement
        self.place_settlement_buildings(tiles, x, y, template_config)
        
        # Mark area as occupied
        self.occupied_areas.append((x, y, settlement_width, settlement_height))
        
        # Add safe zone
        safe_radius = template_config.get('safe_radius', 30)  # Increased default from 15
        center_x = x + settlement_width // 2
        center_y = y + settlement_height // 2
        self.settlement_safe_zones.append((center_x, center_y, safe_radius))
        
        settlement_info = {
            'name': template_name,
            'x': x,
            'y': y,
            'center_x': center_x,
            'center_y': center_y,
            'size': template_config['size'],
            'buildings': template_config['buildings'],
            'biome': center_biome
        }
        
        print(f"Placed {template_name} at ({x}, {y}) in {center_biome} biome")
        return settlement_info
    
    def place_settlement_buildings(self, tiles, start_x, start_y, template_config):
        """Place buildings for a settlement with improved placement logic"""
        settlement_width, settlement_height = template_config['size']
        
        # Create smaller stone square in center to leave more room for buildings
        center_size = min(settlement_width, settlement_height) // 3  # Reduced from // 2
        center_start_x = start_x + (settlement_width - center_size) // 2
        center_start_y = start_y + (settlement_height - center_size) // 2
        
        for x in range(center_start_x, center_start_x + center_size):
            for y in range(center_start_y, center_start_y + center_size):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = 2  # TILE_STONE
        
        # Place buildings around the center with improved logic
        buildings = template_config['buildings']
        placed_buildings = []
        
        for building in buildings:
            building_width, building_height = building['size']
            
            # Try to find a good spot for this building with more attempts
            for attempt in range(50):  # Increased from 20
                # Random position within settlement bounds with better margins
                margin = 1  # Reduced margin
                bx = start_x + margin + random.randint(0, settlement_width - building_width - margin * 2)
                by = start_y + margin + random.randint(0, settlement_height - building_height - margin * 2)
                
                # Check if building would overlap with center square (with smaller margin)
                if self.building_overlaps_area_relaxed(bx, by, building_width, building_height, 
                                             center_start_x, center_start_y, center_size, center_size):
                    continue
                
                if any(self.building_overlaps_area_relaxed(bx, by, building_width, building_height,
                                                 pb['x'], pb['y'], pb['width'], pb['height'])
                       for pb in placed_buildings):
                    continue
                
                # Place the building
                self.create_building(tiles, bx, by, building_width, building_height)
                
                placed_buildings.append({
                    'x': bx, 'y': by, 'width': building_width, 'height': building_height,
                    'name': building['name'], 'npc': building.get('npc'),
                    'has_shop': building.get('has_shop', False)
                })
                break
        
        return placed_buildings
    
    def building_overlaps_area_relaxed(self, bx, by, bw, bh, ax, ay, aw, ah):
        """Check if building overlaps with an area (with smaller margin)"""
        margin = 1  # Reduced from 2
        return not (bx + bw + margin <= ax or ax + aw + margin <= bx or 
                   by + bh + margin <= ay or ay + ah + margin <= by)
    
    def create_building(self, tiles, start_x, start_y, width, height):
        """Create a building structure using enhanced building system from level.py"""
        # Building interior floor - use brick tiles for more realistic interiors
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                if 0 <= x < self.width and 0 <= y < self.height:
                    tiles[y][x] = 13  # TILE_BRICK
        
        # Building walls - use enhanced wall system
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if 0 <= x < self.width and 0 <= y < self.height:
                    # Skip interior
                    if (x > start_x and x < start_x + width - 1 and 
                        y > start_y and y < start_y + height - 1):
                        continue
                    
                    # Use regular walls for all positions initially
                    tiles[y][x] = 4  # TILE_WALL
        
        # Add variety with horizontal and vertical walls
        # Top and bottom walls
        for x in range(start_x + 1, start_x + width - 1):
            if 0 <= x < self.width:
                # Top wall
                if start_y >= 0 and start_y < self.height:
                    if random.random() < 0.2:  # 20% chance for windows
                        tiles[start_y][x] = 14  # TILE_WALL_WINDOW_HORIZONTAL
                    else:
                        tiles[start_y][x] = 10  # TILE_WALL_HORIZONTAL
                
                # Bottom wall (will be overridden by doors)
                bottom_y = start_y + height - 1
                if 0 <= bottom_y < self.height:
                    if random.random() < 0.2:  # 20% chance for windows
                        tiles[bottom_y][x] = 14  # TILE_WALL_WINDOW_HORIZONTAL
                    else:
                        tiles[bottom_y][x] = 10  # TILE_WALL_HORIZONTAL
        
        # Left and right walls
        for y in range(start_y + 1, start_y + height - 1):
            if 0 <= y < self.height:
                # Left wall
                if start_x >= 0 and start_x < self.width:
                    if random.random() < 0.15:  # 15% chance for windows
                        tiles[y][start_x] = 15  # TILE_WALL_WINDOW_VERTICAL
                    else:
                        tiles[y][start_x] = 11  # TILE_WALL_VERTICAL
                
                # Right wall
                right_x = start_x + width - 1
                if 0 <= right_x < self.width:
                    if random.random() < 0.15:  # 15% chance for windows
                        tiles[y][right_x] = 15  # TILE_WALL_WINDOW_VERTICAL
                    else:
                        tiles[y][right_x] = 11  # TILE_WALL_VERTICAL
        
        # Add double doors (2 tiles wide) - replace bottom wall sections
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        
        # Create 2-tile wide door centered on the building
        door_x1 = door_center_x - 1
        door_x2 = door_center_x
        
        # Make sure both door positions are valid and within the building wall
        if (0 <= door_x1 < self.width and 0 <= door_y < self.height and 
            door_x1 > start_x and door_x1 < start_x + width - 1):
            tiles[door_y][door_x1] = 5  # TILE_DOOR
        
        if (0 <= door_x2 < self.width and 0 <= door_y < self.height and 
            door_x2 > start_x and door_x2 < start_x + width - 1):
            tiles[door_y][door_x2] = 5  # TILE_DOOR
    
    def spawn_npcs(self, settlements, asset_loader):
        """Spawn NPCs in settlements"""
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
                    
                    npc = NPC(npc_x, npc_y, npc_name, dialog=dialog, 
                             asset_loader=asset_loader, has_shop=has_shop)
                    npcs.append(npc)
                    
                    print(f"Spawned {npc_name} at ({npc_x}, {npc_y})")
        
        return npcs
    
    def get_npc_dialog(self, npc_name):
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
    
    def spawn_enemies(self, tiles, asset_loader):
        """Spawn enemies based on biomes with safe zone restrictions"""
        enemies = []
        
        # Calculate enemy density (fewer enemies than current system)
        total_area = self.width * self.height
        target_enemies = int(total_area * 0.0008)  # Reduced from 0.001 to 0.0008 - 0.08% of tiles have enemies
        
        attempts = 0
        max_attempts = target_enemies * 10
        
        while len(enemies) < target_enemies and attempts < max_attempts:
            attempts += 1
            
            # Random position
            x = random.randint(5, self.width - 6)
            y = random.randint(5, self.height - 6)
            
            # Check if position is in safe zone
            if self.is_in_safe_zone(x, y):
                continue
            
            # Check if terrain is suitable (not water or walls)
            if tiles[y][x] in [3, 4]:  # TILE_WATER or TILE_WALL
                continue
            
            # Get biome and spawn appropriate enemy
            biome = self.biome_map[y][x]
            enemy_types = self.BIOME_ENEMIES.get(biome, [])
            
            if not enemy_types:
                continue
            
            enemy_config = random.choice(enemy_types)
            enemy = Enemy(x, y, enemy_config['name'],
                         health=enemy_config['health'],
                         damage=enemy_config['damage'],
                         experience=enemy_config['experience'],
                         asset_loader=asset_loader)
            enemies.append(enemy)
        
        print(f"Spawned {len(enemies)} enemies")
        return enemies
    
    def spawn_bosses(self, tiles, asset_loader):
        """Spawn boss enemies in appropriate locations"""
        bosses = []
        
        for boss_config in self.BOSS_LOCATIONS:
            boss_biome = boss_config['biome']
            
            # Find suitable location in the specified biome
            for attempt in range(100):
                x = random.randint(20, self.width - 21)
                y = random.randint(20, self.height - 21)
                
                # Check biome
                if self.biome_map[y][x] != boss_biome:
                    continue
                
                # Check if far from settlements (increased distance requirement)
                if self.is_in_safe_zone(x, y) or self.distance_to_nearest_settlement(x, y) < 80:  # Increased from 40
                    continue
                
                # Check terrain
                if tiles[y][x] in [3, 4]:  # TILE_WATER or TILE_WALL
                    continue
                
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
    
    def spawn_objects(self, tiles, asset_loader):
        """Spawn environmental objects (trees, rocks) based on biomes"""
        objects = []
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Skip if tile is not suitable
                if tiles[y][x] != 0:  # Only spawn on grass
                    continue
                
                # Skip if in safe zone
                if self.is_in_safe_zone(x, y):
                    continue
                
                biome = self.biome_map[y][x]
                
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
                    obj = Entity(x, y, object_type, entity_type="object", 
                               blocks_movement=True, asset_loader=asset_loader)
                    objects.append(obj)
        
        print(f"Spawned {len(objects)} objects")
        return objects
    
    def spawn_chests(self, tiles, asset_loader):
        """Spawn treasure chests in appropriate locations"""
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
            if self.is_in_safe_zone(x, y):
                continue
            
            # Determine chest type based on distance from settlements
            distance = self.distance_to_nearest_settlement(x, y)
            
            if distance < 25:
                chest_type = "wooden"
            elif distance < 50:
                chest_type = "iron"
            else:
                chest_type = "gold"
            
            chest = Chest(x, y, chest_type, asset_loader)
            chests.append(chest)
            
            if len(chests) >= target_chests:
                break
        
        print(f"Spawned {len(chests)} chests")
        return chests
    
    # Helper methods
    def check_area_collision(self, x, y, width, height):
        """Check if area collides with existing occupied areas"""
        new_rect = (x, y, width, height)
        for existing_rect in self.occupied_areas:
            if self.rectangles_overlap(new_rect, existing_rect):
                return True
        return False
    
    def rectangles_overlap(self, rect1, rect2):
        """Check if two rectangles overlap"""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)
    
    def building_overlaps_area(self, bx, by, bw, bh, ax, ay, aw, ah):
        """Check if building overlaps with an area (with margin)"""
        margin = 2
        return not (bx + bw + margin <= ax or ax + aw + margin <= bx or 
                   by + bh + margin <= ay or ay + ah + margin <= by)
    
    def has_water_in_area(self, tiles, x, y, width, height, max_water_tiles=3):
        """Check if area contains too many water tiles"""
        water_count = 0
        total_tiles = width * height
        
        for cy in range(y, y + height):
            for cx in range(x, x + width):
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    if tiles[cy][cx] == 3:  # TILE_WATER
                        water_count += 1
                        if water_count > max_water_tiles:
                            return True
        
        # Allow small amounts of water (like a pond or stream)
        return False
    
    def is_in_safe_zone(self, x, y):
        """Check if position is within any settlement safe zone"""
        for center_x, center_y, radius in self.settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if distance < radius:
                return True
        return False
    
    def distance_to_nearest_settlement(self, x, y):
        """Calculate distance to nearest settlement"""
        if not self.settlement_safe_zones:
            return float('inf')
        
        min_distance = float('inf')
        for center_x, center_y, _ in self.settlement_safe_zones:
            distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def generate_walkable_grid(self, tiles):
        """Generate walkable grid from tiles"""
        walkable = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_type = tiles[y][x]
                # Walkable tiles: grass, dirt, stone, door, brick, sand, snow, forest_floor, swamp
                is_walkable = tile_type in [0, 1, 2, 5, 13, 16, 17, 18, 19]
                row.append(1.0 if is_walkable else 0.0)
            walkable.append(row)
        
        return walkable