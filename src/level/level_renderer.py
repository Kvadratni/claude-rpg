"""
Level rendering functionality
"""

import pygame
try:
    from ..core.isometric import sort_by_depth
except ImportError:
    from src.core.isometric import sort_by_depth


class LevelRendererMixin:
    """Mixin class for level rendering functionality"""
    
    def render(self, screen):
        """Render the level with improved isometric building rendering"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Reserve space for bottom UI
        ui_height = 150
        game_area_height = screen_height - ui_height
        
        # Update camera
        self.update_camera(screen_width, game_area_height)
        
        # Create game area surface
        game_surface = pygame.Surface((screen_width, game_area_height))
        game_surface.fill((0, 0, 0))
        
        # Calculate visible tile range - much larger rendering area
        visible_width = (screen_width // self.tile_width) + 30  # Much larger area
        visible_height = (game_area_height // (self.tile_height // 2)) + 30  # Much larger area
        
        # Calculate center tile
        center_x = int(self.player.x)
        center_y = int(self.player.y)
        
        # Calculate tile range - render much more area
        start_x = max(0, center_x - visible_width)  # Remove // 2 to get full range
        end_x = min(self.width, center_x + visible_width)
        start_y = max(0, center_y - visible_height)  # Remove // 2 to get full range
        end_y = min(self.height, center_y + visible_height)
        
        # Render tiles in proper isometric order (back to front)
        # This ensures proper depth sorting for buildings
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.render_tile_at_position(game_surface, x, y)
        
        # Collect all entities for depth sorting
        all_entities = []
        all_entities.append(self.player)
        all_entities.extend(self.enemies)
        all_entities.extend(self.npcs)
        all_entities.extend(self.items)
        all_entities.extend(self.objects)
        all_entities.extend(self.chests)
        
        # Sort entities by depth
        sorted_entities = sort_by_depth(all_entities)
        
        # Render entities to game surface
        for entity in sorted_entities:
            entity.render(game_surface, self.iso_renderer, self.camera_x, self.camera_y)
        
        # Debug: Render pathfinding visualization if player has a path
        if hasattr(self.player, 'path') and self.player.path and len(self.player.path) > 1:
            self.render_path_debug(game_surface, self.player.path)
        
        # Blit game surface to main screen
        screen.blit(game_surface, (0, 0))
        
        # Render XP bar at the top
        self.render_xp_bar(screen)
        
        # Render UI on top
        self.render_ui(screen)
        
        # Render shops on top of everything
        for npc in self.npcs:
            if hasattr(npc, 'shop') and npc.shop:
                # Set player items for sell mode
                npc.shop.set_player_items(self.player.inventory.items)
                npc.shop.render(screen)
        
        # Render dialogue window on top of everything
        if self.player.current_dialogue and self.player.current_dialogue.show:
            self.player.current_dialogue.render(screen)
    
    def render_tile_at_position(self, surface, x, y):
        """Render a single tile with new flat surface wall system"""
        tile_type = self.tiles[y][x]
        height = self.heightmap[y][x]
        
        # Calculate screen position using proper isometric conversion
        screen_x, screen_y = self.iso_renderer.world_to_screen(x, y, self.camera_x, self.camera_y)
        
        # Adjust for height
        screen_y -= height * 16
        
        # ALWAYS render floor tile first (even under walls)
        floor_sprite = None
        if self.wall_renderer.is_wall_tile(tile_type):
            # Render appropriate floor tile underneath walls
            if tile_type == self.TILE_DOOR:
                floor_sprite = self.tile_sprites[self.TILE_STONE]  # Stone under doors
            else:
                floor_sprite = self.tile_sprites[self.TILE_BRICK]  # Brick under walls (interior)
        else:
            # Normal floor tiles
            floor_sprite = self.tile_sprites[tile_type]
        
        if floor_sprite:
            floor_rect = floor_sprite.get_rect()
            floor_rect.center = (screen_x, screen_y)
            surface.blit(floor_sprite, floor_rect)
        
        # Now render walls using flat surfaces
        if self.wall_renderer.is_wall_tile(tile_type):
            self.wall_renderer.render_flat_wall(surface, screen_x, screen_y, tile_type, x, y)
        elif tile_type == self.TILE_DOOR:
            self.door_renderer.render_door_tile(surface, screen_x, screen_y, tile_type, self, self.tile_width, self.tile_height)
    
    def render_path_debug(self, surface, path):
        """Render debug visualization of the current path"""
        if len(path) < 2:
            return
        
        # Draw path lines
        for i in range(len(path) - 1):
            start_world = path[i]
            end_world = path[i + 1]
            
            # Convert world coordinates to screen coordinates
            start_screen = self.iso_renderer.world_to_screen(start_world[0], start_world[1], self.camera_x, self.camera_y)
            end_screen = self.iso_renderer.world_to_screen(end_world[0], end_world[1], self.camera_x, self.camera_y)
            
            # Draw line between waypoints
            pygame.draw.line(surface, (255, 255, 0), start_screen, end_screen, 2)  # Yellow line
        
        # Draw waypoint circles
        for i, waypoint in enumerate(path):
            screen_pos = self.iso_renderer.world_to_screen(waypoint[0], waypoint[1], self.camera_x, self.camera_y)
            
            # Different colors for different waypoint types
            if i == 0:
                color = (0, 255, 0)  # Green for start
            elif i == len(path) - 1:
                color = (255, 0, 0)  # Red for end
            else:
                # Check if this waypoint is near a door
                tile_x, tile_y = int(waypoint[0]), int(waypoint[1])
                is_door_waypoint = False
                
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        check_x, check_y = tile_x + dx, tile_y + dy
                        if (0 <= check_x < self.width and 0 <= check_y < self.height):
                            if self.tiles[check_y][check_x] == self.TILE_DOOR:
                                is_door_waypoint = True
                                break
                    if is_door_waypoint:
                        break
                
                color = (0, 255, 255) if is_door_waypoint else (255, 255, 255)  # Cyan for door waypoints, white for others
            
            pygame.draw.circle(surface, color, screen_pos, 4)
            pygame.draw.circle(surface, (0, 0, 0), screen_pos, 4, 1)  # Black border