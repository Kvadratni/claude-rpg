"""
Player class for the RPG
"""

import pygame
import math
import random
from .ui.inventory import Inventory
from .systems import CombatSystem, MovementSystem

class Player:
    """Player character class"""
    
    def __init__(self, x, y, asset_loader=None, game_log=None):
        # Convert to integer tile coordinates
        self.tile_x = int(x)
        self.tile_y = int(y)
        self.asset_loader = asset_loader
        self.game_log = game_log
        
        # Movement animation properties (separate from movement_system)
        self._moving = False  # Internal moving state for animation
        self.move_animation_progress = 0.0
        self.move_animation_speed = 0.15  # How fast movement animation plays
        self.move_start_tile = (self.tile_x, self.tile_y)
        self.move_target_tile = (self.tile_x, self.tile_y)
        
        self.size = 0.4  # Keep for compatibility but not used for collision
        
        # RPG stats
        self.level = 1
        self.health = 100
        self.max_health = 100
        self.stamina = 50
        self.max_stamina = 50
        self.experience = 0
        self.experience_to_next = 100
        self.gold = 50
        
        # Combat stats
        self.attack_damage = 25
        self.attack_range = 1.5  # More forgiving melee attack range
        self.defense = 5
        
        # Inventory
        self.inventory = Inventory(max_size=20)
        self.equipped_weapon = None
        self.equipped_armor = None
        
        # Stamina regeneration
        self.stamina_regen_timer = 0
        self.stamina_regen_rate = 30  # Regenerate 1 stamina every 30 frames (0.5 seconds at 60 FPS)
        
        # UI state
        self.show_stats = False
        self.show_dialog = False
        self.dialog_text = ""
        self.current_dialogue = None  # For dialogue windows
        self.current_ai_chat = None   # For AI chat windows
        self.current_shop = None      # For shop windows
        
        # Create player sprite
        self.create_sprite()
        
        # Initialize systems
        self.combat_system = CombatSystem(self)
        self.movement_system = MovementSystem(self)
        
        # DEBUG: Start with a Magic Bow for testing ranged weapons
        self._add_debug_starting_bow()
    
    def _add_debug_starting_bow(self):
        """DEBUG: Add a Magic Bow for testing ranged weapons"""
        try:
            from .entities.item import Item
            
            # Create a Magic Bow
            magic_bow = Item(
                name="Magic Bow",
                item_type="weapon",
                effect={"damage": 22},
                value=180,
                asset_loader=self.asset_loader
            )
            
            # Equip it directly
            self.equipped_weapon = magic_bow
            
            if self.game_log:
                self.game_log.add_message("DEBUG: Started with Magic Bow equipped!", "item")
                
        except Exception as e:
            print(f"DEBUG: Could not add starting bow: {e}")
    
    # Properties for world coordinates (for rendering and compatibility)
    @property
    def x(self):
        """Get current world X coordinate (for rendering)"""
        if self._moving:
            # Interpolate between start and target during movement animation
            start_x = self.move_start_tile[0] + 0.5
            target_x = self.move_target_tile[0] + 0.5
            return start_x + (target_x - start_x) * self.move_animation_progress
        else:
            return self.tile_x + 0.5  # Center of tile
    
    @property
    def y(self):
        """Get current world Y coordinate (for rendering)"""
        if self._moving:
            # Interpolate between start and target during movement animation
            start_y = self.move_start_tile[1] + 0.5
            target_y = self.move_target_tile[1] + 0.5
            return start_y + (target_y - start_y) * self.move_animation_progress
        else:
            return self.tile_y + 0.5  # Center of tile
    
    # Properties for backward compatibility with movement system
    @property
    def moving(self):
        if hasattr(self, 'movement_system'):
            return self.movement_system.moving
        else:
            return self._moving
    
    @moving.setter
    def moving(self, value):
        if hasattr(self, 'movement_system'):
            self.movement_system.moving = value
        else:
            self._moving = value
    
    @property
    def direction(self):
        if hasattr(self, 'movement_system'):
            return self.movement_system.direction
        else:
            return 0  # Default direction
    
    @direction.setter
    def direction(self, value):
        if hasattr(self, 'movement_system'):
            self.movement_system.direction = value
    
    @property
    def target_x(self):
        if hasattr(self, 'movement_system'):
            return self.movement_system.target_x
        else:
            return self.x
    
    @target_x.setter
    def target_x(self, value):
        if hasattr(self, 'movement_system'):
            self.movement_system.target_x = value
    
    @property
    def target_y(self):
        if hasattr(self, 'movement_system'):
            return self.movement_system.target_y
        else:
            return self.y
    
    @target_y.setter
    def target_y(self, value):
        if hasattr(self, 'movement_system'):
            self.movement_system.target_y = value
    
    @property
    def path(self):
        if hasattr(self, 'movement_system'):
            return self.movement_system.path
        else:
            return []
    
    @path.setter
    def path(self, value):
        if hasattr(self, 'movement_system'):
            self.movement_system.path = value
    
    @property
    def path_index(self):
        if hasattr(self, 'movement_system'):
            return self.movement_system.path_index
        else:
            return 0
    
    @path_index.setter
    def path_index(self, value):
        if hasattr(self, 'movement_system'):
            self.movement_system.path_index = value
    
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
        self.movement_system.handle_input(keys, level)
        
        # Handle furniture interaction with E key
        if keys[pygame.K_e] and level and hasattr(level, 'handle_furniture_interaction'):
            level.handle_furniture_interaction(self)
    
    def recalculate_path(self, level):
        """Recalculate path to target"""
        self.movement_system.recalculate_path(level)
    
    def handle_mouse_click(self, world_x, world_y, level):
        """Handle mouse click for movement and interaction"""
        self.movement_system.handle_mouse_click(world_x, world_y, level)
    
    def update(self, level):
        """Update player logic"""
        # Update movement animation
        if self._moving:
            self.move_animation_progress += self.move_animation_speed
            if self.move_animation_progress >= 1.0:
                # Movement animation complete
                self.move_animation_progress = 0.0
                self.tile_x = self.move_target_tile[0]
                self.tile_y = self.move_target_tile[1]
                self.move_start_tile = (self.tile_x, self.tile_y)
                self.move_target_tile = (self.tile_x, self.tile_y)
                self._moving = False
        
        # Update combat system (projectile effects, etc.)
        self.combat_system.update()
        
        # Regenerate stamina at a fixed rate
        if self.stamina < self.max_stamina:
            self.stamina_regen_timer += 1
            if self.stamina_regen_timer >= self.stamina_regen_rate:
                self.stamina_regen_timer = 0
                self.stamina += 1
    
    def move_to_tile(self, target_tile_x, target_tile_y):
        """Start movement to a target tile"""
        if self._moving:
            return False  # Already moving
        
        # Validate target tile
        if target_tile_x == self.tile_x and target_tile_y == self.tile_y:
            return False  # Already at target
        
        # Start movement animation
        self.move_start_tile = (self.tile_x, self.tile_y)
        self.move_target_tile = (target_tile_x, target_tile_y)
        self.move_animation_progress = 0.0
        self._moving = True
        return True
    
    def get_weapon_stamina_cost(self):
        """Get stamina cost based on equipped weapon"""
        return self.combat_system.get_weapon_stamina_cost()
    
    def attack(self, enemies, level=None):
        """Attack nearby enemies or use ranged attack"""
        self.combat_system.attack(enemies, level)
    
    def take_damage(self, damage):
        """Take damage"""
        return self.combat_system.take_damage(damage)
    
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
    
    def render(self, screen, camera_x, camera_y, iso_renderer):
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
        self.movement_system.render_movement_indicators(screen, iso_renderer, camera_x, camera_y)
        
        # Render health bar
        self.render_health_bar(screen, screen_x, screen_y - 30)
        
        # Render projectile effects
        self.combat_system.render_projectile_effects(screen, iso_renderer, camera_x, camera_y)
    
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
            "tile_x": self.tile_x,
            "tile_y": self.tile_y,
            "x": self.tile_x,  # Backward compatibility
            "y": self.tile_y,  # Backward compatibility
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
        from .entities import Item
        
        # Handle both old (x, y) and new (tile_x, tile_y) save formats
        tile_x = data.get("tile_x", int(data.get("x", 0)))
        tile_y = data.get("tile_y", int(data.get("y", 0)))
        
        player = cls(tile_x, tile_y, asset_loader, game_log)
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