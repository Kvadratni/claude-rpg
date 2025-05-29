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
        self.door_texture = None
        self._load_door_texture()
    
    def _load_door_texture(self):
        """Load door texture from assets"""
        door_texture_image = self.asset_loader.get_image("door")
        if door_texture_image:
            self.door_texture = door_texture_image
        else:
            self.door_texture = None
    
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
        """Render door exactly like walls but with door texture on all faces"""
        # Door height in pixels (same as walls)
        door_height = 48
        
        # Get world coordinates for adjacency checking
        # Convert screen coordinates back to world coordinates using the isometric renderer
        world_x, world_y = self.iso_renderer.screen_to_world(screen_x, screen_y, level.camera_x, level.camera_y)
        world_x = int(world_x)
        world_y = int(world_y)
        
        # Check adjacent tiles to determine which faces to draw (same logic as walls)
        north_wall = level.wall_renderer.has_wall_or_door_at(world_x - 1, world_y)
        south_wall = level.wall_renderer.has_wall_or_door_at(world_x + 1, world_y)  
        east_wall = level.wall_renderer.has_wall_or_door_at(world_x, world_y + 1)
        west_wall = level.wall_renderer.has_wall_or_door_at(world_x, world_y - 1)
        
        # Calculate isometric door face points (same as walls)
        
        # Use same positioning as the original door code (which was correct)
        floor_y = screen_y + tile_height // 4
        
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
        
        # Render door faces with texture (similar to walls)
        
        # North face (top-left edge in isometric view)
        if not north_wall:
            north_face = [left_point, top_point, top_top, left_top]
            self.render_textured_door_face(surface, north_face, "north")
        
        # East face (top-right edge in isometric view)  
        if not east_wall:
            east_face = [top_point, right_point, right_top, top_top]
            self.render_textured_door_face(surface, east_face, "east")
        
        # South face (bottom-right edge in isometric view) - THE FRONT FACE
        if not south_wall:
            south_face = [bottom_point, right_point, right_top, bottom_top]
            self.render_textured_door_face(surface, south_face, "south")
        
        # West face (bottom-left edge in isometric view)
        if not west_wall:
            west_face = [left_point, bottom_point, bottom_top, left_top]
            self.render_textured_door_face(surface, west_face, "west")
        
        # Skip drawing the top face to make it transparent (doors are open at top)
        
        # Add door handle on the front (south) face if it's visible
        if not south_wall:
            handle_x = screen_x + tile_width // 3
            handle_y = floor_y - door_height // 2
            pygame.draw.circle(surface, (255, 215, 0), (handle_x, handle_y), 3)  # Gold handle
            pygame.draw.circle(surface, (200, 160, 0), (handle_x, handle_y), 3, 1)  # Handle border
    
    def render_textured_door_face(self, surface, face_points, face_direction):
        """Render a single door face with texture or fallback color"""
        if self.door_texture and len(face_points) == 4:
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
                scaled_texture = pygame.transform.scale(self.door_texture, (face_width, face_height))
                
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
                pygame.draw.polygon(surface, (60, 30, 5), face_points, 1)
        else:
            # Fallback to solid color rendering
            if face_direction == "north":
                color = (180, 90, 30)  # Door highlight
            elif face_direction == "east":
                color = (139, 69, 19)  # Door normal
            elif face_direction in ["south", "west"]:
                color = (100, 50, 10)  # Door shadow
            else:  # top
                color = (139, 69, 19)  # Door normal
            
            pygame.draw.polygon(surface, color, face_points)
            pygame.draw.polygon(surface, (60, 30, 5), face_points, 1)
    
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
    
    def render_rounded_door_face(self, surface, bottom_point, right_point, right_top, bottom_top, color):
        """Render a rounded door face using the door texture"""
        # Get the door texture from assets
        door_texture = self.asset_loader.get_image("door")
        
        if door_texture:
            # For simplicity, let's just render the texture as a flat face first
            # Calculate the face rectangle
            face_left = min(bottom_point[0], right_point[0], bottom_top[0], right_top[0])
            face_top = min(bottom_point[1], right_point[1], bottom_top[1], right_top[1])
            face_width = max(bottom_point[0], right_point[0], bottom_top[0], right_top[0]) - face_left
            face_height = max(bottom_point[1], right_point[1], bottom_top[1], right_top[1]) - face_top
            
            if face_width > 0 and face_height > 0:
                # Scale the door texture to fit the face
                scaled_door = pygame.transform.scale(door_texture, (int(face_width), int(face_height)))
                
                # Create a surface for the door face
                face_surface = pygame.Surface((int(face_width), int(face_height)), pygame.SRCALPHA)
                
                # Draw the door face shape as a mask
                face_points = [
                    (bottom_point[0] - face_left, bottom_point[1] - face_top),
                    (right_point[0] - face_left, right_point[1] - face_top),
                    (right_top[0] - face_left, right_top[1] - face_top),
                    (bottom_top[0] - face_left, bottom_top[1] - face_top)
                ]
                
                # First, blit the texture
                face_surface.blit(scaled_door, (0, 0))
                
                # Create a mask surface
                mask_surface = pygame.Surface((int(face_width), int(face_height)), pygame.SRCALPHA)
                pygame.draw.polygon(mask_surface, (255, 255, 255, 255), face_points)
                
                # Apply the mask to the texture
                face_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
                
                # Blit the final textured face to the main surface
                surface.blit(face_surface, (face_left, face_top))
                
                # Draw border
                actual_face_points = [bottom_point, right_point, right_top, bottom_top]
                pygame.draw.polygon(surface, (60, 30, 5), actual_face_points, 2)
            else:
                # Fallback to solid color
                self.render_rounded_door_face_fallback(surface, bottom_point, right_point, right_top, bottom_top, color)
        else:
            # Fallback to solid color if no texture
            self.render_rounded_door_face_fallback(surface, bottom_point, right_point, right_top, bottom_top, color)
    
    def render_rounded_door_face_fallback(self, surface, bottom_point, right_point, right_top, bottom_top, color):
        """Fallback method for rounded door face with solid color"""
        # Calculate the center line of the face
        center_bottom_x = (bottom_point[0] + right_point[0]) // 2
        center_bottom_y = (bottom_point[1] + right_point[1]) // 2
        center_top_x = (bottom_top[0] + right_top[0]) // 2
        center_top_y = (bottom_top[1] + right_top[1]) // 2
        
        # Create curved segments by offsetting the center outward
        curve_offset = 8  # How much to curve outward
        
        # Calculate the outward direction (perpendicular to the face)
        face_dx = right_point[0] - bottom_point[0]
        face_dy = right_point[1] - bottom_point[1]
        # Rotate 90 degrees to get perpendicular (outward direction)
        outward_dx = -face_dy
        outward_dy = face_dx
        # Normalize
        length = math.sqrt(outward_dx * outward_dx + outward_dy * outward_dy)
        if length > 0:
            outward_dx = outward_dx / length * curve_offset
            outward_dy = outward_dy / length * curve_offset
        
        # Create curved points
        curved_bottom = (center_bottom_x + outward_dx, center_bottom_y + outward_dy)
        curved_top = (center_top_x + outward_dx, center_top_y + outward_dy)
        
        # Draw the curved face as multiple segments
        # Left segment
        left_segment = [bottom_point, curved_bottom, curved_top, bottom_top]
        pygame.draw.polygon(surface, color, left_segment)
        pygame.draw.polygon(surface, (60, 30, 5), left_segment, 1)
        
        # Right segment  
        right_segment = [curved_bottom, right_point, right_top, curved_top]
        pygame.draw.polygon(surface, color, right_segment)
        pygame.draw.polygon(surface, (60, 30, 5), right_segment, 1)