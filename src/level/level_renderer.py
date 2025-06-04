"""
Level rendering functionality
"""

import pygame
try:
    from ..core.isometric import sort_by_depth
    from ..roof_renderer import RoofRenderer
except ImportError:
    from src.core.isometric import sort_by_depth
    from src.roof_renderer import RoofRenderer


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
        visible_width = (screen_width // self.tile_width) + 10  # Optimized for large worlds
        visible_height = (game_area_height // (self.tile_height // 2)) + 30  # Much larger area
        
        # Calculate center tile
        center_x = int(self.player.x)
        center_y = int(self.player.y)
        
        # Calculate tile range - render visible area (optimized for chunked worlds)
        # FIXED: Don't use max(0, ...) for chunked worlds that can have negative coordinates
        start_x = center_x - visible_width
        end_x = center_x + visible_width
        start_y = center_y - visible_height
        end_y = center_y + visible_height
        
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
        
        # Render entities to game surface with building visibility logic
        for entity in sorted_entities:
            # Check if entity should be visible (not hidden by roof)
            should_render_entity = True
            
            # Check if entity is inside a building
            entity_x, entity_y = int(entity.x), int(entity.y)
            entity_building_bounds = self.get_building_bounds_at(entity_x, entity_y)
            
            if entity_building_bounds:
                # Entity is inside a building - only show if player is in the SAME building
                player_building_bounds = self.get_building_bounds_at(int(self.player.x), int(self.player.y))
                
                # Hide entity if player is not in the same building
                if not player_building_bounds or entity_building_bounds != player_building_bounds:
                    should_render_entity = False
            
            if should_render_entity:
                entity.render(game_surface, self.camera_x, self.camera_y, self.iso_renderer)
        
        # Blit game surface to main screen
        screen.blit(game_surface, (0, 0))
        
        # Render XP bar at the top
        self.render_xp_bar(screen)
        
        # Render bottom UI panel (equipment, inventory button, game log)
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
        """Render a single tile with improved roof rendering system"""
        # Use get_tile method if available (for chunk-based worlds), otherwise fall back to tiles array
        if hasattr(self, 'get_tile'):
            tile_type = self.get_tile(x, y)
            if tile_type is None:
                return  # Don't render unloaded chunks
        else:
            # Bounds check for traditional tile arrays
            if not hasattr(self, 'tiles') or not self.tiles or len(self.tiles) == 0:
                return  # No tiles array available or empty
            if not (0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[0])):
                return
            tile_type = self.tiles[y][x]
        
        # Get height with bounds checking
        height = 0
        if hasattr(self, 'heightmap') and self.heightmap:
            if 0 <= y < len(self.heightmap) and 0 <= x < len(self.heightmap[0]):
                height = self.heightmap[y][x]
        
        # Calculate screen position using proper isometric conversion
        screen_x, screen_y = self.iso_renderer.world_to_screen(x, y, self.camera_x, self.camera_y)
        
        # Adjust for height
        screen_y -= height * 16
        
        # Determine if this tile is part of a building
        is_building_tile = self.is_building_tile(x, y, tile_type)
        should_render_roof = False
        
        if is_building_tile:
            # Check if player is inside this building
            building_bounds = self.get_building_bounds(x, y)
            if building_bounds:
                player_in_building = self.is_player_in_building(building_bounds)
                should_render_roof = not player_in_building
        
        # ALWAYS render floor tile first (even under walls)
        floor_sprite = None
        if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
            # Render appropriate floor tile underneath walls
            if tile_type == self.TILE_DOOR:
                floor_sprite = self.tile_sprites.get(self.TILE_STONE)  # Stone under doors
            else:
                floor_sprite = self.tile_sprites.get(self.TILE_BRICK)  # Brick under walls (interior)
        elif tile_type == self.TILE_DOOR:
            # Render stone floor under doors
            floor_sprite = self.tile_sprites.get(self.TILE_STONE)
        else:
            # Normal floor tiles - use .get() to avoid KeyError
            floor_sprite = self.tile_sprites.get(tile_type)
        
        if floor_sprite:
            floor_rect = floor_sprite.get_rect()
            floor_rect.center = (screen_x, screen_y)
            surface.blit(floor_sprite, floor_rect)
        
        # Render based on roof visibility
        if should_render_roof:
            # First render the normal tile (wall or floor)
            if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                # Render walls with roof texture as top face
                self.render_wall_with_roof_top(surface, screen_x, screen_y, tile_type, x, y)
            elif tile_type == self.TILE_DOOR and hasattr(self, 'door_renderer'):
                # Door renderer already includes roof texture on top - no need to add extra roof
                self.door_renderer.render_door_tile(surface, screen_x, screen_y, tile_type, self, self.tile_width, self.tile_height)
            else:
                # For interior floors, render the roof at floor level (not wall height)
                self.render_roof_tile_at_floor_level(surface, screen_x, screen_y)
        else:
            # No roof - render walls normally or show interior
            if is_building_tile:
                # Player is inside - show interior view
                if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                    if tile_type == self.TILE_DOOR:
                        # Special door rendering when inside
                        self.render_interior_door(surface, screen_x, screen_y)
                    else:
                        # Show wall outline when inside
                        self.render_wall_outline(surface, screen_x, screen_y, tile_type)
            else:
                # Outside building - render normally with all faces for regular walls
                if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                    # Check if we should render with roof top (when player is outside other buildings)
                    # Get the building bounds for this wall tile
                    wall_building_bounds = self.get_building_bounds_at(x, y)
                    if wall_building_bounds:
                        # This wall is part of a building - check if player is outside it
                        player_in_this_building = self.is_player_in_building(wall_building_bounds)
                        if not player_in_this_building:
                            # Player is outside this building - render with roof texture on top
                            self.render_wall_with_roof_top(surface, screen_x, screen_y, tile_type, x, y)
                        else:
                            # Player is inside this building - render normally
                            self.wall_renderer.render_flat_wall(surface, screen_x, screen_y, tile_type, x, y)
                    else:
                        # Not part of a building - render normally
                        self.wall_renderer.render_flat_wall(surface, screen_x, screen_y, tile_type, x, y)
                elif tile_type == self.TILE_DOOR and hasattr(self, 'door_renderer'):
                    self.door_renderer.render_door_tile(surface, screen_x, screen_y, tile_type, self, self.tile_width, self.tile_height)
    
    def render_wall_with_roof_top(self, surface, screen_x, screen_y, tile_type, world_x, world_y):
        """Render wall with roof texture as the top face"""
        # Use the new wall renderer method that uses roof texture for top face
        self.wall_renderer.render_flat_wall_with_roof_top(surface, screen_x, screen_y, tile_type, world_x, world_y)
    
    def is_building_tile(self, x, y, tile_type):
        """Check if a tile is part of a building"""
        if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
            return True
        if tile_type == self.TILE_DOOR:
            return True
        if tile_type == self.TILE_BRICK:  # Interior floor - but only if enclosed by walls
            return self.is_enclosed_by_walls(x, y)
        return False
    
    def is_enclosed_by_walls(self, x, y):
        """Check if a tile is enclosed by walls (simple flood fill to find if there's a wall boundary)"""
        # Simple check: look for walls within a reasonable distance
        search_radius = 10  # Maximum distance to look for enclosing walls
        
        # Use flood fill to see if we can reach the edge of the search area without hitting walls
        visited = set()
        to_visit = [(x, y)]
        
        while to_visit:
            curr_x, curr_y = to_visit.pop()
            if (curr_x, curr_y) in visited:
                continue
            visited.add((curr_x, curr_y))
            
            # If we've reached the edge of our search area, it's not enclosed
            if abs(curr_x - x) >= search_radius or abs(curr_y - y) >= search_radius:
                return False
            
            # Get tile type
            if hasattr(self, 'get_tile'):
                tile_type = self.get_tile(curr_x, curr_y)
            else:
                if not (0 <= curr_y < len(self.tiles) and 0 <= curr_x < len(self.tiles[0])):
                    return False  # Hit boundary, not enclosed
                tile_type = self.tiles[curr_y][curr_x]
            
            # If we hit a wall or door, don't continue in this direction
            if (hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type)) or tile_type == self.TILE_DOOR:
                continue
            
            # Continue searching in adjacent tiles
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = curr_x + dx, curr_y + dy
                if (nx, ny) not in visited:
                    to_visit.append((nx, ny))
        
        # If we didn't reach the edge, it's enclosed
        return True
    
    def get_building_bounds(self, x, y):
        """Get the bounds of the building containing this tile"""
        # Simple flood fill to find building bounds
        visited = set()
        building_tiles = set()
        to_visit = [(x, y)]
        
        while to_visit:
            curr_x, curr_y = to_visit.pop()
            if (curr_x, curr_y) in visited:
                continue
            visited.add((curr_x, curr_y))
            
            # Get tile type
            if hasattr(self, 'get_tile'):
                tile_type = self.get_tile(curr_x, curr_y)
            else:
                if not (0 <= curr_y < len(self.tiles) and 0 <= curr_x < len(self.tiles[0])):
                    continue
                tile_type = self.tiles[curr_y][curr_x]
            
            if self.is_building_tile(curr_x, curr_y, tile_type):
                building_tiles.add((curr_x, curr_y))
                # Check adjacent tiles
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = curr_x + dx, curr_y + dy
                    if (nx, ny) not in visited:
                        to_visit.append((nx, ny))
        
        if building_tiles:
            min_x = min(x for x, y in building_tiles)
            max_x = max(x for x, y in building_tiles)
            min_y = min(y for x, y in building_tiles)
            max_y = max(y for x, y in building_tiles)
            return (min_x, min_y, max_x, max_y)
        return None
    
    def is_player_in_building(self, building_bounds):
        """Check if player is inside the given building bounds"""
        min_x, min_y, max_x, max_y = building_bounds
        player_x = int(self.player.x)
        player_y = int(self.player.y)
        return min_x <= player_x <= max_x and min_y <= player_y <= max_y
    
    def get_building_bounds_at(self, x, y):
        """Get building bounds for a specific position (optimized version)"""
        # Check if the position is a building tile
        if hasattr(self, 'get_tile'):
            tile_type = self.get_tile(x, y)
        else:
            if not (0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[0])):
                return None
            tile_type = self.tiles[y][x]
        
        if self.is_building_tile(x, y, tile_type):
            return self.get_building_bounds(x, y)
        return None
    
    def render_roof_tile(self, surface, screen_x, screen_y):
        """Render a roof tile at the given position"""
        roof_texture = self.asset_loader.get_image('roof_texture')
        if roof_texture:
            # FIXED: Rotate the roof texture 45 degrees to match isometric tiles
            rotated_roof = pygame.transform.rotate(roof_texture, 45)
            scaled_roof = pygame.transform.scale(rotated_roof, (self.tile_width, self.tile_height))
            
            # Position roof to match wall renderer positioning
            # Wall renderer uses: floor_y - tile_height // 2 - wall_height
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - wall_height
            roof_rect = scaled_roof.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(scaled_roof, roof_rect)
        else:
            # Fallback: simple dark rectangle (also rotated for consistency)
            roof_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
            roof_surface.fill((80, 40, 20))  # Dark brown
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - wall_height
            roof_rect = roof_surface.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(roof_surface, roof_rect)
    
    def render_roof_tile_at_floor_level(self, surface, screen_x, screen_y):
        """Render a roof tile at floor level (for interior floors)"""
        roof_texture = self.asset_loader.get_image('roof_texture')
        if roof_texture:
            # FIXED: Rotate the roof texture 45 degrees to match isometric tiles
            rotated_roof = pygame.transform.rotate(roof_texture, 45)
            scaled_roof = pygame.transform.scale(rotated_roof, (self.tile_width, self.tile_height))
            
            # FIXED: Position interior roofs at three-quarters wall height
            # Use 3/4 wall height instead of 1/2 wall height for interior roofs
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - (wall_height * 3 // 4)
            roof_rect = scaled_roof.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(scaled_roof, roof_rect)
        else:
            # Fallback: simple dark rectangle (also rotated for consistency)
            roof_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
            roof_surface.fill((80, 40, 20))  # Dark brown
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - (wall_height * 3 // 4)
            roof_rect = roof_surface.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(roof_surface, roof_rect)
    
    def render_wall_outline(self, surface, screen_x, screen_y, tile_type):
        """Render wall outline when player is inside"""
        # Use window texture for window walls, regular wall texture for others
        if tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL]:
            wall_texture = self.asset_loader.get_image('wall_texture_window')
            if not wall_texture:
                wall_texture = self.asset_loader.get_image('wall_texture')
        else:
            wall_texture = self.asset_loader.get_image('wall_texture')
        
        if wall_texture:
            rotated_wall = pygame.transform.rotate(wall_texture, 45)
            scaled_wall = pygame.transform.scale(rotated_wall, (self.tile_width, self.tile_height))
            wall_rect = scaled_wall.get_rect()
            wall_rect.center = (screen_x, screen_y)
            surface.blit(scaled_wall, wall_rect)
        else:
            # Fallback: gray diamond (or blue-tinted for windows)
            wall_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
            if tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL]:
                wall_surface.fill((150, 150, 200))  # Blue-tinted for windows
            else:
                wall_surface.fill((150, 150, 150))  # Gray for regular walls
            wall_rect = wall_surface.get_rect()
            wall_rect.center = (screen_x, screen_y)
            surface.blit(wall_surface, wall_rect)
    
    def render_interior_door(self, surface, screen_x, screen_y):
        """Render door when player is inside building"""
        archway_texture = self.asset_loader.get_image('archway_texture')
        if archway_texture:
            # Rotate 90 degrees first, then 45 for isometric
            rotated_archway = pygame.transform.rotate(archway_texture, 90)
            final_archway = pygame.transform.rotate(rotated_archway, 45)
            scaled_archway = pygame.transform.scale(final_archway, (self.tile_width, self.tile_height))
            archway_rect = scaled_archway.get_rect()
            archway_rect.center = (screen_x, screen_y)
            surface.blit(scaled_archway, archway_rect)
        else:
            # Fallback: light brown diamond
            door_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
            door_surface.fill((200, 150, 100))
            door_rect = door_surface.get_rect()
            door_rect.center = (screen_x, screen_y)
            surface.blit(door_surface, door_rect)