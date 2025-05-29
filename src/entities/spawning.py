"""
Spawning system for the Claude RPG game.

This module contains all methods related to enemy, NPC, and object spawning
that were extracted from level.py to improve code organization.
"""

import random
import math
try:
    from . import Enemy, NPC, Item, Entity, Chest
except ImportError:
    # Fallback for direct execution
    from . import Enemy, NPC, Item, Entity, Chest


class SpawningMixin:
    """
    Mixin class containing all spawning-related methods.
    This should be mixed into the Level class.
    """
    
    def spawn_entities(self):
        """Spawn entities in specific story locations"""
        # Spawn enemies in designated areas
        self.spawn_story_enemies()
        
        # Spawn NPCs in village
        self.spawn_story_npcs()
        
        # Remove random item spawning - items only come from shops and enemy drops
        # self.spawn_items()  # Commented out
        
        # Spawn environmental objects
        self.spawn_story_objects()
        
        # Spawn treasure chests
        self.spawn_chests()
    

    def spawn_story_enemies(self):
        """Spawn enemies in specific story locations across the expanded world"""
        # Dark Forest Goblins (North-West)
        dark_forest_positions = [
            (35, 35), (40, 38), (45, 40), (38, 45), (42, 42),
            (30, 40), (45, 35), (35, 45), (40, 30), (50, 45),
            (32, 50), (48, 32), (55, 38), (38, 55), (42, 48)
        ]
        
        for x, y in dark_forest_positions:
            if self.is_valid_story_position(x, y):
                goblin = Enemy(x, y, "Forest Goblin", health=45, damage=9, experience=30, asset_loader=self.asset_loader)
                self.enemies.append(goblin)
        
        # Enchanted Grove - Magical creatures
        grove_positions = [
            (85, 30), (90, 35), (95, 32), (88, 40), (92, 45),
            (100, 30), (105, 35), (110, 32), (95, 45), (102, 40)
        ]
        
        for x, y in grove_positions:
            if self.is_valid_story_position(x, y):
                sprite_enemy = Enemy(x, y, "Forest Sprite", health=35, damage=12, experience=40, asset_loader=self.asset_loader)
                self.enemies.append(sprite_enemy)
        
        # Ancient Woods - Undead guardians
        ancient_positions = [
            (145, 35), (150, 40), (155, 35), (148, 50), (152, 45),
            (160, 40), (165, 45), (170, 38), (155, 55), (162, 50),
            (175, 42), (168, 35), (158, 60), (172, 55), (165, 32)
        ]
        
        for x, y in ancient_positions:
            if self.is_valid_story_position(x, y):
                skeleton = Enemy(x, y, "Ancient Guardian", health=60, damage=15, experience=50, asset_loader=self.asset_loader)
                self.enemies.append(skeleton)
        
        # Orc Stronghold (Far North-East) - Multiple bosses and minions
        stronghold_positions = [
            (165, 25), (170, 30), (175, 25), (168, 35), (172, 32),
            (180, 28), (175, 35), (185, 30), (178, 40), (182, 35)
        ]
        
        for i, (x, y) in enumerate(stronghold_positions):
            if self.is_valid_story_position(x, y):
                if i == 0:  # First one is the boss
                    orc_chief = Enemy(x, y, "Orc Warlord", 
                                    health=400, damage=30, experience=300, 
                                    is_boss=True, asset_loader=self.asset_loader)
                    self.enemies.append(orc_chief)
                else:
                    orc = Enemy(x, y, "Orc Warrior", health=80, damage=18, experience=60, asset_loader=self.asset_loader)
                    self.enemies.append(orc)
        
        # Dragon's Peak - Dragon and minions
        dragon_positions = [
            (25, 25), (30, 28), (35, 25), (28, 32), (32, 30)
        ]
        
        for i, (x, y) in enumerate(dragon_positions):
            if self.is_valid_story_position(x, y):
                if i == 0:  # Dragon boss
                    dragon = Enemy(x, y, "Ancient Dragon", 
                                 health=800, damage=50, experience=500, 
                                 is_boss=True, asset_loader=self.asset_loader)
                    self.enemies.append(dragon)
                else:
                    drake = Enemy(x, y, "Fire Drake", health=120, damage=25, experience=80, asset_loader=self.asset_loader)
                    self.enemies.append(drake)
        
        # Crystal Caves - Crystal elementals
        crystal_positions = [
            (175, 85), (180, 90), (185, 85), (178, 95), (182, 100),
            (175, 105), (180, 110), (185, 105), (188, 95), (192, 88)
        ]
        
        for x, y in crystal_positions:
            if self.is_valid_story_position(x, y):
                elemental = Enemy(x, y, "Crystal Elemental", health=70, damage=20, experience=65, asset_loader=self.asset_loader)
                self.enemies.append(elemental)
        
        # Desert enemies
        desert_positions = [
            (25, 150), (35, 155), (45, 160), (30, 165), (40, 170),
            (50, 155), (55, 165), (60, 150), (65, 160), (70, 155)
        ]
        
        for x, y in desert_positions:
            if self.is_valid_story_position(x, y):
                scorpion = Enemy(x, y, "Giant Scorpion", health=55, damage=16, experience=45, asset_loader=self.asset_loader)
                self.enemies.append(scorpion)
        
        # Swamp enemies
        swamp_positions = [
            (25, 90), (30, 95), (35, 100), (40, 105), (45, 110),
            (25, 115), (30, 120), (35, 125), (40, 115), (45, 120)
        ]
        
        for x, y in swamp_positions:
            if self.is_valid_story_position(x, y):
                troll = Enemy(x, y, "Swamp Troll", health=90, damage=22, experience=70, asset_loader=self.asset_loader)
                self.enemies.append(troll)
        
        # Village area patrol enemies (easier for new players)
        village_patrol_positions = [
            (70, 70), (130, 70), (70, 130), (130, 130),
            (60, 100), (140, 100), (100, 60), (100, 140)
        ]
        
        for x, y in village_patrol_positions:
            if self.is_valid_story_position(x, y):
                bandit = Enemy(x, y, "Bandit Scout", health=35, damage=8, experience=20, asset_loader=self.asset_loader)
                self.enemies.append(bandit)
    

    def spawn_story_npcs(self):
        """Spawn NPCs across the expanded world"""
        # MAIN VILLAGE NPCs
        # Shopkeeper in the large store
        shopkeeper_x, shopkeeper_y = 77, 85  # Inside large shop building
        shopkeeper = NPC(shopkeeper_x, shopkeeper_y, "Master Merchant", 
                        dialog=[
                            "Welcome to the finest shop in all the lands!",
                            "I have goods from every corner of the realm!",
                            "The roads are dangerous, but profitable for traders.",
                            "I hear the ancient ruins hold great treasures..."
                        ], 
                        asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(shopkeeper)
        
        # Village Elder in his house
        elder_x, elder_y = 122, 85  # Inside elder's house
        elder = NPC(elder_x, elder_y, "Village Elder", 
                   dialog=[
                       "Welcome, brave adventurer!",
                       "Our peaceful village sits at the crossroads of many realms.",
                       "To the north lie ancient forests filled with danger.",
                       "The mountains hold both treasure and terror.",
                       "The desert sands conceal forgotten secrets.",
                       "May your journey bring you wisdom and fortune!"
                   ], 
                   asset_loader=self.asset_loader)
        self.npcs.append(elder)
        
        # Blacksmith
        blacksmith_x, blacksmith_y = 76, 109  # Inside blacksmith
        blacksmith = NPC(blacksmith_x, blacksmith_y, "Master Smith", 
                        dialog=[
                            "The forge burns hot today!",
                            "I craft the finest weapons and armor.",
                            "Bring me rare metals and I'll make you legendary gear!",
                            "The crystal caves have materials I need..."
                        ], 
                        asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(blacksmith)
        
        # Innkeeper
        innkeeper_x, innkeeper_y = 121, 109  # Inside inn
        innkeeper = NPC(innkeeper_x, innkeeper_y, "Innkeeper", 
                       dialog=[
                           "Welcome to the Crossroads Inn!",
                           "Travelers from all lands rest here.",
                           "I've heard tales of dragons in the northern peaks.",
                           "The swamp folk speak of ancient magic.",
                           "Rest well, the roads are perilous."
                       ], 
                       asset_loader=self.asset_loader)
        self.npcs.append(innkeeper)
        
        # Temple Priest
        priest_x, priest_y = 100, 70  # Inside temple
        priest = NPC(priest_x, priest_y, "High Priest", 
                    dialog=[
                        "The light guides all who seek it.",
                        "Ancient evils stir in the forgotten places.",
                        "The stone circles hold power beyond understanding.",
                        "May the divine protect you on your journey."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(priest)
        
        # Village Guard Captain
        guard_x, guard_y = 65, 97  # In guard house
        guard = NPC(guard_x, guard_y, "Guard Captain", 
                   dialog=[
                       "I keep watch over our village.",
                       "Bandits have been spotted on the roads.",
                       "The northern forests grow more dangerous each day.",
                       "If you're heading out, be well armed!",
                       "Report any suspicious activity to me."
                   ], 
                   asset_loader=self.asset_loader)
        self.npcs.append(guard)
        
        # MINING TOWN NPCs
        # Mine Foreman
        foreman_x, foreman_y = 155, 57  # In mine office
        foreman = NPC(foreman_x, foreman_y, "Mine Foreman", 
                     dialog=[
                         "The mines run deep into the mountain.",
                         "We've found strange crystals in the lower tunnels.",
                         "Some miners speak of hearing voices in the dark.",
                         "The work is hard but the pay is good."
                     ], 
                     asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(foreman)
        
        # FISHING VILLAGE NPCs
        # Harbor Master
        harbor_x, harbor_y = 125, 167  # In fish market
        harbor = NPC(harbor_x, harbor_y, "Harbor Master", 
                    dialog=[
                        "The great lake provides for our village.",
                        "Strange lights have been seen beneath the waters.",
                        "The fish have been acting oddly lately.",
                        "Ancient ruins lie submerged in the deep parts."
                    ], 
                    asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(harbor)
        
        # DESERT OUTPOST NPCs
        # Caravan Leader
        caravan_x, caravan_y = 32, 162  # In trading post
        caravan = NPC(caravan_x, caravan_y, "Caravan Master", 
                     dialog=[
                         "The desert trade routes are treacherous.",
                         "Sandstorms hide ancient ruins from view.",
                         "The oasis is sacred to the desert dwellers.",
                         "Scorpions grow large in these parts."
                     ], 
                     asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(caravan)
        
        # FOREST HAMLET NPCs
        # Ranger
        ranger_x, ranger_y = 97, 32  # In ranger station
        ranger = NPC(ranger_x, ranger_y, "Forest Ranger", 
                    dialog=[
                        "The ancient woods hold many secrets.",
                        "Spirits of the old world still walk these paths.",
                        "The stone circles are gathering points for magic.",
                        "Beware the guardians of the ruins."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(ranger)
        
        # Herbalist
        herbalist_x, herbalist_y = 107, 32  # In herbalist hut
        herbalist = NPC(herbalist_x, herbalist_y, "Master Herbalist", 
                       dialog=[
                           "The forest provides all manner of healing herbs.",
                           "Magical plants grow near the stone circles.",
                           "The swamp has rare ingredients, but it's dangerous.",
                           "I can brew potions from the right materials."
                       ], 
                       asset_loader=self.asset_loader, has_shop=True)
        self.npcs.append(herbalist)
        
        # MYSTERIOUS WANDERERS (scattered around the world)
        # Mysterious Wizard near stone circle
        wizard_x, wizard_y = 70, 52
        wizard = NPC(wizard_x, wizard_y, "Mysterious Wizard", 
                    dialog=[
                        "The ancient magics still flow through these stones...",
                        "Power calls to power, young one.",
                        "The circles are older than any kingdom.",
                        "Seek the truth in the forgotten places."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(wizard)
        
        # Hermit near ruins
        hermit_x, hermit_y = 52, 62
        hermit = NPC(hermit_x, hermit_y, "Old Hermit", 
                    dialog=[
                        "I've lived here since before the village grew large.",
                        "These ruins... they're older than you think.",
                        "Sometimes I hear whispers from the stones.",
                        "The past has a way of returning."
                    ], 
                    asset_loader=self.asset_loader)
        self.npcs.append(hermit)
    

    def spawn_story_objects(self):
        """Spawn environmental objects across the expanded world"""
        # Dense forests in multiple regions
        # Dark Forest (North-West)
        dark_forest_trees = []
        for y in range(25, 65):
            for x in range(25, 65):
                if random.random() < 0.4 and self.is_valid_tree_terrain(x, y):
                    # Avoid clearings and paths
                    if not (35 <= x <= 45 and 35 <= y <= 45):  # Main clearing
                        dark_forest_trees.append((x, y))
        
        for x, y in dark_forest_trees:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Enchanted Grove (North-Center)
        grove_trees = []
        for y in range(20, 50):
            for x in range(75, 115):
                if random.random() < 0.3 and self.is_valid_tree_terrain(x, y):
                    grove_trees.append((x, y))
        
        for x, y in grove_trees:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Ancient Woods (North-East)
        ancient_trees = []
        for y in range(25, 65):
            for x in range(135, 185):
                if random.random() < 0.5 and self.is_valid_tree_terrain(x, y):
                    ancient_trees.append((x, y))
        
        for x, y in ancient_trees:
            tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            self.objects.append(tree)
        
        # Scattered trees around settlements
        settlement_tree_positions = [
            # Around main village
            (55, 75), (145, 75), (55, 125), (145, 125),
            (75, 55), (125, 55), (75, 145), (125, 145),
            # Around other settlements
            (140, 45), (180, 75), (45, 125), (75, 175),
            (25, 45), (175, 125), (125, 25), (175, 175)
        ]
        
        for x, y in settlement_tree_positions:
            if self.is_valid_tree_terrain(x, y) and self.is_valid_story_position(x, y):
                tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(tree)
        
        # Rocks in mountain regions
        # Dragon's Peak rocks
        dragon_peak_rocks = [
            (20, 20), (25, 18), (30, 22), (35, 19), (40, 25),
            (18, 30), (22, 35), (28, 38), (35, 40), (42, 35)
        ]
        
        for x, y in dragon_peak_rocks:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Orc Stronghold rocks
        stronghold_rocks = [
            (162, 18), (168, 16), (175, 20), (185, 25), (192, 28),
            (160, 25), (170, 30), (180, 35), (190, 32), (185, 18)
        ]
        
        for x, y in stronghold_rocks:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Crystal Caves rocks
        crystal_rocks = [
            (172, 82), (178, 88), (185, 92), (192, 85), (188, 95),
            (175, 100), (182, 105), (190, 110), (185, 115), (178, 118)
        ]
        
        for x, y in crystal_rocks:
            if self.is_valid_story_position(x, y):
                rock = Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(rock)
        
        # Decorative rocks around all lakes
        lake_positions = [(150, 150), (40, 140), (60, 155), (100, 40)]
        for lake_x, lake_y in lake_positions:
            for i in range(8):  # 8 rocks around each lake
                angle = i * 45  # Every 45 degrees
                distance = random.randint(25, 35)
                rock_x = lake_x + int(distance * math.cos(math.radians(angle)))
                rock_y = lake_y + int(distance * math.sin(math.radians(angle)))
                
                if self.is_valid_story_position(rock_x, rock_y):
                    rock = Entity(rock_x, rock_y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                    self.objects.append(rock)
    

    def spawn_chests(self):
        """Spawn treasure chests across the expanded world"""
        # Wooden chests - common, scattered in safe-ish areas
        wooden_chest_positions = [
            # Near main village
            (75, 65), (125, 65), (75, 135), (125, 135),
            # Near settlements
            (140, 50), (110, 45), (45, 175), (175, 175),
            # In forests (clearings)
            (45, 45), (95, 35), (155, 45),
            # Near ruins
            (55, 65), (165, 125), (30, 175)
        ]
        
        for x, y in wooden_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "wooden", self.asset_loader)
                self.chests.append(chest)
        
        # Iron chests - better loot, in more dangerous areas
        iron_chest_positions = [
            # Deep in forests
            (35, 55), (105, 25), (165, 55),
            # Mountain areas
            (25, 35), (175, 35), (185, 95),
            # Desert and swamp edges
            (55, 145), (35, 105),
            # Near lakes
            (125, 175), (65, 145), (115, 45)
        ]
        
        for x, y in iron_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "iron", self.asset_loader)
                self.chests.append(chest)
        
        # Gold chests - high-value loot, hidden/dangerous locations
        gold_chest_positions = [
            # Boss areas
            (175, 25),  # Near Orc Stronghold
            (30, 25),   # Near Dragon's Peak
            (185, 85),  # In Crystal Caves
            # Deep wilderness
            (45, 165),  # Deep desert
            (35, 115),  # Deep swamp
            # Ancient ruins
            (165, 120), (25, 170)
        ]
        
        for x, y in gold_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "gold", self.asset_loader)
                self.chests.append(chest)
        
        # Magical chests - rare, powerful items in special locations
        magical_chest_positions = [
            # Stone circles
            (70, 50), (130, 130), (180, 40),
            # Hidden corners
            (15, 15), (185, 185), (15, 185), (185, 15),
            # Boss lairs (after defeating bosses)
            (25, 25),   # Dragon's treasure
            (175, 25),  # Orc warlord's hoard
        ]
        
        for x, y in magical_chest_positions:
            if self.is_valid_story_position(x, y):
                chest = Chest(x, y, "magical", self.asset_loader)
                self.chests.append(chest)
    

    def is_valid_story_position(self, x, y):
        """Check if a position is valid for story entity placement"""
        # Check if position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if tile is walkable (using numeric walkable grid)
        if self.walkable[y][x] <= 0:
            return False
        
        # Don't place entities too close to player starting position
        start_x, start_y = 100, 102  # Updated to match new village center
        if abs(x - start_x) < 3 and abs(y - start_y) < 3:
            return False
        
        return True
    

    def spawn_tree_at_valid_position(self):
        """Spawn a tree only on grass or dirt tiles"""
        attempts = 0
        max_attempts = 200
        
        while attempts < max_attempts:
            x = random.randint(5, self.width - 6)
            y = random.randint(5, self.height - 6)
            
            # Check if position is valid and on correct terrain
            if self.is_valid_position(x, y) and self.is_valid_tree_terrain(x, y):
                tree = Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
                self.objects.append(tree)
                return tree
            
            attempts += 1
        
        return None
    

    def is_valid_tree_terrain(self, x, y):
        """Check if a tree can be placed on this terrain type"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        tile_type = self.tiles[y][x]
        # Trees can only spawn on grass or dirt
        return tile_type in [self.TILE_GRASS, self.TILE_DIRT]
    

    def spawn_entity_at_valid_position(self, entity_creator):
        """Spawn an entity at a valid position"""
        attempts = 0
        max_attempts = 200  # Increased attempts for larger map
        
        while attempts < max_attempts:
            x = random.randint(5, self.width - 6)  # Stay away from edges
            y = random.randint(5, self.height - 6)
            
            # Check if position is valid
            if self.is_valid_position(x, y):
                entity = entity_creator(x, y)
                
                # Add entity to appropriate list
                if isinstance(entity, Enemy):
                    self.enemies.append(entity)
                elif isinstance(entity, NPC):
                    self.npcs.append(entity)
                elif isinstance(entity, Item):
                    self.items.append(entity)
                else:
                    self.objects.append(entity)
                
                return entity
            
            attempts += 1
        
        # If we couldn't find a valid position, try a fallback position
        print(f"Warning: Could not find valid position after {max_attempts} attempts")
        return None
    

    def is_valid_position(self, x, y):
        """Check if a position is valid for entity placement"""
        # Check if position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        
        # Check if tile is walkable (using numeric walkable grid)
        if self.walkable[y][x] <= 0:
            return False
        
        # Check if position is too close to player
        player_x, player_y = int(self.player.x), int(self.player.y)
        if abs(x - player_x) < 5 and abs(y - player_y) < 5:
            return False
        
        # Check if position is too close to other entities
        for entity_list in [self.enemies, self.npcs, self.objects, self.items]:
            for entity in entity_list:
                if abs(x - entity.x) < 2 and abs(y - entity.y) < 2:
                    return False
        
        return True
    

