"""
Settings Menu - Game settings configuration interface
"""

import pygame
from .base_menu import BaseMenu

class SettingsMenu(BaseMenu):
    """Menu for configuring game settings"""
    
    def __init__(self, game, parent_menu=None):
        super().__init__(game)
        
        self.parent_menu = parent_menu
        self.menu_type = "settings"
        
        # Settings items
        self.settings_items = ["Resolution", "Music Volume", "SFX Volume", "Fullscreen", "Apply", "Back"]
        self.selected_item = 0
        self.menu_hover_time = [0] * len(self.settings_items)
        
        # Settings values (temporary until applied)
        settings = self.game.settings
        self.settings_values = {
            "music_volume": settings.get("music_volume"),
            "sfx_volume": settings.get("sfx_volume"),
            "fullscreen": settings.get("fullscreen")
        }
        
        # Resolution settings
        current_res = settings.get_current_resolution()
        available_res = settings.get_available_resolutions()
        try:
            self.resolution_index = available_res.index(current_res)
        except ValueError:
            self.resolution_index = 0
        
        # UI state
        self.resolution_dropdown_open = False
        self.dragging_music_slider = False
        self.dragging_sfx_slider = False
        
        # UI element rectangles
        self._resolution_dropdown_rect = None
        self._resolution_option_rects = []
        self._music_slider_rect = None
        self._sfx_slider_rect = None
        self._fullscreen_toggle_rect = None
    
    def handle_event(self, event):
        """Handle settings menu events"""
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            self.update_mouse_hover(mouse_x, mouse_y)
            
            # Handle slider dragging
            if self.dragging_music_slider:
                self.update_volume_from_mouse(event.pos, "music")
            elif self.dragging_sfx_slider:
                self.update_volume_from_mouse(event.pos, "sfx")
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.handle_settings_click(event.pos):
                    return  # Handled by settings controls
                
                # Handle normal menu selection
                if self.mouse_hover >= 0:
                    self.selected_item = self.mouse_hover
                    self.select_item()
            elif event.button == 3:  # Right click (decrease values)
                if self.mouse_hover >= 0:
                    self.adjust_setting(self.mouse_hover, -1)
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging_music_slider = False
                self.dragging_sfx_slider = False
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.back_to_parent()
            elif event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.settings_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.settings_items)
            elif event.key == pygame.K_LEFT:
                self.adjust_setting(self.selected_item, -1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_setting(self.selected_item, 1)
            elif event.key == pygame.K_RETURN:
                self.select_item()
    
    def adjust_setting(self, setting_index, direction):
        """Adjust a setting value (direction: 1 for increase, -1 for decrease)"""
        if setting_index == 0:  # Resolution
            available_res = self.game.settings.get_available_resolutions()
            self.resolution_index = (self.resolution_index + direction) % len(available_res)
        elif setting_index == 1:  # Music Volume
            self.settings_values["music_volume"] = max(0.0, min(1.0, 
                self.settings_values["music_volume"] + direction * 0.1))
        elif setting_index == 2:  # SFX Volume
            self.settings_values["sfx_volume"] = max(0.0, min(1.0, 
                self.settings_values["sfx_volume"] + direction * 0.1))
        elif setting_index == 3:  # Fullscreen
            self.settings_values["fullscreen"] = not self.settings_values["fullscreen"]
    
    def handle_settings_click(self, mouse_pos):
        """Handle clicks on settings UI elements. Returns True if handled."""
        mouse_x, mouse_y = mouse_pos
        
        # Check if clicking on resolution dropdown
        if self._resolution_dropdown_rect and self._resolution_dropdown_rect.collidepoint(mouse_x, mouse_y):
            self.resolution_dropdown_open = not self.resolution_dropdown_open
            return True
        
        # Check if clicking on dropdown options when open
        if self.resolution_dropdown_open and self._resolution_option_rects:
            for i, rect in enumerate(self._resolution_option_rects):
                if rect.collidepoint(mouse_x, mouse_y):
                    self.resolution_index = i
                    self.resolution_dropdown_open = False
                    return True
        
        # Check if clicking on volume sliders
        if self._music_slider_rect and self._music_slider_rect.collidepoint(mouse_x, mouse_y):
            self.dragging_music_slider = True
            self.update_volume_from_mouse(mouse_pos, "music")
            return True
        
        if self._sfx_slider_rect and self._sfx_slider_rect.collidepoint(mouse_x, mouse_y):
            self.dragging_sfx_slider = True
            self.update_volume_from_mouse(mouse_pos, "sfx")
            return True
        
        # Check if clicking on fullscreen toggle
        if self._fullscreen_toggle_rect and self._fullscreen_toggle_rect.collidepoint(mouse_x, mouse_y):
            self.settings_values["fullscreen"] = not self.settings_values["fullscreen"]
            return True
        
        return False
    
    def update_volume_from_mouse(self, mouse_pos, volume_type):
        """Update volume based on mouse position on slider"""
        mouse_x, mouse_y = mouse_pos
        
        if volume_type == "music" and self._music_slider_rect:
            slider_rect = self._music_slider_rect
        elif volume_type == "sfx" and self._sfx_slider_rect:
            slider_rect = self._sfx_slider_rect
        else:
            return
        
        # Calculate volume based on mouse position
        relative_x = mouse_x - slider_rect.x
        volume = max(0.0, min(1.0, relative_x / slider_rect.width))
        
        if volume_type == "music":
            self.settings_values["music_volume"] = volume
        else:
            self.settings_values["sfx_volume"] = volume
    
    def select_item(self):
        """Handle settings menu item selection"""
        if self.selected_item == 0:  # Resolution
            self.adjust_setting(0, 1)
        elif self.selected_item == 1:  # Music Volume
            self.adjust_setting(1, 1)
        elif self.selected_item == 2:  # SFX Volume
            self.adjust_setting(2, 1)
        elif self.selected_item == 3:  # Fullscreen
            self.adjust_setting(3, 1)
        elif self.selected_item == 4:  # Apply
            self.apply_settings()
        elif self.selected_item == 5:  # Back
            self.back_to_parent()
    
    def apply_settings(self):
        """Apply the current settings"""
        settings = self.game.settings
        
        # Apply resolution
        available_res = settings.get_available_resolutions()
        if 0 <= self.resolution_index < len(available_res):
            new_resolution = available_res[self.resolution_index]
            settings.set("window_width", new_resolution[0])
            settings.set("window_height", new_resolution[1])
        
        # Apply other settings
        settings.set("music_volume", self.settings_values["music_volume"])
        settings.set("sfx_volume", self.settings_values["sfx_volume"])
        settings.set("fullscreen", self.settings_values["fullscreen"])
        
        # Save settings
        settings.save_settings()
        
        # Apply settings to the game
        self.game.apply_settings()
        
        print("Settings applied successfully!")
    
    def back_to_parent(self):
        """Return to parent menu"""
        if self.parent_menu:
            self.game.menu = self.parent_menu
        else:
            from .main_menu import MainMenu
            self.game.menu = MainMenu(self.game)
    
    def render(self, screen):
        """Render the settings menu"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Render background
        if hasattr(self.parent_menu, 'menu_type') and self.parent_menu.menu_type == "pause":
            # Semi-transparent overlay for pause menu
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(180)
            overlay.fill(self.colors['bg_dark'])
            screen.blit(overlay, (0, 0))
        else:
            # Full background for main menu
            self.render_gradient_background(screen, screen_width, screen_height)
            self.render_background_stars(screen)
        
        # Render particles
        self.render_particles(screen)
        
        # Settings title
        title_text = "SETTINGS"
        title_surface = self.title_font.render(title_text, True, self.colors['title_gold'])
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_surface, title_rect)
        
        # Render settings menu
        self.render_settings_menu(screen, screen_width, screen_height)
        
        # Render dropdown overlay if open
        if self.resolution_dropdown_open:
            self.render_dropdown_overlay(screen)
        
        # Render instructions
        instruction_text = "Left Click: Increase/Toggle • Right Click: Decrease • Esc to Go Back"
        self.render_instructions(screen, screen_width, screen_height, instruction_text)
    
    def render_settings_menu(self, screen, width, height):
        """Render the settings menu with sliders and dropdown"""
        # Clear and initialize rectangles list
        self.menu_rects = [None] * len(self.settings_items)
        
        start_y = height // 2 - 150
        item_spacing = 80
        
        for i, item in enumerate(self.settings_items):
            y_pos = start_y + i * item_spacing
            
            # Determine if this item is hovered
            is_hovered = (i == self.mouse_hover)
            
            # Render label (except for Apply/Back buttons)
            if i < 4:
                label_color = self.colors['menu_selected'] if is_hovered else self.colors['menu_normal']
                label_surface = self.menu_font.render(item, True, label_color)
                label_rect = label_surface.get_rect()
                label_rect.x = width // 2 - 200
                label_rect.centery = y_pos
                screen.blit(label_surface, label_rect)
            
            # Render control based on item type
            if i == 0:  # Resolution dropdown
                self.render_resolution_dropdown(screen, width // 2 + 50, y_pos, is_hovered)
            elif i == 1:  # Music Volume slider
                self.render_volume_slider(screen, width // 2 + 50, y_pos, "music", is_hovered)
            elif i == 2:  # SFX Volume slider
                self.render_volume_slider(screen, width // 2 + 50, y_pos, "sfx", is_hovered)
            elif i == 3:  # Fullscreen toggle
                self.render_fullscreen_toggle(screen, width // 2 + 50, y_pos, is_hovered)
            elif i == 4 or i == 5:  # Apply/Back buttons
                self.render_button(screen, width // 2, y_pos, item, is_hovered, i)
    
    def render_resolution_dropdown(self, screen, x, y, is_hovered):
        """Render resolution dropdown"""
        available_res = self.game.settings.get_available_resolutions()
        current_res = available_res[self.resolution_index] if 0 <= self.resolution_index < len(available_res) else (1024, 768)
        
        # Dropdown button
        dropdown_width = 200
        dropdown_height = 40
        dropdown_rect = pygame.Rect(x, y - dropdown_height // 2, dropdown_width, dropdown_height)
        self._resolution_dropdown_rect = dropdown_rect
        
        # Button background
        button_color = self.colors['accent_blue'] if is_hovered else (60, 60, 60)
        pygame.draw.rect(screen, button_color, dropdown_rect)
        pygame.draw.rect(screen, self.colors['border_color'], dropdown_rect, 2)
        
        # Current resolution text
        res_text = f"{current_res[0]}x{current_res[1]}"
        text_surface = self.subtitle_font.render(res_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=dropdown_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Dropdown arrow
        arrow_points = [
            (x + dropdown_width - 20, y - 5),
            (x + dropdown_width - 10, y + 5),
            (x + dropdown_width - 30, y + 5)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points)
        
        # Store dropdown rect for menu system
        self.menu_rects[0] = dropdown_rect
    
    def render_volume_slider(self, screen, x, y, volume_type, is_hovered):
        """Render volume slider"""
        slider_width = 200
        slider_height = 20
        slider_rect = pygame.Rect(x, y - slider_height // 2, slider_width, slider_height)
        
        # Store slider rect for interaction
        if volume_type == "music":
            self._music_slider_rect = slider_rect
            volume = self.settings_values["music_volume"]
            slider_index = 1
        else:
            self._sfx_slider_rect = slider_rect
            volume = self.settings_values["sfx_volume"]
            slider_index = 2
        
        # Slider background
        pygame.draw.rect(screen, (40, 40, 40), slider_rect)
        pygame.draw.rect(screen, self.colors['border_color'], slider_rect, 2)
        
        # Slider fill
        fill_width = int(slider_width * volume)
        fill_rect = pygame.Rect(x, y - slider_height // 2, fill_width, slider_height)
        fill_color = self.colors['accent_blue'] if is_hovered else self.colors['accent_purple']
        pygame.draw.rect(screen, fill_color, fill_rect)
        
        # Volume percentage text
        volume_text = f"{int(volume * 100)}%"
        text_surface = self.small_font.render(volume_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + slider_width + 30, y))
        screen.blit(text_surface, text_rect)
        
        # Store slider rect for menu system
        self.menu_rects[slider_index] = slider_rect
    
    def render_fullscreen_toggle(self, screen, x, y, is_hovered):
        """Render fullscreen toggle"""
        toggle_width = 60
        toggle_height = 30
        toggle_rect = pygame.Rect(x, y - toggle_height // 2, toggle_width, toggle_height)
        self._fullscreen_toggle_rect = toggle_rect
        
        # Toggle background
        bg_color = self.colors['accent_blue'] if self.settings_values["fullscreen"] else (60, 60, 60)
        pygame.draw.rect(screen, bg_color, toggle_rect, border_radius=15)
        pygame.draw.rect(screen, self.colors['border_color'], toggle_rect, 2, border_radius=15)
        
        # Toggle switch
        switch_x = x + toggle_width - 20 if self.settings_values["fullscreen"] else x + 10
        switch_rect = pygame.Rect(switch_x, y - 10, 20, 20)
        pygame.draw.ellipse(screen, (255, 255, 255), switch_rect)
        
        # Toggle text
        toggle_text = "ON" if self.settings_values["fullscreen"] else "OFF"
        text_surface = self.small_font.render(toggle_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + toggle_width + 30, y))
        screen.blit(text_surface, text_rect)
        
        # Store toggle rect for menu system
        self.menu_rects[3] = toggle_rect
    
    def render_button(self, screen, x, y, text, is_hovered, index):
        """Render Apply/Back buttons"""
        button_rect = pygame.Rect(x - 100, y - 25, 200, 50)
        self.menu_rects[index] = button_rect
        
        if is_hovered:
            pygame.draw.rect(screen, self.colors['accent_blue'], button_rect)
            pygame.draw.rect(screen, self.colors['menu_selected'], button_rect, 2)
            text_color = (255, 255, 255)
        else:
            pygame.draw.rect(screen, (60, 60, 60), button_rect)
            pygame.draw.rect(screen, self.colors['border_color'], button_rect, 2)
            text_color = self.colors['menu_normal']
        
        # Render button text
        button_text = self.menu_font.render(text, True, text_color)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
    
    def render_dropdown_overlay(self, screen):
        """Render dropdown options overlay"""
        if not self._resolution_dropdown_rect:
            return
        
        available_res = self.game.settings.get_available_resolutions()
        self._resolution_option_rects = []
        
        option_height = 35
        start_y = self._resolution_dropdown_rect.bottom
        
        for i, resolution in enumerate(available_res):
            option_rect = pygame.Rect(
                self._resolution_dropdown_rect.x,
                start_y + i * option_height,
                self._resolution_dropdown_rect.width,
                option_height
            )
            self._resolution_option_rects.append(option_rect)
            
            # Option background
            if i == self.resolution_index:
                pygame.draw.rect(screen, self.colors['accent_blue'], option_rect)
            else:
                pygame.draw.rect(screen, (80, 80, 80), option_rect)
            pygame.draw.rect(screen, self.colors['border_color'], option_rect, 1)
            
            # Option text
            res_text = f"{resolution[0]}x{resolution[1]}"
            text_surface = self.subtitle_font.render(res_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=option_rect.center)
            screen.blit(text_surface, text_rect)
