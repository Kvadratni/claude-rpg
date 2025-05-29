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
        self.stamina = 50
        self.max_stamina = 50
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
        self.move_speed = 0.15  # Increased for smoother pathfinding movement
        
        # Pathfinding
        self.path = []  # Current path to follow
        self.path_index = 0  # Current index in path
        
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
        self.current_dialogue = None  # For dialogue windows
        
        # Create player sprite
        self.create_sprite()
    
    def create_sprite(self):
        """Create player sprite"""
        size = 48  # Increased from 32 to 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            player_image = self.asset_loader.get_image("player_sprite")
            if player_image:
                # Create base sprite
                self.sprite = pygame.transform.scale(player_image, (size, size))
                # Create direction sprites - mirror for right movement
                self.direction_sprites = [
                    self.sprite,  # Down (0)
                    self.sprite,  # Left (1) - original (facing left)
                    self.sprite,  # Up (2)
                    pygame.transform.flip(self.sprite, True, False)   # Right (3) - mirrored
                ]
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
        
        # Create direction sprites - mirror for right movement
        self.direction_sprites = [
            self.sprite,  # Down (0)
            self.sprite,  # Left (1) - original (facing left)
            self.sprite,  # Up (2)
            pygame.transform.flip(self.sprite, True, False)   # Right (3) - mirrored
        ]
    
    def handle_input(self, keys, level=None):
        """Handle player input"""
        self.moving = False
        
        # Check if any shop is open - if so, disable movement
        if level:
            for npc in level.npcs:
                if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                    return  # Don't allow movement while shop is open
        
        # Check if dialogue window is open - if so, disable movement
        if self.current_dialogue and self.current_dialogue.show:
            return  # Don't allow movement while dialogue is open
        
        # Follow current path if we have one
        if self.path and self.path_index < len(self.path):
            target_x, target_y = self.path[self.path_index]
            
            # Calculate distance to current path target
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if we're moving through a door and play sound
            if level:
                current_tile_x = int(self.x)
                current_tile_y = int(self.y)
                target_tile_x = int(target_x)
                target_tile_y = int(target_y)
                
                # Check if we're entering a door tile
                if (0 <= target_tile_x < level.width and 0 <= target_tile_y < level.height and
                    level.tiles[target_tile_y][target_tile_x] == level.TILE_DOOR and
                    (current_tile_x != target_tile_x or current_tile_y != target_tile_y)):
                    
                    # Play door sound occasionally (not every frame)
                    if not hasattr(self, 'last_door_sound_tile') or self.last_door_sound_tile != (target_tile_x, target_tile_y):
                        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
                        if audio:
                            audio.play_sound("environment", "door_open_1")
                        self.last_door_sound_tile = (target_tile_x, target_tile_y)
            
            # If we're close enough to the current path point, move to next
            if distance < 0.6:  # Increased from 0.2 for smoother pathfinding
                self.path_index += 1
                if self.path_index >= len(self.path):
                    # Reached end of path
                    self.path = []
                    self.path_index = 0
                    self.target_x = None
                    self.target_y = None
            else:
                # Move towards current path target
                move_x = (dx / distance) * self.move_speed
                move_y = (dy / distance) * self.move_speed
                
                # Try to move
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                # Check collision before moving
                if level and level.check_collision(new_x, new_y, self.size):
                    # Path is blocked, recalculate
                    if self.target_x is not None and self.target_y is not None:
                        self.recalculate_path(level)
                    else:
                        self.path = []
                        self.path_index = 0
                        if self.game_log:
                            self.game_log.add_message("Path blocked!", "system")
                else:
                    self.x = new_x
                    self.y = new_y
                    self.moving = True
                    
                    # Play footstep sounds occasionally while moving
                    if hasattr(self, 'footstep_timer'):
                        self.footstep_timer += 1
                    else:
                        self.footstep_timer = 0
                    
                    if self.footstep_timer >= 20:  # Play footstep every 20 frames
                        self.footstep_timer = 0
                        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
                        if audio and level:
                            # Determine surface type based on current tile
                            tile_x = int(self.x)
                            tile_y = int(self.y)
                            if 0 <= tile_x < level.width and 0 <= tile_y < level.height:
                                tile_type = level.tiles[tile_y][tile_x]
                                if tile_type == level.TILE_STONE:
                                    audio.play_footstep("stone")
                                elif tile_type == level.TILE_WATER:
                                    audio.play_footstep("water")
                                else:
                                    audio.play_footstep("dirt")  # Default for grass/dirt
                
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
    
    def recalculate_path(self, level):
        """Recalculate path to target"""
        if self.target_x is not None and self.target_y is not None and level:
            new_path = level.find_path(self.x, self.y, self.target_x, self.target_y, self.size)
            if new_path:
                self.path = new_path
                self.path_index = 0
            else:
                # No path found
                self.path = []
                self.path_index = 0
                self.target_x = None
                self.target_y = None
                if self.game_log:
                    self.game_log.add_message("No path found!", "system")
    
    def handle_mouse_click(self, world_x, world_y, level):
        """Handle mouse click for movement and interaction"""
        # Check if any shop is open - if so, disable mouse movement
        if level:
            for npc in level.npcs:
                if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                    return  # Don't allow movement while shop is open
        
        # Check if dialogue window is open - if so, disable mouse movement
        if self.current_dialogue and self.current_dialogue.show:
            return  # Don't allow movement while dialogue is open
        
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Check if clicking on an entity first
        clicked_entity = None
        
        # Check NPCs
        for npc in level.npcs:
            # Use larger detection area for easier clicking
            if abs(world_x - npc.x) < 1.2 and abs(world_y - npc.y) < 1.2:
                # Check if player is close enough to interact
                dist = math.sqrt((self.x - npc.x)**2 + (self.y - npc.y)**2)
                if dist < 2.0:  # Same proximity requirement as item pickup
                    clicked_entity = npc
                    break
                else:
                    # Use pathfinding to move towards the NPC
                    path = level.find_path(self.x, self.y, npc.x, npc.y, self.size)
                    if path:
                        self.path = path
                        self.path_index = 0
                        self.target_x = npc.x
                        self.target_y = npc.y
                    else:
                        if self.game_log:
                            self.game_log.add_message(f"Can't reach {npc.name}!", "system")
                    clicked_entity = npc  # Still set clicked_entity to prevent movement
                    break
        
        # Check chests
        if not clicked_entity:
            for chest in level.chests:
                # Use larger detection area for easier clicking
                if abs(world_x - chest.x) < 1.2 and abs(world_y - chest.y) < 1.2:
                    # Check if player is close enough to interact
                    dist = math.sqrt((self.x - chest.x)**2 + (self.y - chest.y)**2)
                    if dist < 1.5:  # Must be right next to chest to interact
                        clicked_entity = chest
                        break
                    else:
                        # Use pathfinding to move towards the chest
                        path = level.find_path(self.x, self.y, chest.x, chest.y, self.size)
                        if path:
                            self.path = path
                            self.path_index = 0
                            self.target_x = chest.x
                            self.target_y = chest.y
                        else:
                            if self.game_log:
                                self.game_log.add_message(f"Can't reach {chest.name}!", "system")
                        clicked_entity = chest  # Still set clicked_entity to prevent movement
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
                                elif item.item_type == "consumable":
                                    audio.play_sound("ui", "leather_item")  # Use leather item sound for potions
                                else:
                                    audio.play_ui_sound("click")
                            if self.game_log:
                                self.game_log.add_message(f"Picked up {item.name}", "item")
                        else:
                            if self.game_log:
                                self.game_log.add_message("Inventory is full!", "system")
                    else:
                        # Use pathfinding to move towards the item
                        path = level.find_path(self.x, self.y, item.x, item.y, self.size)
                        if path:
                            self.path = path
                            self.path_index = 0
                            self.target_x = item.x
                            self.target_y = item.y
                        else:
                            if self.game_log:
                                self.game_log.add_message(f"Can't reach {item.name}!", "system")
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
                        # Use pathfinding to move towards enemy for attack
                        path = level.find_path(self.x, self.y, enemy.x, enemy.y, self.size)
                        if path:
                            self.path = path
                            self.path_index = 0
                            self.target_x = enemy.x
                            self.target_y = enemy.y
                        else:
                            if self.game_log:
                                self.game_log.add_message(f"Can't reach {enemy.name}!", "combat")
                    clicked_entity = enemy
                    break
        
        # If no entity was clicked, move to the location
        if not clicked_entity:
            # Use pathfinding to move to the clicked location
            path = level.find_path(self.x, self.y, world_x, world_y, self.size)
            if path:
                self.path = path
                self.path_index = 0
                self.target_x = world_x
                self.target_y = world_y
            else:
                if self.game_log:
                    self.game_log.add_message("Can't move there!", "system")
        
        # Interact with clicked entity (only if close enough)
        if clicked_entity:
            if hasattr(clicked_entity, 'interact'):
                # For NPCs, check if we're close enough to actually interact
                if clicked_entity.entity_type == "npc":
                    dist = math.sqrt((self.x - clicked_entity.x)**2 + (self.y - clicked_entity.y)**2)
                    if dist < 2.0:  # Only interact if close enough
                        clicked_entity.interact(self)
                    # If not close enough, we've already set up pathfinding above
                else:
                    # For other entities, interact normally
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
        
        # Update projectile effects
        if hasattr(self, 'projectiles'):
            for projectile in self.projectiles[:]:
                projectile['timer'] -= 1
                if projectile['timer'] <= 0:
                    self.projectiles.remove(projectile)
        
        # Regenerate stamina slowly over time
        if self.stamina < self.max_stamina and random.random() < 0.02:
            self.stamina += 1
    
    def attack(self, enemies):
        """Attack nearby enemies or use ranged attack"""
        # Check if player has enough stamina to attack
        stamina_cost = 10  # Cost 10 stamina per attack
        if self.stamina < stamina_cost:
            if self.game_log:
                self.game_log.add_message("Not enough stamina to attack!", "combat")
            return
        
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Consume stamina
        self.stamina -= stamina_cost
        
        # Check if equipped weapon is ranged
        is_ranged_weapon = False
        ranged_weapons = ["Magic Bow", "Crossbow", "Throwing Knife", "Crystal Staff"]
        
        if self.equipped_weapon and self.equipped_weapon.name in ranged_weapons:
            is_ranged_weapon = True
        
        if is_ranged_weapon:
            # Ranged attack - target all enemies within range
            self.ranged_attack(enemies, audio)
        else:
            # Melee attack - only attack enemies in front of player
            self.melee_attack(enemies, audio)
    
    def melee_attack(self, enemies, audio):
        """Perform melee attack on nearby enemies"""
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
                    # Calculate base damage (unarmed combat)
                    base_damage = 15  # Base unarmed damage
                    damage = base_damage
                    
                    # Add weapon bonus if equipped
                    if self.equipped_weapon:
                        damage += self.equipped_weapon.effect.get("damage", 0)
                        # Play weapon-specific sound
                        if audio:
                            if 'axe' in self.equipped_weapon.name.lower():
                                audio.play_combat_sound("axe_hit")
                            else:
                                audio.play_combat_sound("sword_hit")
                    else:
                        # Unarmed combat sound
                        if audio:
                            audio.play_combat_sound("weapon_hit")  # Generic punch sound
                    
                    # Random damage variation
                    damage += random.randint(-3, 3)
                    
                    # Attack the enemy
                    if enemy.take_damage(damage):
                        if self.game_log:
                            self.game_log.add_message(f"Enemy {enemy.name} defeated!", "combat")
                        # Experience is handled in the level class
                    
                    # Show different attack messages for armed vs unarmed
                    if self.equipped_weapon:
                        if self.game_log:
                            self.game_log.add_message(f"Hit with {self.equipped_weapon.name} for {damage} damage!", "combat")
                    else:
                        if self.game_log:
                            self.game_log.add_message(f"Punched for {damage} damage!", "combat")
                    
                    # Trigger combat music when player attacks
                    if audio and not audio.is_combat_music_active():
                        audio.start_combat_music()
    
    def ranged_attack(self, enemies, audio):
        """Perform ranged attack on enemies within range"""
        ranged_attack_range = 8.0  # Much longer range for ranged weapons
        
        # Find target enemy (closest enemy within range)
        target_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= ranged_attack_range and distance < closest_distance:
                target_enemy = enemy
                closest_distance = distance
        
        if target_enemy:
            # Calculate damage
            base_damage = 12  # Base ranged damage
            damage = base_damage
            
            if self.equipped_weapon:
                damage += self.equipped_weapon.effect.get("damage", 0)
                
                # Play weapon-specific sound
                if audio:
                    if "Bow" in self.equipped_weapon.name:
                        audio.play_combat_sound("bow_shot")  # We'll need to add this sound
                    elif "Crossbow" in self.equipped_weapon.name:
                        audio.play_combat_sound("crossbow_shot")  # We'll need to add this sound
                    elif "Throwing Knife" in self.equipped_weapon.name:
                        audio.play_combat_sound("blade_slice")  # Use existing blade sound
                    elif "Crystal Staff" in self.equipped_weapon.name:
                        audio.play_magic_sound("spell_cast")  # Use magic sound for staff
                    else:
                        audio.play_combat_sound("weapon_hit")  # Fallback
            
            # Random damage variation
            damage += random.randint(-2, 2)
            
            # Create projectile effect (visual)
            self.create_projectile_effect(target_enemy)
            
            # Apply damage
            if target_enemy.take_damage(damage):
                if self.game_log:
                    self.game_log.add_message(f"Enemy {target_enemy.name} defeated!", "combat")
            
            if self.game_log:
                weapon_name = self.equipped_weapon.name if self.equipped_weapon else "ranged attack"
                self.game_log.add_message(f"Hit {target_enemy.name} with {weapon_name} for {damage} damage!", "combat")
            
            # Trigger combat music when player attacks
            if audio and not audio.is_combat_music_active():
                audio.start_combat_music()
        else:
            if self.game_log:
                self.game_log.add_message("No enemies in ranged attack range!", "combat")
    
    def create_projectile_effect(self, target_enemy):
        """Create a visual projectile effect (placeholder for now)"""
        # For now, we'll just add a visual indicator
        # In a more advanced implementation, we could create actual projectile entities
        # that travel from player to target
        
        # Store projectile data for rendering
        if not hasattr(self, 'projectiles'):
            self.projectiles = []
        
        projectile = {
            'start_x': self.x,
            'start_y': self.y,
            'end_x': target_enemy.x,
            'end_y': target_enemy.y,
            'timer': 30,  # Show effect for 30 frames (0.5 seconds at 60 FPS)
            'weapon_type': self.equipped_weapon.name if self.equipped_weapon else "arrow"
        }
        
        self.projectiles.append(projectile)
    
    def take_damage(self, damage):
        """Take damage"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Apply defense reduction
        defense = self.defense
        if self.equipped_armor:
            defense += self.equipped_armor.effect.get("defense", 0)
        
        actual_damage = max(1, damage - defense)
        self.health = max(0, self.health - actual_damage)
        
        # Play hurt sound
        if audio:
            audio.play_combat_sound("blade_slice")  # Use blade slice as hurt sound
        
        if self.game_log:
            self.game_log.add_message(f"Player takes {actual_damage} damage! ({self.health}/{self.max_health})", "combat")
        
        return self.health <= 0  # Return True if player died
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        if self.game_log:
            self.game_log.add_message(f"Player healed for {amount}! ({self.health}/{self.max_health})", "item")
    
    def restore_stamina(self, amount):
        """Restore player stamina"""
        self.stamina = min(self.max_stamina, self.stamina + amount)
        if self.game_log:
            self.game_log.add_message(f"Player restored {amount} stamina! ({self.stamina}/{self.max_stamina})", "item")
    
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
        self.max_stamina += 10
        self.health = self.max_health  # Full heal on level up
        self.stamina = self.max_stamina
        self.attack_damage += 5
        self.defense += 2
        
        # Increase experience requirement
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        if self.game_log:
            self.game_log.add_message(f"Level up! Now level {self.level}", "experience")
            self.game_log.add_message(f"Health increased to {self.max_health}", "experience")
            self.game_log.add_message(f"Stamina increased to {self.max_stamina}", "experience")
            self.game_log.add_message(f"Attack increased to {self.attack_damage}", "experience")
            self.game_log.add_message(f"Defense increased to {self.defense}", "experience")
    
    def add_item(self, item):
        """Add item to inventory"""
        success = self.inventory.add_item(item)
        if success:
            # Update quest progress for item collection
            if hasattr(self, 'game') and hasattr(self.game, 'quest_manager'):
                self.game.quest_manager.update_quest_progress("collect", item.name)
                self.game.quest_manager.update_quest_progress("collect", "any")
        return success
    
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
            if "stamina" in item.effect:
                self.restore_stamina(item.effect["stamina"])
            
            # Play consumption sound - use metal pot sounds for potions
            if audio:
                audio.play_sound("ambient", "metal_pot")
            
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
            
            # Update quest progress for equipment
            if hasattr(self, 'game') and hasattr(self.game, 'quest_manager'):
                self.game.quest_manager.update_quest_progress("equip", "weapon")
            
            if self.game_log:
                self.game_log.add_message(f"Equipped {item.name}", "item")
        elif item.item_type == "armor":
            # Play equip sound - use cloth equip sounds for armor
            if audio:
                if "leather" in item.name.lower() or "cloth" in item.name.lower():
                    audio.play_sound("ui", "cloth_equip")
                else:
                    audio.play_sound("ui", "armor_equip")
            
            # Equip armor
            old_armor = self.equipped_armor
            self.equipped_armor = item
            if old_armor:
                self.inventory.add_item(old_armor)
            self.inventory.remove_item(item)
            
            # Update quest progress for equipment
            if hasattr(self, 'game') and hasattr(self.game, 'quest_manager'):
                self.game.quest_manager.update_quest_progress("equip", "armor")
            
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
        
        # Render movement target indicator and path
        if self.target_x is not None and self.target_y is not None:
            target_screen_x, target_screen_y = iso_renderer.world_to_screen(self.target_x, self.target_y, camera_x, camera_y)
            # Draw a pulsing circle at the target location
            import time
            pulse = int(abs(math.sin(time.time() * 5)) * 10) + 5
            pygame.draw.circle(screen, (255, 255, 0), (int(target_screen_x), int(target_screen_y)), pulse, 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(target_screen_x), int(target_screen_y)), 3)
            
            # Draw path if we have one
            if self.path and len(self.path) > 1:
                path_points = []
                for path_x, path_y in self.path:
                    path_screen_x, path_screen_y = iso_renderer.world_to_screen(path_x, path_y, camera_x, camera_y)
                    path_points.append((int(path_screen_x), int(path_screen_y)))
                
                # Draw path lines
                if len(path_points) > 1:
                    pygame.draw.lines(screen, (100, 255, 100), False, path_points, 2)
                
                # Draw path points
                for point in path_points:
                    pygame.draw.circle(screen, (0, 255, 0), point, 3)
        
        # Render attack indicator if attacking
        if self.attacking:
            self.render_attack(screen, screen_x, screen_y)
        
        # Render health bar
        self.render_health_bar(screen, screen_x, screen_y - 30)
        
        # Render projectile effects
        if hasattr(self, 'projectiles'):
            for projectile in self.projectiles:
                self.render_projectile_effect(screen, projectile, iso_renderer, camera_x, camera_y)
    
    def render_projectile_effect(self, screen, projectile, iso_renderer, camera_x, camera_y):
        """Render projectile effect"""
        # Convert world coordinates to screen coordinates
        start_screen_x, start_screen_y = iso_renderer.world_to_screen(projectile['start_x'], projectile['start_y'], camera_x, camera_y)
        end_screen_x, end_screen_y = iso_renderer.world_to_screen(projectile['end_x'], projectile['end_y'], camera_x, camera_y)
        
        # Calculate projectile color based on weapon type
        if "Bow" in projectile['weapon_type']:
            color = (139, 69, 19)  # Brown for arrows
        elif "Crossbow" in projectile['weapon_type']:
            color = (100, 100, 100)  # Gray for bolts
        elif "Knife" in projectile['weapon_type']:
            color = (192, 192, 192)  # Silver for knives
        elif "Staff" in projectile['weapon_type']:
            color = (138, 43, 226)  # Purple for magic
        else:
            color = (255, 255, 0)  # Yellow default
        
        # Draw projectile trail
        pygame.draw.line(screen, color, (start_screen_x, start_screen_y), (end_screen_x, end_screen_y), 3)
        
        # Add a glowing effect for magic weapons
        if "Staff" in projectile['weapon_type']:
            # Draw additional glow lines
            for i in range(1, 4):
                glow_color = (138, 43, 226, 100 - i * 25)  # Fading purple
                pygame.draw.line(screen, glow_color[:3], 
                               (start_screen_x, start_screen_y), 
                               (end_screen_x, end_screen_y), 3 + i)
    
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
        
        # Stamina bar
        pygame.draw.rect(screen, (50, 50, 100), (x - bar_width//2, y + bar_height + 1, bar_width, bar_height - 1))
        stamina_width = int((self.stamina / self.max_stamina) * bar_width)
        pygame.draw.rect(screen, (0, 100, 255), (x - bar_width//2, y + bar_height + 1, stamina_width, bar_height - 1))
    
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
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
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
        player.stamina = data.get("stamina", data.get("mana", 50))  # Backward compatibility
        player.max_stamina = data.get("max_stamina", data.get("max_mana", 50))  # Backward compatibility
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