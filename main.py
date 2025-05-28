#!/usr/bin/env python3
"""
Claude RPG - An Isometric RPG Game
Main entry point for the game
"""

import pygame
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.game import Game

def main():
    """Main function to start the game"""
    pygame.init()
    
    # Initialize the game
    game = Game()
    
    try:
        # Run the game
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()