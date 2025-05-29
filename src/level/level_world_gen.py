"""
World generation and building creation functionality
"""

import random


class WorldGenerationMixin:
    """Mixin class for world generation functionality"""
    
    def create_test_corner_building(self, tiles, start_x, start_y, corner_test_type):
        """Create a small test building to test corner orientations"""
        width, height = 4, 4
        
        # Interior
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                tiles[y][x] = self.TILE_BRICK
        
        # Walls
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if (x > start_x and x < start_x + width - 1 and 
                    y > start_y and y < start_y + height - 1):
                    continue
                
                is_top = (y == start_y)
                is_bottom = (y == start_y + height - 1)
                is_left = (x == start_x)
                is_right = (x == start_x + width - 1)
                
                # Test different corner mappings
                if corner_test_type == 0:  # Test mapping 1
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    else:
                        tiles[y][x] = self.TILE_WALL
                elif corner_test_type == 1:  # Test mapping 2
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    else:
                        tiles[y][x] = self.TILE_WALL
                elif corner_test_type == 2:  # Test mapping 3
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    else:
                        tiles[y][x] = self.TILE_WALL
                elif corner_test_type == 3:  # Test mapping 4
                    if is_top and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_BR
                    elif is_top and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_BL
                    elif is_bottom and is_left:
                        tiles[y][x] = self.TILE_WALL_CORNER_TR
                    elif is_bottom and is_right:
                        tiles[y][x] = self.TILE_WALL_CORNER_TL
                    else:
                        tiles[y][x] = self.TILE_WALL
    
    def create_building(self, tiles, start_x, start_y, width, height):
        """Create a building structure with varied wall types and windows"""
        # Building interior floor - use brick tiles for more realistic interiors
        for y in range(start_y + 1, start_y + height - 1):
            for x in range(start_x + 1, start_x + width - 1):
                tiles[y][x] = self.TILE_BRICK  # Interior brick floor
        
        # Building walls - use simple, consistent approach
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                # Skip interior
                if (x > start_x and x < start_x + width - 1 and 
                    y > start_y and y < start_y + height - 1):
                    continue
                
                # Use regular walls for all positions - no complex corner logic
                tiles[y][x] = self.TILE_WALL
        
        # Add some variety with horizontal and vertical walls
        # Top and bottom walls
        for x in range(start_x + 1, start_x + width - 1):
            # Top wall
            if random.random() < 0.2:  # 20% chance for windows
                tiles[start_y][x] = self.TILE_WALL_WINDOW_HORIZONTAL
            else:
                tiles[start_y][x] = self.TILE_WALL_HORIZONTAL
            
            # Bottom wall (will be overridden by doors)
            if random.random() < 0.2:  # 20% chance for windows
                tiles[start_y + height - 1][x] = self.TILE_WALL_WINDOW_HORIZONTAL
            else:
                tiles[start_y + height - 1][x] = self.TILE_WALL_HORIZONTAL
        
        # Left and right walls
        for y in range(start_y + 1, start_y + height - 1):
            # Left wall
            if random.random() < 0.15:  # 15% chance for windows
                tiles[y][start_x] = self.TILE_WALL_WINDOW_VERTICAL
            else:
                tiles[y][start_x] = self.TILE_WALL_VERTICAL
            
            # Right wall
            if random.random() < 0.15:  # 15% chance for windows
                tiles[y][start_x + width - 1] = self.TILE_WALL_WINDOW_VERTICAL
            else:
                tiles[y][start_x + width - 1] = self.TILE_WALL_VERTICAL
        
        # Add double doors (2 tiles wide) - replace bottom wall sections
        door_center_x = start_x + width // 2
        door_y = start_y + height - 1
        
        # Create 2-tile wide door centered on the building
        door_x1 = door_center_x - 1
        door_x2 = door_center_x
        
        # Make sure both door positions are valid and within the building wall
        if (0 <= door_x1 < self.width and 0 <= door_y < self.height and 
            door_x1 > start_x and door_x1 < start_x + width - 1):
            tiles[door_y][door_x1] = self.TILE_DOOR
        
        if (0 <= door_x2 < self.width and 0 <= door_y < self.height and 
            door_x2 > start_x and door_x2 < start_x + width - 1):
            tiles[door_y][door_x2] = self.TILE_DOOR
    
    def create_lake(self, tiles, center_x, center_y, radius):
        """Create a circular lake"""
        for y in range(max(1, center_y - radius), min(self.height - 1, center_y + radius)):
            for x in range(max(1, center_x - radius), min(self.width - 1, center_x + radius)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance < radius - 2:
                    tiles[y][x] = self.TILE_WATER
                elif distance < radius:
                    tiles[y][x] = self.TILE_DIRT  # Shore
    
    def create_forest_clearing(self, tiles, center_x, center_y, size):
        """Create a forest clearing area"""
        for y in range(max(1, center_y - size//2), min(self.height - 1, center_y + size//2)):
            for x in range(max(1, center_x - size//2), min(self.width - 1, center_x + size//2)):
                if random.random() < 0.3:  # 30% chance for dirt patches
                    tiles[y][x] = self.TILE_DIRT
    
    def create_dirt_path(self, tiles, start_x, start_y, end_x, end_y):
        """Create a dirt path between two points"""
        # Simple straight line path
        if start_x == end_x:  # Vertical path
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                if 1 <= y < self.height - 1:
                    tiles[y][start_x] = self.TILE_DIRT
        elif start_y == end_y:  # Horizontal path
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                if 1 <= x < self.width - 1:
                    tiles[start_y][x] = self.TILE_DIRT