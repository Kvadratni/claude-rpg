"""
Entity system for the RPG
"""

import pygame
import math
import random

class Entity:
    """Base entity class"""
    
    def __init__(self, x, y, name, entity_type="entity", blocks_movement=False, asset_loader=None):
        self.x = x
        self.y = y
        self.name = name
        self.entity_type = entity_type
        self.blocks_movement = blocks_movement
        self.asset_loader = asset_loader
        self.sprite = None
        self.size = 0.4
        
        # Create basic sprite
        self.create_sprite()
    
    def create_sprite(self):
        """Create a basic sprite"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded assets first
        if self.asset_loader and self.entity_type == "object":
            if "Tree" in self.name:
                tree_image = self.asset_loader.get_image("tree")
                if tree_image:
                    self.sprite = pygame.transform.scale(tree_image, (size, size))
                    return
            elif "Rock" in self.name:
                rock_image = self.asset_loader.get_image("rock")
                if rock_image:
                    self.sprite = pygame.transform.scale(rock_image, (size, size))
                    return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Default color based on entity type
        if self.entity_type == "object":
            if "Tree" in self.name:
                color = (34, 139, 34)  # Forest green
            elif "Rock" in self.name:
                color = (128, 128, 128)  # Gray
            else:
                color = (139, 69, 19)  # Brown
        else:
            color = (255, 255, 255)  # White
        
        # Draw a simple shape
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, color, center, size // 3)
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Thicker border
    
    def update(self, level):
        """Update entity logic"""
        pass
    
    def render(self, screen, iso_renderer, camera_x, camera_y):
        """Render the entity with proper depth and occlusion"""
        if self.sprite:
            screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
            
            # Adjust rendering position based on entity type for proper layering
            if self.entity_type == "object" and ("Tree" in self.name or "Wall" in self.name):
                # Trees and walls render taller and should occlude other entities
                sprite_rect = self.sprite.get_rect()
                sprite_rect.center = (screen_x, screen_y - 32)  # Render higher for occlusion
            else:
                # Regular entities
                sprite_rect = self.sprite.get_rect()
                sprite_rect.center = (screen_x, screen_y - 16)
            
            screen.blit(self.sprite, sprite_rect)
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "x": self.x,
            "y": self.y,
            "name": self.name,
            "entity_type": self.entity_type,
            "blocks_movement": self.blocks_movement
        }
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create entity from save data"""
        entity = cls(data["x"], data["y"], data["name"], data["entity_type"], data["blocks_movement"], asset_loader)
        return entity


class NPC(Entity):
    """Non-player character"""
    
    def __init__(self, x, y, name, dialog=None, shop_items=None, asset_loader=None, has_shop=False):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.shop_items = shop_items or []
        self.dialog_index = 0
        self.asset_loader = asset_loader
        self.has_shop = has_shop
        self.shop = None
        
        # Create shop if this NPC is a shopkeeper
        if self.has_shop:
            from .shop import Shop
            shop_name = f"{self.name}'s Shop"
            self.shop = Shop(shop_name, asset_loader)
        
        # Create NPC sprite
        self.create_npc_sprite()
    
    def create_npc_sprite(self):
        """Create NPC sprite"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            if "Shopkeeper" in self.name:
                npc_image = self.asset_loader.get_image("npc_shopkeeper")
                if npc_image:
                    self.sprite = pygame.transform.scale(npc_image, (size, size))
                    return
            elif "Elder" in self.name:
                elder_image = self.asset_loader.get_image("elder_npc")
                if elder_image:
                    self.sprite = pygame.transform.scale(elder_image, (size, size))
                    return
            elif "Guard" in self.name:
                guard_image = self.asset_loader.get_image("village_guard_sprite")
                if guard_image:
                    self.sprite = pygame.transform.scale(guard_image, (size, size))
                    return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different NPCs
        if "Shopkeeper" in self.name:
            color = (255, 215, 0)  # Gold
        elif "Elder" in self.name:
            color = (128, 0, 128)  # Purple
        elif "Guard" in self.name:
            color = (70, 130, 180)  # Steel blue
        else:
            color = (0, 191, 255)  # Deep sky blue
        
        # Draw NPC
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, color, center, size // 3)
        pygame.draw.circle(self.sprite, (255, 255, 255), center, size // 4)
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Thicker border
        
        # Add a hat or distinguishing feature
        if "Shopkeeper" in self.name:
            pygame.draw.rect(self.sprite, (139, 69, 19), (size//2 - 12, 3, 24, 12))  # Larger hat
        elif "Elder" in self.name:
            pygame.draw.circle(self.sprite, (255, 255, 255), (size//2, 12), 9)  # Larger beard
        elif "Guard" in self.name:
            # Draw a simple helmet/armor
            pygame.draw.rect(self.sprite, (105, 105, 105), (size//2 - 10, 5, 20, 8))  # Helmet
            pygame.draw.rect(self.sprite, (169, 169, 169), (size//2 - 8, 8, 16, 4))   # Helmet detail
    
    def interact(self, player):
        """Interact with the NPC"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play dialog sound
        if audio:
            if "Elder" in self.name:
                audio.play_magic_sound("turn_page")  # Use page turn for elder wisdom
            else:
                audio.play_ui_sound("button_click")  # Generic NPC talk sound
        
        # Handle shop interaction
        if self.has_shop and self.shop:
            self.shop.open_shop()
            if player.game_log:
                player.game_log.add_message(f"{self.name}: Welcome to my shop!", "dialog")
            
            # Update quest progress for talking to shopkeeper
            if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                player.game.quest_manager.update_quest_progress("talk", self.name)
        else:
            # Open dialogue window instead of just logging messages
            if self.dialog:
                from .dialogue import DialogueWindow
                
                # Create dialogue window with all dialogue lines
                dialogue_window = DialogueWindow(self.name, self.dialog, self.asset_loader)
                
                # Store dialogue window in player or level for rendering
                if hasattr(player, 'current_dialogue'):
                    player.current_dialogue = dialogue_window
                
                # Quest giving logic for Village Elder
                if "Elder" in self.name and hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                    quest_manager = player.game.quest_manager
                    
                    # Check if we should offer the main quest
                    if "main_story" not in quest_manager.active_quests and "main_story" not in quest_manager.completed_quests:
                        # Check if tutorial is completed
                        if "tutorial" in quest_manager.completed_quests:
                            quest_manager.start_quest("main_story")
                            if player.game_log:
                                player.game_log.add_message("New Quest: The Orc Threat", "quest")
                
                # Update quest progress for talking to NPCs
                if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
                    player.game.quest_manager.update_quest_progress("talk", self.name)
            
            # Handle shop (legacy)
            if self.shop_items:
                if player.game_log:
                    player.game_log.add_message(f"{self.name} has items for sale!", "dialog")
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "dialog": self.dialog,
            "shop_items": self.shop_items,
            "dialog_index": self.dialog_index,
            "has_shop": self.has_shop
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create NPC from save data"""
        npc = cls(data["x"], data["y"], data["name"], data["dialog"], data["shop_items"], 
                 asset_loader, data.get("has_shop", False))
        npc.dialog_index = data["dialog_index"]
        return npc


class Enemy(Entity):
    """Enemy entity"""
    
    def __init__(self, x, y, name, health=50, damage=10, experience=25, is_boss=False, asset_loader=None):
        super().__init__(x, y, name, "enemy")
        self.health = health
        self.max_health = health
        self.damage = damage
        self.experience = experience
        self.is_boss = is_boss
        self.asset_loader = asset_loader
        
        # AI properties
        self.speed = 0.02 if not is_boss else 0.015  # Much slower speeds
        self.detection_range = 6 if not is_boss else 8
        self.attack_range = 1.2
        self.attack_cooldown = 0
        self.max_attack_cooldown = 60 if not is_boss else 40
        
        # State
        self.state = "idle"  # idle, chasing, attacking, fleeing
        self.target = None
        self.path = []
        
        # Create enemy sprite
        self.create_enemy_sprite()
    
    def create_enemy_sprite(self):
        """Create enemy sprite"""
        size = 60 if self.is_boss else 48  # Increased sizes - boss 60, regular 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            if self.is_boss and "Orc" in self.name:
                orc_image = self.asset_loader.get_image("orc_boss_sprite")
                if orc_image:
                    self.sprite = pygame.transform.scale(orc_image, (size, size))
                    return
            elif "Goblin" in self.name:
                goblin_image = self.asset_loader.get_image("goblin_sprite")
                if goblin_image:
                    self.sprite = pygame.transform.scale(goblin_image, (size, size))
                    return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different enemies
        if self.is_boss:
            color = (139, 0, 0)  # Dark red
            eye_color = (255, 0, 0)  # Red eyes
        elif "Goblin" in self.name:
            color = (0, 100, 0)  # Dark green
            eye_color = (255, 255, 0)  # Yellow eyes
        else:
            color = (139, 69, 19)  # Brown
            eye_color = (255, 0, 0)  # Red eyes
        
        # Draw enemy body
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, color, center, size // 3)
        
        # Draw eyes
        eye_size = 5 if not self.is_boss else 6  # Larger eyes
        pygame.draw.circle(self.sprite, eye_color, (center[0] - 9, center[1] - 6), eye_size)
        pygame.draw.circle(self.sprite, eye_color, (center[0] + 9, center[1] - 6), eye_size)
        
        # Draw border
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Thicker border
        
        # Boss gets a crown
        if self.is_boss:
            crown_points = [
                (center[0] - 15, center[1] - size//3),
                (center[0] - 8, center[1] - size//3 - 12),
                (center[0], center[1] - size//3 - 18),
                (center[0] + 8, center[1] - size//3 - 12),
                (center[0] + 15, center[1] - size//3)
            ]
            pygame.draw.polygon(self.sprite, (255, 215, 0), crown_points)
    
    def update(self, level, player):
        """Update enemy AI"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # AI state machine
        if distance < self.detection_range:
            # Play detection sound only when first seeing the player
            if self.state == "idle":
                # Get audio manager
                audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
                if audio:
                    if "Goblin" in self.name:
                        audio.play_creature_sound("goblin")
                    elif self.is_boss and "Orc" in self.name:
                        audio.play_creature_sound("orc_boss", "voice")
                    elif "Orc" in self.name:
                        audio.play_creature_sound("orc", "voice")
            
            if distance <= self.attack_range:
                self.state = "attacking"
                if self.attack_cooldown <= 0:
                    self.attack_player(player)
                    self.attack_cooldown = self.max_attack_cooldown
            else:
                self.state = "chasing"
                # Move towards player but stop at a reasonable distance
                if distance > self.attack_range + 0.3:  # Stop a bit further than attack range
                    move_x = (dx / distance) * self.speed
                    move_y = (dy / distance) * self.speed
                    
                    # Check collision before moving
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    # Check collision with level and avoid overlapping with player
                    if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                        # Also check if we're not getting too close to player
                        new_distance = math.sqrt((new_x - player.x)**2 + (new_y - player.y)**2)
                        if new_distance >= self.attack_range:
                            self.x = new_x
                            self.y = new_y
        else:
            self.state = "idle"
            # Random movement when idle
            if random.random() < 0.01:  # 1% chance per frame
                move_x = random.uniform(-0.2, 0.2)
                move_y = random.uniform(-0.2, 0.2)
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                    self.x = new_x
                    self.y = new_y
    
    def attack_player(self, player):
        """Attack the player"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play attack sound - different sounds for different enemies
        if audio:
            if self.is_boss and "Orc" in self.name:
                audio.play_creature_sound("orc_boss", "attack")
            elif "Orc" in self.name:
                audio.play_creature_sound("orc", "attack")
            elif "Goblin" in self.name:
                audio.play_combat_sound("weapon_hit")  # Generic attack sound for goblins
            else:
                audio.play_combat_sound("weapon_hit")  # Generic attack sound
        
        damage_dealt = self.damage + random.randint(-5, 5)  # Random damage variation
        if player.take_damage(damage_dealt):
            print(f"{self.name} defeated the player!")
        else:
            print(f"{self.name} attacks for {damage_dealt} damage!")
    
    def take_damage(self, damage):
        """Take damage"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        actual_damage = max(1, damage - random.randint(0, 3))  # Random defense
        self.health -= actual_damage
        
        # Play hurt sound - different sounds for different enemies
        if audio:
            if self.is_boss and "Orc" in self.name:
                audio.play_creature_sound("orc_boss", "hurt")
            elif "Orc" in self.name:
                audio.play_creature_sound("orc", "hurt")
            elif "Goblin" in self.name:
                # Use blade slice for goblin hurt sound
                audio.play_combat_sound("blade_slice")
            else:
                # Use a combat sound for generic hurt
                audio.play_combat_sound("blade_slice")
        
        print(f"{self.name} takes {actual_damage} damage! ({self.health}/{self.max_health})")
        
        # Play death sound if enemy dies
        if self.health <= 0 and audio:
            audio.play_ui_sound("defeat")  # Use defeat sound for enemy death
        
        return self.health <= 0
    
    def render(self, screen, iso_renderer, camera_x, camera_y):
        """Render the enemy"""
        super().render(screen, iso_renderer, camera_x, camera_y)
        
        # Render health bar
        screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
        self.render_health_bar(screen, screen_x, screen_y - 30)
    
    def render_health_bar(self, screen, x, y):
        """Render enemy health bar"""
        bar_width = 30 if not self.is_boss else 40
        bar_height = 4
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (x - bar_width//2, y, bar_width, bar_height))
        
        # Health
        health_ratio = self.health / self.max_health
        health_width = int(health_ratio * bar_width)
        health_color = (255, 0, 0) if health_ratio < 0.3 else (255, 255, 0) if health_ratio < 0.7 else (0, 255, 0)
        pygame.draw.rect(screen, health_color, (x - bar_width//2, y, health_width, bar_height))
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "health": self.health,
            "max_health": self.max_health,
            "damage": self.damage,
            "experience": self.experience,
            "is_boss": self.is_boss
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create enemy from save data"""
        enemy = cls(data["x"], data["y"], data["name"], data["max_health"], data["damage"], data["experience"], data["is_boss"], asset_loader)
        enemy.health = data["health"]
        return enemy


class Chest(Entity):
    """Chest entity that can be opened for loot"""
    
    def __init__(self, x, y, chest_type="wooden", asset_loader=None):
        super().__init__(x, y, f"{chest_type.title()} Chest", "chest", blocks_movement=True, asset_loader=asset_loader)
        self.chest_type = chest_type  # wooden, iron, gold, magical
        self.is_opened = False
        self.loot_items = []
        self.asset_loader = asset_loader
        
        # Generate loot based on chest type
        self.generate_loot()
        
        # Create chest sprite
        self.create_chest_sprite()
    
    def create_chest_sprite(self):
        """Create chest sprite"""
        size = 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            # Check for chest-specific sprites
            chest_image = None
            if self.chest_type == "wooden":
                chest_image = self.asset_loader.get_image("wooden_chest")
            elif self.chest_type == "iron":
                chest_image = self.asset_loader.get_image("iron_chest")
            elif self.chest_type == "gold":
                chest_image = self.asset_loader.get_image("gold_chest")
            elif self.chest_type == "magical":
                chest_image = self.asset_loader.get_image("magical_chest")
            
            # Fallback to generic chest
            if not chest_image:
                chest_image = self.asset_loader.get_image("chest")
            
            if chest_image:
                self.sprite = pygame.transform.scale(chest_image, (size, size))
                return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different chest types
        if self.chest_type == "wooden":
            color = (139, 69, 19)  # Brown
            accent_color = (160, 82, 45)  # Saddle brown
        elif self.chest_type == "iron":
            color = (105, 105, 105)  # Dim gray
            accent_color = (169, 169, 169)  # Dark gray
        elif self.chest_type == "gold":
            color = (255, 215, 0)  # Gold
            accent_color = (255, 255, 0)  # Yellow
        elif self.chest_type == "magical":
            color = (138, 43, 226)  # Blue violet
            accent_color = (147, 112, 219)  # Medium purple
        else:
            color = (139, 69, 19)  # Default brown
            accent_color = (160, 82, 45)
        
        # Draw chest body
        chest_body = pygame.Rect(size//6, size//3, 2*size//3, 2*size//3)
        pygame.draw.rect(self.sprite, color, chest_body)
        pygame.draw.rect(self.sprite, (0, 0, 0), chest_body, 2)
        
        # Draw chest lid
        if not self.is_opened:
            lid_rect = pygame.Rect(size//6, size//4, 2*size//3, size//3)
            pygame.draw.rect(self.sprite, accent_color, lid_rect)
            pygame.draw.rect(self.sprite, (0, 0, 0), lid_rect, 2)
            
            # Draw lock/latch
            lock_rect = pygame.Rect(size//2 - 3, size//2 - 2, 6, 4)
            pygame.draw.rect(self.sprite, (255, 215, 0), lock_rect)
            pygame.draw.rect(self.sprite, (0, 0, 0), lock_rect, 1)
        else:
            # Opened chest - lid is up
            lid_rect = pygame.Rect(size//6, size//8, 2*size//3, size//4)
            pygame.draw.rect(self.sprite, accent_color, lid_rect)
            pygame.draw.rect(self.sprite, (0, 0, 0), lid_rect, 2)
            
            # Draw interior
            interior_rect = pygame.Rect(size//6 + 2, size//3 + 2, 2*size//3 - 4, 2*size//3 - 4)
            pygame.draw.rect(self.sprite, (101, 67, 33), interior_rect)  # Dark brown interior
    
    def generate_loot(self):
        """Generate loot based on chest type"""
        self.loot_items = []
        
        if self.chest_type == "wooden":
            # Basic loot - 1-2 items
            num_items = random.randint(1, 2)
            for _ in range(num_items):
                item_type = random.choice(["consumable", "consumable", "weapon", "misc"])  # Favor consumables
                if item_type == "consumable":
                    potion_types = ["Health Potion", "Stamina Potion"]
                    potion_name = random.choice(potion_types)
                    if potion_name == "Health Potion":
                        item = Item(self.x, self.y, "Health Potion", item_type="consumable", 
                                  effect={"health": 50}, value=25, asset_loader=self.asset_loader)
                    else:
                        item = Item(self.x, self.y, "Stamina Potion", item_type="consumable", 
                                  effect={"stamina": 30}, value=20, asset_loader=self.asset_loader)
                elif item_type == "weapon":
                    weapons = ["Iron Sword", "Bronze Mace", "Silver Dagger"]
                    weapon_name = random.choice(weapons)
                    damage = random.randint(10, 15)
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage}, value=100, asset_loader=self.asset_loader)
                else:  # misc
                    item = Item(self.x, self.y, "Gold Ring", item_type="misc", 
                              effect={"magic_resistance": 3}, value=150, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
        
        elif self.chest_type == "iron":
            # Better loot - 2-3 items
            num_items = random.randint(2, 3)
            for _ in range(num_items):
                item_type = random.choice(["consumable", "weapon", "armor", "misc"])
                if item_type == "consumable":
                    potion_types = ["Health Potion", "Stamina Potion", "Mana Potion", "Strength Potion"]
                    potion_name = random.choice(potion_types)
                    if potion_name == "Health Potion":
                        item = Item(self.x, self.y, "Health Potion", item_type="consumable", 
                                  effect={"health": 50}, value=25, asset_loader=self.asset_loader)
                    elif potion_name == "Stamina Potion":
                        item = Item(self.x, self.y, "Stamina Potion", item_type="consumable", 
                                  effect={"stamina": 30}, value=20, asset_loader=self.asset_loader)
                    elif potion_name == "Mana Potion":
                        item = Item(self.x, self.y, "Mana Potion", item_type="consumable", 
                                  effect={"mana": 40}, value=30, asset_loader=self.asset_loader)
                    else:
                        item = Item(self.x, self.y, "Strength Potion", item_type="consumable", 
                                  effect={"damage_boost": 10, "duration": 60}, value=50, asset_loader=self.asset_loader)
                elif item_type == "weapon":
                    weapons = ["Steel Axe", "War Hammer", "Magic Bow", "Crossbow"]
                    weapon_name = random.choice(weapons)
                    damage = random.randint(15, 20)
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage}, value=150, asset_loader=self.asset_loader)
                elif item_type == "armor":
                    armors = ["Chain Mail", "Studded Leather", "Scale Mail"]
                    armor_name = random.choice(armors)
                    defense = random.randint(8, 12)
                    item = Item(self.x, self.y, armor_name, item_type="armor", 
                              effect={"defense": defense}, value=120, asset_loader=self.asset_loader)
                else:  # misc
                    misc_items = [("Magic Scroll", {"spell_power": 15}), ("Crystal Gem", {"value": 100})]
                    item_name, effect = random.choice(misc_items)
                    item = Item(self.x, self.y, item_name, item_type="misc", 
                              effect=effect, value=200, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
        
        elif self.chest_type == "gold":
            # High-quality loot - 3-4 items
            num_items = random.randint(3, 4)
            for _ in range(num_items):
                item_type = random.choice(["weapon", "armor", "consumable", "misc"])
                if item_type == "weapon":
                    weapons = ["Crystal Staff", "Throwing Knife", "War Hammer"]
                    weapon_name = random.choice(weapons)
                    damage = random.randint(18, 25)
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage}, value=200, asset_loader=self.asset_loader)
                elif item_type == "armor":
                    armors = ["Plate Armor", "Dragon Scale Armor", "Mage Robes"]
                    armor_name = random.choice(armors)
                    defense = random.randint(15, 20)
                    item = Item(self.x, self.y, armor_name, item_type="armor", 
                              effect={"defense": defense}, value=250, asset_loader=self.asset_loader)
                elif item_type == "consumable":
                    # High-quality consumables
                    consumables = ["Strength Potion", "Mana Potion", "Antidote"]
                    consumable_name = random.choice(consumables)
                    if consumable_name == "Strength Potion":
                        item = Item(self.x, self.y, "Strength Potion", item_type="consumable", 
                                  effect={"damage_boost": 15, "duration": 90}, value=75, asset_loader=self.asset_loader)
                    elif consumable_name == "Mana Potion":
                        item = Item(self.x, self.y, "Mana Potion", item_type="consumable", 
                                  effect={"mana": 60}, value=45, asset_loader=self.asset_loader)
                    else:
                        item = Item(self.x, self.y, "Antidote", item_type="consumable", 
                                  effect={"cure_poison": True}, value=50, asset_loader=self.asset_loader)
                else:  # misc
                    item = Item(self.x, self.y, "Gold Ring", item_type="misc", 
                              effect={"magic_resistance": 8}, value=300, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
        
        elif self.chest_type == "magical":
            # Rare magical loot - 2-3 high-value items
            num_items = random.randint(2, 3)
            for _ in range(num_items):
                item_type = random.choice(["weapon", "armor", "misc"])
                if item_type == "weapon":
                    weapons = ["Crystal Staff", "Magic Bow"]
                    weapon_name = random.choice(weapons)
                    damage = random.randint(20, 30)
                    spell_power = random.randint(10, 20)
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage, "spell_power": spell_power}, value=300, asset_loader=self.asset_loader)
                elif item_type == "armor":
                    armors = ["Mage Robes", "Royal Armor"]
                    armor_name = random.choice(armors)
                    defense = random.randint(18, 25)
                    magic_resist = random.randint(8, 15)
                    item = Item(self.x, self.y, armor_name, item_type="armor", 
                              effect={"defense": defense, "magic_resistance": magic_resist}, value=400, asset_loader=self.asset_loader)
                else:  # misc
                    misc_items = [
                        ("Magic Scroll", {"spell_power": 25}),
                        ("Crystal Gem", {"value": 200}),
                        ("Gold Ring", {"magic_resistance": 12})
                    ]
                    item_name, effect = random.choice(misc_items)
                    item = Item(self.x, self.y, item_name, item_type="misc", 
                              effect=effect, value=350, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
    
    def interact(self, player):
        """Open the chest and give loot to player"""
        if self.is_opened:
            if player.game_log:
                player.game_log.add_message("This chest is already empty.", "system")
            return
        
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play chest opening sound
        if audio:
            audio.play_ui_sound("achievement")  # Use achievement sound for chest opening
        
        self.is_opened = True
        
        # Update sprite to show opened chest
        self.create_chest_sprite()
        
        # Give loot to player
        items_received = []
        items_dropped = []
        
        for item in self.loot_items:
            if player.add_item(item):
                items_received.append(item.name)
            else:
                # Drop item on ground if inventory is full
                item.x = self.x + random.uniform(-0.5, 0.5)
                item.y = self.y + random.uniform(-0.5, 0.5)
                items_dropped.append(item)
        
        # Add dropped items to level
        if hasattr(player, 'game') and hasattr(player.game, 'level'):
            player.game.level.items.extend(items_dropped)
        
        # Show messages
        if player.game_log:
            player.game_log.add_message(f"Opened {self.name}!", "item")
            if items_received:
                for item_name in items_received:
                    player.game_log.add_message(f"Found {item_name}!", "item")
            if items_dropped:
                player.game_log.add_message(f"{len(items_dropped)} items dropped (inventory full)", "system")
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "chest_type": self.chest_type,
            "is_opened": self.is_opened,
            "loot_items": [item.get_save_data() for item in self.loot_items]
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create chest from save data"""
        chest = cls(data["x"], data["y"], data["chest_type"], asset_loader)
        chest.is_opened = data["is_opened"]
        chest.loot_items = []
        for item_data in data["loot_items"]:
            item = Item.from_save_data(item_data, asset_loader)
            chest.loot_items.append(item)
        return chest


class Item(Entity):
    """Item entity"""
    
    def __init__(self, x, y, name, item_type="misc", effect=None, value=0, asset_loader=None):
        super().__init__(x, y, name, "item")
        self.item_type = item_type  # weapon, armor, consumable, misc
        self.effect = effect or {}
        self.value = value
        self.asset_loader = asset_loader
        
        # Animation
        self.bob_offset = 0
        self.bob_speed = 0.1
        
        # Create item sprite
        self.create_item_sprite()
    
    def create_item_sprite(self):
        """Create item sprite using individual sprite files"""
        size = 36  # Increased from 24 to 36
        
        # Map item names to sprite names with values
        sprite_mapping = {
            # Weapons
            "Iron Sword": ("iron_sword", 100),
            "Steel Axe": ("steel_axe", 150), 
            "Bronze Mace": ("bronze_mace", 80),
            "Silver Dagger": ("silver_dagger", 120),
            "War Hammer": ("war_hammer", 200),
            "Magic Bow": ("magic_bow", 180),
            "Crystal Staff": ("crystal_staff", 220),
            "Throwing Knife": ("throwing_knife", 90),
            "Crossbow": ("crossbow", 160),
            # Armor
            "Leather Armor": ("leather_armor", 80),
            "Chain Mail": ("chain_mail", 120),
            "Plate Armor": ("plate_armor", 200), 
            "Studded Leather": ("studded_leather", 100),
            "Scale Mail": ("scale_mail", 160),
            "Dragon Scale Armor": ("dragon_scale_armor", 300),
            "Mage Robes": ("mage_robes", 180),
            "Royal Armor": ("royal_armor", 350),
            # Consumables
            "Health Potion": ("health_potion", 25),
            "Stamina Potion": ("stamina_potion", 20),
            "Mana Potion": ("mana_potion", 30),
            "Antidote": ("antidote", 35),
            "Strength Potion": ("strength_potion", 50),
            # Miscellaneous
            "Gold Ring": ("gold_ring", 250),
            "Magic Scroll": ("magic_scroll", 200),
            "Crystal Gem": ("crystal_gem", 150)
        }
        
        # Set item value if not already set
        if self.value == 0 and self.name in sprite_mapping:
            self.value = sprite_mapping[self.name][1]
        
        # Try to use individual sprite files
        if self.asset_loader and self.name in sprite_mapping:
            sprite_name = sprite_mapping[self.name][0]
            item_image = self.asset_loader.get_image(sprite_name)
            if item_image:
                self.sprite = pygame.transform.scale(item_image, (size, size))
                return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different item types
        if self.item_type == "weapon":
            color = (192, 192, 192)  # Silver
            # Draw sword shape
            pygame.draw.rect(self.sprite, color, (size//2 - 3, 6, 6, size - 12))
            pygame.draw.rect(self.sprite, (139, 69, 19), (size//2 - 6, size - 12, 12, 6))
        elif self.item_type == "armor":
            color = (165, 42, 42)  # Brown
            # Draw armor shape
            pygame.draw.ellipse(self.sprite, color, (6, 9, size - 12, size - 15))
        elif self.item_type == "consumable":
            if "Health" in self.name:
                color = (255, 0, 0)  # Red for health
            else:
                color = (0, 0, 255)  # Blue for mana
            # Draw potion shape
            pygame.draw.ellipse(self.sprite, color, (9, 12, size - 18, size - 18))
            pygame.draw.rect(self.sprite, (139, 69, 19), (size//2 - 3, 6, 6, 9))
        else:
            color = (255, 215, 0)  # Gold
            # Draw generic item
            pygame.draw.circle(self.sprite, color, (size//2, size//2), size//3)
        
        # Add border
        pygame.draw.circle(self.sprite, (0, 0, 0), (size//2, size//2), size//3, 3)  # Thicker border
    
    def update(self, level):
        """Update item (bobbing animation)"""
        self.bob_offset += self.bob_speed
        if self.bob_offset > math.pi * 2:
            self.bob_offset = 0
    
    def render(self, screen, iso_renderer, camera_x, camera_y):
        """Render the item with bobbing animation"""
        if self.sprite:
            screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
            
            # Add bobbing effect
            bob_y = math.sin(self.bob_offset) * 3
            
            # Center the sprite
            sprite_rect = self.sprite.get_rect()
            sprite_rect.center = (screen_x, screen_y - 16 + bob_y)
            
            screen.blit(self.sprite, sprite_rect)
            
            # Render item name when close to player
            # This would be better handled by the level or UI system
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "item_type": self.item_type,
            "effect": self.effect,
            "value": self.value
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create item from save data"""
        item = cls(data["x"], data["y"], data["name"], data["item_type"], data["effect"], data["value"], asset_loader)
        return item