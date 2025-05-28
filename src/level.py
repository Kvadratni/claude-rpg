"""
Level system for the RPG
"""

import pygame
import random
import math
from .isometric import IsometricRenderer, sort_by_depth
from .entity import Entity, NPC, Enemy, Item

class Level:
    """Game level class"""
    
    # Tile types
    TILE_GRASS = 0
    TILE_DIRT = 1
    TILE_STONE = 2
    TILE_WATER = 3
    TILE_WALL = 4
    TILE_DOOR = 5
    
    def __init__(self, level_name, player, asset_loader):
        self.name = level_name
        self.player = player
        self.asset_loader = asset_loader
        self.width = 120  # Much bigger map
        self.height = 120
        
        # Isometric renderer
        self.iso_renderer = IsometricRenderer(64, 32)
        self.tile_width = self.iso_renderer.tile_width
        self.tile_height = self.iso_renderer.tile_height
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        
        # Generate level
        self.tiles = self.generate_level()
        self.heightmap = self.generate_heightmap()
        
        # Generate pathfinding grid AFTER tiles are created
        self.walkable = self.generate_walkable_grid()
        
        # Entities
        self.npcs = []
        self.enemies = []
        self.items = []
        self.objects = []  # Static objects like trees, rocks, etc.
        
        # Spawn entities
        self.spawn_entities()
        
        # Create tile sprites
        self.create_tile_sprites()
    
    def generate_level(self):
        """Generate a well-designed level layout"""
        tiles = []
        
        # Initialize with grass
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(self.TILE_GRASS)
            tiles.append(row)
        
        # Create border walls
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    tiles[y][x] = self.TILE_WALL
        
        # Create a central town area with stone paths
        town_center_x, town_center_y = 60, 60
        
        # Main cross roads through the center
        for x in range(20, 100):
            tiles[town_center_y][x] = self.TILE_STONE
            tiles[town_center_y + 1][x] = self.TILE_STONE
        
        for y in range(20, 100):
            tiles[y][town_center_x] = self.TILE_STONE
            tiles[y][town_center_x + 1] = self.TILE_STONE
        
        # Create town buildings
        self.create_building(tiles, 25, 25, 15, 10)  # Top-left building
        self.create_building(tiles, 80, 25, 15, 10)  # Top-right building
        self.create_building(tiles, 25, 85, 15, 10)  # Bottom-left building
        self.create_building(tiles, 80, 85, 15, 10)  # Bottom-right building
        
        # Central marketplace
        for y in range(55, 66):
            for x in range(55, 66):
                tiles[y][x] = self.TILE_STONE
        
        # Create a lake in the northeast
        self.create_lake(tiles, 85, 35, 12)
        
        # Create a forest area in the southwest
        self.create_forest_clearing(tiles, 25, 75, 20)
        
        # Add dirt paths connecting areas
        self.create_dirt_path(tiles, 40, 30, 60, 30)  # Horizontal path
        self.create_dirt_path(tiles, 30, 40, 30, 80)  # Vertical path
        self.create_dirt_path(tiles, 70, 40, 70, 80)  # Another vertical path
        
        # Ensure player starting area is clear
        start_x, start_y = 60, 60
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if 0 <= start_x + dx < self.width and 0 <= start_y + dy < self.height:
                    if tiles[start_y + dy][start_x + dx] == self.TILE_WALL:
                        tiles[start_y + dy][start_x + dx] = self.TILE_STONE
        
        return tiles
    
    def create_building(self, tiles, start_x, start_y, width, height):
        """Create a building structure"""
        # Building walls
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if (x == start_x or x == start_x + width - 1 or 
                    y == start_y or y == start_y + height - 1):
                    tiles[y][x] = self.TILE_WALL
                else:
                    tiles[y][x] = self.TILE_STONE  # Interior floor
        
        # Add a door
        door_x = start_x + width // 2
        door_y = start_y + height - 1
        if 0 <= door_x < self.width and 0 <= door_y < self.height:
            tiles[door_y][door_x] = self.TILE_DOOR
    
    def create_lake(self, tiles, center_x, center_y, radius):
        """Create a circular lake"""
        for y in range(max(1, center_y - radius), min(self.height - 1, center_y + radius)):
            for x in range(max(1, center_x - radius), min(self.width - 1, center_x + radius)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance < radius - 2:
                    tiles[y][x] = self.TILE_WATER
                elif distance < radius:
                    tiles[y][x] = self.TILE_DIRT  # Shore
    
    def create_forest_clearing(self, tiles, center_x, center_y, size):
        """Create a forest clearing area"""
        for y in range(max(1, center_y - size//2), min(self.height - 1, center_y + size//2)):
            for x in range(max(1, center_x - size//2), min(self.width - 1, center_x + size//2)):
                if random.random() < 0.3:  # 30% chance for dirt patches
                    tiles[y][x] = self.TILE_DIRT
    
    def create_dirt_path(self, tiles, start_x, start_y, end_x, end_y):
        """Create a dirt path between two points"""
        # Simple straight line path
        if start_x == end_x:  # Vertical path
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                if 1 <= y < self.height - 1:
                    tiles[y][start_x] = self.TILE_DIRT
        elif start_y == end_y:  # Horizontal path
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                if 1 <= x < self.width - 1:
                    tiles[start_y][x] = self.TILE_DIRT
    
    def generate_heightmap(self):
        """Generate a heightmap for the level"""
        heightmap = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Default height
                height = 0
                
                # Walls are higher
                if self.tiles[y][x] == self.TILE_WALL:
                    height = 1
                # Water is lower
                elif self.tiles[y][x] == self.TILE_WATER:
                    height = -0.5
                # Add some random height variations
                elif random.random() < 0.1:
                    height = random.uniform(-0.1, 0.1)
                
                row.append(height)
            heightmap.append(row)
        
        # Don't mirror the heightmap 
        return heightmap
    
    def generate_walkable_grid(self):
        """Generate a grid of walkable tiles for pathfinding"""
        walkable = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Check if tile is walkable
                tile_type = self.tiles[y][x]
                if tile_type in [self.TILE_GRASS, self.TILE_DIRT, self.TILE_STONE, self.TILE_DOOR]:
                    row.append(True)
                else:
                    row.append(False)
            walkable.append(row)
        
        # Don't mirror the walkable grid
        return walkable
    
    def create_tile_sprites(self):
        """Create isometric tile sprites using loaded assets"""
        self.tile_sprites = {}
        
        # Try to use loaded images, fall back to generated sprites
        grass_image = self.asset_loader.get_image("grass_tile")
        if grass_image:
            # Rotate the tile 45 degrees for proper isometric alignment
            rotated_grass = pygame.transform.rotate(grass_image, 45)
            self.tile_sprites[self.TILE_GRASS] = pygame.transform.scale(rotated_grass, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_GRASS] = self.iso_renderer.create_diamond_tile((50, 150, 50))
        
        stone_image = self.asset_loader.get_image("stone_tile")
        if stone_image:
            rotated_stone = pygame.transform.rotate(stone_image, 45)
            self.tile_sprites[self.TILE_STONE] = pygame.transform.scale(rotated_stone, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_STONE] = self.iso_renderer.create_diamond_tile((150, 150, 150))
        
        water_image = self.asset_loader.get_image("water_tile")
        if water_image:
            rotated_water = pygame.transform.rotate(water_image, 45)
            self.tile_sprites[self.TILE_WATER] = pygame.transform.scale(rotated_water, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_WATER] = self.iso_renderer.create_diamond_tile((50, 100, 200))
        
        wall_image = self.asset_loader.get_image("wall_tile")
        if wall_image:
            # Don't rotate the wall tile - use it as-is
            self.tile_sprites[self.TILE_WALL] = pygame.transform.scale(wall_image, (self.tile_width, self.tile_height + 16))
        else:
            self.tile_sprites[self.TILE_WALL] = self.iso_renderer.create_cube_tile((200, 200, 200), (150, 150, 150), (100, 100, 100))
        
        dirt_image = self.asset_loader.get_image("dirt_tile")
        if dirt_image:
            rotated_dirt = pygame.transform.rotate(dirt_image, 45)
            self.tile_sprites[self.TILE_DIRT] = pygame.transform.scale(rotated_dirt, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_DIRT] = self.iso_renderer.create_diamond_tile((150, 100, 50))
        
        # Door (fallback)
        self.tile_sprites[self.TILE_DOOR] = self.iso_renderer.create_cube_tile((150, 100, 50), (120, 80, 40), (100, 60, 30))
    
    def spawn_entities(self):
        """Spawn entities in the level"""
        # Spawn enemies
        self.spawn_enemies()
        
        # Spawn NPCs
        self.spawn_npcs()
        
        # Spawn items
        self.spawn_items()
        
        # Spawn objects (trees, rocks, etc.)
        self.spawn_objects()
    
    def spawn_enemies(self):
        """Spawn enemies in the level"""
        # Spawn 10 enemies
        for _ in range(10):
            self.spawn_entity_at_valid_position(
                lambda x, y: Enemy(x, y, "Goblin", health=50, damage=10, experience=25, asset_loader=self.asset_loader)
            )
        
        # Spawn a boss enemy
        self.spawn_entity_at_valid_position(
            lambda x, y: Enemy(x, y, "Orc Chief", health=200, damage=20, experience=100, is_boss=True, asset_loader=self.asset_loader)
        )
    
    def spawn_npcs(self):
        """Spawn NPCs in the level"""
        # Spawn a shopkeeper
        self.spawn_entity_at_valid_position(
            lambda x, y: NPC(x, y, "Shopkeeper", dialog=["Welcome to my shop!", "What would you like to buy?"], asset_loader=self.asset_loader)
        )
        
        # Spawn a quest giver
        self.spawn_entity_at_valid_position(
            lambda x, y: NPC(x, y, "Village Elder", dialog=["Our village is in danger.", "Please defeat the Orc Chief!"], asset_loader=self.asset_loader)
        )
    
    def spawn_items(self):
        """Spawn items in the level"""
        # Spawn more health potions
        for _ in range(15):  # Increased from 5 to 15
            self.spawn_entity_at_valid_position(
                lambda x, y: Item(x, y, "Health Potion", item_type="consumable", effect={"health": 50}, asset_loader=self.asset_loader)
            )
        
        # Spawn more weapons
        for _ in range(5):  # Increased from 1 to 5
            weapon_names = ["Iron Sword", "Steel Axe", "Bronze Mace", "Silver Dagger", "War Hammer"]
            weapon_name = random.choice(weapon_names)
            damage_bonus = random.randint(10, 25)
            self.spawn_entity_at_valid_position(
                lambda x, y: Item(x, y, weapon_name, item_type="weapon", effect={"damage": damage_bonus}, asset_loader=self.asset_loader)
            )
        
        # Spawn more armor
        for _ in range(5):  # Increased from 1 to 5
            armor_names = ["Leather Armor", "Chain Mail", "Plate Armor", "Studded Leather", "Scale Mail"]
            armor_name = random.choice(armor_names)
            defense_bonus = random.randint(5, 15)
            self.spawn_entity_at_valid_position(
                lambda x, y: Item(x, y, armor_name, item_type="armor", effect={"defense": defense_bonus}, asset_loader=self.asset_loader)
            )
        
        # Add mana potions
        for _ in range(10):
            self.spawn_entity_at_valid_position(
                lambda x, y: Item(x, y, "Mana Potion", item_type="consumable", effect={"mana": 30}, asset_loader=self.asset_loader)
            )
    
    def spawn_objects(self):
        """Spawn static objects in the level"""
        # Spawn many more trees with proper terrain restrictions
        for _ in range(80):  # Increased from 20 to 80
            self.spawn_tree_at_valid_position()
        
        # Spawn rocks with proper sprites
        for _ in range(25):  # Increased from 15 to 25
            self.spawn_entity_at_valid_position(
                lambda x, y: Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            )
    
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
        
        # Check if tile is walkable
        if not self.walkable[y][x]:
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
    
    def check_collision(self, x, y, size=0.4):
        """Check collision with level geometry and entities"""
        # Convert to tile coordinates
        tile_x = int(x)
        tile_y = int(y)
        
        # Check if the position is within level bounds
        if x < 0.5 or x >= self.width - 0.5 or y < 0.5 or y >= self.height - 0.5:
            return True
        
        # Check the tile the entity is on
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            if not self.walkable[tile_y][tile_x]:
                return True
        
        # Check surrounding tiles for edge cases
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                check_x = tile_x + dx
                check_y = tile_y + dy
                
                # Check if tile is within bounds
                if 0 <= check_x < self.width and 0 <= check_y < self.height:
                    # Check if tile is not walkable
                    if not self.walkable[check_y][check_x]:
                        # Calculate distance to tile center
                        dist_x = abs(x - (check_x + 0.5))
                        dist_y = abs(y - (check_y + 0.5))
                        
                        # Check if entity overlaps with tile (more precise collision)
                        if dist_x < 0.4 + size and dist_y < 0.4 + size:
                            return True
        
        # Check collision with objects
        for obj in self.objects:
            if obj.blocks_movement:
                dist_x = abs(x - obj.x)
                dist_y = abs(y - obj.y)
                
                # Use smaller collision box for objects
                if dist_x < size + 0.3 and dist_y < size + 0.3:
                    return True
        
        return False
    
    def update_camera(self, screen_width, screen_height):
        """Update camera to follow player"""
        # Convert player position to isometric coordinates
        player_iso_x, player_iso_y = self.iso_renderer.cart_to_iso(self.player.x, self.player.y)
        
        # Center camera on player
        self.camera_x = player_iso_x - screen_width // 2
        self.camera_y = player_iso_y - screen_height // 2
    
    def handle_event(self, event):
        """Handle level events"""
        # Handle mouse clicks for interaction and movement
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos)
            elif event.button == 3:  # Right click
                self.handle_right_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                print("Zoom in (not implemented)")
            elif event.button == 5:  # Mouse wheel down
                print("Zoom out (not implemented)")
    
    def handle_click(self, pos):
        """Handle mouse click at position"""
        # Check if clicking on inventory button
        if hasattr(self, 'inventory_button_rect') and self.inventory_button_rect.collidepoint(pos):
            # Toggle inventory
            self.player.inventory.show = not self.player.inventory.show
            if self.player.game_log:
                if self.player.inventory.show:
                    self.player.game_log.add_message("Inventory opened", "system")
                else:
                    self.player.game_log.add_message("Inventory closed", "system")
            return
        
        # Convert screen position to world position
        world_x, world_y = self.iso_renderer.screen_to_world(pos[0], pos[1], self.camera_x, self.camera_y)
        
        # Let the player handle the click
        self.player.handle_mouse_click(world_x, world_y, self)
    
    def handle_right_click(self, pos):
        """Handle right mouse click for context actions"""
        # Convert screen position to world position
        world_x, world_y = self.iso_renderer.screen_to_world(pos[0], pos[1], self.camera_x, self.camera_y)
        
        # Check what was right-clicked
        clicked_entity = None
        
        # Check enemies for info
        for enemy in self.enemies:
            if abs(world_x - enemy.x) < 1.2 and abs(world_y - enemy.y) < 1.2:
                if self.player.game_log:
                    self.player.game_log.add_message(f"{enemy.name}: Health {enemy.health}/{enemy.max_health}, Damage {enemy.damage}", "system")
                clicked_entity = enemy
                break
        
        # Check NPCs for info
        if not clicked_entity:
            for npc in self.npcs:
                if abs(world_x - npc.x) < 1.2 and abs(world_y - npc.y) < 1.2:
                    if self.player.game_log:
                        self.player.game_log.add_message(f"{npc.name}: {npc.dialog[0] if npc.dialog else 'No dialog'}", "dialog")
                    clicked_entity = npc
                    break
        
        # Check items for info
        if not clicked_entity:
            for item in self.items:
                if abs(world_x - item.x) < 1.2 and abs(world_y - item.y) < 1.2:
                    effect_str = ", ".join([f"{k}: {v}" for k, v in item.effect.items()])
                    if self.player.game_log:
                        self.player.game_log.add_message(f"{item.name} ({item.item_type}): {effect_str}", "item")
                    clicked_entity = item
                    break
        
        if not clicked_entity:
            # Show tile info
            tile_x = int(world_x)
            tile_y = int(world_y)
            if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
                tile_names = {
                    self.TILE_GRASS: "Grass",
                    self.TILE_DIRT: "Dirt",
                    self.TILE_STONE: "Stone Path",
                    self.TILE_WATER: "Water",
                    self.TILE_WALL: "Wall",
                    self.TILE_DOOR: "Door"
                }
                tile_type = self.tiles[tile_y][tile_x]
                tile_name = tile_names.get(tile_type, "Unknown")
                walkable = "walkable" if self.walkable[tile_y][tile_x] else "blocked"
                if self.player.game_log:
                    self.player.game_log.add_message(f"Tile ({tile_x}, {tile_y}): {tile_name} ({walkable})", "system")
    
    def update(self):
        """Update level logic"""
        # Handle player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self)  # Pass level to handle_input
        
        # Update player
        self.player.update(self)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update(self, self.player)
            
            # Check if enemy is dead
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.player.gain_experience(enemy.experience)
                
                # Drop loot
                if random.random() < 0.3:  # 30% chance to drop item
                    item_type = random.choice(["consumable", "weapon", "armor"])
                    if item_type == "consumable":
                        item = Item(enemy.x, enemy.y, "Health Potion", item_type="consumable", effect={"health": 50}, asset_loader=self.asset_loader)
                    elif item_type == "weapon":
                        item = Item(enemy.x, enemy.y, "Weapon", item_type="weapon", effect={"damage": 5 + random.randint(0, 10)}, asset_loader=self.asset_loader)
                    else:
                        item = Item(enemy.x, enemy.y, "Armor", item_type="armor", effect={"defense": 5 + random.randint(0, 10)}, asset_loader=self.asset_loader)
                    self.items.append(item)
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(self)
        
        # Update items
        for item in self.items:
            item.update(self)
    
    def render(self, screen):
        """Render the level"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Update camera
        self.update_camera(screen_width, screen_height)
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Calculate visible tile range - much larger rendering area
        visible_width = (screen_width // self.tile_width) + 30  # Much larger area
        visible_height = (screen_height // (self.tile_height // 2)) + 30  # Much larger area
        
        # Calculate center tile
        center_x = int(self.player.x)
        center_y = int(self.player.y)
        
        # Calculate tile range - render much more area
        start_x = max(0, center_x - visible_width)  # Remove // 2 to get full range
        end_x = min(self.width, center_x + visible_width)
        start_y = max(0, center_y - visible_height)  # Remove // 2 to get full range
        end_y = min(self.height, center_y + visible_height)
        
        # Render tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                height = self.heightmap[y][x]
                
                # Get tile sprite
                sprite = self.tile_sprites[tile_type]
                
                # Calculate screen position
                screen_x, screen_y = self.iso_renderer.world_to_screen(x, y, self.camera_x, self.camera_y)
                
                # Adjust for height
                screen_y -= height * 16
                
                # Draw tile
                screen.blit(sprite, (screen_x - self.tile_width // 2, screen_y - self.tile_height // 2))
        
        # Collect all entities for depth sorting
        all_entities = []
        all_entities.append(self.player)
        all_entities.extend(self.enemies)
        all_entities.extend(self.npcs)
        all_entities.extend(self.items)
        all_entities.extend(self.objects)
        
        # Sort entities by depth
        sorted_entities = sort_by_depth(all_entities)
        
        # Render entities
        for entity in sorted_entities:
            entity.render(screen, self.iso_renderer, self.camera_x, self.camera_y)
        
        # Render UI
        self.render_ui(screen)
    
    def render_ui(self, screen):
        """Render enhanced game UI"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create UI panel at bottom
        ui_height = 150
        ui_panel = pygame.Surface((screen_width, ui_height))
        ui_panel.fill((40, 40, 40))  # Dark gray background
        
        # Draw border
        pygame.draw.rect(ui_panel, (100, 100, 100), (0, 0, screen_width, ui_height), 2)
        
        # Left side - Player stats
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        stats_text = [
            f"Level: {self.player.level}",
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Mana: {self.player.mana}/{self.player.max_mana}",
            f"Exp: {self.player.experience}/{self.player.experience_to_next}",
            f"Gold: {self.player.gold}"
        ]
        
        for i, text in enumerate(stats_text):
            surface = small_font.render(text, True, (255, 255, 255))
            ui_panel.blit(surface, (10, 10 + i * 22))
        
        # Center-left - Equipment display
        equipment_x = 200
        
        # Current weapon display
        weapon_rect = pygame.Rect(equipment_x, 10, 60, 60)
        pygame.draw.rect(ui_panel, (60, 60, 60), weapon_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), weapon_rect, 2)
        
        if self.player.equipped_weapon:
            # Draw weapon icon (simplified)
            pygame.draw.rect(ui_panel, (192, 192, 192), (equipment_x + 15, 20, 30, 40))
            weapon_text = font.render("Weapon:", True, (255, 255, 255))
            ui_panel.blit(weapon_text, (equipment_x, 75))
            weapon_name = small_font.render(self.player.equipped_weapon.name, True, (255, 255, 255))
            ui_panel.blit(weapon_name, (equipment_x, 95))
        else:
            no_weapon = small_font.render("No Weapon", True, (150, 150, 150))
            ui_panel.blit(no_weapon, (equipment_x + 5, 35))
        
        # Current armor display
        armor_x = equipment_x + 80
        armor_rect = pygame.Rect(armor_x, 10, 60, 60)
        pygame.draw.rect(ui_panel, (60, 60, 60), armor_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), armor_rect, 2)
        
        if self.player.equipped_armor:
            # Draw armor icon (simplified)
            pygame.draw.ellipse(ui_panel, (139, 69, 19), (armor_x + 15, 20, 30, 40))
            armor_text = font.render("Armor:", True, (255, 255, 255))
            ui_panel.blit(armor_text, (armor_x, 75))
            armor_name = small_font.render(self.player.equipped_armor.name, True, (255, 255, 255))
            ui_panel.blit(armor_name, (armor_x, 95))
        else:
            no_armor = small_font.render("No Armor", True, (150, 150, 150))
            ui_panel.blit(no_armor, (armor_x + 5, 35))
        
        # Inventory button
        inv_button_x = armor_x + 100
        inv_button = pygame.Rect(inv_button_x, 20, 100, 40)
        pygame.draw.rect(ui_panel, (80, 80, 80), inv_button)
        pygame.draw.rect(ui_panel, (120, 120, 120), inv_button, 2)
        
        inv_text = font.render("Inventory", True, (255, 255, 255))
        text_rect = inv_text.get_rect(center=inv_button.center)
        ui_panel.blit(inv_text, text_rect)
        
        # Store button rect for click detection (adjust for screen position)
        self.inventory_button_rect = pygame.Rect(inv_button_x, screen_height - ui_height + 20, 100, 40)
        
        # Right side - Game log (non-transparent)
        log_x = screen_width - 350
        log_width = 340
        log_height = ui_height - 20
        
        log_panel = pygame.Surface((log_width, log_height))
        log_panel.fill((30, 30, 30))  # Darker background for log
        pygame.draw.rect(log_panel, (80, 80, 80), (0, 0, log_width, log_height), 2)
        
        # Game log title
        log_title = font.render("Game Log:", True, (200, 200, 200))
        log_panel.blit(log_title, (5, 5))
        
        # Render recent messages
        if hasattr(self.player, 'game_log') and self.player.game_log:
            recent_messages = self.player.game_log.messages[-6:]  # Last 6 messages
            for i, message_data in enumerate(recent_messages):
                if isinstance(message_data, tuple) and len(message_data) >= 2:
                    message, msg_type = message_data[:2]
                else:
                    message = str(message_data)
                    msg_type = "system"
                color = self.player.game_log.get_message_color(msg_type)
                msg_surface = small_font.render(message[:45], True, color)  # Truncate long messages
                log_panel.blit(msg_surface, (5, 30 + i * 18))
        
        ui_panel.blit(log_panel, (log_x, 10))
        
        # Blit the entire UI panel to screen
        screen.blit(ui_panel, (0, screen_height - ui_height))
        
        # Instructions (moved to top)
        instructions = [
            "Left Click: Move/Interact/Attack  |  Right Click: Inspect  |  SPACE: Attack  |  ESC: Menu"
        ]
        
        for i, text in enumerate(instructions):
            surface = small_font.render(text, True, (200, 200, 200))
            screen.blit(surface, (10, 10 + i * 20))
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "name": self.name,
            "tiles": self.tiles,
            "heightmap": self.heightmap,
            "enemies": [enemy.get_save_data() for enemy in self.enemies],
            "npcs": [npc.get_save_data() for npc in self.npcs],
            "items": [item.get_save_data() for item in self.items],
            "objects": [obj.get_save_data() for obj in self.objects],
            "camera_x": self.camera_x,
            "camera_y": self.camera_y
        }
    
    @classmethod
    def from_save_data(cls, data, player, asset_loader):
        """Create level from save data"""
        level = cls(data["name"], player, asset_loader)
        level.tiles = data["tiles"]
        level.heightmap = data["heightmap"]
        level.camera_x = data["camera_x"]
        level.camera_y = data["camera_y"]
        
        # Recreate entities
        level.enemies = []
        for enemy_data in data["enemies"]:
            enemy = Enemy.from_save_data(enemy_data, asset_loader)
            level.enemies.append(enemy)
        
        level.npcs = []
        for npc_data in data["npcs"]:
            npc = NPC.from_save_data(npc_data, asset_loader)
            level.npcs.append(npc)
        
        level.items = []
        for item_data in data["items"]:
            item = Item.from_save_data(item_data, asset_loader)
            level.items.append(item)
        
        level.objects = []
        for obj_data in data["objects"]:
            obj = Entity.from_save_data(obj_data, asset_loader)
            level.objects.append(obj)
        
        return level