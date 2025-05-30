"""
Tile sprite creation and management
"""

import pygame


class TileManagerMixin:
    """Mixin class for tile sprite management"""
    
    def create_tile_sprites(self):
        """Create isometric tile sprites using loaded assets"""
        self.tile_sprites = {}
        
        # Try to use loaded images, fall back to generated sprites
        grass_image = self.asset_loader.get_image("grass_tile")
        if grass_image:
            # Rotate the tile 45 degrees for proper isometric alignment
            rotated_grass = pygame.transform.rotate(grass_image, 45)
            self.tile_sprites[self.TILE_GRASS] = pygame.transform.scale(rotated_grass, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_GRASS] = self.iso_renderer.create_diamond_tile((50, 150, 50))
        
        stone_image = self.asset_loader.get_image("stone_tile")
        if stone_image:
            rotated_stone = pygame.transform.rotate(stone_image, 45)
            self.tile_sprites[self.TILE_STONE] = pygame.transform.scale(rotated_stone, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_STONE] = self.iso_renderer.create_diamond_tile((150, 150, 150))
        
        water_image = self.asset_loader.get_image("water_tile")
        if water_image:
            rotated_water = pygame.transform.rotate(water_image, 45)
            self.tile_sprites[self.TILE_WATER] = pygame.transform.scale(rotated_water, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_WATER] = self.iso_renderer.create_diamond_tile((50, 100, 200))
        
        # Load base wall image - try improved isometric version first
        wall_image = self.asset_loader.get_image("wall_tile_isometric")
        if not wall_image:
            wall_image = self.asset_loader.get_image("wall_tile")
        
        if wall_image:
            # Scale wall to be taller and more prominent
            wall_height = self.tile_height + 32  # Make walls taller
            base_wall_sprite = pygame.transform.scale(wall_image, (self.tile_width + 8, wall_height))
            
            # Create variations of the wall sprite
            self.tile_sprites[self.TILE_WALL] = base_wall_sprite
            
            # Load dedicated wall assets instead of creating programmatically
            self.wall_renderer.load_corner_wall_sprites()
            self.wall_renderer.load_directional_wall_sprites()
            self.wall_renderer.load_window_wall_sprites()
            
        else:
            # Fallback to generated sprites with improved isometric cube rendering
            base_wall = self.iso_renderer.create_cube_tile((220, 220, 220), (180, 180, 180), (140, 140, 140))
            self.tile_sprites[self.TILE_WALL] = base_wall
            
            # Create variations for different wall types with different colors
            # Corner walls - slightly darker for distinction
            corner_wall = self.iso_renderer.create_cube_tile((200, 200, 200), (160, 160, 160), (120, 120, 120))
            self.tile_sprites[self.TILE_WALL_CORNER_TL] = corner_wall
            self.tile_sprites[self.TILE_WALL_CORNER_TR] = corner_wall
            self.tile_sprites[self.TILE_WALL_CORNER_BL] = corner_wall
            self.tile_sprites[self.TILE_WALL_CORNER_BR] = corner_wall
            
            # Directional walls - slightly different tint
            horizontal_wall = self.iso_renderer.create_cube_tile((210, 210, 210), (170, 170, 170), (130, 130, 130))
            self.tile_sprites[self.TILE_WALL_HORIZONTAL] = horizontal_wall
            self.tile_sprites[self.TILE_WALL_VERTICAL] = horizontal_wall
            
            # Window walls - lighter color to suggest windows
            window_wall = self.iso_renderer.create_cube_tile((230, 230, 250), (190, 190, 210), (150, 150, 170))
            self.tile_sprites[self.TILE_WALL_WINDOW] = window_wall
            self.tile_sprites[self.TILE_WALL_WINDOW_HORIZONTAL] = window_wall
            self.tile_sprites[self.TILE_WALL_WINDOW_VERTICAL] = window_wall
        
        dirt_image = self.asset_loader.get_image("dirt_tile")
        if dirt_image:
            rotated_dirt = pygame.transform.rotate(dirt_image, 45)
            self.tile_sprites[self.TILE_DIRT] = pygame.transform.scale(rotated_dirt, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_DIRT] = self.iso_renderer.create_diamond_tile((150, 100, 50))
        
        # Brick tile for building interiors
        brick_image = self.asset_loader.get_image("brick_tile")
        if brick_image:
            rotated_brick = pygame.transform.rotate(brick_image, 45)
            self.tile_sprites[self.TILE_BRICK] = pygame.transform.scale(rotated_brick, (self.tile_width, self.tile_height))
        else:
            # Fallback to a reddish-brown color for brick
            self.tile_sprites[self.TILE_BRICK] = self.iso_renderer.create_diamond_tile((150, 80, 60))
        
        # Door - try improved isometric version first
        door_image = self.asset_loader.get_image("door_tile_isometric")
        if not door_image:
            door_image = self.asset_loader.get_image("door_tile")
        
        if door_image:
            # Scale door to be taller and more prominent
            door_height = self.tile_height + 24  # Make doors taller than normal tiles
            scaled_door = pygame.transform.scale(door_image, (self.tile_width, door_height))
            
            # Use the scaled door directly - no need for complex enhancement that might cause issues
            self.tile_sprites[self.TILE_DOOR] = scaled_door
        else:
            # Create enhanced door sprite with proper isometric proportions
            door_sprite = self.door_renderer.create_enhanced_door_sprite(self.tile_width, self.tile_height)
            self.tile_sprites[self.TILE_DOOR] = door_sprite

        # Load biome-specific tiles
        sand_image = self.asset_loader.get_image("sand_tile")
        if sand_image:
            rotated_sand = pygame.transform.rotate(sand_image, 45)
            self.tile_sprites[self.TILE_SAND] = pygame.transform.scale(rotated_sand, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_SAND] = self.iso_renderer.create_diamond_tile((220, 180, 120))  # Sandy color

        snow_image = self.asset_loader.get_image("snow_tile")
        if snow_image:
            rotated_snow = pygame.transform.rotate(snow_image, 45)
            self.tile_sprites[self.TILE_SNOW] = pygame.transform.scale(rotated_snow, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_SNOW] = self.iso_renderer.create_diamond_tile((240, 240, 255))  # Snowy white

        forest_floor_image = self.asset_loader.get_image("forest_floor_tile")
        if forest_floor_image:
            rotated_forest = pygame.transform.rotate(forest_floor_image, 45)
            self.tile_sprites[self.TILE_FOREST_FLOOR] = pygame.transform.scale(rotated_forest, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_FOREST_FLOOR] = self.iso_renderer.create_diamond_tile((80, 60, 40))  # Dark forest floor

        swamp_image = self.asset_loader.get_image("swamp_tile")
        if swamp_image:
            rotated_swamp = pygame.transform.rotate(swamp_image, 45)
            self.tile_sprites[self.TILE_SWAMP] = pygame.transform.scale(rotated_swamp, (self.tile_width, self.tile_height))
        else:
            self.tile_sprites[self.TILE_SWAMP] = self.iso_renderer.create_diamond_tile((60, 80, 50))  # Murky swamp color
