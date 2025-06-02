"""
HUD (Heads-Up Display) - In-game UI elements
"""

import pygame
import math

class HUD:
    """Heads-up display for in-game UI elements"""
    
    def __init__(self, game):
        self.game = game
        self.player = game.player
        
        # Fonts
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 32)
        
        # Colors
        self.colors = {
            'panel_bg': (40, 40, 40),
            'panel_border': (100, 100, 100),
            'health_color': (220, 50, 50),
            'stamina_color': (50, 150, 220),
            'xp_color': (100, 255, 100),
            'gold_color': (255, 215, 0),
            'text_color': (255, 255, 255),
            'slot_bg': (60, 60, 60),
            'slot_border': (100, 100, 100)
        }
    
    def render(self, screen):
        """Render the complete HUD"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create UI panel at bottom
        ui_height = 150
        ui_panel = pygame.Surface((screen_width, ui_height))
        ui_panel.fill(self.colors['panel_bg'])
        
        # Draw border
        pygame.draw.rect(ui_panel, self.colors['panel_border'], (0, 0, screen_width, ui_height), 2)
        
        # Render different sections
        self.render_player_stats(ui_panel)
        self.render_equipment_slots(ui_panel, screen_width)
        self.render_xp_bar(ui_panel, screen_width)
        self.render_movement_mode_indicator(ui_panel, screen_width)
        
        # Blit the UI panel to the screen
        screen.blit(ui_panel, (0, screen_height - ui_height))
    
    def render_player_stats(self, surface):
        """Render player health, stamina, level, and gold"""
        # Render circular health and stamina bars
        self.render_circular_bars(surface, 20, 30)
        
        # Player level and gold
        stats_x = 160
        level_text = f"Level {self.player.level}"
        gold_text = f"Gold: {self.player.gold}"
        
        level_surface = self.small_font.render(level_text, True, self.colors['gold_color'])
        gold_surface = self.small_font.render(gold_text, True, self.colors['gold_color'])
        surface.blit(level_surface, (stats_x, 15))
        surface.blit(gold_surface, (stats_x, 35))
    
    def render_circular_bars(self, surface, x, y):
        """Render circular health and stamina bars"""
        # Health circle (left)
        health_center = (x + 40, y + 40)
        health_radius = 35
        health_percentage = self.player.health / self.player.max_health
        
        # Background circle
        pygame.draw.circle(surface, (80, 80, 80), health_center, health_radius, 3)
        
        # Health arc
        if health_percentage > 0:
            self.draw_arc(surface, self.colors['health_color'], health_center, health_radius, 
                         -90, -90 + (360 * health_percentage), 6)
        
        # Health text
        health_text = f"{int(self.player.health)}"
        health_surface = self.small_font.render(health_text, True, self.colors['text_color'])
        health_rect = health_surface.get_rect(center=health_center)
        surface.blit(health_surface, health_rect)
        
        # Stamina circle (right)
        stamina_center = (x + 100, y + 40)
        stamina_radius = 35
        stamina_percentage = self.player.stamina / self.player.max_stamina
        
        # Background circle
        pygame.draw.circle(surface, (80, 80, 80), stamina_center, stamina_radius, 3)
        
        # Stamina arc
        if stamina_percentage > 0:
            self.draw_arc(surface, self.colors['stamina_color'], stamina_center, stamina_radius,
                         -90, -90 + (360 * stamina_percentage), 6)
        
        # Stamina text
        stamina_text = f"{int(self.player.stamina)}"
        stamina_surface = self.small_font.render(stamina_text, True, self.colors['text_color'])
        stamina_rect = stamina_surface.get_rect(center=stamina_center)
        surface.blit(stamina_surface, stamina_rect)
    
    def draw_arc(self, surface, color, center, radius, start_angle, end_angle, width):
        """Draw an arc (portion of a circle)"""
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Calculate points for the arc
        points = []
        num_points = max(3, int(abs(end_angle - start_angle) / 5))  # More points for smoother arc
        
        for i in range(num_points + 1):
            angle = start_rad + (end_rad - start_rad) * i / num_points
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        
        # Draw the arc as connected lines
        if len(points) > 1:
            for i in range(len(points) - 1):
                pygame.draw.line(surface, color, points[i], points[i + 1], width)
    
    def render_equipment_slots(self, surface, screen_width):
        """Render equipment slots showing current weapon and armor"""
        equipment_x = 280
        slot_size = 80
        slot_y = 30
        
        # Current weapon display
        weapon_rect = pygame.Rect(equipment_x, slot_y, slot_size, slot_size)
        pygame.draw.rect(surface, self.colors['slot_bg'], weapon_rect)
        pygame.draw.rect(surface, self.colors['slot_border'], weapon_rect, 2)
        
        # Weapon sprite and name
        if self.player.equipped_weapon:
            weapon_sprite = self.player.equipped_weapon.sprite
            if weapon_sprite:
                # Scale sprite to fit slot
                scaled_sprite = pygame.transform.scale(weapon_sprite, (slot_size - 10, slot_size - 10))
                sprite_rect = scaled_sprite.get_rect(center=weapon_rect.center)
                surface.blit(scaled_sprite, sprite_rect)
            
            # Weapon name below slot
            weapon_name = self.small_font.render(self.player.equipped_weapon.name, True, self.colors['text_color'])
            weapon_name_rect = weapon_name.get_rect(center=(weapon_rect.centerx, weapon_rect.bottom + 15))
            surface.blit(weapon_name, weapon_name_rect)
        else:
            # Empty slot indicator
            empty_text = self.small_font.render("No Weapon", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=weapon_rect.center)
            surface.blit(empty_text, empty_rect)
        
        # Current armor display
        armor_rect = pygame.Rect(equipment_x + 110, slot_y, slot_size, slot_size)
        pygame.draw.rect(surface, self.colors['slot_bg'], armor_rect)
        pygame.draw.rect(surface, self.colors['slot_border'], armor_rect, 2)
        
        # Armor sprite and name
        if self.player.equipped_armor:
            armor_sprite = self.player.equipped_armor.sprite
            if armor_sprite:
                # Scale sprite to fit slot
                scaled_sprite = pygame.transform.scale(armor_sprite, (slot_size - 10, slot_size - 10))
                sprite_rect = scaled_sprite.get_rect(center=armor_rect.center)
                surface.blit(scaled_sprite, sprite_rect)
            
            # Armor name below slot
            armor_name = self.small_font.render(self.player.equipped_armor.name, True, self.colors['text_color'])
            armor_name_rect = armor_name.get_rect(center=(armor_rect.centerx, armor_rect.bottom + 15))
            surface.blit(armor_name, armor_name_rect)
        else:
            # Empty slot indicator
            empty_text = self.small_font.render("No Armor", True, (150, 150, 150))
            empty_rect = empty_text.get_rect(center=armor_rect.center)
            surface.blit(empty_text, empty_rect)
    
    def render_xp_bar(self, surface, screen_width):
        """Render experience bar"""
        # XP bar at the top of the UI panel
        xp_bar_width = screen_width - 40
        xp_bar_height = 20
        xp_bar_x = 20
        xp_bar_y = 5
        
        # Background
        xp_bg_rect = pygame.Rect(xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height)
        pygame.draw.rect(surface, (60, 60, 60), xp_bg_rect)
        pygame.draw.rect(surface, self.colors['panel_border'], xp_bg_rect, 2)
        
        # XP fill
        if self.player.experience_to_next > 0:
            xp_percentage = self.player.experience / self.player.experience_to_next
            xp_fill_width = int(xp_bar_width * xp_percentage)
            xp_fill_rect = pygame.Rect(xp_bar_x, xp_bar_y, xp_fill_width, xp_bar_height)
            pygame.draw.rect(surface, self.colors['xp_color'], xp_fill_rect)
        
        # XP text
        xp_text = f"XP: {self.player.experience}/{self.player.experience_to_next}"
        xp_surface = self.small_font.render(xp_text, True, self.colors['text_color'])
        xp_rect = xp_surface.get_rect(center=(xp_bar_x + xp_bar_width // 2, xp_bar_y + xp_bar_height // 2))
        surface.blit(xp_surface, xp_rect)
    
    def render_movement_mode_indicator(self, surface, screen_width):
        """Render movement mode indicator in the top-right corner"""
        if hasattr(self.player, 'movement_system') and self.player.movement_system:
            mode = self.player.movement_system.movement_mode
            mode_text = "WASD" if mode == "wasd" else "Mouse"
            
            # Create indicator background
            indicator_width = 80
            indicator_height = 25
            indicator_x = screen_width - indicator_width - 10
            indicator_y = 30
            
            # Background with border
            indicator_rect = pygame.Rect(indicator_x, indicator_y, indicator_width, indicator_height)
            pygame.draw.rect(surface, (50, 50, 50), indicator_rect)
            pygame.draw.rect(surface, self.colors['panel_border'], indicator_rect, 2)
            
            # Mode text
            mode_color = (100, 255, 100) if mode == "wasd" else (100, 150, 255)
            mode_surface = self.small_font.render(mode_text, True, mode_color)
            mode_rect = mode_surface.get_rect(center=indicator_rect.center)
            surface.blit(mode_surface, mode_rect)
            
            # F5 hint text below
            hint_text = "F5"
            hint_surface = pygame.font.Font(None, 16).render(hint_text, True, (150, 150, 150))
            hint_rect = hint_surface.get_rect(center=(indicator_rect.centerx, indicator_rect.bottom + 10))
            surface.blit(hint_surface, hint_rect)
