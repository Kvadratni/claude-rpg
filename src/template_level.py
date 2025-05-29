"""
Enhanced level generation using image-based map templates
"""

import pygame
import random
import math
import os
from typing import Dict, List, Tuple, Set, Optional
from .map_template import MapTemplate
from .entity import Entity, NPC, Enemy, Item, Chest

class TemplateBasedLevel:
    """
    Level generator that uses image templates for deterministic map generation
    """
    
    # Tile type mappings from template colors
    TILE_MAPPINGS = {
        'GRASS': 0,      # TILE_GRASS
        'DIRT': 1,       # TILE_DIRT  
        'STONE': 2,      # TILE_STONE
        'WATER': 3,      # TILE_WATER
        'IMPASSABLE': 4, # TILE_WALL
        'BUILDING': 4,   # TILE_WALL
        'INTERIOR': 13,  # TILE_BRICK
        'DOOR': 5,       # TILE_DOOR
        'FOREST': 0,     # TILE_GRASS (will have trees)
        'NPC_SPAWN': 13, # TILE_BRICK (interior floor for NPCs)
    }
    
    def __init__(self, template_path: str):
        """Initialize with map template"""
        self.template = MapTemplate(template_path)
        self.width = self.template.width
        self.height = self.template.height
        
        # Entity lists
        self.npcs = []
        self.enemies = []
        self.items = []
        self.objects = []
        self.chests = []
        
        print(f"Initialized template-based level: {self.width}x{self.height}")
    
    def generate_tiles(self) -> List[List[int]]:
        """Generate tile grid from template with corner detection"""
        tiles = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                terrain_type = self.template.get_terrain_type(x, y)
                tile_id = self.TILE_MAPPINGS.get(terrain_type, 0)  # Default to grass
                row.append(tile_id)
            tiles.append(row)
        
        # POST-PROCESS: Add corner detection for buildings
        tiles = self.add_wall_corners(tiles)
        
        print("Generated tiles from template")
        return tiles
    
    def add_wall_corners(self, tiles: List[List[int]]) -> List[List[int]]:
        """Add proper corner tiles to wall structures"""
        # Create a copy to modify
        new_tiles = [row[:] for row in tiles]
        
        # Corner tile constants (matching level.py)
        TILE_WALL = 4
        TILE_WALL_CORNER_TL = 6  # Top-left corner
        TILE_WALL_CORNER_TR = 7  # Top-right corner
        TILE_WALL_CORNER_BL = 8  # Bottom-left corner
        TILE_WALL_CORNER_BR = 9  # Bottom-right corner
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if tiles[y][x] == TILE_WALL:
                    # Check if this wall tile should be a corner
                    # Check 8 directions around this tile
                    n = tiles[y-1][x] == TILE_WALL      # North
                    s = tiles[y+1][x] == TILE_WALL      # South  
                    e = tiles[y][x+1] == TILE_WALL      # East
                    w = tiles[y][x-1] == TILE_WALL      # West
                    ne = tiles[y-1][x+1] == TILE_WALL   # Northeast
                    nw = tiles[y-1][x-1] == TILE_WALL   # Northwest
                    se = tiles[y+1][x+1] == TILE_WALL   # Southeast
                    sw = tiles[y+1][x-1] == TILE_WALL   # Southwest
                    
                    # Detect corner patterns
                    # Top-left corner: has walls to south and east, but not north or west
                    if s and e and not n and not w:
                        new_tiles[y][x] = TILE_WALL_CORNER_TL
                    
                    # Top-right corner: has walls to south and west, but not north or east
                    elif s and w and not n and not e:
                        new_tiles[y][x] = TILE_WALL_CORNER_TR
                    
                    # Bottom-left corner: has walls to north and east, but not south or west
                    elif n and e and not s and not w:
                        new_tiles[y][x] = TILE_WALL_CORNER_BL
                    
                    # Bottom-right corner: has walls to north and west, but not south or east
                    elif n and w and not s and not e:
                        new_tiles[y][x] = TILE_WALL_CORNER_BR
        
        return new_tiles
    
    def generate_walkable_grid(self, tiles: List[List[int]]) -> List[List[bool]]:
        """Generate walkable grid from tiles"""
        walkable = []
        
        # Walkable tile types
        walkable_tiles = {0, 1, 2, 5, 13}  # GRASS, DIRT, STONE, DOOR, BRICK
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_type = tiles[y][x]
                row.append(tile_type in walkable_tiles)
            walkable.append(row)
        
        return walkable
    
    def spawn_npcs(self, asset_loader) -> List[NPC]:
        """Spawn NPCs at designated template locations"""
        npcs = []
        npc_spawns = self.template.get_spawn_points('NPC_SPAWN')
        
        # Predefined NPC data matching original positions
        npc_data = [
            {
                'name': 'Master Merchant',
                'dialog': [
                    "Welcome to the finest shop in all the lands!",
                    "I have goods from every corner of the realm!",
                    "The roads are dangerous, but profitable for traders.",
                    "I hear the ancient ruins hold great treasures..."
                ],
                'has_shop': True,
                'expected_pos': (77, 85)
            },
            {
                'name': 'Village Elder',
                'dialog': [
                    "Welcome, brave adventurer!",
                    "Our peaceful village sits at the crossroads of many realms.",
                    "To the north lie ancient forests filled with danger.",
                    "The mountains hold both treasure and terror.",
                    "The desert sands conceal forgotten secrets.",
                    "May your journey bring you wisdom and fortune!"
                ],
                'has_shop': False,
                'expected_pos': (122, 85)
            },
            {
                'name': 'Master Smith',
                'dialog': [
                    "The forge burns hot today!",
                    "I craft the finest weapons and armor.",
                    "Bring me rare metals and I'll make you legendary gear!",
                    "The crystal caves have materials I need..."
                ],
                'has_shop': True,
                'expected_pos': (76, 109)
            },
            {
                'name': 'Innkeeper',
                'dialog': [
                    "Welcome to the Crossroads Inn!",
                    "Travelers from all lands rest here.",
                    "I've heard tales of dragons in the northern peaks.",
                    "The swamp folk speak of ancient magic.",
                    "Rest well, the roads are perilous."
                ],
                'has_shop': False,
                'expected_pos': (121, 109)
            },
            {
                'name': 'High Priest',
                'dialog': [
                    "The light guides all who seek it.",
                    "Ancient evils stir in the forgotten places.",
                    "The stone circles hold power beyond understanding.",
                    "May the divine protect you on your journey."
                ],
                'has_shop': False,
                'expected_pos': (100, 70)
            },
            {
                'name': 'Guard Captain',
                'dialog': [
                    "I keep watch over our village.",
                    "Bandits have been spotted on the roads.",
                    "The northern forests grow more dangerous each day.",
                    "If you're heading out, be well armed!",
                    "Report any suspicious activity to me."
                ],
                'has_shop': False,
                'expected_pos': (65, 97)
            }
        ]
        
        # Match NPCs to spawn points
        for npc_info in npc_data:
            # Find closest spawn point to expected position
            expected_x, expected_y = npc_info['expected_pos']
            closest_spawn = self.template.find_nearest_spawn_point(expected_x, expected_y, 'NPC_SPAWN')
            
            if closest_spawn:
                x, y = closest_spawn
                # Mark this spawn point as used
                if closest_spawn in npc_spawns:
                    npc_spawns.remove(closest_spawn)
                
                npc = NPC(
                    x, y, npc_info['name'],
                    dialog=npc_info['dialog'],
                    asset_loader=asset_loader,
                    has_shop=npc_info['has_shop']
                )
                npcs.append(npc)
                self.template.mark_occupied(x, y)
                
                print(f"Spawned {npc_info['name']} at ({x}, {y})")
        
        return npcs
    
    def spawn_enemies(self, asset_loader) -> List[Enemy]:
        """Spawn enemies at designated template locations"""
        enemies = []
        enemy_spawns = self.template.get_spawn_points('ENEMY_SPAWN')
        
        # Enemy types for different areas
        enemy_types = [
            {'name': 'Forest Goblin', 'health': 45, 'damage': 9, 'experience': 30},
            {'name': 'Forest Sprite', 'health': 35, 'damage': 12, 'experience': 40},
            {'name': 'Ancient Guardian', 'health': 60, 'damage': 15, 'experience': 50},
            {'name': 'Bandit Scout', 'health': 35, 'damage': 8, 'experience': 20},
            {'name': 'Wild Wolf', 'health': 40, 'damage': 10, 'experience': 25},
        ]
        
        # Spawn enemies at template locations
        for x, y in enemy_spawns:
            if self.template.is_position_available(x, y):
                # Choose enemy type based on location
                terrain = self.template.get_terrain_type(x, y)
                
                if terrain == 'ENEMY_SPAWN':
                    # Determine enemy type by area
                    if 30 <= x <= 70 and 30 <= y <= 70:  # Dark forest area
                        enemy_type = enemy_types[0]  # Forest Goblin
                    elif 140 <= x <= 180 and 30 <= y <= 70:  # Ancient woods
                        enemy_type = enemy_types[2]  # Ancient Guardian
                    elif 80 <= x <= 120 and 25 <= y <= 55:  # Enchanted grove
                        enemy_type = enemy_types[1]  # Forest Sprite
                    else:  # Village patrol areas
                        enemy_type = enemy_types[3]  # Bandit Scout
                    
                    enemy = Enemy(
                        x, y, enemy_type['name'],
                        health=enemy_type['health'],
                        damage=enemy_type['damage'],
                        experience=enemy_type['experience'],
                        asset_loader=asset_loader
                    )
                    enemies.append(enemy)
                    self.template.mark_occupied(x, y)
        
        print(f"Spawned {len(enemies)} enemies")
        return enemies
    
    def spawn_objects(self, asset_loader) -> List[Entity]:
        """Spawn environmental objects at designated template locations"""
        objects = []
        object_spawns = self.template.get_spawn_points('OBJECT_SPAWN')
        
        # Spawn trees and rocks at object spawn points
        for x, y in object_spawns:
            if self.template.is_position_available(x, y):
                # Determine object type by surrounding terrain
                terrain = self.template.get_terrain_type(x, y)
                
                # Check nearby terrain to decide object type
                nearby_water = False
                nearby_stone = False
                
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        check_terrain = self.template.get_terrain_type(x + dx, y + dy)
                        if check_terrain == 'WATER':
                            nearby_water = True
                        elif check_terrain == 'STONE':
                            nearby_stone = True
                
                # Choose object type
                if nearby_water or nearby_stone:
                    # Rocks near water or stone areas
                    obj = Entity(x, y, "Rock", entity_type="object", 
                               blocks_movement=True, asset_loader=asset_loader)
                else:
                    # Trees in forest areas
                    obj = Entity(x, y, "Tree", entity_type="object", 
                               blocks_movement=True, asset_loader=asset_loader)
                
                objects.append(obj)
                self.template.mark_occupied(x, y)
        
        print(f"Spawned {len(objects)} objects")
        return objects
    
    def spawn_chests(self, asset_loader) -> List[Chest]:
        """Spawn treasure chests at designated template locations"""
        chests = []
        chest_spawns = self.template.get_spawn_points('CHEST_SPAWN')
        
        # Chest types based on location danger level
        for x, y in chest_spawns:
            if self.template.is_position_available(x, y):
                # Determine chest type by distance from village center
                village_center = (100, 100)
                distance = ((x - village_center[0]) ** 2 + (y - village_center[1]) ** 2) ** 0.5
                
                if distance < 30:
                    chest_type = "wooden"  # Safe areas
                elif distance < 60:
                    chest_type = "iron"    # Medium danger
                else:
                    chest_type = "gold"    # High danger areas
                
                chest = Chest(x, y, chest_type, asset_loader)
                chests.append(chest)
                self.template.mark_occupied(x, y)
        
        print(f"Spawned {len(chests)} chests")
        return chests
    
    def generate_all_entities(self, asset_loader):
        """Generate all entities using template-based spawning"""
        print("Generating entities from template...")
        
        self.npcs = self.spawn_npcs(asset_loader)
        self.enemies = self.spawn_enemies(asset_loader)
        self.objects = self.spawn_objects(asset_loader)
        self.chests = self.spawn_chests(asset_loader)
        
        print(f"Template-based generation complete:")
        print(f"  NPCs: {len(self.npcs)}")
        print(f"  Enemies: {len(self.enemies)}")
        print(f"  Objects: {len(self.objects)}")
        print(f"  Chests: {len(self.chests)}")
    
    def validate_spawning(self) -> List[str]:
        """Validate that entities were spawned correctly"""
        issues = []
        
        # Check for overlapping entities
        all_positions = set()
        
        for entity_list in [self.npcs, self.enemies, self.objects, self.chests]:
            for entity in entity_list:
                pos = (int(entity.x), int(entity.y))
                if pos in all_positions:
                    issues.append(f"Overlapping entities at {pos}")
                all_positions.add(pos)
        
        # Check that NPCs are in accessible locations
        for npc in self.npcs:
            terrain = self.template.get_terrain_type(int(npc.x), int(npc.y))
            if terrain not in ['NPC_SPAWN', 'INTERIOR', 'DOOR']:
                issues.append(f"NPC {npc.name} at ({npc.x}, {npc.y}) in invalid terrain: {terrain}")
        
        return issues


def integrate_template_generation(level_instance, template_path: str = None):
    """
    Integrate template-based generation into existing Level class
    """
    if template_path is None:
        template_path = "/Users/mnovich/Development/claude-rpg/assets/maps/main_world.png"
    
    if not os.path.exists(template_path):
        print(f"Template not found: {template_path}")
        return False
    
    try:
        # Initialize entity lists first
        level_instance.npcs = []
        level_instance.enemies = []
        level_instance.objects = []
        level_instance.chests = []
        level_instance.items = []
        
        # Create template-based generator
        template_gen = TemplateBasedLevel(template_path)
        
        # Replace level's generation methods
        level_instance.template_generator = template_gen
        level_instance.width = template_gen.width
        level_instance.height = template_gen.height
        
        # Generate tiles from template
        level_instance.tiles = template_gen.generate_tiles()
        level_instance.walkable = template_gen.generate_walkable_grid(level_instance.tiles)
        
        # Generate entities from template
        template_gen.generate_all_entities(level_instance.asset_loader)
        
        # Copy entities to level
        level_instance.npcs = template_gen.npcs
        level_instance.enemies = template_gen.enemies
        level_instance.objects = template_gen.objects
        level_instance.chests = template_gen.chests
        
        # Validate generation
        issues = template_gen.validate_spawning()
        if issues:
            print("Template generation issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Template generation validation passed!")
        
        return True
        
    except Exception as e:
        print(f"Error integrating template generation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the template-based generation
    pygame.init()
    
    template_path = "/Users/mnovich/Development/claude-rpg/assets/maps/main_world.png"
    
    if os.path.exists(template_path):
        generator = TemplateBasedLevel(template_path)
        tiles = generator.generate_tiles()
        walkable = generator.generate_walkable_grid(tiles)
        
        print(f"Generated {len(tiles)}x{len(tiles[0])} tile grid")
        print(f"Walkable tiles: {sum(sum(row) for row in walkable)}/{len(tiles) * len(tiles[0])}")
        
        # Test entity generation (would need asset_loader for full test)
        print("Template-based generation test completed successfully!")
    else:
        print(f"Template file not found: {template_path}")
        print("Run map_template.py first to generate the template.")