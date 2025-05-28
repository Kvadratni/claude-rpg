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
    
    def __init__(self, x, y, name, dialog=None, shop_items=None, asset_loader=None):
        super().__init__(x, y, name, "npc")
        self.dialog = dialog or ["Hello, traveler!"]
        self.shop_items = shop_items or []
        self.dialog_index = 0
        self.asset_loader = asset_loader
        
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
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different NPCs
        if "Shopkeeper" in self.name:
            color = (255, 215, 0)  # Gold
        elif "Elder" in self.name:
            color = (128, 0, 128)  # Purple
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
    
    def interact(self, player):
        """Interact with the NPC"""
        if self.dialog:
            print(f"{self.name}: {self.dialog[self.dialog_index]}")
            self.dialog_index = (self.dialog_index + 1) % len(self.dialog)
        
        # Handle shop
        if self.shop_items:
            print(f"{self.name} has items for sale!")
            # TODO: Implement shop interface
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "dialog": self.dialog,
            "shop_items": self.shop_items,
            "dialog_index": self.dialog_index
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create NPC from save data"""
        npc = cls(data["x"], data["y"], data["name"], data["dialog"], data["shop_items"], asset_loader)
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
            if distance <= self.attack_range:
                self.state = "attacking"
                if self.attack_cooldown <= 0:
                    self.attack_player(player)
                    self.attack_cooldown = self.max_attack_cooldown
            else:
                self.state = "chasing"
                # Move towards player
                if distance > 0:
                    move_x = (dx / distance) * self.speed
                    move_y = (dy / distance) * self.speed
                    
                    # Check collision before moving
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    if not level.check_collision(new_x, new_y, self.size):
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
                
                if not level.check_collision(new_x, new_y, self.size):
                    self.x = new_x
                    self.y = new_y
    
    def attack_player(self, player):
        """Attack the player"""
        damage_dealt = self.damage + random.randint(-5, 5)  # Random damage variation
        if player.take_damage(damage_dealt):
            print(f"{self.name} defeated the player!")
        else:
            print(f"{self.name} attacks for {damage_dealt} damage!")
    
    def take_damage(self, damage):
        """Take damage"""
        actual_damage = max(1, damage - random.randint(0, 3))  # Random defense
        self.health -= actual_damage
        print(f"{self.name} takes {actual_damage} damage! ({self.health}/{self.max_health})")
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
        
        # Map item names to sprite names
        sprite_mapping = {
            "Iron Sword": "iron_sword",
            "Steel Axe": "steel_axe", 
            "Bronze Mace": "bronze_mace",
            "Silver Dagger": "silver_dagger",
            "War Hammer": "war_hammer",
            "Leather Armor": "leather_armor",
            "Chain Mail": "chain_mail",
            "Plate Armor": "plate_armor", 
            "Studded Leather": "studded_leather",
            "Scale Mail": "scale_mail",
            "Health Potion": "health_potion",
            "Mana Potion": "mana_potion"
        }
        
        # Try to use individual sprite files
        if self.asset_loader and self.name in sprite_mapping:
            sprite_name = sprite_mapping[self.name]
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