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
        """Generate a simple level"""
        tiles = []
        
        # Create a more interesting level layout for the bigger map
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Create borders
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    row.append(self.TILE_WALL)
                # Add some water features (scaled up for bigger map)
                elif 30 <= x <= 45 and 60 <= y <= 75:
                    # Large lake
                    if 33 <= x <= 42 and 63 <= y <= 72:
                        row.append(self.TILE_WATER)
                    else:
                        row.append(self.TILE_DIRT)
                # Add some stone paths (scaled up)
                elif (x == 60 or x == 61) and 15 <= y <= 105:
                    row.append(self.TILE_STONE)
                elif 15 <= x <= 105 and (y == 45 or y == 46):
                    row.append(self.TILE_STONE)
                # Add some buildings (scaled up)
                elif 75 <= x <= 90 and 15 <= y <= 30:
                    if x == 82 and y == 30:
                        row.append(self.TILE_DOOR)  # Door
                    else:
                        row.append(self.TILE_WALL)
                elif 15 <= x <= 30 and 75 <= y <= 90:
                    if x == 22 and y == 90:
                        row.append(self.TILE_DOOR)  # Door
                    else:
                        row.append(self.TILE_WALL)
                # Add more varied terrain for the larger map
                elif 90 <= x <= 110 and 90 <= y <= 110:
                    # Another building area
                    if x == 100 and y == 110:
                        row.append(self.TILE_DOOR)
                    else:
                        row.append(self.TILE_WALL)
                # Random features (less dense for bigger map)
                elif random.random() < 0.03:  # Reduced from 0.05
                    row.append(self.TILE_STONE)
                elif random.random() < 0.05:  # Reduced from 0.08
                    row.append(self.TILE_DIRT)
                else:
                    row.append(self.TILE_GRASS)
            tiles.append(row)
        
        # Ensure player starting area is clear (scaled up)
        start_x = self.width // 2
        start_y = self.height // 2
        
        for dy in range(-5, 6):  # Larger clear area
            for dx in range(-5, 6):
                if 0 <= start_x + dx < self.width and 0 <= start_y + dy < self.height:
                    tiles[start_y + dy][start_x + dx] = self.TILE_GRASS
        
        # Mirror the tiles horizontally to fix the mirroring issue
        # Actually, let's not mirror the data - let's fix it in the rendering instead
        return tiles
    
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
        
        # Dirt (fallback)
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
        # Spawn trees with proper sprites
        for _ in range(20):
            self.spawn_entity_at_valid_position(
                lambda x, y: Entity(x, y, "Tree", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            )
        
        # Spawn rocks with proper sprites
        for _ in range(15):
            self.spawn_entity_at_valid_position(
                lambda x, y: Entity(x, y, "Rock", entity_type="object", blocks_movement=True, asset_loader=self.asset_loader)
            )
    
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
        """Render game UI"""
        font = pygame.font.Font(None, 24)
        
        # Player stats
        stats_text = [
            f"Level: {self.player.level}",
            f"Health: {self.player.health}/{self.player.max_health}",
            f"Mana: {self.player.mana}/{self.player.max_mana}",
            f"Exp: {self.player.experience}/{self.player.experience_to_next}",
            f"Gold: {self.player.gold}",
            f"Position: ({int(self.player.x)}, {int(self.player.y)})"
        ]
        
        for i, text in enumerate(stats_text):
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (10, 10 + i * 25))
        
        # Equipped items
        if self.player.equipped_weapon:
            weapon_text = f"Weapon: {self.player.equipped_weapon.name}"
            surface = font.render(weapon_text, True, (255, 255, 255))
            screen.blit(surface, (screen.get_width() - 200, 10))
        
        if self.player.equipped_armor:
            armor_text = f"Armor: {self.player.equipped_armor.name}"
            surface = font.render(armor_text, True, (255, 255, 255))
            screen.blit(surface, (screen.get_width() - 200, 35))
        
        # Instructions
        instructions = [
            "Left Click: Move/Interact/Attack",
            "Right Click: Inspect/Info",
            "SPACE: Attack",
            "I: Inventory",
            "Cmd+Shift+F: Toggle Fullscreen",
            "ESC: Pause Menu"
        ]
        
        for i, text in enumerate(instructions):
            surface = pygame.font.Font(None, 20).render(text, True, (200, 200, 200))
            screen.blit(surface, (10, screen.get_height() - 110 + i * 20))
    
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