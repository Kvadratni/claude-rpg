"""
Movement system for player character.

This module handles all movement-related functionality including:
- Pathfinding
- Mouse movement
- Animation
- Direction handling
- Collision detection
- Audio feedback for movement
"""

import pygame
import math


class MovementSystem:
    """Handles all movement-related functionality for the player"""
    
    def __init__(self, player):
        """Initialize movement system with reference to player"""
        self.player = player
        
        # Movement state
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
        
        # Audio
        self.footstep_timer = 0
        self.last_door_sound_tile = None
    
    def handle_input(self, keys, level=None):
        """Handle player input for movement"""
        self.moving = False
        
        # Check if any shop is open - if so, disable movement
        if level:
            for npc in level.npcs:
                if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                    return  # Don't allow movement while shop is open
        
        # Check if dialogue window is open - if so, disable movement
        if self.player.current_dialogue and self.player.current_dialogue.show:
            return  # Don't allow movement while dialogue is open
        
        # Follow current path if we have one
        if self.path and self.path_index < len(self.path):
            target_x, target_y = self.path[self.path_index]
            
            # Calculate distance to current path target
            dx = target_x - self.player.x
            dy = target_y - self.player.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Check if we're moving through a door and play sound
            if level:
                current_tile_x = int(self.player.x)
                current_tile_y = int(self.player.y)
                target_tile_x = int(target_x)
                target_tile_y = int(target_y)
                
                # Check if we're entering a door tile
                if (0 <= target_tile_x < level.width and 0 <= target_tile_y < level.height and
                    level.tiles[target_tile_y][target_tile_x] == level.TILE_DOOR and
                    (current_tile_x != target_tile_x or current_tile_y != target_tile_y)):
                    
                    # Play door sound occasionally (not every frame)
                    if not self.last_door_sound_tile or self.last_door_sound_tile != (target_tile_x, target_tile_y):
                        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
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
                new_x = self.player.x + move_x
                new_y = self.player.y + move_y
                
                # Check collision before moving
                if level and level.check_collision(new_x, new_y, self.player.size):
                    # Path is blocked, recalculate
                    if self.target_x is not None and self.target_y is not None:
                        self.recalculate_path(level)
                    else:
                        self.path = []
                        self.path_index = 0
                        if self.player.game_log:
                            self.player.game_log.add_message("Path blocked!", "system")
                else:
                    self.player.x = new_x
                    self.player.y = new_y
                    self.moving = True
                    
                    # Play footstep sounds occasionally while moving
                    self.footstep_timer += 1
                    
                    if self.footstep_timer >= 20:  # Play footstep every 20 frames
                        self.footstep_timer = 0
                        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
                        if audio and level:
                            # Determine surface type based on current tile
                            tile_x = int(self.player.x)
                            tile_y = int(self.player.y)
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
        
        # Update animation
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
    
    def recalculate_path(self, level):
        """Recalculate path to target"""
        if self.target_x is not None and self.target_y is not None and level:
            new_path = level.find_path(self.player.x, self.player.y, self.target_x, self.target_y, self.player.size)
            if new_path:
                self.path = new_path
                self.path_index = 0
            else:
                # No path found
                self.path = []
                self.path_index = 0
                self.target_x = None
                self.target_y = None
                if self.player.game_log:
                    self.player.game_log.add_message("No path found!", "system")
    
    def handle_mouse_click(self, world_x, world_y, level):
        """Handle mouse click for movement and interaction"""
        # Check if any shop is open - if so, disable mouse movement
        if level:
            for npc in level.npcs:
                if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                    return  # Don't allow movement while shop is open
        
        # Check if dialogue window is open - if so, disable mouse movement
        if self.player.current_dialogue and self.player.current_dialogue.show:
            return  # Don't allow movement while dialogue is open
        
        # Get audio manager
        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
        
        # Check if clicking on an entity first
        clicked_entity = None
        
        # Check NPCs
        for npc in level.npcs:
            # Use larger detection area for easier clicking
            if abs(world_x - npc.x) < 1.2 and abs(world_y - npc.y) < 1.2:
                # Check if player is close enough to interact
                dist = math.sqrt((self.player.x - npc.x)**2 + (self.player.y - npc.y)**2)
                if dist < 2.0:  # Same proximity requirement as item pickup
                    clicked_entity = npc
                    break
                else:
                    # Use pathfinding to move towards the NPC
                    path = level.find_path(self.player.x, self.player.y, npc.x, npc.y, self.player.size)
                    if path:
                        self.path = path
                        self.path_index = 0
                        self.target_x = npc.x
                        self.target_y = npc.y
                    else:
                        if self.player.game_log:
                            self.player.game_log.add_message(f"Can't reach {npc.name}!", "system")
                    clicked_entity = npc  # Still set clicked_entity to prevent movement
                    break
        
        # Check chests
        if not clicked_entity:
            for chest in level.chests:
                # Use larger detection area for easier clicking
                if abs(world_x - chest.x) < 1.2 and abs(world_y - chest.y) < 1.2:
                    # Check if player is close enough to interact
                    dist = math.sqrt((self.player.x - chest.x)**2 + (self.player.y - chest.y)**2)
                    if dist < 1.5:  # Must be right next to chest to interact
                        clicked_entity = chest
                        break
                    else:
                        # Use pathfinding to move towards the chest
                        path = level.find_path(self.player.x, self.player.y, chest.x, chest.y, self.player.size)
                        if path:
                            self.path = path
                            self.path_index = 0
                            self.target_x = chest.x
                            self.target_y = chest.y
                        else:
                            if self.player.game_log:
                                self.player.game_log.add_message(f"Can't reach {chest.name}!", "system")
                        clicked_entity = chest  # Still set clicked_entity to prevent movement
                        break
        
        # Check items
        if not clicked_entity:
            for item in level.items[:]:
                # Use larger detection area for easier clicking
                if abs(world_x - item.x) < 1.2 and abs(world_y - item.y) < 1.2:
                    # Check if player is close enough to pick up
                    dist = math.sqrt((self.player.x - item.x)**2 + (self.player.y - item.y)**2)
                    if dist < 2.0:
                        if self.player.add_item(item):
                            level.items.remove(item)
                            # Play pickup sound based on item type
                            if audio:
                                if item.name.lower().find('gold') != -1 or item.name.lower().find('coin') != -1:
                                    audio.play_ui_sound("coin")
                                elif item.item_type == "consumable":
                                    audio.play_sound("ui", "leather_item")  # Use leather item sound for potions
                                else:
                                    audio.play_ui_sound("click")
                            if self.player.game_log:
                                self.player.game_log.add_message(f"Picked up {item.name}", "item")
                        else:
                            if self.player.game_log:
                                self.player.game_log.add_message("Inventory is full!", "system")
                    else:
                        # Use pathfinding to move towards the item
                        path = level.find_path(self.player.x, self.player.y, item.x, item.y, self.player.size)
                        if path:
                            self.path = path
                            self.path_index = 0
                            self.target_x = item.x
                            self.target_y = item.y
                        else:
                            if self.player.game_log:
                                self.player.game_log.add_message(f"Can't reach {item.name}!", "system")
                    clicked_entity = item
                    break
        
        # Check enemies for attack
        if not clicked_entity:
            for enemy in level.enemies:
                # Use larger detection area for easier clicking - circular area around enemy
                dx = world_x - enemy.x
                dy = world_y - enemy.y
                click_distance = math.sqrt(dx * dx + dy * dy)
                
                if click_distance < 1.0:  # Circular hitbox instead of square
                    # Check if player is close enough to attack
                    player_dist = math.sqrt((self.player.x - enemy.x)**2 + (self.player.y - enemy.y)**2)
                    if player_dist <= self.player.combat_system.attack_range:
                        # Update player direction to face the enemy before attacking
                        enemy_dx = enemy.x - self.player.x
                        enemy_dy = enemy.y - self.player.y
                        if abs(enemy_dx) > abs(enemy_dy):
                            self.direction = 3 if enemy_dx > 0 else 1  # Right or Left
                        else:
                            self.direction = 0 if enemy_dy > 0 else 2  # Down or Up
                        
                        # Attack immediately if in range and have stamina
                        stamina_cost = self.player.combat_system.get_weapon_stamina_cost()
                        if self.player.stamina >= stamina_cost:
                            self.player.combat_system.attack([enemy])
                            if self.player.game_log:
                                self.player.game_log.add_message(f"Attacking {enemy.name}!", "combat")
                        else:
                            if self.player.game_log:
                                weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "fists"
                                self.player.game_log.add_message(f"Not enough stamina to attack with {weapon_name}! (Need {stamina_cost})", "combat")
                    else:
                        # Use pathfinding to move towards enemy for attack
                        path = level.find_path(self.player.x, self.player.y, enemy.x, enemy.y, self.player.size)
                        if path:
                            self.path = path
                            self.path_index = 0
                            self.target_x = enemy.x
                            self.target_y = enemy.y
                        else:
                            if self.player.game_log:
                                self.player.game_log.add_message(f"Can't reach {enemy.name}!", "combat")
                    clicked_entity = enemy
                    break
        
        # If no entity was clicked, move to the location
        if not clicked_entity:
            # Use pathfinding to move to the clicked location
            path = level.find_path(self.player.x, self.player.y, world_x, world_y, self.player.size)
            if path:
                self.path = path
                self.path_index = 0
                self.target_x = world_x
                self.target_y = world_y
            else:
                if self.player.game_log:
                    self.player.game_log.add_message("Can't move there!", "system")
        
        # Interact with clicked entity (only if close enough)
        if clicked_entity:
            if hasattr(clicked_entity, 'interact'):
                # For NPCs, check if we're close enough to actually interact
                if clicked_entity.entity_type == "npc":
                    dist = math.sqrt((self.player.x - clicked_entity.x)**2 + (self.player.y - clicked_entity.y)**2)
                    if dist < 2.0:  # Only interact if close enough
                        clicked_entity.interact(self.player)
                    # If not close enough, we've already set up pathfinding above
                else:
                    # For other entities, interact normally
                    clicked_entity.interact(self.player)
    
    def render_movement_indicators(self, screen, iso_renderer, camera_x, camera_y):
        """Render movement target indicator and path"""
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