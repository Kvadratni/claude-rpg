"""
Menu Coordinator - Handles menu transitions and state management
"""

from .menu import MainMenu, PauseMenu, LoadMenu, SettingsMenu, GameOverMenu

class MenuCoordinator:
    """Coordinates between different menu types and handles transitions"""
    
    def __init__(self, game):
        self.game = game
        self.current_menu = None
        self.menu_stack = []  # For nested menus
        
        # Initialize with main menu
        self.show_main_menu()
    
    def show_main_menu(self):
        """Show the main menu"""
        self.current_menu = MainMenu(self.game)
        self.menu_stack = []
    
    def show_pause_menu(self):
        """Show the pause menu"""
        self.current_menu = PauseMenu(self.game)
        self.menu_stack = []
    
    def show_game_over_menu(self):
        """Show the game over menu"""
        self.current_menu = GameOverMenu(self.game)
        self.menu_stack = []
    
    def show_load_menu(self, parent_menu=None):
        """Show the load game menu"""
        if parent_menu:
            self.menu_stack.append(self.current_menu)
        self.current_menu = LoadMenu(self.game, parent_menu or self.current_menu)
    
    def show_settings_menu(self, parent_menu=None):
        """Show the settings menu"""
        if parent_menu:
            self.menu_stack.append(self.current_menu)
        self.current_menu = SettingsMenu(self.game, parent_menu or self.current_menu)
    
    def go_back(self):
        """Go back to the previous menu in the stack"""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
        else:
            self.show_main_menu()
    
    def handle_event(self, event):
        """Handle events for the current menu"""
        if self.current_menu:
            self.current_menu.handle_event(event)
    
    def update(self):
        """Update the current menu"""
        if self.current_menu:
            self.current_menu.update()
    
    def render(self, screen):
        """Render the current menu"""
        if self.current_menu:
            self.current_menu.render(screen)
    
    def get_menu_type(self):
        """Get the current menu type"""
        if self.current_menu:
            return getattr(self.current_menu, 'menu_type', 'unknown')
        return 'none'
