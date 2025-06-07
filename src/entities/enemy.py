"""
Enemy entities for the RPG
"""

import pygame
import math
import random
from .base import Entity

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
        
        # AI properties - speed varies by enemy type
        self.speed = self.get_enemy_speed()
        self.detection_range = 6 if not is_boss else 8
        self.attack_range = 1.0  # Exactly 1 tile for melee attacks
        self.attack_cooldown = 0
        self.max_attack_cooldown = 60 if not is_boss else 40
        
        # State
        self.state = "idle"  # idle, chasing, attacking, fleeing
        self.target = None
        self.path = []
        self.direction = 3  # 0=down, 1=left, 2=up, 3=right (start facing right)
        
        # Create enemy sprite
        self.create_enemy_sprite()
    
    def get_enemy_speed(self):
        """Get movement speed based on enemy type"""
        # Speed categories:
        # Very Fast: 0.035-0.04 (agile creatures)
        # Fast: 0.025-0.03 (quick enemies)
        # Normal: 0.018-0.022 (standard enemies)
        # Slow: 0.012-0.016 (heavy/tanky enemies)
        # Very Slow: 0.008-0.012 (bosses/massive creatures)
        
        speed_table = {
            # Fast, agile enemies
            "Forest Sprite": 0.095,      # Very fast magical creature
            "Bandit Scout": 0.080,       # Quick and nimble
            "Goblin": 0.070,             # Fast and aggressive
            "Forest Goblin": 0.065,      # Slightly slower in forest
            
            # Normal speed enemies
            "Giant Scorpion": 0.055,     # Decent speed with claws
            "Crystal Elemental": 0.050,  # Magical floating movement
            "Orc Warrior": 0.048,        # Armored but mobile
            "Fire Drake": 0.045,         # Flying but cautious
            
            # Slow, heavy enemies
            "Ancient Guardian": 0.040,   # Skeletal, deliberate movement
            "Swamp Troll": 0.035,       # Large and lumbering
            
            # Boss enemies (slow but powerful)
            "Orc Warlord": 0.030,       # Heavy armor, commanding presence
            "Ancient Dragon": 0.025,     # Massive, deliberate movements
        }
        
        # Get speed for this enemy type, with fallback for unknown types
        base_speed = speed_table.get(self.name, 0.050)  # Default to normal speed
        
        # Apply boss modifier if needed (some bosses already have their speed set above)
        if self.is_boss and self.name not in speed_table:
            base_speed *= 0.6  # Bosses are generally 40% slower
        
        # Add small random variation (±10%) to make each enemy unique
        speed_variation = random.uniform(0.9, 1.1)
        final_speed = base_speed * speed_variation
        
        return final_speed
    
    def apply_movement_style(self, move_x, move_y, dx, dy, distance):
        """Apply enemy-specific movement patterns and behaviors"""
        # Different enemies have different movement styles
        
        if "Sprite" in self.name:
            # Forest Sprites: Erratic, darting movement
            if random.random() < 0.3:  # 30% chance to dart sideways
                # Add perpendicular movement
                perp_x = -dy / distance * self.speed * 0.5
                perp_y = dx / distance * self.speed * 0.5
                move_x += perp_x
                move_y += perp_y
        
        elif "Goblin" in self.name:
            # Goblins: Aggressive, direct approach with occasional zigzag
            if random.random() < 0.2:  # 20% chance to zigzag
                move_x *= 1.2  # Burst of speed
                move_y *= 1.2
        
        elif "Bandit" in self.name:
            # Bandits: Try to circle around the player
            if distance > 3:  # Only when not too close
                # Add circular movement component
                angle_offset = math.pi / 4  # 45 degrees
                circle_x = math.cos(math.atan2(dy, dx) + angle_offset) * self.speed * 0.3
                circle_y = math.sin(math.atan2(dy, dx) + angle_offset) * self.speed * 0.3
                move_x += circle_x
                move_y += circle_y
        
        elif "Scorpion" in self.name:
            # Scorpions: Side-stepping movement, like real scorpions
            if random.random() < 0.4:  # 40% chance to sidestep
                # Add perpendicular movement
                perp_x = -dy / distance * self.speed * 0.4
                perp_y = dx / distance * self.speed * 0.4
                move_x += perp_x
                move_y += perp_y
        
        elif "Troll" in self.name or "Guardian" in self.name:
            # Large enemies: Steady, unstoppable movement
            # No modifications - they move straight and steady
            pass
        
        elif "Dragon" in self.name or "Drake" in self.name:
            # Flying enemies: Smooth, swooping movement
            if hasattr(self, 'swoop_counter'):
                self.swoop_counter += 1
            else:
                self.swoop_counter = 0
            
            # Add sine wave movement for swooping effect
            swoop_offset = math.sin(self.swoop_counter * 0.1) * 0.01
            move_x += swoop_offset
            move_y += swoop_offset
        
        elif "Elemental" in self.name:
            # Elementals: Floating, oscillating movement
            if hasattr(self, 'float_counter'):
                self.float_counter += 1
            else:
                self.float_counter = 0
            
            # Add floating oscillation
            float_x = math.sin(self.float_counter * 0.15) * 0.008
            float_y = math.cos(self.float_counter * 0.15) * 0.008
            move_x += float_x
            move_y += float_y
        
        elif self.is_boss:
            # Bosses: Powerful, deliberate movement with occasional charges
            if random.random() < 0.05:  # 5% chance to charge
                move_x *= 2.0  # Double speed charge
                move_y *= 2.0
        
        return move_x, move_y
    
    def create_enemy_sprite(self):
        """Create enemy sprite with support for all new enemy types"""
        size = 60 if self.is_boss else 48  # Increased sizes - boss 60, regular 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            # Map enemy names to sprite assets
            sprite_mappings = {
                # Existing enemies
                "Orc Warlord": "orc_boss_sprite",
                "Orc Boss": "orc_boss_sprite",
                "Goblin": "goblin_sprite",
                "Forest Goblin": "goblin_sprite",
                "Bandit Scout": "bandit_scout",
                # New enemies
                "Forest Sprite": "forest_sprite",
                "Ancient Guardian": "ancient_guardian",
                "Orc Warrior": "orc_warrior", 
                "Ancient Dragon": "ancient_dragon",
                "Fire Drake": "fire_drake",
                "Crystal Elemental": "crystal_elemental",
                "Giant Scorpion": "giant_scorpion",
                "Swamp Troll": "swamp_troll"
            }
            
            sprite_name = sprite_mappings.get(self.name)
            if sprite_name:
                enemy_image = self.asset_loader.get_image(sprite_name)
                if enemy_image:
                    # Create base sprite
                    self.sprite = pygame.transform.scale(enemy_image, (size, size))
                    # Create direction sprites - mirror for right movement
                    self.direction_sprites = [
                        self.sprite,  # Down (0)
                        self.sprite,  # Left (1) - original (facing left)
                        self.sprite,  # Up (2)
                        pygame.transform.flip(self.sprite, True, False)   # Right (3) - mirrored
                    ]
                    return
        
        # Fallback to generated sprite with unique styles for each enemy type
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors and features for different enemies
        enemy_styles = {
            # Existing enemies
            "Orc Warlord": {"color": (139, 0, 0), "eye_color": (255, 0, 0), "feature": "crown"},  # Dark red with crown
            "Orc Boss": {"color": (139, 0, 0), "eye_color": (255, 0, 0), "feature": "crown"},
            "Goblin": {"color": (0, 100, 0), "eye_color": (255, 255, 0), "feature": "ears"},  # Dark green with yellow eyes
            "Forest Goblin": {"color": (34, 139, 34), "eye_color": (255, 255, 0), "feature": "ears"},  # Forest green
            "Bandit Scout": {"color": (101, 67, 33), "eye_color": (255, 0, 0), "feature": "mask"},  # Brown with mask
            # New enemies
            "Forest Sprite": {"color": (50, 205, 50), "eye_color": (255, 255, 255), "feature": "glow"},  # Lime green with glow
            "Ancient Guardian": {"color": (245, 245, 220), "eye_color": (255, 0, 0), "feature": "bones"},  # Beige skeleton with red eyes
            "Orc Warrior": {"color": (139, 69, 19), "eye_color": (255, 165, 0), "feature": "tusks"},  # Brown with orange eyes
            "Ancient Dragon": {"color": (128, 0, 128), "eye_color": (255, 215, 0), "feature": "scales"},  # Purple with gold eyes
            "Fire Drake": {"color": (255, 69, 0), "eye_color": (255, 255, 0), "feature": "flames"},  # Red-orange with yellow eyes
            "Crystal Elemental": {"color": (173, 216, 230), "eye_color": (0, 191, 255), "feature": "crystals"},  # Light blue with blue eyes
            "Giant Scorpion": {"color": (160, 82, 45), "eye_color": (255, 0, 0), "feature": "claws"},  # Saddle brown with red eyes
            "Swamp Troll": {"color": (85, 107, 47), "eye_color": (255, 255, 0), "feature": "moss"}  # Dark olive green with yellow eyes
        }
        
        # Get style for this enemy, default to generic style
        style = enemy_styles.get(self.name, {
            "color": (139, 69, 19) if not self.is_boss else (139, 0, 0), 
            "eye_color": (255, 0, 0), 
            "feature": "none"
        })
        
        # Draw enemy body
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, style["color"], center, size // 3)
        
        # Draw eyes
        eye_size = 6 if self.is_boss else 5
        pygame.draw.circle(self.sprite, style["eye_color"], (center[0] - 9, center[1] - 6), eye_size)
        pygame.draw.circle(self.sprite, style["eye_color"], (center[0] + 9, center[1] - 6), eye_size)
        
        # Draw border
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Thicker border
        
        # Add special features based on enemy type
        feature = style["feature"]
        
        if feature == "crown":
            # Boss crown
            crown_points = [
                (center[0] - 15, center[1] - size//3),
                (center[0] - 8, center[1] - size//3 - 12),
                (center[0], center[1] - size//3 - 18),
                (center[0] + 8, center[1] - size//3 - 12),
                (center[0] + 15, center[1] - size//3)
            ]
            pygame.draw.polygon(self.sprite, (255, 215, 0), crown_points)
        elif feature == "ears":
            # Goblin ears
            pygame.draw.ellipse(self.sprite, style["color"], (center[0] - 20, center[1] - 10, 8, 15))  # Left ear
            pygame.draw.ellipse(self.sprite, style["color"], (center[0] + 12, center[1] - 10, 8, 15))  # Right ear
        elif feature == "mask":
            # Bandit mask
            pygame.draw.ellipse(self.sprite, (0, 0, 0), (center[0] - 12, center[1] - 8, 24, 10))
        elif feature == "glow":
            # Forest sprite glow effect
            glow_surface = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (50, 255, 50, 100), (size//2 + 5, size//2 + 5), size//2 + 5)
            self.sprite.blit(glow_surface, (-5, -5), special_flags=pygame.BLEND_ALPHA_SDL2)
        elif feature == "bones":
            # Skeleton bones
            pygame.draw.line(self.sprite, (255, 255, 255), (center[0] - 8, center[1] + 5), (center[0] + 8, center[1] + 5), 2)
            pygame.draw.line(self.sprite, (255, 255, 255), (center[0], center[1] - 5), (center[0], center[1] + 10), 2)
        elif feature == "tusks":
            # Orc tusks
            pygame.draw.polygon(self.sprite, (255, 255, 255), [(center[0] - 6, center[1] + 2), (center[0] - 4, center[1] + 8), (center[0] - 2, center[1] + 2)])
            pygame.draw.polygon(self.sprite, (255, 255, 255), [(center[0] + 2, center[1] + 2), (center[0] + 4, center[1] + 8), (center[0] + 6, center[1] + 2)])
        elif feature == "scales":
            # Dragon scales
            for i in range(3):
                for j in range(3):
                    scale_x = center[0] - 6 + i * 6
                    scale_y = center[1] - 6 + j * 6
                    pygame.draw.circle(self.sprite, (148, 0, 211), (scale_x, scale_y), 2)
        elif feature == "flames":
            # Fire drake flames
            flame_points = [
                (center[0] - 8, center[1] + 8), (center[0] - 4, center[1] + 12), 
                (center[0], center[1] + 8), (center[0] + 4, center[1] + 12), 
                (center[0] + 8, center[1] + 8)
            ]
            pygame.draw.polygon(self.sprite, (255, 140, 0), flame_points)
        elif feature == "crystals":
            # Crystal formations
            crystal_points = [
                (center[0] - 8, center[1] - 8), (center[0] - 6, center[1] - 12), (center[0] - 4, center[1] - 8),
                (center[0] + 4, center[1] - 8), (center[0] + 6, center[1] - 12), (center[0] + 8, center[1] - 8)
            ]
            for i in range(0, len(crystal_points), 3):
                if i + 2 < len(crystal_points):
                    pygame.draw.polygon(self.sprite, (135, 206, 235), crystal_points[i:i+3])
        elif feature == "claws":
            # Scorpion claws
            pygame.draw.ellipse(self.sprite, (139, 69, 19), (center[0] - 18, center[1] - 2, 12, 8))  # Left claw
            pygame.draw.ellipse(self.sprite, (139, 69, 19), (center[0] + 6, center[1] - 2, 12, 8))   # Right claw
        elif feature == "moss":
            # Swamp troll moss
            for _ in range(5):
                moss_x = center[0] + random.randint(-10, 10)
                moss_y = center[1] + random.randint(-10, 10)
                pygame.draw.circle(self.sprite, (124, 252, 0), (moss_x, moss_y), 2)
        
        # Create direction sprites for generated sprites - mirror for left movement
        self.direction_sprites = [
            self.sprite,  # Down (0)
            pygame.transform.flip(self.sprite, True, False),  # Left (1) - mirrored
            self.sprite,  # Up (2)
            self.sprite   # Right (3) - original
        ]
    
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
                    
                    # Apply enemy-specific movement modifiers
                    move_x, move_y = self.apply_movement_style(move_x, move_y, dx, dy, distance)
                    
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
                            
                            # Update direction based on movement
                            if abs(dx) > abs(dy):
                                self.direction = 3 if dx > 0 else 1  # Right or Left
                            else:
                                self.direction = 0 if dy > 0 else 2  # Down or Up
        else:
            self.state = "idle"
            # Random movement when idle - speed affects idle movement frequency
            idle_chance = 0.005 + (self.speed * 0.2)  # Faster enemies move more when idle
            if random.random() < idle_chance:
                # Idle movement distance based on enemy speed
                idle_speed = self.speed * 0.3  # 30% of combat speed for idle movement
                move_x = random.uniform(-idle_speed, idle_speed)
                move_y = random.uniform(-idle_speed, idle_speed)
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                    self.x = new_x
                    self.y = new_y
                    
                    # Update direction based on idle movement
                    if abs(move_x) > abs(move_y):
                        self.direction = 3 if move_x > 0 else 1  # Right or Left
                    else:
                        self.direction = 0 if move_y > 0 else 2  # Down or Up
    
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
    
    def render(self, screen, camera_x, camera_y, iso_renderer):
        """Render the enemy with direction-based sprite"""
        # Use direction-based sprite if available
        if hasattr(self, 'direction_sprites') and self.direction_sprites:
            current_sprite = self.direction_sprites[self.direction]
        else:
            current_sprite = self.sprite
            
        if current_sprite:
            screen_x, screen_y = iso_renderer.world_to_screen(self.x, self.y, camera_x, camera_y)
            
            # Regular entities
            sprite_rect = current_sprite.get_rect()
            sprite_rect.center = (screen_x, screen_y - 16)
            
            screen.blit(current_sprite, sprite_rect)
        
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


class RangedEnemy(Enemy):
    """Ranged enemy that can attack from distance"""
    
    def __init__(self, x, y, name, health=50, damage=10, experience=25, is_boss=False, asset_loader=None, weapon_type="bow"):
        # Set weapon_type first before calling super().__init__
        self.weapon_type = weapon_type
        
        super().__init__(x, y, name, health, damage, experience, is_boss, asset_loader)
        
        # Ranged combat properties
        self.ranged_attack_range = self.get_weapon_range()
        self.ranged_attack_cooldown = 0
        self.max_ranged_attack_cooldown = self.get_weapon_cooldown()
        self.projectiles = []  # Enemy projectiles
        
        # Ranged enemies prefer to keep distance
        self.preferred_distance = self.ranged_attack_range * 0.7  # Stay at 70% of max range
        self.min_distance = 3.0  # Don't get too close to player
        
        # Override attack range for ranged enemies (they can attack from much further)
        self.attack_range = self.ranged_attack_range
        
        # Ranged enemies are typically more cautious
        self.detection_range = max(self.detection_range, self.ranged_attack_range + 2)
    
    def get_weapon_range(self):
        """Get attack range based on weapon type"""
        weapon_ranges = {
            "bow": 8.0,
            "crossbow": 9.0,
            "magic_staff": 7.0,
            "throwing_knife": 5.0,
            "dark_magic": 6.0
        }
        return weapon_ranges.get(self.weapon_type, 7.0)
    
    def get_weapon_cooldown(self):
        """Get attack cooldown based on weapon type"""
        weapon_cooldowns = {
            "bow": 90,          # 1.5 seconds at 60 FPS
            "crossbow": 120,    # 2 seconds (slower but more damage)
            "magic_staff": 100, # 1.67 seconds
            "throwing_knife": 60, # 1 second (fast)
            "dark_magic": 110   # 1.83 seconds
        }
        return weapon_cooldowns.get(self.weapon_type, 90)
    
    def create_enemy_sprite(self):
        """Create ranged enemy sprite"""
        size = 60 if self.is_boss else 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            sprite_mappings = {
                "Goblin Archer": "goblin_archer",
                "Orc Crossbow": "orc_crossbow", 
                "Skeleton Archer": "skeleton_archer",
                "Dark Mage": "dark_mage",
                # Boss variants
                "Goblin Archer Chief": "goblin_archer",
                "Orc Crossbow Captain": "orc_crossbow",
                "Lich": "dark_mage"
            }
            
            sprite_name = sprite_mappings.get(self.name)
            if sprite_name:
                enemy_image = self.asset_loader.get_image(sprite_name)
                if enemy_image:
                    self.sprite = pygame.transform.scale(enemy_image, (size, size))
                    self.direction_sprites = [
                        self.sprite,  # Down (0)
                        self.sprite,  # Left (1) - original (facing left)
                        self.sprite,  # Up (2)
                        pygame.transform.flip(self.sprite, True, False)   # Right (3) - mirrored
                    ]
                    return
        
        # Fallback to generated sprite
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different ranged enemy types
        enemy_styles = {
            "Goblin Archer": {"color": (0, 120, 0), "eye_color": (255, 255, 0), "weapon_color": (139, 69, 19)},
            "Orc Crossbow": {"color": (139, 69, 19), "eye_color": (255, 0, 0), "weapon_color": (101, 67, 33)},
            "Skeleton Archer": {"color": (245, 245, 220), "eye_color": (255, 0, 0), "weapon_color": (220, 220, 190)},
            "Dark Mage": {"color": (75, 0, 130), "eye_color": (138, 43, 226), "weapon_color": (139, 69, 19)},
            # Boss variants
            "Goblin Archer Chief": {"color": (0, 100, 0), "eye_color": (255, 215, 0), "weapon_color": (139, 69, 19)},
            "Orc Crossbow Captain": {"color": (139, 0, 0), "eye_color": (255, 0, 0), "weapon_color": (101, 67, 33)},
            "Lich": {"color": (25, 25, 112), "eye_color": (0, 255, 255), "weapon_color": (139, 69, 19)}
        }
        
        style = enemy_styles.get(self.name, {
            "color": (139, 69, 19), 
            "eye_color": (255, 0, 0), 
            "weapon_color": (139, 69, 19)
        })
        
        center = (size // 2, size // 2)
        
        # Draw enemy body
        pygame.draw.circle(self.sprite, style["color"], center, size // 3)
        
        # Draw eyes
        eye_size = 6 if self.is_boss else 5
        pygame.draw.circle(self.sprite, style["eye_color"], (center[0] - 9, center[1] - 6), eye_size)
        pygame.draw.circle(self.sprite, style["eye_color"], (center[0] + 9, center[1] - 6), eye_size)
        
        # Draw weapon based on type
        if self.weapon_type in ["bow", "crossbow"]:
            # Draw bow/crossbow
            weapon_rect = pygame.Rect(center[0] - 20, center[1] - 5, 15, 3)
            pygame.draw.rect(self.sprite, style["weapon_color"], weapon_rect)
            # Draw string
            pygame.draw.line(self.sprite, (255, 255, 255), 
                           (center[0] - 20, center[1] - 3), 
                           (center[0] - 20, center[1] + 3), 1)
        elif self.weapon_type in ["magic_staff", "dark_magic"]:
            # Draw staff
            pygame.draw.line(self.sprite, style["weapon_color"], 
                           (center[0] - 18, center[1] + 10), 
                           (center[0] - 15, center[1] - 8), 3)
            # Draw crystal/orb at top
            pygame.draw.circle(self.sprite, style["eye_color"], (center[0] - 15, center[1] - 8), 4)
        
        # Draw border
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)
        
        # Create direction sprites
        self.direction_sprites = [
            self.sprite,  # Down (0)
            self.sprite,  # Left (1) - original
            self.sprite,  # Up (2)
            pygame.transform.flip(self.sprite, True, False)   # Right (3) - mirrored
        ]
    
    def update(self, level, player):
        """Update ranged enemy AI"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.ranged_attack_cooldown > 0:
            self.ranged_attack_cooldown -= 1
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            result = projectile.update()
            if result is True:  # Hit target
                # Apply damage to player
                if hasattr(player, 'combat_system'):
                    player.combat_system.take_damage(projectile.damage)
                else:
                    # Fallback damage application
                    player.health = max(0, player.health - projectile.damage)
                
                self.projectiles.remove(projectile)
            elif result is False:  # Projectile expired
                self.projectiles.remove(projectile)
        
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # AI state machine for ranged enemies
        if distance < self.detection_range:
            # Play detection sound only when first seeing the player
            if self.state == "idle":
                audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
                if audio:
                    if "Goblin" in self.name:
                        audio.play_creature_sound("goblin")
                    elif "Orc" in self.name:
                        audio.play_creature_sound("orc", "voice")
            
            # Ranged enemy behavior
            if distance <= self.ranged_attack_range and distance >= self.min_distance:
                # In optimal range - attack if possible
                self.state = "attacking"
                if self.ranged_attack_cooldown <= 0:
                    self.ranged_attack_player(player)
                    self.ranged_attack_cooldown = self.max_ranged_attack_cooldown
            elif distance < self.min_distance:
                # Too close - back away while trying to attack
                self.state = "retreating"
                # Move away from player
                if distance > 0:
                    move_x = -(dx / distance) * self.speed * 1.2  # Move away faster
                    move_y = -(dy / distance) * self.speed * 1.2
                    
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                        self.x = new_x
                        self.y = new_y
                        
                        # Update direction based on movement
                        if abs(move_x) > abs(move_y):
                            self.direction = 3 if move_x > 0 else 1
                        else:
                            self.direction = 0 if move_y > 0 else 2
                
                # Still try to attack while retreating
                if self.ranged_attack_cooldown <= 0:
                    self.ranged_attack_player(player)
                    self.ranged_attack_cooldown = self.max_ranged_attack_cooldown
            elif distance > self.ranged_attack_range:
                # Too far - move closer to preferred distance
                self.state = "positioning"
                target_distance = self.preferred_distance
                move_distance = distance - target_distance
                
                if move_distance > 0.5:  # Only move if significantly out of position
                    move_x = (dx / distance) * self.speed * 0.8  # Move slower when positioning
                    move_y = (dy / distance) * self.speed * 0.8
                    
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                        self.x = new_x
                        self.y = new_y
                        
                        # Update direction based on movement
                        if abs(dx) > abs(dy):
                            self.direction = 3 if dx > 0 else 1
                        else:
                            self.direction = 0 if dy > 0 else 2
            else:
                # In range but not optimal - try to maintain preferred distance
                self.state = "positioning"
                # Slight positioning adjustments
                if random.random() < 0.1:  # 10% chance to adjust position
                    angle = random.uniform(0, 2 * math.pi)
                    move_x = math.cos(angle) * self.speed * 0.3
                    move_y = math.sin(angle) * self.speed * 0.3
                    
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                        self.x = new_x
                        self.y = new_y
        else:
            # Out of detection range - idle behavior
            self.state = "idle"
            if random.random() < 0.005:  # Less frequent idle movement for ranged enemies
                move_x = random.uniform(-self.speed * 0.2, self.speed * 0.2)
                move_y = random.uniform(-self.speed * 0.2, self.speed * 0.2)
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if not level.check_collision(new_x, new_y, self.size, exclude_entity=self):
                    self.x = new_x
                    self.y = new_y
    
    def ranged_attack_player(self, player):
        """Perform ranged attack on player"""
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play weapon-specific attack sound
        if audio:
            if self.weapon_type == "bow":
                audio.play_combat_sound("weapon_draw")  # Bow string sound
            elif self.weapon_type == "crossbow":
                audio.play_combat_sound("blade_slice")  # Crossbow release
            elif self.weapon_type in ["magic_staff", "dark_magic"]:
                audio.play_magic_sound("spell_cast")
            elif self.weapon_type == "throwing_knife":
                audio.play_combat_sound("blade_slice")
        
        # Calculate damage
        base_damage = self.damage
        damage = base_damage + random.randint(-2, 2)  # Small damage variation
        
        # Create projectile
        from ..systems.combat import Projectile  # Import here to avoid circular imports
        
        projectile = Projectile(
            self.x, self.y,
            player.x, player.y,
            self.weapon_type, damage, player
        )
        
        # Adjust projectile speed based on weapon type
        distance = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        if distance > 0:
            if self.weapon_type == "throwing_knife":
                speed = 0.5  # Fast
            elif self.weapon_type == "crossbow":
                speed = 0.4  # Fast
            elif self.weapon_type == "bow":
                speed = 0.35  # Medium
            elif self.weapon_type in ["magic_staff", "dark_magic"]:
                speed = 0.25  # Slower but tracking
            else:
                speed = 0.3  # Default
            
            projectile.velocity_x = ((player.x - self.x) / distance) * speed
            projectile.velocity_y = ((player.y - self.y) / distance) * speed
        
        self.projectiles.append(projectile)
        
        print(f"{self.name} fires {self.weapon_type} at player for {damage} damage!")
    
    def render(self, screen, camera_x, camera_y, iso_renderer):
        """Render the ranged enemy and its projectiles"""
        # Render the enemy itself
        super().render(screen, camera_x, camera_y, iso_renderer)
        
        # Render projectiles
        for projectile in self.projectiles:
            self.render_projectile(screen, projectile, iso_renderer, camera_x, camera_y)
    
    def render_projectile(self, screen, projectile, iso_renderer, camera_x, camera_y):
        """Render enemy projectile"""
        screen_x, screen_y = iso_renderer.world_to_screen(projectile.current_x, projectile.current_y, camera_x, camera_y)
        
        # Different projectile appearances based on weapon type
        if self.weapon_type == "bow":
            # Arrow
            color = (139, 69, 19)  # Brown
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 3)
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 2)
        elif self.weapon_type == "crossbow":
            # Crossbow bolt
            color = (100, 100, 100)  # Gray
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 1)
        elif self.weapon_type in ["magic_staff", "dark_magic"]:
            # Magic projectile
            color = (138, 43, 226) if self.weapon_type == "magic_staff" else (75, 0, 130)
            # Glowing effect
            for i in range(3, 0, -1):
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), i * 2)
        elif self.weapon_type == "throwing_knife":
            # Spinning knife
            color = (192, 192, 192)
            angle = (projectile.distance_traveled * 10) % 360
            offset = 4
            x1 = screen_x + math.cos(math.radians(angle)) * offset
            y1 = screen_y + math.sin(math.radians(angle)) * offset
            x2 = screen_x - math.cos(math.radians(angle)) * offset
            y2 = screen_y - math.sin(math.radians(angle)) * offset
            pygame.draw.line(screen, color, (int(x1), int(y1)), (int(x2), int(y2)), 3)
        else:
            # Default projectile
            pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), 2)
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "weapon_type": self.weapon_type,
            "enemy_type": "ranged"  # Mark as ranged enemy for loading
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create ranged enemy from save data"""
        weapon_type = data.get("weapon_type", "bow")
        enemy = cls(data["x"], data["y"], data["name"], data["max_health"], 
                   data["damage"], data["experience"], data["is_boss"], 
                   asset_loader, weapon_type)
        enemy.health = data["health"]
        return enemy


