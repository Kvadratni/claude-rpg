"""
Combat system for player character.

This module handles all combat-related functionality including:
- Attack mechanics (melee and ranged)
- Damage calculation
- Weapon handling
- Projectile effects
- Combat audio
"""

import pygame
import math
import random


class Projectile:
    """Represents a traveling projectile"""
    
    def __init__(self, start_x, start_y, target_x, target_y, weapon_type, damage, target_enemy):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.current_x = start_x
        self.current_y = start_y
        self.weapon_type = weapon_type
        self.damage = damage
        self.target_enemy = target_enemy
        
        # Calculate trajectory
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Normalize direction and set speed
        if distance > 0:
            self.velocity_x = (dx / distance) * 0.3  # Projectile speed
            self.velocity_y = (dy / distance) * 0.3
        else:
            self.velocity_x = 0
            self.velocity_y = 0
        
        self.distance_traveled = 0
        self.total_distance = distance
        self.hit = False
        self.lifetime = 60  # Maximum frames before projectile disappears
    
    def update(self):
        """Update projectile position"""
        if self.hit:
            return False
        
        # Move projectile
        self.current_x += self.velocity_x
        self.current_y += self.velocity_y
        self.distance_traveled += math.sqrt(self.velocity_x * self.velocity_x + self.velocity_y * self.velocity_y)
        
        # Check if reached target or maximum distance
        if self.distance_traveled >= self.total_distance * 0.95:  # Allow some tolerance
            self.hit = True
            return True  # Hit target
        
        # Check lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            return False  # Projectile expired
        
        return None  # Still traveling


class CombatSystem:
    """Handles all combat-related functionality for the player"""
    
    def __init__(self, player):
        """Initialize combat system with reference to player"""
        self.player = player
        
        # Combat stats (references to player stats)
        self.attack_damage = player.attack_damage
        self.attack_range = player.attack_range
        self.defense = player.defense
        
        # Projectile system
        self.projectiles = []  # Active traveling projectiles
        self.projectile_effects = []  # Visual effects (trails, impacts)
    
    def get_weapon_stamina_cost(self):
        """Get stamina cost based on equipped weapon"""
        if not self.player.equipped_weapon:
            return 6  # Unarmed attacks cost less stamina (reduced from 8)
        
        weapon_name = self.player.equipped_weapon.name
        
        # Define stamina costs for different weapon types (reduced by 20%)
        weapon_stamina_costs = {
            # Light weapons - low stamina cost
            "Silver Dagger": 5,      # was 6
            "Throwing Knife": 6,     # was 7
            
            # Medium weapons - moderate stamina cost
            "Iron Sword": 8,         # was 10
            "Bronze Mace": 9,        # was 11
            "Magic Bow": 7,          # was 9
            "Crossbow": 10,          # was 12
            
            # Heavy weapons - high stamina cost
            "Steel Axe": 12,         # was 15
            "War Hammer": 14,        # was 18
            
            # Magical weapons - variable stamina cost
            "Crystal Staff": 11,     # was 14
        }
        
        return weapon_stamina_costs.get(weapon_name, 8)  # Default to 8 if weapon not found (was 10)
    
    def attack(self, enemies, level=None):
        """Attack nearby enemies or use ranged attack"""
        # Get audio manager
        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
        
        # Check if equipped weapon is ranged
        is_ranged_weapon = False
        ranged_weapons = ["Magic Bow", "Crossbow", "Throwing Knife", "Crystal Staff"]
        
        if self.player.equipped_weapon and self.player.equipped_weapon.name in ranged_weapons:
            is_ranged_weapon = True
        
        # Check stamina cost first
        stamina_cost = self.get_weapon_stamina_cost()
        if self.player.stamina < stamina_cost:
            if self.player.game_log:
                weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else ("ranged attack" if is_ranged_weapon else "fists")
                self.player.game_log.add_message(f"Not enough stamina to attack with {weapon_name}! (Need {stamina_cost})", "combat")
            return
        
        # Consume stamina for attack
        self.player.stamina -= stamina_cost
        
        if is_ranged_weapon:
            # Ranged attack - target enemies within ranged weapon range
            self.ranged_attack(enemies, audio)
        else:
            # Melee attack - check if any enemies are in melee range first
            enemies_in_range = []
            for enemy in enemies:
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                distance = math.sqrt(dx * dx + dy * dy)
                if distance <= self.attack_range:
                    enemies_in_range.append(enemy)
            
            if enemies_in_range:
                self.melee_attack(enemies_in_range, audio)
            else:
                # No enemies in range - try to move to closest enemy
                closest_enemy = None
                closest_distance = float('inf')
                
                for enemy in enemies:
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    distance = math.sqrt(dx * dx + dy * dy)
                    if distance < closest_distance:
                        closest_enemy = enemy
                        closest_distance = distance
                
                if closest_enemy and closest_distance <= 5.0 and level:  # Only auto-move if enemy is reasonably close and we have level
                    # Move towards the closest enemy
                    target_tile_x = int(closest_enemy.x)
                    target_tile_y = int(closest_enemy.y)
                    
                    # Try to get adjacent to the enemy
                    if hasattr(self.player, 'movement_system'):
                        self.player.movement_system._move_to_tile(target_tile_x, target_tile_y, level)
                        if self.player.game_log:
                            self.player.game_log.add_message(f"Moving closer to {closest_enemy.name}...", "combat")
                else:
                    if self.player.game_log:
                        self.player.game_log.add_message("No enemies in melee range!", "combat")
    
    def melee_attack(self, enemies, audio):
        """Perform melee attack on nearby enemies"""
        for enemy in enemies[:]:
            # Calculate distance to enemy
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if enemy is within attack range (circular area around player)
            if distance <= self.attack_range:
                # Calculate base damage (unarmed combat)
                base_damage = 15  # Base unarmed damage
                damage = base_damage
                
                # Add weapon bonus if equipped
                if self.player.equipped_weapon:
                    damage += self.player.equipped_weapon.effect.get("damage", 0)
                    # Play weapon-specific sound
                    if audio:
                        if 'axe' in self.player.equipped_weapon.name.lower():
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
                    if self.player.game_log:
                        self.player.game_log.add_message(f"Enemy {enemy.name} defeated!", "combat")
                    # Experience is handled in the level class
                
                # Show different attack messages for armed vs unarmed
                if self.player.equipped_weapon:
                    if self.player.game_log:
                        self.player.game_log.add_message(f"Hit with {self.player.equipped_weapon.name} for {damage} damage!", "combat")
                else:
                    if self.player.game_log:
                        self.player.game_log.add_message(f"Punched for {damage} damage!", "combat")
                
                # Trigger combat music when player attacks
                if audio and not audio.is_combat_music_active():
                    audio.start_combat_music()
    
    def ranged_attack(self, enemies, audio):
        """Perform ranged attack on enemies within range"""
        # Different ranges for different ranged weapons
        ranged_attack_range = 8.0  # Default range
        
        if self.player.equipped_weapon:
            weapon_name = self.player.equipped_weapon.name
            if "Magic Bow" in weapon_name:
                ranged_attack_range = 10.0  # Longest range
            elif "Crossbow" in weapon_name:
                ranged_attack_range = 9.0   # Long range, high damage
            elif "Crystal Staff" in weapon_name:
                ranged_attack_range = 7.0   # Medium range, magical
            elif "Throwing Knife" in weapon_name:
                ranged_attack_range = 6.0   # Shorter range, fast
        
        # Find target enemy (closest enemy within range)
        target_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= ranged_attack_range and distance < closest_distance:
                target_enemy = enemy
                closest_distance = distance
        
        if target_enemy:
            # Calculate damage based on weapon type
            base_damage = 12  # Base ranged damage
            damage = base_damage
            
            weapon_type = "arrow"  # Default projectile type
            
            if self.player.equipped_weapon:
                damage += self.player.equipped_weapon.effect.get("damage", 0)
                weapon_type = self.player.equipped_weapon.name
                
                # Weapon-specific damage bonuses
                if "Magic Bow" in weapon_type:
                    damage += 3  # Magic bow bonus
                elif "Crossbow" in weapon_type:
                    damage += 5  # Crossbow hits hard
                elif "Crystal Staff" in weapon_type:
                    damage += 2  # Magic damage
                    # Staff also has spell power bonus
                    spell_power = self.player.equipped_weapon.effect.get("spell_power", 0)
                    damage += spell_power // 2
                
                # Play weapon-specific sound
                if audio:
                    if "Bow" in self.player.equipped_weapon.name:
                        # Use weapon draw sound as bow string sound
                        audio.play_combat_sound("weapon_draw")
                    elif "Crossbow" in self.player.equipped_weapon.name:
                        # Use blade slice as crossbow release sound
                        audio.play_combat_sound("blade_slice")
                    elif "Throwing Knife" in self.player.equipped_weapon.name:
                        # Use blade slice for throwing knife
                        audio.play_combat_sound("blade_slice")
                    elif "Crystal Staff" in self.player.equipped_weapon.name:
                        # Use magic sound for staff
                        audio.play_magic_sound("spell_cast")
                    else:
                        audio.play_combat_sound("weapon_draw")  # Fallback
            
            # Random damage variation
            damage += random.randint(-2, 2)
            
            # Create traveling projectile with weapon-specific speed
            projectile_speed = 0.3  # Default speed
            if self.player.equipped_weapon:
                if "Throwing Knife" in weapon_type:
                    projectile_speed = 0.5  # Knives are faster
                elif "Crossbow" in weapon_type:
                    projectile_speed = 0.4  # Bolts are fast
                elif "Crystal Staff" in weapon_type:
                    projectile_speed = 0.25  # Magic is slower but tracking
            
            projectile = Projectile(
                self.player.x, self.player.y,
                target_enemy.x, target_enemy.y,
                weapon_type, damage, target_enemy
            )
            # Override speed for specific weapons
            if projectile_speed != 0.3:
                distance = math.sqrt((target_enemy.x - self.player.x)**2 + (target_enemy.y - self.player.y)**2)
                if distance > 0:
                    projectile.velocity_x = ((target_enemy.x - self.player.x) / distance) * projectile_speed
                    projectile.velocity_y = ((target_enemy.y - self.player.y) / distance) * projectile_speed
            
            self.projectiles.append(projectile)
            
            if self.player.game_log:
                weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "ranged attack"
                self.player.game_log.add_message(f"Fired {weapon_name} at {target_enemy.name}!", "combat")
            
            # Trigger combat music when player attacks
            if audio and not audio.is_combat_music_active():
                audio.start_combat_music()
        else:
            if self.player.game_log:
                weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "ranged weapon"
                self.player.game_log.add_message(f"No enemies in {weapon_name} range! (Range: {ranged_attack_range:.1f})", "combat")

    
    def take_damage(self, damage):
        """Take damage"""
        # Get audio manager
        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
        
        # Apply defense reduction
        defense = self.player.defense
        if self.player.equipped_armor:
            defense += self.player.equipped_armor.effect.get("defense", 0)
        
        actual_damage = max(1, damage - defense)
        self.player.health = max(0, self.player.health - actual_damage)
        
        # Play hurt sound
        if audio:
            audio.play_combat_sound("blade_slice")  # Use blade slice as hurt sound
        
        if self.player.game_log:
            self.player.game_log.add_message(f"Player takes {actual_damage} damage! ({self.player.health}/{self.player.max_health})", "combat")
        
        return self.player.health <= 0  # Return True if player died
    
    def update(self):
        """Update combat system (projectile effects, etc.)"""
        # Update traveling projectiles
        for projectile in self.projectiles[:]:
            result = projectile.update()
            
            if result is True:  # Projectile hit target
                # Apply damage to target
                if projectile.target_enemy.take_damage(projectile.damage):
                    if self.player.game_log:
                        self.player.game_log.add_message(f"Enemy {projectile.target_enemy.name} defeated!", "combat")
                
                if self.player.game_log:
                    weapon_name = projectile.weapon_type if projectile.weapon_type != "arrow" else "ranged attack"
                    self.player.game_log.add_message(f"Hit {projectile.target_enemy.name} with {weapon_name} for {projectile.damage} damage!", "combat")
                
                # Create impact effect
                self.create_impact_effect(projectile)
                
                # Remove projectile
                self.projectiles.remove(projectile)
                
            elif result is False:  # Projectile expired or missed
                # Remove projectile
                self.projectiles.remove(projectile)
        
        # Update visual effects
        for effect in self.projectile_effects[:]:
            effect['timer'] -= 1
            if effect['timer'] <= 0:
                self.projectile_effects.remove(effect)
    
    def create_impact_effect(self, projectile):
        """Create visual impact effect when projectile hits"""
        impact_effect = {
            'x': projectile.current_x,
            'y': projectile.current_y,
            'weapon_type': projectile.weapon_type,
            'timer': 20,  # Show impact for 20 frames
            'type': 'impact'
        }
        self.projectile_effects.append(impact_effect)
    
    def render_projectile_effects(self, screen, iso_renderer, camera_x, camera_y):
        """Render projectile effects"""
        # Render traveling projectiles
        for projectile in self.projectiles:
            self.render_projectile(screen, projectile, iso_renderer, camera_x, camera_y)
        
        # Render visual effects (impacts, trails)
        for effect in self.projectile_effects:
            self.render_effect(screen, effect, iso_renderer, camera_x, camera_y)
    
    def render_projectile(self, screen, projectile, iso_renderer, camera_x, camera_y):
        """Render a traveling projectile"""
        # Convert world coordinates to screen coordinates
        screen_x, screen_y = iso_renderer.world_to_screen(projectile.current_x, projectile.current_y, camera_x, camera_y)
        
        # Calculate projectile appearance based on weapon type
        if "Bow" in projectile.weapon_type:
            # Draw arrow
            color = (139, 69, 19)  # Brown for arrows
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 3)
            # Draw arrow fletching
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 2)
        elif "Crossbow" in projectile.weapon_type:
            # Draw crossbow bolt
            color = (100, 100, 100)  # Gray for bolts
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 2)
        elif "Knife" in projectile.weapon_type:
            # Draw spinning knife
            color = (192, 192, 192)  # Silver for knives
            # Create spinning effect
            angle = (projectile.distance_traveled * 10) % 360
            offset = 4
            x1 = screen_x + math.cos(math.radians(angle)) * offset
            y1 = screen_y + math.sin(math.radians(angle)) * offset
            x2 = screen_x - math.cos(math.radians(angle)) * offset
            y2 = screen_y - math.sin(math.radians(angle)) * offset
            pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 3)
        elif "Staff" in projectile.weapon_type:
            # Draw magic projectile with glowing effect
            color = (138, 43, 226)  # Purple for magic
            # Draw multiple circles for glow effect
            for i in range(3, 0, -1):
                alpha = 100 - (i * 20)
                glow_color = (*color, alpha)
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), i * 2)
        else:
            # Default projectile
            color = (255, 255, 0)  # Yellow default
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 2)
    
    def render_effect(self, screen, effect, iso_renderer, camera_x, camera_y):
        """Render visual effects"""
        screen_x, screen_y = iso_renderer.world_to_screen(effect['x'], effect['y'], camera_x, camera_y)
        
        if effect['type'] == 'impact':
            # Draw impact explosion
            size = max(1, effect['timer'] // 2)
            
            if "Bow" in effect['weapon_type']:
                color = (255, 200, 0)  # Orange impact
            elif "Crossbow" in effect['weapon_type']:
                color = (255, 255, 255)  # White impact
            elif "Knife" in effect['weapon_type']:
                color = (255, 100, 100)  # Red impact
            elif "Staff" in effect['weapon_type']:
                color = (200, 100, 255)  # Purple magic impact
            else:
                color = (255, 255, 0)  # Yellow default
            
            # Draw impact burst
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), size)
            
            # Draw impact sparks for non-magic weapons
            if "Staff" not in effect['weapon_type']:
                for i in range(4):
                    angle = (i * 90 + effect['timer'] * 20) % 360
                    spark_x = screen_x + math.cos(math.radians(angle)) * size * 2
                    spark_y = screen_y + math.sin(math.radians(angle)) * size * 2
                    pygame.draw.circle(screen, color, (int(spark_x), int(spark_y)), 1)