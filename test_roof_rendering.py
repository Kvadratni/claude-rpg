#!/usr/bin/env python3
"""
Roof rendering test
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.assets import AssetLoader
from src.core.isometric import IsometricRenderer
from src.wall_renderer import WallRenderer
from src.roof_renderer import RoofRenderer

class MockLevel:
    """Mock level class for testing"""
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.tile_width = 64
        self.tile_height = 32
        self.width = 20
        self.height = 20
        self.tile_sprites = {}
        
        # Create a tiles array to store our building data
        self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Define tile constants
        self.TILE_GRASS = 1
        self.TILE_STONE = 2
        self.TILE_WATER = 3
        self.TILE_DIRT = 4
        self.TILE_WALL = 5
        self.TILE_WALL_CORNER_TL = 6
        self.TILE_WALL_CORNER_TR = 7
        self.TILE_WALL_CORNER_BL = 8
        self.TILE_WALL_CORNER_BR = 9
        self.TILE_WALL_HORIZONTAL = 10
        self.TILE_WALL_VERTICAL = 11
        self.TILE_WALL_WINDOW = 12
        self.TILE_WALL_WINDOW_HORIZONTAL = 14
        self.TILE_WALL_WINDOW_VERTICAL = 15
        self.TILE_DOOR = 16
    
    def populate_tiles(self, building_tiles):
        """Populate the tiles array with building data"""
        for world_x, world_y, tile_type in building_tiles:
            if 0 <= world_x < self.width and 0 <= world_y < self.height:
                self.tiles[world_y][world_x] = tile_type

def main():
    pygame.init()
    
    # Set up display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Roof Rendering Test")
    
    # Load assets
    asset_loader = AssetLoader()
    iso_renderer = IsometricRenderer()
    
    # Create mock level
    level = MockLevel()
    level.asset_loader = asset_loader
    
    # Create wall renderer
    wall_renderer = WallRenderer(level)
    
    # Create roof renderer
    roof_renderer = RoofRenderer(level)
    
    # Simple player position for testing roof visibility
    player_x, player_y = 7.0, 7.0  # Start outside buildings
    
    print("Starting roof rendering test...")
    print(f"Wall texture loaded: {asset_loader.get_image('wall_texture') is not None}")
    print(f"Roof texture loaded: {asset_loader.get_image('roof_texture') is not None}")
    
    # Create two simple 5x5 buildings for testing
    def create_building_tiles(building_x, building_y):
        """Create a 5x5 building with walls around the perimeter and floor inside"""
        building_tiles = []
        for dy in range(5):
            for dx in range(5):
                x, y = building_x + dx, building_y + dy
                
                # Determine tile type based on position
                if dx == 0 or dx == 4 or dy == 0 or dy == 4:
                    # Perimeter - walls
                    if (dx == 0 and dy == 0):
                        tile_type = level.TILE_WALL_CORNER_TL
                    elif (dx == 4 and dy == 0):
                        tile_type = level.TILE_WALL_CORNER_TR
                    elif (dx == 0 and dy == 4):
                        tile_type = level.TILE_WALL_CORNER_BL
                    elif (dx == 4 and dy == 4):
                        tile_type = level.TILE_WALL_CORNER_BR
                    elif dx == 2 and dy == 0:
                        tile_type = level.TILE_DOOR  # Door at top center
                    elif dx == 0 or dx == 4:
                        tile_type = level.TILE_WALL_VERTICAL
                    else:
                        tile_type = level.TILE_WALL_HORIZONTAL
                else:
                    # Interior - floor
                    tile_type = 1  # Stone floor
                
                building_tiles.append((x, y, tile_type))
        return building_tiles
    
    # Create two buildings
    building1_tiles = create_building_tiles(2, 2)   # Building 1 at (2,2)
    building2_tiles = create_building_tiles(10, 2)  # Building 2 at (10,2)
    all_building_tiles = building1_tiles + building2_tiles
    
    # Populate the mock level's tiles array so wall renderer can check adjacencies
    level.populate_tiles(all_building_tiles)
    
    # Add some test NPCs and objects inside buildings
    test_entities = [
        # Building 1 NPCs/objects
        {'type': 'npc', 'x': 3, 'y': 3, 'sprite': 'npc_shopkeeper', 'name': 'Shopkeeper'},
        {'type': 'object', 'x': 4, 'y': 4, 'sprite': 'wooden_chest_closed', 'name': 'Chest'},
        {'type': 'npc', 'x': 5, 'y': 3, 'sprite': 'trader', 'name': 'Trader'},
        
        # Building 2 NPCs/objects  
        {'type': 'npc', 'x': 11, 'y': 3, 'sprite': 'elder_npc', 'name': 'Elder'},
        {'type': 'object', 'x': 12, 'y': 4, 'sprite': 'iron_chest_closed', 'name': 'Iron Chest'},
        {'type': 'npc', 'x': 13, 'y': 3, 'sprite': 'innkeeper', 'name': 'Innkeeper'},
        
        # Outside entities (should always be visible)
        {'type': 'npc', 'x': 8, 'y': 4, 'sprite': 'village_guard_sprite', 'name': 'Guard'},
        {'type': 'object', 'x': 1, 'y': 1, 'sprite': 'tree', 'name': 'Tree'},
    ]
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Player movement for testing roof visibility
                elif event.key == pygame.K_UP:
                    player_y -= 1
                elif event.key == pygame.K_DOWN:
                    player_y += 1
                elif event.key == pygame.K_LEFT:
                    player_x -= 1
                elif event.key == pygame.K_RIGHT:
                    player_x += 1
        
        # Clear screen
        screen.fill((34, 139, 34))  # Forest green background
        
        # Render all building tiles
        for world_x, world_y, tile_type in all_building_tiles:
            # Calculate screen position using isometric conversion
            screen_x, screen_y = iso_renderer.world_to_screen(world_x, world_y, 0, 0)
            
            # Adjust to center on screen
            screen_x += 400  # Center horizontally
            screen_y += 200  # Center vertically
            
            # Create a surface for this tile
            tile_surface = pygame.Surface((150, 100), pygame.SRCALPHA)
            
            # Determine render type
            if wall_renderer.is_wall_tile(tile_type) or tile_type == level.TILE_DOOR:
                render_type = 'wall'
            else:
                render_type = 'floor'
            
            # Simple roof rendering logic for our test
            # Show roofs when player is outside buildings, hide when inside
            should_render_roof = False
            
            # Check if player is inside any building
            player_tile_x = int(player_x)
            player_tile_y = int(player_y)
            
            # Check if this tile is part of a building
            is_building_tile = False
            building_id = 0
            
            # Building 1 (2-6, 2-6)
            if 2 <= world_x <= 6 and 2 <= world_y <= 6:
                is_building_tile = True
                building_id = 1
            
            # Building 2 (10-14, 2-6)
            if 10 <= world_x <= 14 and 2 <= world_y <= 6:
                is_building_tile = True
                building_id = 2
            
            if is_building_tile:
                # Default: show roof
                should_render_roof = True
                
                # Hide roof if player is inside THIS building
                if building_id == 1 and (2 <= player_tile_x <= 6 and 2 <= player_tile_y <= 6):
                    should_render_roof = False
                elif building_id == 2 and (10 <= player_tile_x <= 14 and 2 <= player_tile_y <= 6):
                    should_render_roof = False
            
            if should_render_roof:
                # First render the normal tile (wall or floor) - but skip wall tops since roof covers them
                if render_type == 'wall':
                    # Render wall using wall renderer (without top face since roof covers it)
                    wall_renderer.render_flat_wall(
                        tile_surface, 
                        75,   # center of the 150px wide surface
                        50,   # center of the 100px tall surface
                        tile_type,
                        world_x,
                        world_y
                    )
                elif render_type == 'floor':
                    # Render floor tile using the same method as the main game
                    floor_sprite = asset_loader.get_image('stone_tile')  # Stone floor for buildings
                    if floor_sprite:
                        # Rotate the tile 45 degrees for proper isometric alignment (same as main game)
                        rotated_stone = pygame.transform.rotate(floor_sprite, 45)
                        # Scale to tile dimensions
                        scaled_sprite = pygame.transform.scale(rotated_stone, (level.tile_width, level.tile_height))
                        
                        # Center the sprite in our surface
                        sprite_rect = scaled_sprite.get_rect()
                        sprite_rect.center = (75, 50)
                        tile_surface.blit(scaled_sprite, sprite_rect)
                
                # Then render roof ON TOP (roof replaces wall top faces)
                roof_texture = asset_loader.get_image('roof_texture')
                if roof_texture:
                    # Create isometric roof tile (same method as floor tiles)
                    rotated_roof = pygame.transform.rotate(roof_texture, 45)
                    scaled_roof = pygame.transform.scale(rotated_roof, (level.tile_width, level.tile_height))
                    
                    # Position roof even higher to be clearly on top of walls
                    roof_rect = scaled_roof.get_rect()
                    roof_rect.center = (75, 5)  # Even higher (was 15, now 5)
                    tile_surface.blit(scaled_roof, roof_rect)
                else:
                    # Fallback: simple dark rectangle
                    roof_surface = pygame.Surface((level.tile_width, level.tile_height), pygame.SRCALPHA)
                    roof_surface.fill((80, 40, 20))  # Dark brown
                    roof_rect = roof_surface.get_rect()
                    roof_rect.center = (75, 5)  # Even higher
                    tile_surface.blit(roof_surface, roof_rect)
            else:
                # No roof - render walls normally or just floor for interior
                if is_building_tile:
                    # Player is inside - show wall outlines and interior floors
                    if render_type == 'wall':
                        # Show just the top face of walls (outline) when inside
                        if tile_type == level.TILE_DOOR:
                            # Special rendering for doors - show archway texture rotated 90 degrees
                            archway_texture = asset_loader.get_image('archway_texture')
                            if archway_texture:
                                # Rotate 90 degrees first, then 45 for isometric
                                rotated_archway = pygame.transform.rotate(archway_texture, 90)
                                final_archway = pygame.transform.rotate(rotated_archway, 45)
                                scaled_archway = pygame.transform.scale(final_archway, (level.tile_width, level.tile_height))
                                archway_rect = scaled_archway.get_rect()
                                archway_rect.center = (75, 50)
                                tile_surface.blit(scaled_archway, archway_rect)
                            else:
                                # Fallback: lighter colored diamond for door
                                door_surface = pygame.Surface((level.tile_width, level.tile_height), pygame.SRCALPHA)
                                door_surface.fill((200, 150, 100))  # Light brown for door
                                door_rect = door_surface.get_rect()
                                door_rect.center = (75, 50)
                                tile_surface.blit(door_surface, door_rect)
                        else:
                            # Show wall top face (outline) - use wall texture
                            wall_texture = asset_loader.get_image('wall_texture')
                            if wall_texture:
                                rotated_wall = pygame.transform.rotate(wall_texture, 45)
                                scaled_wall = pygame.transform.scale(rotated_wall, (level.tile_width, level.tile_height))
                                wall_rect = scaled_wall.get_rect()
                                wall_rect.center = (75, 50)
                                tile_surface.blit(scaled_wall, wall_rect)
                            else:
                                # Fallback: gray diamond for wall outline
                                wall_surface = pygame.Surface((level.tile_width, level.tile_height), pygame.SRCALPHA)
                                wall_surface.fill((150, 150, 150))  # Gray for wall outline
                                wall_rect = wall_surface.get_rect()
                                wall_rect.center = (75, 50)
                                tile_surface.blit(wall_surface, wall_rect)
                    elif render_type == 'floor':
                        # Render interior floor tile
                        floor_sprite = asset_loader.get_image('stone_tile')  # Stone floor for buildings
                        if floor_sprite:
                            # Rotate the tile 45 degrees for proper isometric alignment (same as main game)
                            rotated_stone = pygame.transform.rotate(floor_sprite, 45)
                            # Scale to tile dimensions
                            scaled_sprite = pygame.transform.scale(rotated_stone, (level.tile_width, level.tile_height))
                            
                            # Center the sprite in our surface
                            sprite_rect = scaled_sprite.get_rect()
                            sprite_rect.center = (75, 50)
                            tile_surface.blit(scaled_sprite, sprite_rect)
                else:
                    # Outside building - render normally
                    if render_type == 'wall':
                        # Render wall using wall renderer
                        wall_renderer.render_flat_wall(
                            tile_surface, 
                            75,   # center of the 150px wide surface
                            50,   # center of the 100px tall surface
                            tile_type,
                            world_x,
                            world_y
                        )
                    elif render_type == 'floor':
                        # Render floor tile using the same method as the main game
                        floor_sprite = asset_loader.get_image('stone_tile')  # Stone floor for buildings
                        if floor_sprite:
                            # Rotate the tile 45 degrees for proper isometric alignment (same as main game)
                            rotated_stone = pygame.transform.rotate(floor_sprite, 45)
                            # Scale to tile dimensions
                            scaled_sprite = pygame.transform.scale(rotated_stone, (level.tile_width, level.tile_height))
                            
                            # Center the sprite in our surface
                            sprite_rect = scaled_sprite.get_rect()
                            sprite_rect.center = (75, 50)
                            tile_surface.blit(scaled_sprite, sprite_rect)
            
            # Blit to main screen
            screen.blit(tile_surface, (screen_x - 75, screen_y - 50))
        
        # Render entities (NPCs and objects) with visibility logic
        for entity in test_entities:
            entity_x, entity_y = entity['x'], entity['y']
            
            # Check if entity should be visible
            should_render_entity = True
            
            # Check if entity is inside a building
            entity_in_building_1 = (2 <= entity_x <= 6 and 2 <= entity_y <= 6)
            entity_in_building_2 = (10 <= entity_x <= 14 and 2 <= entity_y <= 6)
            
            if entity_in_building_1 or entity_in_building_2:
                # Entity is inside a building - only show if player is in the SAME building
                player_tile_x = int(player_x)
                player_tile_y = int(player_y)
                
                player_in_building_1 = (2 <= player_tile_x <= 6 and 2 <= player_tile_y <= 6)
                player_in_building_2 = (10 <= player_tile_x <= 14 and 2 <= player_tile_y <= 6)
                
                if entity_in_building_1 and not player_in_building_1:
                    should_render_entity = False  # Entity in building 1, player not in building 1
                elif entity_in_building_2 and not player_in_building_2:
                    should_render_entity = False  # Entity in building 2, player not in building 2
            
            if should_render_entity:
                # Calculate screen position for entity
                entity_screen_x, entity_screen_y = iso_renderer.world_to_screen(entity_x, entity_y, 0, 0)
                entity_screen_x += 400  # Center horizontally
                entity_screen_y += 200  # Center vertically
                
                # Load and render entity sprite
                entity_sprite = asset_loader.get_image(entity['sprite'])
                if entity_sprite:
                    # Scale sprite appropriately
                    scaled_sprite = pygame.transform.scale(entity_sprite, (32, 32))
                    sprite_rect = scaled_sprite.get_rect()
                    sprite_rect.center = (int(entity_screen_x), int(entity_screen_y - 16))  # Slightly above ground
                    screen.blit(scaled_sprite, sprite_rect)
                    
                    # Add name label
                    font = pygame.font.Font(None, 16)
                    name_text = font.render(entity['name'], True, (255, 255, 255))
                    name_rect = name_text.get_rect()
                    name_rect.center = (int(entity_screen_x), int(entity_screen_y + 20))
                    screen.blit(name_text, name_rect)
        
        # Draw player position indicator
        player_screen_x, player_screen_y = iso_renderer.world_to_screen(player_x, player_y, 0, 0)
        player_screen_x += 400
        player_screen_y += 200
        pygame.draw.circle(screen, (255, 255, 0), (int(player_screen_x), int(player_screen_y)), 8)  # Yellow circle
        
        # Add instructions
        font = pygame.font.Font(None, 36)
        title = font.render("Roof Rendering Test", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 20))
        
        instructions_font = pygame.font.Font(None, 20)
        instructions = [
            "Roof Rendering System Test with Entity Visibility:",
            "- Buildings show roofs when you're outside",
            "- Roofs disappear when you enter buildings",
            "- NPCs and objects inside buildings are hidden until you enter",
            "- Use arrow keys to move player (yellow circle)",
            f"Player position: ({player_x:.1f}, {player_y:.1f})",
            "Press ESC to exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instructions_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (20, screen_height - 100 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()