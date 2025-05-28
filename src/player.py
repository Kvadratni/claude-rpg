"""
Player class for the RPG
"""

import pygame
import math
import random
from .inventory import Inventory

class Player:
    """Player character class"""
    
    def __init__(self, x, y, asset_loader=None, game_log=None):
        self.x = x
        self.y = y
        self.asset_loader = asset_loader
        self.game_log = game_log
        self.speed = 0.2  # Increased from 0.1
        self.size = 0.4
        
        # RPG stats
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.mana = 50
        self.max_mana = 50
        self.experience = 0
        self.experience_to_next = 100
        self.gold = 50
        
        # Combat
        self.attack_damage = 25
        self.attack_range = 1.2
        self.attacking = False
        self.attack_cooldown = 0
        self.max_attack_cooldown = 30
        self.defense = 5
        
        # Movement
        self.moving = False
        self.direction = 0  # 0=down, 1=left, 2=up, 3=right
        self.target_x = None  # For mouse movement
        self.target_y = None
        self.move_speed = 0.1  # Increased from 0.05 - speed for mouse movement
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10
        
        # Inventory
        self.inventory = Inventory(max_size=20)
        self.equipped_weapon = None
        self.equipped_armor = None
        
        # UI state
        self.show_stats = False
        self.show_dialog = False
        self.dialog_text = ""
        
        # Create player sprite
        self.create_sprite()
    
    def create_sprite(self):
        """Create player sprite"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            player_image = self.asset_loader.get_image("player_sprite")
            if player_image:
                # Use the same sprite for all directions - no rotation
                self.sprite = pygame.transform.scale(player_image, (size, size))
                self.direction_sprites = [self.sprite] * 4  # Same sprite for all directions
                return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw player body
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, (100, 150, 255), center, size // 3)
        
        # Draw face details
        pygame.draw.circle(self.sprite, (255, 255, 255), (center[0] - 6, center[1] - 6), 4)  # Larger eyes
        pygame.draw.circle(self.sprite, (255, 255, 255), (center[0] + 6, center[1] + 6), 4)
        pygame.draw.circle(self.sprite, (0, 0, 0), (center[0] - 6, center[1] - 6), 2)
        pygame.draw.circle(self.sprite, (0, 0, 0), (center[0] + 6, center[1] + 6), 2)
        
        # Draw border
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Thicker border
        
        # Use the same sprite for all directions - no rotation
        self.direction_sprites = [self.sprite] * 4
    
    def handle_input(self, keys, level=None):
        """Handle player input"""
        self.moving = False
        
        # Check if we have a mouse target to move to
        if self.target_x is not None and self.target_y is not None:
            # Calculate distance to target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # If we're close enough to the target, stop moving
            if distance < 0.1:
                self.target_x = None
                self.target_y = None
            else:
                # Move towards target
                move_x = (dx / distance) * self.move_speed
                move_y = (dy / distance) * self.move_speed
                
                # Store old position
                old_x, old_y = self.x, self.y
                
                # Try to move
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                # Check collision before moving
                if level and level.check_collision(new_x, new_y, self.size):
                    # Cancel mouse movement if blocked
                    self.target_x = None
                    self.target_y = None
                    if self.game_log:
                        self.game_log.add_message("Path blocked!", "system")
                else:
                    self.x = new_x
                    self.y = new_y
                    self.moving = True
                
                # Update direction based on movement (but don't rotate sprite)
                if abs(dx) > abs(dy):
                    self.direction = 3 if dx > 0 else 1  # Right or Left
                else:
                    self.direction = 0 if dy > 0 else 2  # Down or Up
        
        # Attack with space bar (keep this for combat)
        if keys[pygame.K_SPACE]:
            self.attacking = True
        else:
            self.attacking = False
        
        # Update animation
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
    
    def handle_mouse_click(self, world_x, world_y, level):
        """Handle mouse click for movement and interaction"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Check if clicking on an entity first
        clicked_entity = None
        
        # Check NPCs
        for npc in level.npcs:
            # Use larger detection area for easier clicking
            if abs(world_x - npc.x) < 1.2 and abs(world_y - npc.y) < 1.2:
                clicked_entity = npc
                break
        
        # Check items
        if not clicked_entity:
            for item in level.items[:]:
                # Use larger detection area for easier clicking
                if abs(world_x - item.x) < 1.2 and abs(world_y - item.y) < 1.2:
                    # Check if player is close enough to pick up
                    dist = math.sqrt((self.x - item.x)**2 + (self.y - item.y)**2)
                    if dist < 2.0:
                        if self.add_item(item):
                            level.items.remove(item)
                            # Play pickup sound based on item type
                            if audio:
                                if item.name.lower().find('gold') != -1 or item.name.lower().find('coin') != -1:
                                    audio.play_ui_sound("coin")
                                else:
                                    audio.play_ui_sound("click")
                            if self.game_log:
                                self.game_log.add_message(f"Picked up {item.name}", "item")
                        else:
                            if self.game_log:
                                self.game_log.add_message("Inventory is full!", "system")
                    else:
                        # Move towards the item
                        self.target_x = item.x
                        self.target_y = item.y
                        if self.game_log:
                            self.game_log.add_message(f"Moving to pick up {item.name}", "system")
                    clicked_entity = item
                    break
        
        # Check enemies for attack
        if not clicked_entity:
            for enemy in level.enemies:
                # Use larger detection area for easier clicking
                if abs(world_x - enemy.x) < 1.5 and abs(world_y - enemy.y) < 1.5:
                    # Check if player is close enough to attack
                    dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
                    if dist <= self.attack_range:
                        # Attack immediately if in range
                        if self.attack_cooldown <= 0:
                            self.attack([enemy])
                            self.attack_cooldown = self.max_attack_cooldown
                            if self.game_log:
                                self.game_log.add_message(f"Attacking {enemy.name}!", "combat")
                        else:
                            if self.game_log:
                                self.game_log.add_message("Attack on cooldown!", "combat")
                    else:
                        # Move towards enemy for attack
                        self.target_x = enemy.x
                        self.target_y = enemy.y
                        if self.game_log:
                            self.game_log.add_message(f"Moving to attack {enemy.name}", "combat")
                    clicked_entity = enemy
                    break
        
        # If no entity was clicked, move to the location
        if not clicked_entity:
            # Check if the target location is walkable
            tile_x = int(world_x)
            tile_y = int(world_y)
            
            if (0 <= tile_x < level.width and 0 <= tile_y < level.height and
                level.walkable[tile_y][tile_x]):
                self.target_x = world_x
                self.target_y = world_y
                if self.game_log:
                    self.game_log.add_message(f"Moving to ({world_x:.1f}, {world_y:.1f})", "system")
            else:
                if self.game_log:
                    self.game_log.add_message("Can't move there!", "system")
        
        # Interact with clicked entity
        if clicked_entity:
            if hasattr(clicked_entity, 'interact'):
                clicked_entity.interact(self)
    
    def update(self, level):
        """Update player logic"""
        # We've moved collision detection to handle_input
        # This is now just for additional updates
        
        # Handle attacks
        if self.attacking and self.attack_cooldown <= 0:
            self.attack(level.enemies)
            self.attack_cooldown = self.max_attack_cooldown
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Regenerate mana
        if self.mana < self.max_mana and random.random() < 0.01:
            self.mana += 1
    
    def attack(self, enemies):
        """Attack nearby enemies"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        for enemy in enemies[:]:
            # Calculate distance to enemy
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if enemy is in range and in front of player
            if distance <= self.attack_range:
                # Check if enemy is in the direction the player is facing
                in_range = False
                
                if self.direction == 0 and dy > 0:  # Down
                    in_range = True
                elif self.direction == 1 and dx < 0:  # Left
                    in_range = True
                elif self.direction == 2 and dy < 0:  # Up
                    in_range = True
                elif self.direction == 3 and dx > 0:  # Right
                    in_range = True
                
                if in_range:
                    # Play combat sound
                    if audio:
                        if self.equipped_weapon and 'axe' in self.equipped_weapon.name.lower():
                            audio.play_combat_sound("axe_hit")
                        else:
                            audio.play_combat_sound("sword_hit")
                    
                    # Calculate damage with weapon bonus
                    damage = self.attack_damage
                    if self.equipped_weapon:
                        damage += self.equipped_weapon.effect.get("damage", 0)
                    
                    # Random damage variation
                    damage += random.randint(-5, 5)
                    
                    # Attack the enemy
                    if enemy.take_damage(damage):
                        if self.game_log:
                            self.game_log.add_message(f"Enemy {enemy.name} defeated!", "combat")
                        # Experience is handled in the level class
    
    def take_damage(self, damage):
        """Take damage"""
        # Apply defense reduction
        defense = self.defense
        if self.equipped_armor:
            defense += self.equipped_armor.effect.get("defense", 0)
        
        actual_damage = max(1, damage - defense)
        self.health = max(0, self.health - actual_damage)
        if self.game_log:
            self.game_log.add_message(f"Player takes {actual_damage} damage! ({self.health}/{self.max_health})", "combat")
        
        return self.health <= 0  # Return True if player died
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        if self.game_log:
            self.game_log.add_message(f"Player healed for {amount}! ({self.health}/{self.max_health})", "item")
    
    def restore_mana(self, amount):
        """Restore player mana"""
        self.mana = min(self.max_mana, self.mana + amount)
        if self.game_log:
            self.game_log.add_message(f"Player restored {amount} mana! ({self.mana}/{self.max_mana})", "item")
    
    def gain_experience(self, exp):
        """Gain experience points"""
        self.experience += exp
        if self.game_log:
            self.game_log.add_message(f"Gained {exp} experience! ({self.experience}/{self.experience_to_next})", "experience")
        
        # Check for level up
        while self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Level up the player"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        self.experience -= self.experience_to_next
        self.level += 1
        
        # Play level up sound
        if audio:
            audio.play_ui_sound("achievement")
        
        # Increase stats
        self.max_health += 20
        self.max_mana += 10
        self.health = self.max_health  # Full heal on level up
        self.mana = self.max_mana
        self.attack_damage += 5
        self.defense += 2
        
        # Increase experience requirement
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        if self.game_log:
            self.game_log.add_message(f"Level up! Now level {self.level}", "experience")
            self.game_log.add_message(f"Health increased to {self.max_health}", "experience")
            self.game_log.add_message(f"Mana increased to {self.max_mana}", "experience")
            self.game_log.add_message(f"Attack increased to {self.attack_damage}", "experience")
            self.game_log.add_message(f"Defense increased to {self.defense}", "experience")
    
    def add_item(self, item):
        """Add item to inventory"""
        return self.inventory.add_item(item)
    
    def remove_item(self, item):
        """Remove item from inventory"""
        return self.inventory.remove_item(item)
    
    def use_item(self, item):
        """Use an item"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        if item.item_type == "consumable":
            # Apply item effects
            if "health" in item.effect:
                self.heal(item.effect["health"])
            if "mana" in item.effect:
                self.restore_mana(item.effect["mana"])
            
            # Play consumption sound
            if audio:
                audio.play_ui_sound("click")
            
            # Remove item after use
            self.remove_item(item)
        elif item.item_type == "weapon":
            # Play equip sound
            if audio:
                audio.play_combat_sound("draw_weapon")
            
            # Equip weapon
            old_weapon = self.equipped_weapon
            self.equipped_weapon = item
            if old_weapon:
                self.inventory.add_item(old_weapon)
            self.inventory.remove_item(item)
            if self.game_log:
                self.game_log.add_message(f"Equipped {item.name}", "item")
        elif item.item_type == "armor":
            # Play equip sound
            if audio:
                audio.play_ui_sound("click")
            
            # Equip armor
            old_armor = self.equipped_armor
            self.equipped_armor = item
            if old_armor:
                self.inventory.add_item(old_armor)
            self.inventory.remove_item(item)
            if self.game_log:
                self.game_log.add_message(f"Equipped {item.name}", "item")
    
    def render(self, screen, iso_renderer, camera_x, camera_y):
        """Render the player"""
        # Calculate screen position
        screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
        
        # Get current sprite based on direction
        current_sprite = self.direction_sprites[self.direction]
        
        # Center the sprite
        sprite_rect = current_sprite.get_rect()
        sprite_rect.center = (screen_x, screen_y - 16)  # Offset for isometric view
        
        # Draw sprite
        screen.blit(current_sprite, sprite_rect)
        
        # Render movement target indicator
        if self.target_x is not None and self.target_y is not None:
            target_screen_x, target_screen_y = iso_renderer.world_to_screen(self.target_x, self.target_y, camera_x, camera_y)
            # Draw a pulsing circle at the target location
            import time
            pulse = int(abs(math.sin(time.time() * 5)) * 10) + 5
            pygame.draw.circle(screen, (255, 255, 0), (int(target_screen_x), int(target_screen_y)), pulse, 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(target_screen_x), int(target_screen_y)), 3)
        
        # Render attack indicator if attacking
        if self.attacking:
            self.render_attack(screen, screen_x, screen_y)
        
        # Render health bar
        self.render_health_bar(screen, screen_x, screen_y - 30)
    
    def render_attack(self, screen, x, y):
        """Render attack indicator"""
        attack_x, attack_y = x, y
        
        # Adjust position based on direction
        if self.direction == 0:  # Down
            attack_y += 20
        elif self.direction == 1:  # Left
            attack_x -= 20
        elif self.direction == 2:  # Up
            attack_y -= 20
        elif self.direction == 3:  # Right
            attack_x += 20
        
        # Draw attack indicator
        pygame.draw.circle(screen, (255, 255, 0), (attack_x, attack_y), 8)
        pygame.draw.circle(screen, (255, 0, 0), (attack_x, attack_y), 5)
    
    def render_health_bar(self, screen, x, y):
        """Render player health bar"""
        bar_width = 40
        bar_height = 5
        
        # Background
        pygame.draw.rect(screen, (100, 0, 0), (x - bar_width//2, y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (x - bar_width//2, y, health_width, bar_height))
        
        # Mana bar
        pygame.draw.rect(screen, (50, 50, 100), (x - bar_width//2, y + bar_height + 1, bar_width, bar_height - 1))
        mana_width = int((self.mana / self.max_mana) * bar_width)
        pygame.draw.rect(screen, (0, 100, 255), (x - bar_width//2, y + bar_height + 1, mana_width, bar_height - 1))
    
    def render_inventory(self, screen):
        """Render inventory UI"""
        self.inventory.render(screen, self.equipped_weapon, self.equipped_armor)
    
    def get_save_data(self):
        """Get data for saving"""
        return {
            "x": self.x,
            "y": self.y,
            "level": self.level,
            "health": self.health,
            "max_health": self.max_health,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "experience": self.experience,
            "experience_to_next": self.experience_to_next,
            "gold": self.gold,
            "attack_damage": self.attack_damage,
            "defense": self.defense,
            "inventory": [item.get_save_data() for item in self.inventory.items],
            "equipped_weapon": self.equipped_weapon.get_save_data() if self.equipped_weapon else None,
            "equipped_armor": self.equipped_armor.get_save_data() if self.equipped_armor else None
        }
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None, game_log=None):
        """Create player from save data"""
        from .entity import Item
        
        player = cls(data["x"], data["y"], asset_loader, game_log)
        player.level = data["level"]
        player.health = data["health"]
        player.max_health = data["max_health"]
        player.mana = data["mana"]
        player.max_mana = data["max_mana"]
        player.experience = data["experience"]
        player.experience_to_next = data["experience_to_next"]
        player.gold = data["gold"]
        player.attack_damage = data["attack_damage"]
        player.defense = data["defense"]
        
        # Load inventory
        player.inventory = Inventory(max_size=20)
        for item_data in data["inventory"]:
            item = Item.from_save_data(item_data, asset_loader)
            player.inventory.add_item(item)
        
        # Load equipped items
        if data["equipped_weapon"]:
            player.equipped_weapon = Item.from_save_data(data["equipped_weapon"], asset_loader)
        
        if data["equipped_armor"]:
            player.equipped_armor = Item.from_save_data(data["equipped_armor"], asset_loader)
        
        return player