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
        
        # OPTIMIZATION: Cache player building detection for this frame
        player_x, player_y = int(self.player.x), int(self.player.y)
        
        # Calculate visible tile range - REDUCED for better performance
        visible_width = (screen_width // self.tile_width) + 4  # Reduced from 10 to 4
        visible_height = (game_area_height // (self.tile_height // 2)) + 8  # Reduced from 30 to 8
        
        # Calculate center tile
        center_x = int(self.player.x)
        center_y = int(self.player.y)
        
        # Calculate tile range - render visible area (optimized for chunked worlds)
        # FIXED: Don't use max(0, ...) for chunked worlds that can have negative coordinates
        start_x = center_x - visible_width
        end_x = center_x + visible_width
        start_y = center_y - visible_height
        end_y = center_y + visible_height
        
        # Only recalculate building detection if player moved to a new tile
        if not hasattr(self, '_last_player_pos') or self._last_player_pos != (player_x, player_y):
            self._update_building_states(player_x, player_y)
            self._update_entity_visibility_cache()  # Cache entity visibility too
            self._update_tile_visibility_cache(start_x, end_x, start_y, end_y)  # Cache tile visibility too
            self._update_entity_sorting_cache()  # Cache entity sorting too
            self._last_player_pos = (player_x, player_y)
        
        # Render tiles in proper isometric order (back to front)
        # This ensures proper depth sorting for buildings
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.render_tile_at_position(game_surface, x, y)
        
        # Use cached sorted entities instead of sorting every frame
        sorted_entities = self._get_cached_sorted_entities()
        
        # Render entities to game surface using cached visibility
        for entity in sorted_entities:
            # Use cached visibility check instead of expensive per-frame calculations
            if self._should_render_entity_cached(entity):
                entity.render(game_surface, self.camera_x, self.camera_y, self.iso_renderer)
        
        # Blit game surface to main screen
        screen.blit(game_surface, (0, 0))
        
        # Render XP bar at the top
        self.render_xp_bar(screen)
        
        # Render bottom UI panel (equipment, inventory button, game log)
        self.render_ui(screen)
        
        # Render dialogue window 
        if self.player.current_dialogue and self.player.current_dialogue.show:
            self.player.current_dialogue.render(screen)
        
        # Render AI chat window 
        if hasattr(self.player, 'current_ai_chat') and self.player.current_ai_chat and self.player.current_ai_chat.is_active:
            self.player.current_ai_chat.render(screen)
        
        # Render shops on top of everything (including chat windows) - HIGHEST PRIORITY
        for npc in self.npcs:
            if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                # Set player items for sell mode
                npc.shop.set_player_items(self.player.inventory.items)
                npc.shop.render(screen)
        
        # Render player's current shop (from MCP system) - ABSOLUTE HIGHEST PRIORITY
        if hasattr(self.player, 'current_shop') and self.player.current_shop and self.player.current_shop.show:
            # Set player items for sell mode
            self.player.current_shop.set_player_items(self.player.inventory.items)
            self.player.current_shop.render(screen)
    
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
        
        # Determine if this tile is part of a building and if player is close to the building
        is_building_tile = self.is_simple_building_tile(tile_type)  # Use fast version
        should_render_roof = False  # Default to NO roof
        
        if is_building_tile:
            # OPTIMIZATION: Use cached tile visibility instead of expensive per-tile checks
            should_render_roof = not self._get_cached_tile_visibility(x, y)
        
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
            # Player is far from building - render with roof
            if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                # Render walls with roof texture as top face
                self.render_wall_with_roof_top(surface, screen_x, screen_y, tile_type, x, y)
            elif tile_type == self.TILE_DOOR and hasattr(self, 'door_renderer'):
                # Door renderer with roof
                self.door_renderer.render_door_tile(surface, screen_x, screen_y, tile_type, self, self.tile_width, self.tile_height)
            else:
                # For interior floors, render the roof at floor level
                self.render_roof_tile_at_floor_level(surface, screen_x, screen_y)
        else:
            # Player is close - "no walls" mode - show interior
            if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                if tile_type == self.TILE_DOOR:
                    # Show door as archway when close
                    self.render_interior_door(surface, screen_x, screen_y)
                else:
                    # Show wall outline when close
                    self.render_wall_outline(surface, screen_x, screen_y, tile_type)
            elif tile_type == self.TILE_DOOR and hasattr(self, 'door_renderer'):
                # Show door as archway when close
                self.render_interior_door(surface, screen_x, screen_y)
    
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
    
    def is_entity_blocked_by_building(self, entity_x, entity_y, player_x, player_y):
        """
        Simplified check if there's a building between entity and player
        
        Args:
            entity_x, entity_y: Entity position
            player_x, player_y: Player position
            
        Returns:
            True if entity is blocked by a building
        """
        # Check a few points along the line between player and entity
        steps = max(abs(entity_x - player_x), abs(entity_y - player_y))
        if steps == 0:
            return False
        
        # Check 3 points along the line
        for i in range(1, min(4, steps)):
            t = i / steps
            check_x = int(player_x + t * (entity_x - player_x))
            check_y = int(player_y + t * (entity_y - player_y))
            
            # Get tile type at this position
            if hasattr(self, 'get_tile'):
                tile_type = self.get_tile(check_x, check_y)
            else:
                if not (0 <= check_y < len(self.tiles) and 0 <= check_x < len(self.tiles[0])):
                    continue
                tile_type = self.tiles[check_y][check_x]
            
            # If there's a wall tile, it's blocking
            if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                return True
        
        return False
    
    def is_entity_hidden_by_roof(self, entity_x, entity_y):
        """Check if an entity is hidden by a roof tile (simple and fast)"""
        # Check if there's a wall tile adjacent to the entity that would have a roof
        # Only check immediate adjacent tiles for performance
        for dx, dy in [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]:
            check_x = entity_x + dx
            check_y = entity_y + dy
            
            # Get tile type at this position
            if hasattr(self, 'get_tile'):
                tile_type = self.get_tile(check_x, check_y)
            else:
                if not (0 <= check_y < len(self.tiles) and 0 <= check_x < len(self.tiles[0])):
                    continue
                tile_type = self.tiles[check_y][check_x]
            
            # Check if this is a wall tile that has a roof
            if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
                # Simple check: if player is not at this wall position, it has a roof
                player_x, player_y = int(self.player.x), int(self.player.y)
                if not (check_x == player_x and check_y == player_y):
                    # Check if player is under this building's roof
                    if self.is_player_under_roof(check_x, check_y):
                        return False  # Player is under roof, so show entities
                    
                    # FIXED: More strict check for entities being "behind" buildings
                    # Only hide entities if they are clearly behind the building AND
                    # the building is between the entity and the player
                    if entity_y > check_y and entity_y > player_y:
                        # Entity is behind the wall and behind the player - hide it
                        return True
                    
                    # Don't hide entities that are in front or to the sides
                    return False
        
        return False
    
    def is_player_under_roof(self, wall_x, wall_y):
        """Check if player is positioned under a roof tile"""
        player_x, player_y = int(self.player.x), int(self.player.y)
        
        # Check if player is within 1 tile of this wall
        distance = max(abs(player_x - wall_x), abs(player_y - wall_y))
        return distance <= 1
    
    def render_roof_tile(self, surface, screen_x, screen_y):
        """Render a roof tile at the given position"""
        roof_texture = self.asset_loader.get_image('roof_texture')
        if roof_texture:
            # FIXED: Rotate the roof texture 45 degrees to match isometric tiles
            rotated_roof = pygame.transform.rotate(roof_texture, 45)
            # FIXED: Make roof tiles slightly bigger to eliminate gaps (2% larger)
            scaled_roof = pygame.transform.scale(rotated_roof, (int(self.tile_width * 1.02), int(self.tile_height * 1.02)))
            
            # Position roof to match wall renderer positioning
            # Wall renderer uses: floor_y - tile_height // 2 - wall_height
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - wall_height
            roof_rect = scaled_roof.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(scaled_roof, roof_rect)
        else:
            # Fallback: simple dark rectangle (also rotated for consistency)
            roof_surface = pygame.Surface((int(self.tile_width * 1.02), int(self.tile_height * 1.02)), pygame.SRCALPHA)
            roof_surface.fill((80, 40, 20))  # Dark brown
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - wall_height
            roof_rect = roof_surface.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(roof_surface, roof_rect)
    
    def render_roof_tile_at_floor_level(self, surface, screen_x, screen_y):
        """Render a roof tile at floor level (for interior floors) with cached textures"""
        # Cache the transformed roof texture to avoid repeated transforms
        if not hasattr(self, '_cached_roof_texture'):
            roof_texture = self.asset_loader.get_image('roof_texture')
            if roof_texture:
                # FIXED: Rotate the roof texture 45 degrees to match isometric tiles
                rotated_roof = pygame.transform.rotate(roof_texture, 45)
                # FIXED: Make roof tiles slightly bigger to eliminate gaps (2% larger)
                self._cached_roof_texture = pygame.transform.scale(rotated_roof, (int(self.tile_width * 1.02), int(self.tile_height * 1.02)))
            else:
                # Fallback: simple dark rectangle (also rotated for consistency)
                roof_surface = pygame.Surface((int(self.tile_width * 1.02), int(self.tile_height * 1.02)), pygame.SRCALPHA)
                roof_surface.fill((80, 40, 20))  # Dark brown
                self._cached_roof_texture = roof_surface
        
        if self._cached_roof_texture:
            # FIXED: Position interior roofs slightly lower (2px down from 3/4 height)
            wall_height = 48
            roof_y = screen_y - self.tile_height // 2 - (wall_height * 3 // 4) + 2
            roof_rect = self._cached_roof_texture.get_rect()
            roof_rect.center = (screen_x, roof_y)
            surface.blit(self._cached_roof_texture, roof_rect)
    
    def render_wall_outline(self, surface, screen_x, screen_y, tile_type):
        """Render wall outline when player is inside with cached textures"""
        # Cache wall textures to avoid repeated transforms
        cache_key = f"wall_outline_{tile_type}"
        if not hasattr(self, '_cached_wall_textures'):
            self._cached_wall_textures = {}
        
        if cache_key not in self._cached_wall_textures:
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
                self._cached_wall_textures[cache_key] = scaled_wall
            else:
                # Fallback: gray diamond (or blue-tinted for windows)
                wall_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
                if tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL]:
                    wall_surface.fill((150, 150, 200))  # Blue-tinted for windows
                else:
                    wall_surface.fill((150, 150, 150))  # Gray for regular walls
                self._cached_wall_textures[cache_key] = wall_surface
        
        if cache_key in self._cached_wall_textures:
            wall_rect = self._cached_wall_textures[cache_key].get_rect()
            wall_rect.center = (screen_x, screen_y)
            surface.blit(self._cached_wall_textures[cache_key], wall_rect)
    
    def render_interior_door(self, surface, screen_x, screen_y):
        """Render door when player is inside building with cached texture"""
        # Cache the transformed archway texture
        if not hasattr(self, '_cached_archway_texture'):
            archway_texture = self.asset_loader.get_image('archway_texture')
            if archway_texture:
                # Rotate 90 degrees first, then 45 for isometric
                rotated_archway = pygame.transform.rotate(archway_texture, 90)
                final_archway = pygame.transform.rotate(rotated_archway, 45)
                self._cached_archway_texture = pygame.transform.scale(final_archway, (self.tile_width, self.tile_height))
            else:
                # Fallback: light brown diamond
                door_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
                door_surface.fill((200, 150, 100))
                self._cached_archway_texture = door_surface
        
        if self._cached_archway_texture:
            archway_rect = self._cached_archway_texture.get_rect()
            archway_rect.center = (screen_x, screen_y)
            surface.blit(self._cached_archway_texture, archway_rect)
    
    def _get_buildings_near_player(self, player_x, player_y):
        """
        Memoized building detection: cache building bounds to avoid repeated flood fills
        """
        # Initialize building cache if not exists
        if not hasattr(self, '_building_cache'):
            self._building_cache = {}  # Maps tile positions to building bounds
        
        buildings_to_flatten = set()
        
        # Check immediate area around player
        search_radius = 2
        
        for dy in range(-search_radius, search_radius + 1):
            for dx in range(-search_radius, search_radius + 1):
                check_x = player_x + dx
                check_y = player_y + dy
                
                # Get tile type (fast check)
                if hasattr(self, 'get_tile'):
                    tile_type = self.get_tile(check_x, check_y)
                else:
                    if not (0 <= check_y < len(self.tiles) and 0 <= check_x < len(self.tiles[0])):
                        continue
                    tile_type = self.tiles[check_y][check_x]
                
                # If this is a building tile and player is close enough
                if self.is_simple_building_tile(tile_type):
                    distance = max(abs(player_x - check_x), abs(player_y - check_y))
                    if distance <= 1:  # Player within 1 tile
                        # Get or compute building bounds for this tile
                        building_bounds = self._get_cached_building_bounds(check_x, check_y)
                        if building_bounds:
                            buildings_to_flatten.add(building_bounds)
        
        return buildings_to_flatten
        
    def _update_building_states(self, player_x, player_y):
        """
        Update building flattened states based on player position
        Only update when states actually change
        """
        # Initialize building state cache if not exists
        if not hasattr(self, '_building_states'):
            self._building_states = {}  # Maps building bounds to flattened state
        
        # Get buildings that should be flattened based on current position
        buildings_to_flatten = self._get_buildings_near_player(player_x, player_y)
        
        # Only update states that have changed
        # First, unflatten buildings that are no longer in range
        for building_bounds in list(self._building_states.keys()):
            if self._building_states[building_bounds] and building_bounds not in buildings_to_flatten:
                self._building_states[building_bounds] = False
        
        # Then, flatten buildings that are now in range
        for building_bounds in buildings_to_flatten:
            if not self._building_states.get(building_bounds, False):
                self._building_states[building_bounds] = True
    
    def _get_cached_building_bounds(self, tile_x, tile_y):
        """
        Get building bounds with caching to avoid repeated flood fills
        """
        cache_key = (tile_x, tile_y)
        
        # Check if we already computed bounds for this tile
        if cache_key in self._building_cache:
            return self._building_cache[cache_key]
        
        # Compute building bounds using flood fill
        building_bounds = self._compute_building_bounds(tile_x, tile_y)
        
        # Cache the result for ALL tiles in this building
        if building_bounds:
            min_x, min_y, max_x, max_y, building_tiles = building_bounds
            bounds_tuple = (min_x, min_y, max_x, max_y)
            
            # Cache bounds for every tile in this building
            for bx, by in building_tiles:
                self._building_cache[(bx, by)] = bounds_tuple
            
            return bounds_tuple
        else:
            # Cache negative result
            self._building_cache[cache_key] = None
            return None
    
    def _compute_building_bounds(self, tile_x, tile_y):
        """
        Compute building bounds using flood fill (only called once per building)
        """
        visited = set()
        building_tiles = set()
        to_visit = [(tile_x, tile_y)]
        
        # Limit search to prevent performance issues
        max_iterations = 200
        iterations = 0
        
        while to_visit and iterations < max_iterations:
            iterations += 1
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
            
            if self.is_simple_building_tile(tile_type):
                building_tiles.add((curr_x, curr_y))
                # Check adjacent tiles (4-directional only for performance)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = curr_x + dx, curr_y + dy
                    if (nx, ny) not in visited:
                        to_visit.append((nx, ny))
        
        if building_tiles:
            min_x = min(x for x, y in building_tiles)
            max_x = max(x for x, y in building_tiles)
            min_y = min(y for x, y in building_tiles)
            max_y = max(y for x, y in building_tiles)
            return (min_x, min_y, max_x, max_y, building_tiles)
        
        return None

    
    def is_simple_building_tile(self, tile_type):
        """Fast building tile check without expensive operations"""
        if hasattr(self, 'wall_renderer') and self.wall_renderer.is_wall_tile(tile_type):
            return True
        if tile_type == self.TILE_DOOR:
            return True
        if tile_type == self.TILE_BRICK:  # Interior floor
            return True
        return False
    
    def _is_player_near_building_tile(self, tile_x, tile_y):
        """
        Check if this building tile should be flattened using cached building states
        """
        if not hasattr(self, '_building_states'):
            return False
        
        # Get cached building bounds for this tile
        if not hasattr(self, '_building_cache'):
            return False
            
        cache_key = (tile_x, tile_y)
        if cache_key not in self._building_cache:
            return False
            
        building_bounds = self._building_cache[cache_key]
        if not building_bounds:
            return False
        
        # Check cached building state
        return self._building_states.get(building_bounds, False)
    
    def _update_entity_visibility_cache(self):
        """
        Cache entity visibility states to avoid expensive per-frame checks
        """
        if not hasattr(self, '_entity_visibility_cache'):
            self._entity_visibility_cache = {}
        
        # Get all entities
        all_entities = []
        all_entities.extend(getattr(self, 'enemies', []))
        all_entities.extend(getattr(self, 'npcs', []))
        all_entities.extend(getattr(self, 'items', []))
        all_entities.extend(getattr(self, 'objects', []))
        all_entities.extend(getattr(self, 'chests', []))
        all_entities.extend(getattr(self, 'furniture', []))
        
        # Cache visibility for each entity
        for entity in all_entities:
            entity_id = id(entity)  # Use object ID as unique identifier
            entity_x, entity_y = int(entity.x), int(entity.y)
            
            # Check if entity is inside a building
            if hasattr(self, 'get_tile'):
                entity_tile_type = self.get_tile(entity_x, entity_y)
            else:
                if 0 <= entity_y < len(self.tiles) and 0 <= entity_x < len(self.tiles[0]):
                    entity_tile_type = self.tiles[entity_y][entity_x]
                else:
                    entity_tile_type = None
            
            # Check if entity is on a building tile (interior floor or wall)
            is_entity_in_building = (entity_tile_type == self.TILE_BRICK or 
                                   (hasattr(self, 'wall_renderer') and 
                                    self.wall_renderer.is_wall_tile(entity_tile_type)) or
                                   entity_tile_type == self.TILE_DOOR)
            
            if is_entity_in_building:
                # Entity is inside a building - check if player is close using cached data
                should_render = self._is_player_near_building_tile(entity_x, entity_y)
            else:
                # Entity is outside - always render
                should_render = True
            
            self._entity_visibility_cache[entity_id] = should_render
    
    def _should_render_entity_cached(self, entity):
        """
        Fast entity visibility check using cached data
        """
        # Always render the player
        if entity == self.player:
            return True
        
        # Use cached visibility if available
        if hasattr(self, '_entity_visibility_cache'):
            entity_id = id(entity)
            return self._entity_visibility_cache.get(entity_id, True)  # Default to visible
        
        # Fallback to always visible if cache not ready
        return True
    
    def _update_tile_visibility_cache(self, start_x, end_x, start_y, end_y):
        """
        Cache tile visibility states for all visible tiles using already-computed building states
        """
        if not hasattr(self, '_tile_visibility_cache'):
            self._tile_visibility_cache = {}
        
        # Clear old cache entries (only keep current visible area)
        self._tile_visibility_cache.clear()
        
        # Use already-computed building states instead of expensive per-tile checks
        if not hasattr(self, '_building_states') or not hasattr(self, '_building_cache'):
            return  # No building data available
        
        # Cache visibility for all visible building tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Get tile type
                if hasattr(self, 'get_tile'):
                    tile_type = self.get_tile(x, y)
                    if tile_type is None:
                        continue  # Don't cache unloaded chunks
                else:
                    if not hasattr(self, 'tiles') or not self.tiles or len(self.tiles) == 0:
                        continue
                    if not (0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[0])):
                        continue
                    tile_type = self.tiles[y][x]
                
                # Only cache building tiles (others don't need visibility checks)
                if self.is_simple_building_tile(tile_type):
                    tile_key = (x, y)
                    
                    # Fast lookup using already-cached building bounds and states
                    cache_key = (x, y)
                    if cache_key in self._building_cache:
                        building_bounds = self._building_cache[cache_key]
                        if building_bounds:
                            is_visible = self._building_states.get(building_bounds, False)
                            self._tile_visibility_cache[tile_key] = is_visible
                        else:
                            self._tile_visibility_cache[tile_key] = False
                    else:
                        self._tile_visibility_cache[tile_key] = False
    
    def _get_cached_tile_visibility(self, tile_x, tile_y):
        """
        Fast tile visibility check using cached data
        """
        if hasattr(self, '_tile_visibility_cache'):
            tile_key = (tile_x, tile_y)
            return self._tile_visibility_cache.get(tile_key, False)  # Default to not visible (show roof)
        
        # Fallback to expensive check if cache not ready
        return self._is_player_near_building_tile(tile_x, tile_y)
    
    def _update_entity_sorting_cache(self):
        """
        Cache sorted entities to avoid expensive sorting every frame
        """
        # Collect all entities for depth sorting
        all_entities = []
        all_entities.append(self.player)
        all_entities.extend(getattr(self, 'enemies', []))
        all_entities.extend(getattr(self, 'npcs', []))
        all_entities.extend(getattr(self, 'items', []))
        all_entities.extend(getattr(self, 'objects', []))
        all_entities.extend(getattr(self, 'chests', []))
        all_entities.extend(getattr(self, 'furniture', []))
        
        # Sort entities by depth and cache the result
        self._cached_sorted_entities = sort_by_depth(all_entities)
    
    def _get_cached_sorted_entities(self):
        """
        Get cached sorted entities, falling back to immediate sorting if cache not ready
        """
        if hasattr(self, '_cached_sorted_entities'):
            return self._cached_sorted_entities
        
        # Fallback: collect and sort immediately (should rarely happen)
        all_entities = []
        all_entities.append(self.player)
        all_entities.extend(getattr(self, 'enemies', []))
        all_entities.extend(getattr(self, 'npcs', []))
        all_entities.extend(getattr(self, 'items', []))
        all_entities.extend(getattr(self, 'objects', []))
        all_entities.extend(getattr(self, 'chests', []))
        all_entities.extend(getattr(self, 'furniture', []))
        
        return sort_by_depth(all_entities)