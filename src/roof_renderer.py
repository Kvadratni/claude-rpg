"""
Roof Renderer Module

This module handles dynamic roof rendering for buildings. When the player is outside
a building, roofs are rendered. When inside, roofs are hidden to show the interior.
"""

import pygame
from typing import Optional, Tuple, List, Dict, Set


class RoofRenderer:
    """Handles dynamic roof rendering for buildings"""
    
    def __init__(self, level_instance):
        """Initialize with reference to level instance for access to shared data"""
        self.level = level_instance
        self.asset_loader = level_instance.asset_loader
        
        # Cache for building detection
        self.building_cache = {}
        self.building_perimeters = {}
        
        # Load roof texture
        self.roof_texture = None
        self.load_roof_texture()
        
    @property
    def tiles(self):
        """Access to level's tiles array"""
        return self.level.tiles
        
    @property
    def tile_width(self):
        """Access to level's tile width"""
        return self.level.tile_width
        
    @property
    def tile_height(self):
        """Access to level's tile height"""
        return self.level.tile_height
    
    @property
    def width(self):
        """Access to level's width"""
        return self.level.width
        
    @property
    def height(self):
        """Access to level's height"""
        return self.level.height
        
    # Tile constants - delegate to level
    @property
    def TILE_WALL(self):
        return self.level.TILE_WALL
        
    @property
    def TILE_WALL_CORNER_TL(self):
        return self.level.TILE_WALL_CORNER_TL
        
    @property
    def TILE_WALL_CORNER_TR(self):
        return self.level.TILE_WALL_CORNER_TR
        
    @property
    def TILE_WALL_CORNER_BL(self):
        return self.level.TILE_WALL_CORNER_BL
        
    @property
    def TILE_WALL_CORNER_BR(self):
        return self.level.TILE_WALL_CORNER_BR
        
    @property
    def TILE_WALL_HORIZONTAL(self):
        return self.level.TILE_WALL_HORIZONTAL
        
    @property
    def TILE_WALL_VERTICAL(self):
        return self.level.TILE_WALL_VERTICAL
        
    @property
    def TILE_WALL_WINDOW(self):
        return self.level.TILE_WALL_WINDOW
        
    @property
    def TILE_WALL_WINDOW_HORIZONTAL(self):
        return self.level.TILE_WALL_WINDOW_HORIZONTAL
        
    @property
    def TILE_WALL_WINDOW_VERTICAL(self):
        return self.level.TILE_WALL_WINDOW_VERTICAL
        
    @property
    def TILE_DOOR(self):
        return getattr(self.level, 'TILE_DOOR', None)
        
    @property
    def TILE_BRICK(self):
        return getattr(self.level, 'TILE_BRICK', None)
    
    def load_roof_texture(self):
        """Load roof texture from assets"""
        if self.asset_loader:
            roof_image = self.asset_loader.get_image("roof_texture")
            if roof_image:
                self.roof_texture = roof_image
            else:
                # Create a simple dark roof texture as fallback
                self.roof_texture = pygame.Surface((64, 64))
                self.roof_texture.fill((60, 40, 20))  # Dark brown
                # Add some texture lines
                for i in range(0, 64, 8):
                    pygame.draw.line(self.roof_texture, (80, 60, 40), (0, i), (64, i), 1)
                    pygame.draw.line(self.roof_texture, (80, 60, 40), (i, 0), (i, 64), 1)
    
    def is_wall_tile(self, tile_type):
        """Check if a tile type is any kind of wall"""
        if tile_type is None:
            return False
        wall_types = [
            self.TILE_WALL, self.TILE_WALL_CORNER_TL, self.TILE_WALL_CORNER_TR,
            self.TILE_WALL_CORNER_BL, self.TILE_WALL_CORNER_BR,
            self.TILE_WALL_HORIZONTAL, self.TILE_WALL_VERTICAL, self.TILE_WALL_WINDOW,
            self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL
        ]
        return tile_type in wall_types
    
    def get_tile_at(self, x, y):
        """Get tile at coordinates with bounds checking"""
        # Use get_tile method if available (for chunk-based worlds)
        if hasattr(self.level, 'get_tile'):
            return self.level.get_tile(x, y)
        else:
            # Fallback to tiles array for template-based worlds
            if not (0 <= x < self.width and 0 <= y < self.height):
                return None
            if hasattr(self.level, 'tiles') and self.level.tiles and len(self.level.tiles) > 0:
                return self.tiles[y][x]
            return None
    
    def is_interior_tile(self, x, y):
        """Check if a tile is an interior floor tile (brick)"""
        tile = self.get_tile_at(x, y)
        return tile == self.TILE_BRICK
    
    def find_building_at(self, x, y):
        """Find the building that contains the given coordinates"""
        # Check cache first
        cache_key = (x, y)
        if cache_key in self.building_cache:
            return self.building_cache[cache_key]
        
        # If this is an interior tile, find the building it belongs to
        if self.is_interior_tile(x, y):
            building = self._trace_building_from_interior(x, y)
            self.building_cache[cache_key] = building
            return building
        
        # If this is a wall tile, find the building it belongs to
        tile = self.get_tile_at(x, y)
        if self.is_wall_tile(tile) or tile == self.TILE_DOOR:
            building = self._trace_building_from_wall(x, y)
            self.building_cache[cache_key] = building
            return building
        
        # Not part of a building
        self.building_cache[cache_key] = None
        return None
    
    def _trace_building_from_interior(self, start_x, start_y):
        """Trace a building's boundaries starting from an interior tile"""
        # Use flood fill to find all connected interior tiles
        interior_tiles = set()
        wall_tiles = set()
        door_tiles = set()
        
        # Flood fill to find all interior tiles
        to_visit = [(start_x, start_y)]
        visited = set()
        
        while to_visit:
            x, y = to_visit.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            
            tile = self.get_tile_at(x, y)
            if tile == self.TILE_BRICK:
                interior_tiles.add((x, y))
                # Check adjacent tiles
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in visited:
                        to_visit.append((nx, ny))
            elif self.is_wall_tile(tile):
                wall_tiles.add((x, y))
            elif tile == self.TILE_DOOR:
                door_tiles.add((x, y))
        
        # Find the bounding box of the building
        if interior_tiles or wall_tiles:
            all_tiles = interior_tiles | wall_tiles | door_tiles
            min_x = min(x for x, y in all_tiles)
            max_x = max(x for x, y in all_tiles)
            min_y = min(y for x, y in all_tiles)
            max_y = max(y for x, y in all_tiles)
            
            building = {
                'min_x': min_x,
                'max_x': max_x,
                'min_y': min_y,
                'max_y': max_y,
                'interior_tiles': interior_tiles,
                'wall_tiles': wall_tiles,
                'door_tiles': door_tiles
            }
            
            return building
        
        return None
    
    def _trace_building_from_wall(self, start_x, start_y):
        """Trace a building's boundaries starting from a wall tile"""
        # Find connected walls and any interior they enclose
        wall_tiles = set()
        door_tiles = set()
        
        # Flood fill to find all connected walls
        to_visit = [(start_x, start_y)]
        visited = set()
        
        while to_visit:
            x, y = to_visit.pop()
            if (x, y) in visited:
                continue
            visited.add((x, y))
            
            tile = self.get_tile_at(x, y)
            if self.is_wall_tile(tile):
                wall_tiles.add((x, y))
                # Check adjacent tiles for more walls
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in visited:
                        next_tile = self.get_tile_at(nx, ny)
                        if self.is_wall_tile(next_tile) or next_tile == self.TILE_DOOR:
                            to_visit.append((nx, ny))
            elif tile == self.TILE_DOOR:
                door_tiles.add((x, y))
                # Continue tracing through doors
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in visited:
                        next_tile = self.get_tile_at(nx, ny)
                        if self.is_wall_tile(next_tile) or next_tile == self.TILE_DOOR:
                            to_visit.append((nx, ny))
        
        # Find interior tiles enclosed by these walls
        if wall_tiles:
            min_x = min(x for x, y in wall_tiles)
            max_x = max(x for x, y in wall_tiles)
            min_y = min(y for x, y in wall_tiles)
            max_y = max(y for x, y in wall_tiles)
            
            interior_tiles = set()
            # Check all tiles within the bounding box
            for y in range(min_y, max_y + 1):
                for x in range(min_x, max_x + 1):
                    if (x, y) not in wall_tiles and (x, y) not in door_tiles:
                        tile = self.get_tile_at(x, y)
                        if tile == self.TILE_BRICK:
                            interior_tiles.add((x, y))
            
            building = {
                'min_x': min_x,
                'max_x': max_x,
                'min_y': min_y,
                'max_y': max_y,
                'interior_tiles': interior_tiles,
                'wall_tiles': wall_tiles,
                'door_tiles': door_tiles
            }
            
            return building
        
        return None
    
    def is_player_inside_building(self, player_x, player_y):
        """Check if the player is inside a building"""
        # Convert player world coordinates to tile coordinates
        tile_x = int(player_x)
        tile_y = int(player_y)
        
        # Check if player is on an interior tile
        if self.is_interior_tile(tile_x, tile_y):
            return True
        
        # Check if player is on a door tile (considered inside)
        tile = self.get_tile_at(tile_x, tile_y)
        if tile == self.TILE_DOOR:
            return True
        
        return False
    
    def get_building_perimeter(self, building):
        """Get the perimeter tiles around a building for proximity detection"""
        if not building:
            return set()
        
        building_id = (building['min_x'], building['min_y'], building['max_x'], building['max_y'])
        if building_id in self.building_perimeters:
            return self.building_perimeters[building_id]
        
        perimeter = set()
        all_building_tiles = building['interior_tiles'] | building['wall_tiles'] | building['door_tiles']
        
        # Find all tiles adjacent to the building
        for x, y in all_building_tiles:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in all_building_tiles:
                    perimeter.add((nx, ny))
        
        self.building_perimeters[building_id] = perimeter
        return perimeter
    
    def is_player_near_building(self, player_x, player_y, building, proximity_distance=2):
        """Check if player is within proximity distance of a building"""
        if not building:
            return False
        
        tile_x = int(player_x)
        tile_y = int(player_y)
        
        # Check if player is within the proximity distance of the building
        min_x = building['min_x'] - proximity_distance
        max_x = building['max_x'] + proximity_distance
        min_y = building['min_y'] - proximity_distance
        max_y = building['max_y'] + proximity_distance
        
        return min_x <= tile_x <= max_x and min_y <= tile_y <= max_y
    
    def should_render_roof(self, building_x, building_y, player_x, player_y):
        """Determine if a roof should be rendered at the given building coordinates"""
        # Find the building at this location
        building = self.find_building_at(building_x, building_y)
        if not building:
            return False
        
        # If player is inside any building, don't render any roofs
        if self.is_player_inside_building(player_x, player_y):
            # Check if player is inside THIS specific building
            player_tile_x = int(player_x)
            player_tile_y = int(player_y)
            
            if ((player_tile_x, player_tile_y) in building['interior_tiles'] or
                (player_tile_x, player_tile_y) in building['door_tiles']):
                # Player is inside this building - don't render its roof
                return False
        
        # If player is near this building, don't render its roof
        if self.is_player_near_building(player_x, player_y, building, proximity_distance=1):
            return False
        
        # Player is outside and not near - render the roof
        return True
    
    def render_roof_at_position(self, surface, building_x, building_y, screen_x, screen_y):
        """Render a roof tile at the given position"""
        # Find the building to get its full extent
        building = self.find_building_at(building_x, building_y)
        if not building:
            return
        
        # Render roof for interior tiles, wall tiles, and door tiles (entire building)
        if ((building_x, building_y) not in building['interior_tiles'] and
            (building_x, building_y) not in building['wall_tiles'] and
            (building_x, building_y) not in building['door_tiles']):
            return
        
        # Roof height above the ground
        roof_height = 32
        
        # Calculate roof position (above the tile)
        roof_screen_y = screen_y - roof_height
        
        # Create roof surface - make it VERY obvious for testing
        roof_surface = pygame.Surface((self.tile_width, self.tile_height), pygame.SRCALPHA)
        
        # Use bright red color for testing instead of texture
        roof_surface.fill((255, 0, 0))  # Bright red
        
        # Make it fully opaque for testing
        roof_surface.set_alpha(255)
        
        # Render the roof
        roof_rect = roof_surface.get_rect()
        roof_rect.center = (screen_x, roof_screen_y)
        surface.blit(roof_surface, roof_rect)
        
        # Add thick border for visibility
        pygame.draw.rect(surface, (255, 255, 0), roof_rect, 3)  # Yellow border
    
    def clear_cache(self):
        """Clear the building detection cache (call when level changes)"""
        self.building_cache.clear()
        self.building_perimeters.clear()