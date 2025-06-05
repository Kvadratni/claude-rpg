"""
UI rendering functionality (bottom panel, XP bar, etc.)
"""

import pygame
import math


class UIRendererMixin:
    """Mixin class for UI rendering functionality"""
    
    def render_ui(self, screen):
        """Render enhanced game UI"""
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create UI panel at bottom
        ui_height = 150
        ui_panel = pygame.Surface((screen_width, ui_height))
        ui_panel.fill((40, 40, 40))  # Dark gray background
        
        # Draw border
        pygame.draw.rect(ui_panel, (100, 100, 100), (0, 0, screen_width, ui_height), 2)
        
        # Left side - Player stats with circular health/stamina bars
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        # Render circular health and stamina bars
        self.render_circular_bars(ui_panel, 20, 30)
        
        # Player level and gold (moved to top right of circles area)
        stats_x = 160
        level_text = f"Level {self.player.level}"
        gold_text = f"Gold: {self.player.gold}"
        
        level_surface = small_font.render(level_text, True, (255, 215, 0))  # Gold color for level
        gold_surface = small_font.render(gold_text, True, (255, 215, 0))   # Gold color for gold
        ui_panel.blit(level_surface, (stats_x, 15))
        ui_panel.blit(gold_surface, (stats_x, 35))
        
        # Center-left - Equipment display
        equipment_x = 280
        slot_size = 80
        slot_y = 30
        
        # Current weapon display
        weapon_rect = pygame.Rect(equipment_x, slot_y, slot_size, slot_size)
        pygame.draw.rect(ui_panel, (60, 60, 60), weapon_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), weapon_rect, 2)
        
        # Weapon label above slot
        weapon_text = font.render("Weapon", True, (255, 255, 255))
        ui_panel.blit(weapon_text, (equipment_x, slot_y - 25))
        
        if self.player.equipped_weapon:
            # Draw actual weapon sprite if available
            if hasattr(self.player.equipped_weapon, 'sprite') and self.player.equipped_weapon.sprite:
                scaled_weapon = pygame.transform.scale(self.player.equipped_weapon.sprite, (slot_size - 8, slot_size - 8))
                weapon_sprite_rect = scaled_weapon.get_rect()
                weapon_sprite_rect.center = weapon_rect.center
                ui_panel.blit(scaled_weapon, weapon_sprite_rect)
            else:
                # Fallback to simple shape
                pygame.draw.rect(ui_panel, (192, 192, 192), (equipment_x + 20, slot_y + 15, slot_size - 40, slot_size - 20))
            
            # Weapon name below slot
            weapon_name = small_font.render(self.player.equipped_weapon.name[:12], True, (255, 255, 255))
            ui_panel.blit(weapon_name, (equipment_x, slot_y + slot_size + 5))
        else:
            no_weapon = small_font.render("No Weapon", True, (150, 150, 150))
            no_weapon_rect = no_weapon.get_rect(center=weapon_rect.center)
            ui_panel.blit(no_weapon, no_weapon_rect)
        
        # Current armor display
        armor_x = equipment_x + slot_size + 30
        armor_rect = pygame.Rect(armor_x, slot_y, slot_size, slot_size)
        pygame.draw.rect(ui_panel, (60, 60, 60), armor_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), armor_rect, 2)
        
        # Armor label above slot
        armor_text = font.render("Armor", True, (255, 255, 255))
        ui_panel.blit(armor_text, (armor_x, slot_y - 25))
        
        if self.player.equipped_armor:
            # Draw actual armor sprite if available
            if hasattr(self.player.equipped_armor, 'sprite') and self.player.equipped_armor.sprite:
                scaled_armor = pygame.transform.scale(self.player.equipped_armor.sprite, (slot_size - 8, slot_size - 8))
                armor_sprite_rect = scaled_armor.get_rect()
                armor_sprite_rect.center = armor_rect.center
                ui_panel.blit(scaled_armor, armor_sprite_rect)
            else:
                # Fallback to simple shape
                pygame.draw.ellipse(ui_panel, (139, 69, 19), (armor_x + 20, slot_y + 15, slot_size - 40, slot_size - 20))
            
            # Armor name below slot
            armor_name = small_font.render(self.player.equipped_armor.name[:12], True, (255, 255, 255))
            ui_panel.blit(armor_name, (armor_x, slot_y + slot_size + 5))
        else:
            no_armor = small_font.render("No Armor", True, (150, 150, 150))
            no_armor_rect = no_armor.get_rect(center=armor_rect.center)
            ui_panel.blit(no_armor, no_armor_rect)
        
        # Inventory button
        inv_button_x = armor_x + slot_size + 20
        inv_button = pygame.Rect(inv_button_x, 20, 100, 40)
        pygame.draw.rect(ui_panel, (80, 80, 80), inv_button)
        pygame.draw.rect(ui_panel, (120, 120, 120), inv_button, 2)
        
        inv_text = font.render("Inventory", True, (255, 255, 255))
        text_rect = inv_text.get_rect(center=inv_button.center)
        ui_panel.blit(inv_text, text_rect)
        
        # Store button rect for click detection (adjust for screen position)
        self.inventory_button_rect = pygame.Rect(inv_button_x, screen_height - ui_height + 20, 100, 40)
        
        # Right side - Game log integrated into HUD
        log_x = inv_button_x + 120  # Start after inventory button
        log_width = screen_width - log_x - 20  # Use remaining width with margin
        log_height = ui_height - 20  # Use most of the UI height
        
        # Draw game log background
        log_rect = pygame.Rect(log_x, 10, log_width, log_height)
        pygame.draw.rect(ui_panel, (50, 50, 50), log_rect)
        pygame.draw.rect(ui_panel, (100, 100, 100), log_rect, 2)
        
        # Render game log content within the HUD
        self.render_game_log_in_hud(ui_panel, log_x, 10, log_width, log_height)
        
        # Blit the entire UI panel to screen
        screen.blit(ui_panel, (0, screen_height - ui_height))
    
    def render_circular_bars(self, surface, x, y):
        """Render circular health and stamina bars"""
        # Circle parameters
        radius = 35
        thickness = 8
        
        # Health circle (red)
        health_center = (x + radius, y + radius)
        health_percentage = self.player.health / self.player.max_health
        
        # Draw background circle for health
        pygame.draw.circle(surface, (60, 20, 20), health_center, radius, thickness)
        
        # Draw health arc
        if health_percentage > 0:
            # Calculate arc angle (0 to 2*pi)
            end_angle = health_percentage * 2 * math.pi - math.pi/2  # Start from top
            start_angle = -math.pi/2
            
            # Draw the health arc as a thick line
            for i in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
                angle_rad = i * math.pi / 180
                start_x = health_center[0] + (radius - thickness) * math.cos(angle_rad)
                start_y = health_center[1] + (radius - thickness) * math.sin(angle_rad)
                end_x = health_center[0] + radius * math.cos(angle_rad)
                end_y = health_center[1] + radius * math.sin(angle_rad)
                pygame.draw.line(surface, (220, 50, 50), (start_x, start_y), (end_x, end_y), 2)
        
        # Health text - show current/max format
        health_text = f"{self.player.health}/{self.player.max_health}"
        font = pygame.font.Font(None, 18)  # Smaller font to fit the text
        text_surface = font.render(health_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=health_center)
        surface.blit(text_surface, text_rect)
        
        # Health label
        health_label = font.render("Health", True, (255, 255, 255))
        surface.blit(health_label, (x, y + radius * 2 + 10))
        
        # Stamina circle (blue) - using stamina instead of mana
        stamina_center = (x + radius * 3, y + radius)
        stamina_percentage = self.player.stamina / self.player.max_stamina
        
        # Draw background circle for stamina
        pygame.draw.circle(surface, (20, 20, 60), stamina_center, radius, thickness)
        
        # Draw stamina arc
        if stamina_percentage > 0:
            # Calculate arc angle (0 to 2*pi)
            end_angle = stamina_percentage * 2 * math.pi - math.pi/2  # Start from top
            start_angle = -math.pi/2
            
            # Draw the stamina arc as a thick line
            for i in range(int(start_angle * 180 / math.pi), int(end_angle * 180 / math.pi)):
                angle_rad = i * math.pi / 180
                start_x = stamina_center[0] + (radius - thickness) * math.cos(angle_rad)
                start_y = stamina_center[1] + (radius - thickness) * math.sin(angle_rad)
                end_x = stamina_center[0] + radius * math.cos(angle_rad)
                end_y = stamina_center[1] + radius * math.sin(angle_rad)
                pygame.draw.line(surface, (50, 150, 220), (start_x, start_y), (end_x, end_y), 2)
        
        # Stamina text - show current/max format
        stamina_text = f"{self.player.stamina}/{self.player.max_stamina}"
        text_surface = font.render(stamina_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=stamina_center)
        surface.blit(text_surface, text_rect)
        
        # Stamina label
        stamina_label = font.render("Stamina", True, (255, 255, 255))
        surface.blit(stamina_label, (x + radius * 2, y + radius * 2 + 10))
    
    def render_xp_bar(self, screen):
        """Render experience bar at the top of the screen"""
        screen_width = screen.get_width()
        
        # XP bar dimensions
        bar_width = screen_width - 40  # Leave 20px margin on each side
        bar_height = 20
        bar_x = 20
        bar_y = 10
        
        # Calculate XP percentage
        xp_percentage = self.player.experience / self.player.experience_to_next
        
        # Draw background
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw XP fill
        if xp_percentage > 0:
            fill_width = int(bar_width * xp_percentage)
            # Gradient effect - brighter in the middle
            for i in range(fill_width):
                intensity = 1.0 - abs(i - fill_width/2) / (fill_width/2) if fill_width > 0 else 1.0
                color = (
                    int(255 * intensity * 0.8),  # Gold color
                    int(215 * intensity * 0.8),
                    int(0 * intensity * 0.8)
                )
                pygame.draw.line(screen, color, (bar_x + i, bar_y + 2), (bar_x + i, bar_y + bar_height - 2))
        
        # Draw XP text
        font = pygame.font.Font(None, 18)
        xp_text = f"XP: {self.player.experience}/{self.player.experience_to_next}"
        text_surface = font.render(xp_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(bar_x + bar_width//2, bar_y + bar_height//2))
        screen.blit(text_surface, text_rect)
    
    def render_game_log_in_hud(self, ui_panel, log_x, log_y, log_width, log_height):
        """Render game log content within the HUD panel"""
        # Get the game log
        game_log = None
        if hasattr(self.player, 'game_log') and self.player.game_log:
            game_log = self.player.game_log
        elif hasattr(self, 'game') and hasattr(self.game, 'game_log'):
            game_log = self.game.game_log
        
        if not game_log:
            return
        
        # Draw title
        font = pygame.font.Font(None, 20)
        small_font = pygame.font.Font(None, 16)
        
        title_text = "Game Log"
        if game_log.scroll_offset > 0:
            title_text += f" (↑{game_log.scroll_offset})"
        title_surface = small_font.render(title_text, True, (200, 200, 200))
        ui_panel.blit(title_surface, (log_x + 5, log_y + 2))
        
        # Calculate visible messages
        visible_messages = min(6, (log_height - 25) // 20)  # Adjust based on available height
        message_height = 20
        
        # Draw scroll arrows if needed
        scroll_up_rect = None
        scroll_down_rect = None
        
        if len(game_log.messages) > visible_messages:
            arrow_size = 14
            arrow_x = log_x + log_width - arrow_size - 5
            up_arrow_y = log_y + 2
            down_arrow_y = log_y + log_height - arrow_size - 2
            
            # Store arrow rects for click detection (in screen coordinates)
            screen_height = pygame.display.get_surface().get_height()
            ui_height = 150
            ui_y_offset = screen_height - ui_height
            
            game_log.scroll_up_rect = pygame.Rect(arrow_x, ui_y_offset + up_arrow_y, arrow_size, arrow_size)
            game_log.scroll_down_rect = pygame.Rect(arrow_x, ui_y_offset + down_arrow_y, arrow_size, arrow_size)
            
            # Draw up arrow
            up_color = (255, 255, 255) if game_log.scroll_offset < len(game_log.messages) - visible_messages else (100, 100, 100)
            up_points = [
                (arrow_x + arrow_size // 2, up_arrow_y + 2),
                (arrow_x + 2, up_arrow_y + arrow_size - 2),
                (arrow_x + arrow_size - 2, up_arrow_y + arrow_size - 2)
            ]
            pygame.draw.polygon(ui_panel, up_color, up_points)
            
            # Draw down arrow
            down_color = (255, 255, 255) if game_log.scroll_offset > 0 else (100, 100, 100)
            down_points = [
                (arrow_x + 2, down_arrow_y + 2),
                (arrow_x + arrow_size - 2, down_arrow_y + 2),
                (arrow_x + arrow_size // 2, down_arrow_y + arrow_size - 2)
            ]
            pygame.draw.polygon(ui_panel, down_color, down_points)
        else:
            game_log.scroll_up_rect = None
            game_log.scroll_down_rect = None
        
        # Calculate which messages to show
        if len(game_log.messages) <= visible_messages:
            messages_to_show = game_log.messages
        else:
            start_index = len(game_log.messages) - visible_messages - game_log.scroll_offset
            end_index = len(game_log.messages) - game_log.scroll_offset
            messages_to_show = game_log.messages[start_index:end_index]
        
        # Draw messages
        for i, message in enumerate(messages_to_show):
            y_pos = log_y + 18 + (i * message_height)
            color = game_log.colors.get(message["type"], game_log.colors["default"])
            
            # Apply alpha for fading
            if message["alpha"] < 255 and game_log.scroll_offset == 0:
                color = (*color, message["alpha"])
                text_surface = font.render(message["text"], True, color)
                text_surface.set_alpha(message["alpha"])
            else:
                text_surface = font.render(message["text"], True, color)
            
            # Truncate long messages
            max_width = log_width - 30 if len(game_log.messages) > visible_messages else log_width - 10
            if text_surface.get_width() > max_width:
                truncated_text = message["text"]
                while font.size(truncated_text + "...")[0] > max_width and len(truncated_text) > 0:
                    truncated_text = truncated_text[:-1]
                text_surface = font.render(truncated_text + "...", True, color)
            
            ui_panel.blit(text_surface, (log_x + 5, y_pos))