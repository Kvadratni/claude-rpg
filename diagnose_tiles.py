#!/usr/bin/env python3
"""
Simple diagnostic to check for wall holes
"""

import pygame
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game

def check_for_holes():
    """Check for holes in buildings around player"""
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    
    # Create game instance
    game = Game()
    game.state = game.STATE_PLAYING
    game.new_game()
    
    if not hasattr(game.current_level, 'get_tile'):
        print("This level doesn't support tile access")
        return
    
    # Get player position
    player_x = int(game.current_level.player.x)
    player_y = int(game.current_level.player.y)
    
    print(f"Checking for wall holes around player at ({player_x}, {player_y})")
    
    # Look for doors and potential holes
    doors_found = []
    holes_found = []
    search_radius = 30
    
    for y in range(player_y - search_radius, player_y + search_radius):
        for x in range(player_x - search_radius, player_x + search_radius):
            tile_type = game.current_level.get_tile(x, y)
            
            # Check for doors
            if tile_type == 5:  # DOOR
                doors_found.append((x, y))
            
            # Check if this is grass (potential hole)
            elif tile_type == 0:  # GRASS
                # Count surrounding walls
                wall_count = 0
                wall_types = [5, 6, 7, 8, 9, 10, 11, 12, 14, 15]  # All wall types
                
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor_tile = game.current_level.get_tile(x + dx, y + dy)
                        if neighbor_tile in wall_types:
                            wall_count += 1
                
                # If surrounded by many walls, it's likely a hole
                if wall_count >= 5:  # At least 5 of 8 neighbors are walls
                    holes_found.append((x, y, wall_count))
    
    print(f"Found {len(doors_found)} doors in the area")
    if doors_found:
        for x, y in doors_found[:5]:  # Show first 5
            print(f"  Door at ({x}, {y})")
    
    if holes_found:
        print(f"Found {len(holes_found)} potential wall holes:")
        for x, y, wall_count in holes_found[:10]:  # Show first 10
            print(f"  Hole at ({x}, {y}) - surrounded by {wall_count}/8 walls")
            
            # Show what's around this hole
            print(f"    Surrounding tiles:")
            for dy in [-1, 0, 1]:
                row = ""
                for dx in [-1, 0, 1]:
                    neighbor_tile = game.current_level.get_tile(x + dx, y + dy)
                    if dx == 0 and dy == 0:
                        row += " [0] "  # The hole
                    else:
                        row += f" {neighbor_tile:2d} "
                print(f"      {row}")
    else:
        print("No obvious wall holes found")
    
    pygame.quit()

if __name__ == "__main__":
    check_for_holes()