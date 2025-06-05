"""
Simplified tile-based movement system for player character.

This module handles discrete tile-to-tile movement with smooth animation.
"""

import pygame
import math


class MovementSystem:
    """Handles tile-based movement for the player"""
    
    def __init__(self, player):
        """Initialize movement system with reference to player"""
        self.player = player
        
        # Movement modes
        self.movement_mode = "mouse"  # "mouse" or "wasd"
        
        # Movement state
        self.direction = 0  # 0=down, 1=left, 2=up, 3=right
        
        # Pathfinding for mouse movement
        self.path = []  # List of tile coordinates to follow
        self.path_index = 0
        
        # Audio
        self.footstep_timer = 0
        self.last_door_sound_tile = None
    
    def toggle_movement_mode(self):
        """Toggle between mouse and WASD movement modes"""
        if self.movement_mode == "mouse":
            self.movement_mode = "wasd"
            # Clear any existing path when switching to WASD
            self.path = []
            self.path_index = 0
        else:
            self.movement_mode = "mouse"
        
        # Log the change
        if self.player.game_log:
            mode_name = "WASD" if self.movement_mode == "wasd" else "Mouse Click"
            self.player.game_log.add_message(f"Movement mode: {mode_name}", "system")
        
        return self.movement_mode
    
    def handle_input(self, keys, level=None):
        """Handle player input for movement"""
        # Check if any shop is open - if so, disable movement
        if level:
            for npc in level.npcs:
                if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                    return  # Don't allow movement while shop is open
        
        # Check if dialogue window is open - if so, disable movement
        if self.player.current_dialogue and self.player.current_dialogue.show:
            return  # Don't allow movement while dialogue is open
        
        # Handle movement based on current mode
        if self.movement_mode == "wasd":
            self._handle_wasd_movement(keys, level)
        else:
            self._handle_mouse_movement(keys, level)
    
    def _handle_wasd_movement(self, keys, level):
        """Handle WASD tile-based movement"""
        if self.player.moving:
            return  # Already moving, wait for animation to complete
        
        # Determine movement direction
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_w]:
            move_y = -1
            self.direction = 2  # Up
        elif keys[pygame.K_s]:
            move_y = 1
            self.direction = 0  # Down
        elif keys[pygame.K_a]:
            move_x = -1
            self.direction = 1  # Left
        elif keys[pygame.K_d]:
            move_x = 1
            self.direction = 3  # Right
        
        # Apply movement if any keys are pressed
        if move_x != 0 or move_y != 0:
            target_tile_x = self.player.tile_x + move_x
            target_tile_y = self.player.tile_y + move_y
            
            # Check if target tile is walkable
            if level and level.is_tile_walkable(target_tile_x, target_tile_y):
                # Start movement to target tile
                if self.player.move_to_tile(target_tile_x, target_tile_y):
                    self._play_footstep_sound(level)
    
    def _handle_mouse_movement(self, keys, level):
        """Handle mouse-based pathfinding movement"""
        if self.player.moving:
            return  # Wait for current movement to complete
        
        # Follow current path if we have one
        if self.path and self.path_index < len(self.path):
            target_tile_x, target_tile_y = self.path[self.path_index]
            
            # Check if we've reached the current path target
            if target_tile_x == self.player.tile_x and target_tile_y == self.player.tile_y:
                # Move to next path point
                self.path_index += 1
                if self.path_index >= len(self.path):
                    # Reached end of path
                    self.path = []
                    self.path_index = 0
                return
            
            # Check if target tile is still walkable
            if level and level.is_tile_walkable(target_tile_x, target_tile_y):
                # Start movement to next tile in path
                if self.player.move_to_tile(target_tile_x, target_tile_y):
                    self._play_footstep_sound(level)
                    
                    # Update direction based on movement
                    dx = target_tile_x - self.player.tile_x
                    dy = target_tile_y - self.player.tile_y
                    if abs(dx) > abs(dy):
                        self.direction = 3 if dx > 0 else 1  # Right or Left
                    else:
                        self.direction = 0 if dy > 0 else 2  # Down or Up
            else:
                # Path is blocked, clear it
                self.path = []
                self.path_index = 0
                if self.player.game_log:
                    self.player.game_log.add_message("Path blocked!", "system")
    
    def handle_mouse_click(self, world_x, world_y, level):
        """Handle mouse click for movement and interaction"""
        # Convert world coordinates to tile coordinates
        target_tile_x = int(world_x)
        target_tile_y = int(world_y)
        
        # Check if any shop is open - if so, disable mouse movement
        if level:
            for npc in level.npcs:
                if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                    return  # Don't allow movement while shop is open
        
        # Check if dialogue window is open - if so, disable mouse movement
        if self.player.current_dialogue and self.player.current_dialogue.show:
            return  # Don't allow movement while dialogue is open
        
        # Check if clicking on an entity first
        clicked_entity = self._check_entity_click(target_tile_x, target_tile_y, level)
        
        if clicked_entity:
            # Handle entity interaction
            self._handle_entity_interaction(clicked_entity, target_tile_x, target_tile_y, level)
        else:
            # Move to the clicked tile
            self._move_to_tile(target_tile_x, target_tile_y, level)
    
    def _check_entity_click(self, tile_x, tile_y, level):
        """Check if click is on an entity - with more forgiving click detection"""
        click_radius = 1.2  # Increased for much more forgiving clicks
        
        # Check NPCs (only if visible and interactive)
        for npc in level.npcs:
            distance = math.sqrt((npc.x - tile_x - 0.5)**2 + (npc.y - tile_y - 0.5)**2)
            if distance <= click_radius:
                # Check if NPC is visible (not hidden by building roof)
                if level._is_npc_visible_for_interaction(npc):
                    # Allow targeting both interactive and background NPCs
                    return npc
                # If NPC is hidden, don't return it (continue checking other entities)
        
        # Check chests
        for chest in level.chests:
            distance = math.sqrt((chest.x - tile_x - 0.5)**2 + (chest.y - tile_y - 0.5)**2)
            if distance <= click_radius:
                return chest
        
        # Check items
        for item in level.items:
            distance = math.sqrt((item.x - tile_x - 0.5)**2 + (item.y - tile_y - 0.5)**2)
            if distance <= click_radius:
                return item
        
        # Check enemies
        for enemy in level.enemies:
            distance = math.sqrt((enemy.x - tile_x - 0.5)**2 + (enemy.y - tile_y - 0.5)**2)
            if distance <= click_radius:
                return enemy
        
        return None
    
    def _handle_entity_interaction(self, entity, tile_x, tile_y, level):
        """Handle interaction with an entity"""
        # Calculate distance to entity's actual position
        entity_tile_x = int(entity.x)
        entity_tile_y = int(entity.y)
        distance = max(abs(self.player.tile_x - entity_tile_x), abs(self.player.tile_y - entity_tile_y))
        
        if distance <= 1:
            # Adjacent or same tile - interact directly
            if hasattr(entity, 'interact'):
                entity.interact(self.player)
            elif entity.entity_type == "item":
                # Pick up item
                if self.player.add_item(entity):
                    level.items.remove(entity)
                    if self.player.game_log:
                        self.player.game_log.add_message(f"Picked up {entity.name}", "item")
                else:
                    if self.player.game_log:
                        self.player.game_log.add_message("Inventory is full!", "system")
            elif entity.entity_type == "enemy":
                # Attack enemy
                stamina_cost = self.player.combat_system.get_weapon_stamina_cost()
                if self.player.stamina >= stamina_cost:
                    self.player.combat_system.attack([entity], level)
                    if self.player.game_log:
                        self.player.game_log.add_message(f"Attacking {entity.name}!", "combat")
                else:
                    if self.player.game_log:
                        weapon_name = self.player.equipped_weapon.name if self.player.equipped_weapon else "fists"
                        self.player.game_log.add_message(f"Not enough stamina to attack with {weapon_name}! (Need {stamina_cost})", "combat")
        else:
            # Too far - move towards entity's position
            self._move_to_tile(entity_tile_x, entity_tile_y, level)
    
    def _move_to_tile(self, target_tile_x, target_tile_y, level):
        """Move to a target tile using pathfinding"""
        if target_tile_x == self.player.tile_x and target_tile_y == self.player.tile_y:
            return  # Already at target
        
        # Find path to target
        path = level.find_tile_path(self.player.tile_x, self.player.tile_y, target_tile_x, target_tile_y)
        if path:
            self.path = path
            self.path_index = 0
        else:
            if self.player.game_log:
                self.player.game_log.add_message("Can't reach that location!", "system")
    
    def render_movement_indicators(self, screen, iso_renderer, camera_x, camera_y):
        """Render movement target indicator and path"""
        if self.path and len(self.path) > 0:
            # Draw path
            for i, (tile_x, tile_y) in enumerate(self.path):
                world_x = tile_x + 0.5
                world_y = tile_y + 0.5
                screen_x, screen_y = iso_renderer.world_to_screen(world_x, world_y, camera_x, camera_y)
                
                if i == len(self.path) - 1:
                    # Final destination - pulsing circle
                    import time
                    pulse = int(abs(math.sin(time.time() * 5)) * 10) + 5
                    pygame.draw.circle(screen, (255, 255, 0), (int(screen_x), int(screen_y)), pulse, 2)
                    pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), 3)
                else:
                    # Path point
                    pygame.draw.circle(screen, (0, 255, 0), (int(screen_x), int(screen_y)), 3)
    
    def _play_footstep_sound(self, level):
        """Play appropriate footstep sound based on current tile"""
        audio = getattr(self.player.asset_loader, 'audio_manager', None) if self.player.asset_loader else None
        if audio and level:
            # Determine surface type based on current tile
            tile_type = level.get_tile(self.player.tile_x, self.player.tile_y)
            
            if tile_type == getattr(level, 'TILE_STONE', 2):
                audio.play_footstep("stone")
            elif tile_type == getattr(level, 'TILE_WATER', 3):
                audio.play_footstep("water")
            else:
                audio.play_footstep("dirt")  # Default for grass/dirt
    
    # Compatibility properties for old movement system
    @property
    def moving(self):
        return self.player._moving
    
    @moving.setter
    def moving(self, value):
        self.player._moving = value
    
    @property
    def target_x(self):
        return self.path[-1][0] + 0.5 if self.path else None
    
    @property
    def target_y(self):
        return self.path[-1][1] + 0.5 if self.path else None