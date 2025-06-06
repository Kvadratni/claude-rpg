"""
Wall Renderer Module

This module contains all wall-related functionality extracted from level.py
including wall creation, loading, rendering, and utility methods.
"""

import pygame
from typing import Optional, Tuple, List


class WallRenderer:
    """Handles all wall-related rendering and sprite management"""
    
    def __init__(self, level_instance):
        """Initialize with reference to level instance for access to shared data"""
        self.level = level_instance
        self.asset_loader = level_instance.asset_loader
        
    @property
    def tile_sprites(self):
        """Access to level's tile sprites"""
        return self.level.tile_sprites
        
    @property
    def tiles(self):
        """Access to level's tiles array"""
        return self.level.tiles
        
    @property
    def level_data(self):
        """Access to level's level_data"""
        return getattr(self.level, 'level_data', None)
        
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
    def TILE_DOOR_HORIZONTAL(self):
        return getattr(self.level, 'TILE_DOOR_HORIZONTAL', None)
        
    @property
    def TILE_DOOR_VERTICAL(self):
        return getattr(self.level, 'TILE_DOOR_VERTICAL', None)
        
    def create_wall_corner_sprites(self, base_wall_sprite):
        """Create corner wall variations from base wall sprite"""
        # Top-left corner - add corner accent
        tl_corner = base_wall_sprite.copy()
        # Add a small corner decoration (darker edge)
        corner_size = 8
        pygame.draw.rect(tl_corner, (120, 120, 120), (0, 0, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_TL] = tl_corner
        
        # Top-right corner
        tr_corner = base_wall_sprite.copy()
        pygame.draw.rect(tr_corner, (120, 120, 120), 
                        (base_wall_sprite.get_width() - corner_size, 0, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_TR] = tr_corner
        
        # Bottom-left corner
        bl_corner = base_wall_sprite.copy()
        pygame.draw.rect(bl_corner, (120, 120, 120), 
                        (0, base_wall_sprite.get_height() - corner_size, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_BL] = bl_corner
        
        # Bottom-right corner
        br_corner = base_wall_sprite.copy()
        pygame.draw.rect(br_corner, (120, 120, 120), 
                        (base_wall_sprite.get_width() - corner_size, 
                         base_wall_sprite.get_height() - corner_size, corner_size, corner_size))
        self.tile_sprites[self.TILE_WALL_CORNER_BR] = br_corner

    def create_wall_directional_sprites(self, base_wall_sprite):
        """Create horizontal and vertical wall variations"""
        # Horizontal wall - add horizontal line accent
        h_wall = base_wall_sprite.copy()
        wall_width = base_wall_sprite.get_width()
        wall_height = base_wall_sprite.get_height()
        # Add horizontal accent line
        pygame.draw.line(h_wall, (180, 180, 180), 
                        (wall_width // 4, wall_height // 2), 
                        (3 * wall_width // 4, wall_height // 2), 2)
        self.tile_sprites[self.TILE_WALL_HORIZONTAL] = h_wall
        
        # Vertical wall - add vertical line accent
        v_wall = base_wall_sprite.copy()
        # Add vertical accent line
        pygame.draw.line(v_wall, (180, 180, 180), 
                        (wall_width // 2, wall_height // 4), 
                        (wall_width // 2, 3 * wall_height // 4), 2)
        self.tile_sprites[self.TILE_WALL_VERTICAL] = v_wall

    def create_wall_window_sprite(self, base_wall_sprite):
        """Create window wall variation"""
        window_wall = base_wall_sprite.copy()
        wall_width = base_wall_sprite.get_width()
        wall_height = base_wall_sprite.get_height()
        
        # Create window rectangle
        window_width = wall_width // 3
        window_height = wall_height // 4
        window_x = (wall_width - window_width) // 2
        window_y = (wall_height - window_height) // 2
        
        # Draw window frame (darker)
        pygame.draw.rect(window_wall, (80, 80, 80), 
                        (window_x - 2, window_y - 2, window_width + 4, window_height + 4))
        
        # Draw window interior (lighter, like glass)
        pygame.draw.rect(window_wall, (150, 200, 255), 
                        (window_x, window_y, window_width, window_height))
        
        # Add window cross pattern
        pygame.draw.line(window_wall, (100, 100, 100), 
                        (window_x, window_y + window_height // 2), 
                        (window_x + window_width, window_y + window_height // 2), 1)
        pygame.draw.line(window_wall, (100, 100, 100), 
                        (window_x + window_width // 2, window_y), 
                        (window_x + window_width // 2, window_y + window_height), 1)
        
        self.tile_sprites[self.TILE_WALL_WINDOW] = window_wall

    def load_window_wall_sprites(self):
        """Load dedicated window wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Load horizontal window wall
        h_window_image = self.asset_loader.get_image("wall_window_horizontal")
        if h_window_image:
            scaled_h_window = pygame.transform.scale(h_window_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = scaled_h_window
            # Also use as generic window wall for backward compatibility
            self.tile_sprites[self.TILE_WALL_WINDOW] = scaled_h_window
        else:
            # Fallback to programmatically created window wall
            if self.TILE_WALL in self.tile_sprites:
                self.create_wall_window_sprite(self.tile_sprites[self.TILE_WALL])
                # Ensure horizontal window wall has a sprite
                if self.TILE_WALL_WINDOW in self.tile_sprites:
                    self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = self.tile_sprites[self.TILE_WALL_WINDOW]
        
        # Load vertical window wall
        v_window_image = self.asset_loader.get_image("wall_window_vertical")
        if v_window_image:
            scaled_v_window = pygame.transform.scale(v_window_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = scaled_v_window
        else:
            # Fallback to horizontal window wall or programmatic creation
            if self.TILE_WALL_WINDOW_HORIZONTAL in self.tile_sprites:
                self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL]
            elif self.TILE_WALL_WINDOW in self.tile_sprites:
                self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL_WINDOW]
            else:
                # Last resort - use regular wall
                if self.TILE_WALL in self.tile_sprites:
                    self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = self.tile_sprites[self.TILE_WALL]

    def load_corner_wall_sprites(self):
        """Load dedicated corner wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Try improved isometric assets first, then fall back to original assets
        corner_assets = {
            self.TILE_WALL_CORNER_TL: ["wall_corner_tl_isometric", "wall_corner_tl"],
            self.TILE_WALL_CORNER_TR: ["wall_corner_tr_isometric", "wall_corner_tr"], 
            self.TILE_WALL_CORNER_BL: ["wall_corner_bl_isometric", "wall_corner_bl"],
            self.TILE_WALL_CORNER_BR: ["wall_corner_br_isometric", "wall_corner_br"]
        }
        
        # Track if any corner assets fail to load
        failed_corners = []
        
        for tile_type, asset_names in corner_assets.items():
            corner_image = None
            # Try each asset name in order
            for asset_name in asset_names:
                corner_image = self.asset_loader.get_image(asset_name)
                if corner_image:
                    break
            
            if corner_image:
                scaled_corner = pygame.transform.scale(corner_image, (self.tile_width + 8, wall_height))
                self.tile_sprites[tile_type] = scaled_corner
            else:
                failed_corners.append(tile_type)
        
        # If any corners failed to load, create programmatic fallbacks for all
        if failed_corners:
            print(f"Warning: {len(failed_corners)} corner assets failed to load, using programmatic fallbacks")
            self.create_wall_corner_sprites(self.tile_sprites[self.TILE_WALL])

    def load_directional_wall_sprites(self):
        """Load dedicated horizontal and vertical wall assets"""
        wall_height = self.tile_height + 32  # Match other wall heights
        
        # Try improved isometric assets first, then fall back to original assets
        # Load horizontal wall
        h_wall_image = self.asset_loader.get_image("wall_horizontal_isometric")
        if not h_wall_image:
            h_wall_image = self.asset_loader.get_image("wall_horizontal")
        
        if h_wall_image:
            scaled_h_wall = pygame.transform.scale(h_wall_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_HORIZONTAL] = scaled_h_wall
        else:
            # Fallback to programmatically created horizontal wall
            print("Warning: wall_horizontal asset not found, using programmatic fallback")
            self.create_wall_directional_sprites(self.tile_sprites[self.TILE_WALL])
        
        # Load vertical wall
        v_wall_image = self.asset_loader.get_image("wall_vertical_isometric")
        if not v_wall_image:
            v_wall_image = self.asset_loader.get_image("wall_vertical")
        
        if v_wall_image:
            scaled_v_wall = pygame.transform.scale(v_wall_image, (self.tile_width + 8, wall_height))
            self.tile_sprites[self.TILE_WALL_VERTICAL] = scaled_v_wall
        else:
            # Fallback to programmatically created vertical wall if horizontal also failed
            if self.TILE_WALL_HORIZONTAL not in self.tile_sprites:
                print("Warning: wall_vertical asset not found, using programmatic fallback")
                self.create_wall_directional_sprites(self.tile_sprites[self.TILE_WALL])

    def render_flat_wall_with_roof_top(self, surface, screen_x, screen_y, tile_type, world_x, world_y):
        """Render walls using flat isometric surfaces with roof texture for top face"""
        # Wall height in pixels
        wall_height = 48
        
        # Load wall textures if not already loaded
        if not hasattr(self, 'wall_texture'):
            wall_texture_image = self.asset_loader.get_image("wall_texture")
            if wall_texture_image:
                self.wall_texture = wall_texture_image
            else:
                self.wall_texture = None
        
        # Load window wall texture if not already loaded
        if not hasattr(self, 'wall_texture_window'):
            window_texture_image = self.asset_loader.get_image("wall_texture_window")
            if window_texture_image:
                self.wall_texture_window = window_texture_image
            else:
                self.wall_texture_window = None
        
        # Load roof texture for top face
        roof_texture = self.asset_loader.get_image("roof_texture")
        
        # Base wall colors (fallback if no texture)
        wall_color = (180, 180, 180)  # Light gray
        shadow_color = (120, 120, 120)  # Darker gray for shadows
        highlight_color = (220, 220, 220)  # Lighter gray for highlights
        
        # Check adjacent tiles to determine which faces to draw
        # Swapped the directions to match isometric orientation
        north_wall = self.has_wall_at(world_x - 1, world_y)  # Actually west in world coords
        south_wall = self.has_wall_at(world_x + 1, world_y)  # Actually east in world coords  
        east_wall = self.has_wall_at(world_x, world_y + 1)   # Actually south in world coords
        west_wall = self.has_wall_at(world_x, world_y - 1)   # Actually north in world coords
        
        # Special handling for corner walls - they should only show outer faces
        is_corner = self.is_corner_wall(tile_type)
        
        # Calculate isometric wall face points
        tile_width = self.tile_width
        tile_height = self.tile_height
        
        # Different positioning for corners vs regular walls
        if is_corner:
            # Corners use original positioning (they were working correctly before)
            floor_y = screen_y  # Original position for corners
        else:
            # Regular walls also use the same positioning as corners to be consistent
            floor_y = screen_y  # Use same positioning for all wall types
        
        # Base diamond points (floor level)
        top_point = (screen_x, floor_y - tile_height // 2)
        right_point = (screen_x + tile_width // 2, floor_y)
        bottom_point = (screen_x, floor_y + tile_height // 2)
        left_point = (screen_x - tile_width // 2, floor_y)
        
        # Top diamond points (wall height) - walls extend upward from floor level
        top_top = (screen_x, floor_y - tile_height // 2 - wall_height)
        right_top = (screen_x + tile_width // 2, floor_y - wall_height)
        bottom_top = (screen_x, floor_y + tile_height // 2 - wall_height)
        left_top = (screen_x - tile_width // 2, floor_y - wall_height)
        
        # Draw wall faces based on adjacent walls and corner type
        if is_corner:
            # Corner walls render ALL faces for a complete 3D look
            # Always render all 4 side faces for corners
            self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
            self.render_textured_wall_face(surface, [top_point, right_point, right_top, top_top], "east", tile_type)
            self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
            self.render_textured_wall_face(surface, [left_point, bottom_point, bottom_top, left_top], "west", tile_type)
        else:
            # Check if this is a window wall - window walls should always show their faces
            is_window_wall = tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL]
            
            # Different rendering based on wall orientation
            is_horizontal_wall = tile_type in [self.TILE_WALL_HORIZONTAL, self.TILE_WALL_WINDOW_HORIZONTAL]
            is_vertical_wall = tile_type in [self.TILE_WALL_VERTICAL, self.TILE_WALL_WINDOW_VERTICAL]
            
            if is_horizontal_wall:
                # Horizontal walls show left and right faces (east and west)
                # East face (right side in isometric view)  
                # Always render horizontal wall faces
                self.render_textured_wall_face(surface, [top_point, right_point, right_top, top_top], "east", tile_type)
                
                # West face (left side in isometric view)
                # Always render horizontal wall faces
                self.render_textured_wall_face(surface, [left_point, bottom_point, bottom_top, left_top], "west", tile_type)
                    
            elif is_vertical_wall:
                # Vertical walls show front and back faces (north and south)
                # North face (front face in isometric view)
                # Always render vertical wall faces
                self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
                
                # South face (back face in isometric view)
                # Always render vertical wall faces
                self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
                    
            else:
                # Regular walls (fallback) - show front and back faces
                # North face (front face in isometric view)
                if not north_wall or is_window_wall:
                    self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
                
                # South face (back face in isometric view)
                if not south_wall or is_window_wall:
                    self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
        
        # Draw the top face with ROOF texture instead of wall texture
        self.render_textured_wall_face_with_custom_texture(surface, [top_top, right_top, bottom_top, left_top], "top", roof_texture)
        
        # Add window details for window walls (only if not using window texture)
        if (tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL] and
            not self.wall_texture_window):
            self.render_window_on_wall(surface, screen_x, screen_y, wall_height, not north_wall, not east_wall, not south_wall, not west_wall)
    
    def render_textured_wall_face_with_custom_texture(self, surface, face_points, face_direction, custom_texture):
        """Render a single wall face with a custom texture"""
        if custom_texture and len(face_points) == 4:
            # Create a temporary surface for the face
            min_x = min(p[0] for p in face_points)
            max_x = max(p[0] for p in face_points)
            min_y = min(p[1] for p in face_points)
            max_y = max(p[1] for p in face_points)
            
            face_width = int(max_x - min_x) + 1
            face_height = int(max_y - min_y) + 1
            
            if face_width > 0 and face_height > 0:
                # Create face surface
                face_surface = pygame.Surface((face_width, face_height), pygame.SRCALPHA)
                
                # FIXED: For roof texture on top faces, rotate it 45 degrees first
                if face_direction == "top":
                    # Rotate roof texture to match isometric orientation
                    rotated_texture = pygame.transform.rotate(custom_texture, 45)
                    scaled_texture = pygame.transform.scale(rotated_texture, (face_width, face_height))
                else:
                    # For side faces, use texture as-is
                    scaled_texture = pygame.transform.scale(custom_texture, (face_width, face_height))
                
                # Apply lighting based on face direction
                if face_direction == "north":
                    # Brightest face (highlight)
                    tinted_texture = self.apply_tint_to_surface(scaled_texture, (255, 255, 255), 1.2)
                elif face_direction == "east":
                    # Normal lighting
                    tinted_texture = scaled_texture
                elif face_direction in ["south", "west"]:
                    # Darker faces (shadow)
                    tinted_texture = self.apply_tint_to_surface(scaled_texture, (180, 180, 180), 0.8)
                else:  # top
                    # Top face - normal lighting
                    tinted_texture = scaled_texture
                
                face_surface.blit(tinted_texture, (0, 0))
                
                # Create a mask for the face shape
                adjusted_points = [(p[0] - min_x, p[1] - min_y) for p in face_points]
                
                # Create mask surface
                mask_surface = pygame.Surface((face_width, face_height), pygame.SRCALPHA)
                pygame.draw.polygon(mask_surface, (255, 255, 255, 255), adjusted_points)
                
                # Apply mask to textured surface
                face_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Blit the textured face to the main surface
                surface.blit(face_surface, (min_x, min_y))
                
                # FIXED: Don't draw border on roof faces to avoid grid lines
                # Only draw borders on side faces, not top faces (roofs)
                if face_direction != "top":
                    pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
        else:
            # Fallback to solid color rendering
            color = (80, 40, 20)  # Dark brown fallback for roof
            pygame.draw.polygon(surface, color, face_points)
            # FIXED: Don't draw border on roof faces in fallback either
            if face_direction != "top":
                pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
    
    def render_flat_wall(self, surface, screen_x, screen_y, tile_type, world_x, world_y):
        """Render walls using flat isometric surfaces with texture support"""
        # Wall height in pixels
        wall_height = 48
        
        # Load wall textures if not already loaded
        if not hasattr(self, 'wall_texture'):
            wall_texture_image = self.asset_loader.get_image("wall_texture")
            if wall_texture_image:
                self.wall_texture = wall_texture_image
            else:
                self.wall_texture = None
        
        # Load window wall texture if not already loaded
        if not hasattr(self, 'wall_texture_window'):
            window_texture_image = self.asset_loader.get_image("wall_texture_window")
            if window_texture_image:
                self.wall_texture_window = window_texture_image
            else:
                self.wall_texture_window = None
        
        # Base wall colors (fallback if no texture)
        wall_color = (180, 180, 180)  # Light gray
        shadow_color = (120, 120, 120)  # Darker gray for shadows
        highlight_color = (220, 220, 220)  # Lighter gray for highlights
        
        # Check adjacent tiles to determine which faces to draw
        # Swapped the directions to match isometric orientation
        north_wall = self.has_wall_at(world_x - 1, world_y)  # Actually west in world coords
        south_wall = self.has_wall_at(world_x + 1, world_y)  # Actually east in world coords  
        east_wall = self.has_wall_at(world_x, world_y + 1)   # Actually south in world coords
        west_wall = self.has_wall_at(world_x, world_y - 1)   # Actually north in world coords
        
        # Special handling for corner walls - they should only show outer faces
        is_corner = self.is_corner_wall(tile_type)
        
        # Calculate isometric wall face points
        tile_width = self.tile_width
        tile_height = self.tile_height
        
        # Different positioning for corners vs regular walls
        if is_corner:
            # Corners use original positioning (they were working correctly before)
            floor_y = screen_y  # Original position for corners
        else:
            # Regular walls also use the same positioning as corners to be consistent
            floor_y = screen_y  # Use same positioning for all wall types
        
        # Base diamond points (floor level)
        top_point = (screen_x, floor_y - tile_height // 2)
        right_point = (screen_x + tile_width // 2, floor_y)
        bottom_point = (screen_x, floor_y + tile_height // 2)
        left_point = (screen_x - tile_width // 2, floor_y)
        
        # Top diamond points (wall height) - walls extend upward from floor level
        top_top = (screen_x, floor_y - tile_height // 2 - wall_height)
        right_top = (screen_x + tile_width // 2, floor_y - wall_height)
        bottom_top = (screen_x, floor_y + tile_height // 2 - wall_height)
        left_top = (screen_x - tile_width // 2, floor_y - wall_height)
        
        # Draw wall faces based on adjacent walls and corner type
        if is_corner:
            # Corner walls render ALL faces for a complete 3D look
            # Always render all 4 side faces for corners
            self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
            self.render_textured_wall_face(surface, [top_point, right_point, right_top, top_top], "east", tile_type)
            self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
            self.render_textured_wall_face(surface, [left_point, bottom_point, bottom_top, left_top], "west", tile_type)
        else:
            # Check if this is a window wall - window walls should always show their faces
            is_window_wall = tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL]
            
            # Different rendering based on wall orientation
            is_horizontal_wall = tile_type in [self.TILE_WALL_HORIZONTAL, self.TILE_WALL_WINDOW_HORIZONTAL]
            is_vertical_wall = tile_type in [self.TILE_WALL_VERTICAL, self.TILE_WALL_WINDOW_VERTICAL]
            
            if is_horizontal_wall:
                # Horizontal walls show left and right faces (east and west)
                # East face (right side in isometric view)  
                # Always render horizontal wall faces
                self.render_textured_wall_face(surface, [top_point, right_point, right_top, top_top], "east", tile_type)
                
                # West face (left side in isometric view)
                # Always render horizontal wall faces
                self.render_textured_wall_face(surface, [left_point, bottom_point, bottom_top, left_top], "west", tile_type)
                    
            elif is_vertical_wall:
                # Vertical walls show front and back faces (north and south)
                # North face (front face in isometric view)
                # Always render vertical wall faces
                self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
                
                # South face (back face in isometric view)
                # Always render vertical wall faces
                self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
                    
            else:
                # Regular walls (fallback) - show front and back faces
                # North face (front face in isometric view)
                if not north_wall or is_window_wall:
                    self.render_textured_wall_face(surface, [left_point, top_point, top_top, left_top], "north", tile_type)
                
                # South face (back face in isometric view)
                if not south_wall or is_window_wall:
                    self.render_textured_wall_face(surface, [bottom_point, right_point, right_top, bottom_top], "south", tile_type)
        
        # Always draw the top face with texture
        self.render_textured_wall_face(surface, [top_top, right_top, bottom_top, left_top], "top", tile_type)
        
        # Add window details for window walls (only if not using window texture)
        if (tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL] and
            not self.wall_texture_window):
            self.render_window_on_wall(surface, screen_x, screen_y, wall_height, not north_wall, not east_wall, not south_wall, not west_wall)

    def render_textured_wall_face(self, surface, face_points, face_direction, tile_type=None):
        """Render a single wall face with texture or fallback color"""
        # Determine which texture to use based on tile type and face direction
        is_window_wall = tile_type in [self.TILE_WALL_WINDOW, self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL] if tile_type else False
        
        # Only use window texture on side faces, not on top faces
        if is_window_wall and face_direction != "top":
            current_texture = self.wall_texture_window if self.wall_texture_window else self.wall_texture
        else:
            # Use regular wall texture for top faces, even on window walls
            current_texture = self.wall_texture
        
        if current_texture and len(face_points) == 4:
            # Create a temporary surface for the face
            min_x = min(p[0] for p in face_points)
            max_x = max(p[0] for p in face_points)
            min_y = min(p[1] for p in face_points)
            max_y = max(p[1] for p in face_points)
            
            face_width = int(max_x - min_x) + 1
            face_height = int(max_y - min_y) + 1
            
            if face_width > 0 and face_height > 0:
                # Create face surface
                face_surface = pygame.Surface((face_width, face_height), pygame.SRCALPHA)
                
                # Scale texture to fit the face
                scaled_texture = pygame.transform.scale(current_texture, (face_width, face_height))
                
                # Apply lighting based on face direction
                if face_direction == "north":
                    # Brightest face (highlight)
                    tinted_texture = self.apply_tint_to_surface(scaled_texture, (255, 255, 255), 1.2)
                elif face_direction == "east":
                    # Normal lighting
                    tinted_texture = scaled_texture
                elif face_direction in ["south", "west"]:
                    # Darker faces (shadow)
                    tinted_texture = self.apply_tint_to_surface(scaled_texture, (180, 180, 180), 0.8)
                else:  # top
                    # Top face - normal lighting
                    tinted_texture = scaled_texture
                
                face_surface.blit(tinted_texture, (0, 0))
                
                # Create a mask for the face shape
                adjusted_points = [(p[0] - min_x, p[1] - min_y) for p in face_points]
                
                # Create mask surface
                mask_surface = pygame.Surface((face_width, face_height), pygame.SRCALPHA)
                pygame.draw.polygon(mask_surface, (255, 255, 255, 255), adjusted_points)
                
                # Apply mask to textured surface
                face_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Blit the textured face to the main surface
                surface.blit(face_surface, (min_x, min_y))
                
                # Draw border
                pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
        else:
            # Fallback to solid color rendering
            # Don't use window-specific colors for top faces
            if face_direction == "top":
                color = (180, 180, 180)  # Normal color for all top faces
            elif face_direction == "north":
                color = (220, 220, 220)  # Highlight
            elif face_direction == "east":
                color = (180, 180, 180)  # Normal
            elif face_direction in ["south", "west"]:
                color = (120, 120, 120)  # Shadow
            else:
                color = (180, 180, 180)  # Default normal
            
            pygame.draw.polygon(surface, color, face_points)
            pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)

    def is_corner_wall(self, tile_type):
        """Check if a tile type is a corner wall"""
        corner_types = [
            self.TILE_WALL_CORNER_TL, self.TILE_WALL_CORNER_TR,
            self.TILE_WALL_CORNER_BL, self.TILE_WALL_CORNER_BR
        ]
        return tile_type in corner_types

    def render_window_on_wall(self, surface, screen_x, screen_y, wall_height, show_north, show_east, show_south, show_west):
        """Render window details on exposed wall faces"""
        window_color = (150, 200, 255)  # Light blue for glass
        frame_color = (80, 60, 40)      # Brown for window frame
        
        window_size = 16
        window_height = 12
        
        # Render windows on exposed faces
        if show_north:  # North face window
            window_center_x = screen_x - self.tile_width // 4
            window_center_y = screen_y - wall_height // 2
            window_rect = pygame.Rect(window_center_x - window_size//2, window_center_y - window_height//2, window_size, window_height)
            pygame.draw.rect(surface, frame_color, window_rect)
            pygame.draw.rect(surface, window_color, (window_rect.x + 2, window_rect.y + 2, window_rect.width - 4, window_rect.height - 4))
        
        if show_east:   # East face window
            window_center_x = screen_x + self.tile_width // 4
            window_center_y = screen_y - wall_height // 2
            window_rect = pygame.Rect(window_center_x - window_size//2, window_center_y - window_height//2, window_size, window_height)
            pygame.draw.rect(surface, frame_color, window_rect)
            pygame.draw.rect(surface, window_color, (window_rect.x + 2, window_rect.y + 2, window_rect.width - 4, window_rect.height - 4))

    def has_wall_at(self, x, y):
        """Check if there's a wall at the given coordinates"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True  # Treat out-of-bounds as walls
        
        # Use get_tile method if available (for chunk-based worlds)
        if hasattr(self.level, 'get_tile'):
            tile_type = self.level.get_tile(x, y)
            if tile_type is None:
                return False  # Unloaded chunks are not walls
            return self.is_wall_tile(tile_type)
        else:
            # Fallback to tiles array for template-based worlds
            if hasattr(self.level, 'tiles') and self.level.tiles and len(self.level.tiles) > 0:
                return self.is_wall_tile(self.tiles[y][x])
            return False

    def is_wall_tile(self, tile_type):
        """Check if a tile type is any kind of wall"""
        wall_types = [
            self.TILE_WALL, self.TILE_WALL_CORNER_TL, self.TILE_WALL_CORNER_TR,
            self.TILE_WALL_CORNER_BL, self.TILE_WALL_CORNER_BR,
            self.TILE_WALL_HORIZONTAL, self.TILE_WALL_VERTICAL, self.TILE_WALL_WINDOW,
            self.TILE_WALL_WINDOW_HORIZONTAL, self.TILE_WALL_WINDOW_VERTICAL
        ]
        return tile_type in wall_types

    def has_wall_or_door_at(self, x, y):
        """Check if there's a wall or door at the given coordinates"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True  # Treat out of bounds as walls
        
        # Use get_tile method if available (for chunk-based worlds)
        if hasattr(self.level, 'get_tile'):
            tile_type = self.level.get_tile(x, y)
            if tile_type is None:
                return False  # Unloaded chunks are not walls
            return self.is_wall_tile(tile_type) or tile_type == self.TILE_DOOR
        else:
            # Fallback to tiles array for template-based worlds
            if hasattr(self.level, 'tiles') and self.level.tiles and len(self.level.tiles) > 0:
                tile = self.tiles[y][x]
                return self.is_wall_tile(tile) or tile == self.TILE_DOOR
            return False


    def apply_tint_to_surface(self, surface, tint_color, intensity=1.0):
        """Apply a tint to a surface for lighting effects"""
        tinted_surface = surface.copy()
        
        # Create tint overlay
        tint_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Adjust tint color by intensity
        adjusted_tint = (
            min(255, int(tint_color[0] * intensity)),
            min(255, int(tint_color[1] * intensity)),
            min(255, int(tint_color[2] * intensity))
        )
        
        tint_overlay.fill(adjusted_tint)
        tinted_surface.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_surface
