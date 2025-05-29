#!/usr/bin/env python3
"""
Test script to demonstrate improved doorway pathfinding
"""

import pygame
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.level import Level
from src.player import Player
from src.assets import AssetLoader

def test_doorway_pathfinding():
    """Test doorway pathfinding improvements"""
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Doorway Pathfinding Test")
    clock = pygame.time.Clock()
    
    # Initialize game components
    asset_loader = AssetLoader()
    player = Player(100, 102, asset_loader)  # Start in village center
    level = Level("test_level", player, asset_loader)
    
    print("=== Doorway Pathfinding Test ===")
    print("Instructions:")
    print("- Click near building doors to test pathfinding")
    print("- Yellow lines show the calculated path")
    print("- Green circle = start, Red circle = destination")
    print("- Cyan circles = door-related waypoints")
    print("- White circles = regular waypoints")
    print("- Press ESC to exit")
    print()
    
    # Test some specific door locations
    door_test_locations = [
        (77, 89),   # Near shopkeeper door
        (122, 89),  # Near elder's house door
        (76, 113),  # Near blacksmith door
        (121, 113), # Near inn door
        (100, 74),  # Near temple door
        (65, 101),  # Near guard house door
    ]
    
    current_test = 0
    auto_test_timer = 0
    auto_test_interval = 300  # 5 seconds at 60 FPS
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Manual test - cycle through door locations
                    if current_test < len(door_test_locations):
                        target_x, target_y = door_test_locations[current_test]
                        print(f"Testing pathfinding to door at ({target_x}, {target_y})")
                        
                        # Calculate path
                        path = level.find_path(player.x, player.y, target_x, target_y, player.size)
                        player.path = path
                        player.path_index = 0
                        
                        if path:
                            print(f"Path found with {len(path)} waypoints")
                            # Check for door-specific waypoints
                            door_waypoints = 0
                            for waypoint in path:
                                tile_x, tile_y = int(waypoint[0]), int(waypoint[1])
                                for dx in [-1, 0, 1]:
                                    for dy in [-1, 0, 1]:
                                        check_x, check_y = tile_x + dx, tile_y + dy
                                        if (0 <= check_x < level.width and 0 <= check_y < level.height):
                                            if level.tiles[check_y][check_x] == level.TILE_DOOR:
                                                door_waypoints += 1
                                                break
                            print(f"Door-related waypoints: {door_waypoints}")
                        else:
                            print("No path found!")
                        
                        current_test = (current_test + 1) % len(door_test_locations)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Convert screen to world coordinates
                    world_x, world_y = level.iso_renderer.screen_to_world(
                        event.pos[0], event.pos[1], level.camera_x, level.camera_y
                    )
                    
                    print(f"Testing pathfinding to clicked location ({world_x:.2f}, {world_y:.2f})")
                    
                    # Calculate path
                    path = level.find_path(player.x, player.y, world_x, world_y, player.size)
                    player.path = path
                    player.path_index = 0
                    
                    if path:
                        print(f"Path found with {len(path)} waypoints")
                    else:
                        print("No path found!")
        
        # Auto-test cycle through door locations
        auto_test_timer += 1
        if auto_test_timer >= auto_test_interval:
            auto_test_timer = 0
            if current_test < len(door_test_locations):
                target_x, target_y = door_test_locations[current_test]
                print(f"Auto-testing pathfinding to door at ({target_x}, {target_y})")
                
                # Calculate path
                path = level.find_path(player.x, player.y, target_x, target_y, player.size)
                player.path = path
                player.path_index = 0
                
                current_test = (current_test + 1) % len(door_test_locations)
        
        # Update game
        level.update()
        
        # Render
        level.render(screen)
        
        # Add test information overlay
        font = pygame.font.Font(None, 24)
        info_text = [
            "Doorway Pathfinding Test",
            f"Click to test pathfinding, SPACE for manual cycle, ESC to exit",
            f"Current test: {current_test + 1}/{len(door_test_locations)}",
            f"Player position: ({player.x:.1f}, {player.y:.1f})",
        ]
        
        if hasattr(player, 'path') and player.path:
            info_text.append(f"Path waypoints: {len(player.path)}")
        
        y_offset = 10
        for text in info_text:
            surface = font.render(text, True, (255, 255, 255))
            # Add background for readability
            bg_rect = surface.get_rect()
            bg_rect.x = 10
            bg_rect.y = y_offset
            bg_surface = pygame.Surface((bg_rect.width + 10, bg_rect.height + 4))
            bg_surface.fill((0, 0, 0))
            bg_surface.set_alpha(128)
            screen.blit(bg_surface, (bg_rect.x - 5, bg_rect.y - 2))
            screen.blit(surface, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()
    
    pygame.quit()
    print("Test completed!")

if __name__ == "__main__":
    test_doorway_pathfinding()