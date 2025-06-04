#!/usr/bin/env python3
"""
Check if window walls exist in the current game world
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game

def check_for_window_walls():
    """Check if window walls exist in the game world"""
    pygame.init()
    
    # Create a minimal display
    screen = pygame.display.set_mode((100, 100))
    
    # Create game instance and start a new game
    game = Game()
    
    # Simulate starting a new game
    game.state = game.STATE_PLAYING
    game.new_game()  # This should initialize the level
    
    if not hasattr(game.current_level, 'get_tile'):
        print("This level doesn't support chunk-based tile access")
        return
    
    # Define window wall tile types
    window_wall_types = [12, 14, 15]  # TILE_WALL_WINDOW, TILE_WALL_WINDOW_HORIZONTAL, TILE_WALL_WINDOW_VERTICAL
    
    # Search around the player's starting area
    player_x = int(game.current_level.player.x)
    player_y = int(game.current_level.player.y)
    
    search_radius = 50
    window_walls_found = []
    
    print(f"Searching for window walls around player position ({player_x}, {player_y})...")
    
    for y in range(player_y - search_radius, player_y + search_radius):
        for x in range(player_x - search_radius, player_x + search_radius):
            tile_type = game.current_level.get_tile(x, y)
            if tile_type in window_wall_types:
                window_walls_found.append((x, y, tile_type))
    
    if window_walls_found:
        print(f"Found {len(window_walls_found)} window walls:")
        for x, y, tile_type in window_walls_found[:10]:  # Show first 10
            tile_name = {12: "TILE_WALL_WINDOW", 14: "TILE_WALL_WINDOW_HORIZONTAL", 15: "TILE_WALL_WINDOW_VERTICAL"}[tile_type]
            print(f"  {tile_name} at ({x}, {y})")
        if len(window_walls_found) > 10:
            print(f"  ... and {len(window_walls_found) - 10} more")
    else:
        print("No window walls found in the search area")
        
        # Let's also check what types of tiles we do have
        tile_counts = {}
        for y in range(player_y - 20, player_y + 20):
            for x in range(player_x - 20, player_x + 20):
                tile_type = game.current_level.get_tile(x, y)
                if tile_type is not None:
                    tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
        
        print("\nTile types found in smaller area:")
        for tile_type, count in sorted(tile_counts.items()):
            print(f"  Tile {tile_type}: {count} instances")
    
    pygame.quit()

if __name__ == "__main__":
    check_for_window_walls()