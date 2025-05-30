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


class CombatSystem:
    """Handles all combat-related functionality for the player"""
    
    def __init__(self, player):
        """Initialize combat system with reference to player"""
        self.player = player
        
        # Combat stats (references to player stats)
        self.attack_damage = player.attack_damage
        self.attack_range = player.attack_range
        self.defense = player.defense
        
        # Projectile effects storage
        self.projectiles = []
    
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
    
    def attack(self, enemies):
        """Attack nearby enemies or use ranged attack"""
        # Check if player has enough stamina to attack
        stamina_cost = self.get_weapon_stamina_cost()
        if self.player.stamina < stamina_cost:
            if self.player.game_log:
                weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "fists"
                self.player.game_log.add_message(f"Not enough stamina to attack with {weapon_name}! (Need {stamina_cost})", "combat")
            return
        
        # Get audio manager
        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
        
        # Consume stamina
        self.player.stamina -= stamina_cost
        
        # Check if equipped weapon is ranged
        is_ranged_weapon = False
        ranged_weapons = ["Magic Bow", "Crossbow", "Throwing Knife", "Crystal Staff"]
        
        if self.player.equipped_weapon and self.player.equipped_weapon.name in ranged_weapons:
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
        ranged_attack_range = 8.0  # Much longer range for ranged weapons
        
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
            # Calculate damage
            base_damage = 12  # Base ranged damage
            damage = base_damage
            
            if self.player.equipped_weapon:
                damage += self.player.equipped_weapon.effect.get("damage", 0)
                
                # Play weapon-specific sound
                if audio:
                    if "Bow" in self.player.equipped_weapon.name:
                        audio.play_combat_sound("bow_shot")  # We'll need to add this sound
                    elif "Crossbow" in self.player.equipped_weapon.name:
                        audio.play_combat_sound("crossbow_shot")  # We'll need to add this sound
                    elif "Throwing Knife" in self.player.equipped_weapon.name:
                        audio.play_combat_sound("blade_slice")  # Use existing blade sound
                    elif "Crystal Staff" in self.player.equipped_weapon.name:
                        audio.play_magic_sound("spell_cast")  # Use magic sound for staff
                    else:
                        audio.play_combat_sound("weapon_hit")  # Fallback
            
            # Random damage variation
            damage += random.randint(-2, 2)
            
            # Create projectile effect (visual)
            self.create_projectile_effect(target_enemy)
            
            # Apply damage
            if target_enemy.take_damage(damage):
                if self.player.game_log:
                    self.player.game_log.add_message(f"Enemy {target_enemy.name} defeated!", "combat")
            
            if self.player.game_log:
                weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "ranged attack"
                self.player.game_log.add_message(f"Hit {target_enemy.name} with {weapon_name} for {damage} damage!", "combat")
            
            # Trigger combat music when player attacks
            if audio and not audio.is_combat_music_active():
                audio.start_combat_music()
        else:
            if self.player.game_log:
                self.player.game_log.add_message("No enemies in ranged attack range!", "combat")
    
    def create_projectile_effect(self, target_enemy):
        """Create a visual projectile effect (placeholder for now)"""
        # For now, we'll just add a visual indicator
        # In a more advanced implementation, we could create actual projectile entities
        # that travel from player to target
        
        projectile = {
            'start_x': self.player.x,
            'start_y': self.player.y,
            'end_x': target_enemy.x,
            'end_y': target_enemy.y,
            'timer': 30,  # Show effect for 30 frames (0.5 seconds at 60 FPS)
            'weapon_type': self.player.equipped_weapon.name if self.player.equipped_weapon else "arrow"
        }
        
        self.projectiles.append(projectile)
    
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
        # Update projectile effects
        for projectile in self.projectiles[:]:
            projectile['timer'] -= 1
            if projectile['timer'] <= 0:
                self.projectiles.remove(projectile)
    
    def render_projectile_effects(self, screen, iso_renderer, camera_x, camera_y):
        """Render projectile effects"""
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