"""
Door rendering system for the RPG
"""

import pygame
import math


class DoorRenderer:
    """Handles all door rendering functionality"""
    
    def __init__(self, asset_loader, iso_renderer):
        self.asset_loader = asset_loader
        self.iso_renderer = iso_renderer
        self.archway_texture = None
        self.wall_door_texture = None
        self._load_textures()
    
    def _load_textures(self):
        """Load archway and wall door textures from assets"""
        # Load archway texture
        archway_texture_image = self.asset_loader.get_image("archway_texture")
        if archway_texture_image:
            self.archway_texture = archway_texture_image
        else:
            self.archway_texture = None
        
        # Load wall door texture
        wall_door_texture_image = self.asset_loader.get_image("wall_door")
        if wall_door_texture_image:
            self.wall_door_texture = wall_door_texture_image
        else:
            self.wall_door_texture = None
    
    def create_enhanced_door_sprite(self, tile_width, tile_height):
        """Create an enhanced door sprite that renders properly"""
        # Create a door sprite that looks like a proper isometric door
        door_width = tile_width
        door_height = tile_height + 32
        
        surface = pygame.Surface((door_width, door_height), pygame.SRCALPHA)
        
        # Door colors
        door_color = (139, 69, 19)      # Brown door
        frame_color = (100, 50, 10)     # Darker brown frame
        handle_color = (255, 215, 0)    # Gold handle
        
        # Calculate door rectangle dimensions
        door_rect_width = door_width // 2
        door_rect_height = door_height - tile_height // 2
        door_x = (door_width - door_rect_width) // 2
        door_y = tile_height // 4
        
        # Draw door frame (slightly larger rectangle)
        frame_rect = pygame.Rect(door_x - 2, door_y - 2, door_rect_width + 4, door_rect_height + 4)
        pygame.draw.rect(surface, frame_color, frame_rect)
        
        # Draw main door
        door_rect = pygame.Rect(door_x, door_y, door_rect_width, door_rect_height)
        pygame.draw.rect(surface, door_color, door_rect)
        
        # Add door handle
        handle_x = door_x + door_rect_width - 6
        handle_y = door_y + door_rect_height // 2
        pygame.draw.circle(surface, handle_color, (handle_x, handle_y), 2)
        
        # Add door panels for detail
        panel_margin = 3
        panel_width = door_rect_width - panel_margin * 2
        panel_height = (door_rect_height - panel_margin * 3) // 2
        
        # Top panel outline
        top_panel_rect = pygame.Rect(door_x + panel_margin, door_y + panel_margin, panel_width, panel_height)
        pygame.draw.rect(surface, frame_color, top_panel_rect, 1)
        
        # Bottom panel outline
        bottom_panel_rect = pygame.Rect(door_x + panel_margin, door_y + panel_margin * 2 + panel_height, panel_width, panel_height)
        pygame.draw.rect(surface, frame_color, bottom_panel_rect, 1)
        
        return surface
    
    def render_door_tile(self, surface, screen_x, screen_y, tile_type, level, tile_width, tile_height):
        """Render door exactly like walls but with archway texture on front face and wall_door on others"""
        # Door height in pixels (same as walls)
        door_height = 48
        
        # Get world coordinates for adjacency checking
        world_x, world_y = self.iso_renderer.screen_to_world(screen_x, screen_y, level.camera_x, level.camera_y)
        world_x = int(world_x)
        world_y = int(world_y)
        
        # Check adjacent tiles to determine which faces to draw and door orientation
        north_wall = level.wall_renderer.has_wall_or_door_at(world_x - 1, world_y)
        south_wall = level.wall_renderer.has_wall_or_door_at(world_x + 1, world_y)  
        east_wall = level.wall_renderer.has_wall_or_door_at(world_x, world_y + 1)
        west_wall = level.wall_renderer.has_wall_or_door_at(world_x, world_y - 1)
        
        # Determine door orientation based on adjacent walls
        # If walls are on BOTH north AND south, door opens east/west (horizontal door)
        # If walls are on BOTH east AND west, door opens north/south (vertical door)
        is_horizontal_door = north_wall and south_wall
        is_vertical_door = east_wall and west_wall
        
        # If neither configuration, determine based on which pair has more walls
        if not is_horizontal_door and not is_vertical_door:
            north_south_walls = (1 if north_wall else 0) + (1 if south_wall else 0)
            east_west_walls = (1 if east_wall else 0) + (1 if west_wall else 0)
            
            if north_south_walls > east_west_walls:
                is_horizontal_door = True
                is_vertical_door = False
            elif east_west_walls > north_south_walls:
                is_horizontal_door = False
                is_vertical_door = True
            else:
                # Default to horizontal if equal or no walls
                is_horizontal_door = True
                is_vertical_door = False
        
        # Calculate isometric door face points (same as walls)
        floor_y = screen_y  # Use same positioning as walls
        
        # Base diamond points (floor level)
        top_point = (screen_x, floor_y - tile_height // 2)
        right_point = (screen_x + tile_width // 2, floor_y)
        bottom_point = (screen_x, floor_y + tile_height // 2)
        left_point = (screen_x - tile_width // 2, floor_y)
        
        # Top diamond points (door height)
        top_top = (screen_x, floor_y - tile_height // 2 - door_height)
        right_top = (screen_x + tile_width // 2, floor_y - door_height)
        bottom_top = (screen_x, floor_y + tile_height // 2 - door_height)
        left_top = (screen_x - tile_width // 2, floor_y - door_height)
        
        # Render door faces with appropriate textures based on orientation
        # Always render all faces - walls are separate entities
        
        # North face (top-left edge in isometric view)
        north_face = [left_point, top_point, top_top, left_top]
        if is_vertical_door:
            # Vertical door - north face shows archway (opening)
            self.render_textured_archway_face(surface, north_face, "north")
        else:
            # Horizontal door - north face shows door (side wall)
            self.render_textured_wall_door_face(surface, north_face, "north")
        
        # East face (top-right edge in isometric view)  
        east_face = [top_point, right_point, right_top, top_top]
        if is_horizontal_door:
            # Horizontal door - east face shows archway (opening)
            self.render_textured_archway_face(surface, east_face, "east")
        else:
            # Vertical door - east face shows door (side wall)
            self.render_textured_wall_door_face(surface, east_face, "east")
        
        # South face (bottom-right edge in isometric view)
        south_face = [bottom_point, right_point, right_top, bottom_top]
        if is_vertical_door:
            # Vertical door - south face shows archway (opening)
            self.render_textured_archway_face(surface, south_face, "south")
        else:
            # Horizontal door - south face shows door (side wall)
            self.render_textured_wall_door_face(surface, south_face, "south")
        
        # West face (bottom-left edge in isometric view)
        west_face = [left_point, bottom_point, bottom_top, left_top]
        if is_horizontal_door:
            # Horizontal door - west face shows archway (opening)
            self.render_textured_archway_face(surface, west_face, "west")
        else:
            # Vertical door - west face shows door (side wall)
            self.render_textured_wall_door_face(surface, west_face, "west")
        
        # Always draw the top face with stone texture (not archway)
        top_face = [top_top, right_top, bottom_top, left_top]
        self.render_stone_face(surface, top_face, "top")
    
    def render_textured_archway_face(self, surface, face_points, face_direction):
        """Render a single door face with archway texture or fallback color"""
        if self.archway_texture and len(face_points) == 4:
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
                
                # Scale archway texture to fit the face
                scaled_texture = pygame.transform.scale(self.archway_texture, (face_width, face_height))
                
                # Apply lighting based on face direction (same as walls)
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
                
                # Draw border (subtle, like walls)
                pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
        else:
            # Fallback to bright red for archway faces (for debugging)
            if face_direction == "north":
                color = (255, 100, 100)  # Bright red highlight for archway
            elif face_direction == "east":
                color = (255, 50, 50)    # Bright red normal for archway
            elif face_direction in ["south", "west"]:
                color = (200, 0, 0)      # Dark red shadow for archway
            else:  # top
                color = (255, 150, 150)  # Light red for archway top
            
            pygame.draw.polygon(surface, color, face_points)
            pygame.draw.polygon(surface, (100, 0, 0), face_points, 2)  # Dark red border
    
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
        
        # Apply tint using multiply blend mode
        tinted_surface.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_surface
    
    def render_textured_wall_door_face(self, surface, face_points, face_direction):
        """Render a single door face with wall_door texture (open door view)"""
        if self.wall_door_texture and len(face_points) == 4:
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
                
                # Scale wall door texture to fit the face
                scaled_texture = pygame.transform.scale(self.wall_door_texture, (face_width, face_height))
                
                # Apply lighting based on face direction (same as walls)
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
                
                # Draw border (subtle, like walls)
                pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
        else:
            # Fallback to bright blue for wall_door faces (for debugging)
            if face_direction == "north":
                color = (100, 100, 255)  # Bright blue highlight for wall_door
            elif face_direction == "east":
                color = (50, 50, 255)    # Bright blue normal for wall_door
            elif face_direction in ["south", "west"]:
                color = (0, 0, 200)      # Dark blue shadow for wall_door
            else:  # top
                color = (150, 150, 255)  # Light blue for wall_door top
            
            pygame.draw.polygon(surface, color, face_points)
            pygame.draw.polygon(surface, (0, 0, 100), face_points, 2)  # Dark blue border
    
    def render_stone_face(self, surface, face_points, face_direction):
        """Render a single door face with stone texture (for top face)"""
        # Get wall texture for the top face
        wall_texture = self.asset_loader.get_image("wall_texture")
        
        if wall_texture and len(face_points) == 4:
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
                
                # Scale wall texture to fit the face
                scaled_texture = pygame.transform.scale(wall_texture, (face_width, face_height))
                
                # Apply normal lighting for top face
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
                
                # Draw border (subtle, like walls)
                pygame.draw.polygon(surface, (100, 100, 100), face_points, 1)
        else:
            # Fallback to stone color for top face
            color = (160, 140, 120)  # Stone color
            pygame.draw.polygon(surface, color, face_points)
            pygame.draw.polygon(surface, (100, 80, 60), face_points, 1)