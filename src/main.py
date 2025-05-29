"""
Goose RPG - An Isometric RPG Game
Module entry point
"""

import pygame
import sys

from .game import Game

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