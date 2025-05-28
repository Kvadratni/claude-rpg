"""
Inventory system for the RPG
"""

import pygame

class Inventory:
    """Player inventory system"""
    
    def __init__(self, max_size=20):
        self.items = []
        self.max_size = max_size
        self.show = False
        self.selected_slot = 0  # Changed from selected_index
    
    def add_item(self, item):
        """Add an item to the inventory"""
        if len(self.items) < self.max_size:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item):
        """Remove an item from the inventory"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_item(self, index):
        """Get item at index"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def render(self, screen, equipped_weapon=None, equipped_armor=None):
        """Render the inventory with equipment slots"""
        if not self.show:
            return
        
        # Create inventory window
        inv_width = 500
        inv_height = 400
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        inv_x = (screen_width - inv_width) // 2
        inv_y = (screen_height - inv_height) // 2
        
        # Main inventory panel
        inv_surface = pygame.Surface((inv_width, inv_height))
        inv_surface.fill((50, 50, 50))
        pygame.draw.rect(inv_surface, (100, 100, 100), (0, 0, inv_width, inv_height), 3)
        
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        # Title
        title = font.render("Inventory", True, (255, 255, 255))
        inv_surface.blit(title, (10, 10))
        
        # Close button (X)
        close_button_size = 25
        close_button_x = inv_width - close_button_size - 10
        close_button_y = 10
        close_button_rect = pygame.Rect(close_button_x, close_button_y, close_button_size, close_button_size)
        
        pygame.draw.rect(inv_surface, (200, 50, 50), close_button_rect)
        pygame.draw.rect(inv_surface, (255, 255, 255), close_button_rect, 2)
        
        close_text = small_font.render("X", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        inv_surface.blit(close_text, close_text_rect)
        
        # Store close button rect for click detection (adjusted for screen position)
        self.close_button_rect = pygame.Rect(inv_x + close_button_x, inv_y + close_button_y, close_button_size, close_button_size)
        
        # Equipment slots on the left
        eq_start_x = 20
        eq_start_y = 50
        
        # Weapon slot
        weapon_slot = pygame.Rect(eq_start_x, eq_start_y, 60, 60)
        pygame.draw.rect(inv_surface, (80, 80, 80), weapon_slot)
        pygame.draw.rect(inv_surface, (120, 120, 120), weapon_slot, 2)
        
        weapon_label = small_font.render("Weapon", True, (200, 200, 200))
        inv_surface.blit(weapon_label, (eq_start_x, eq_start_y - 20))
        
        # Draw equipped weapon sprite
        if equipped_weapon and hasattr(equipped_weapon, 'sprite') and equipped_weapon.sprite:
            scaled_weapon = pygame.transform.scale(equipped_weapon.sprite, (56, 56))
            weapon_rect = scaled_weapon.get_rect()
            weapon_rect.center = weapon_slot.center
            inv_surface.blit(scaled_weapon, weapon_rect)
        
        # Armor slot
        armor_slot = pygame.Rect(eq_start_x, eq_start_y + 80, 60, 60)
        pygame.draw.rect(inv_surface, (80, 80, 80), armor_slot)
        pygame.draw.rect(inv_surface, (120, 120, 120), armor_slot, 2)
        
        armor_label = small_font.render("Armor", True, (200, 200, 200))
        inv_surface.blit(armor_label, (eq_start_x, eq_start_y + 60))
        
        # Draw equipped armor sprite
        if equipped_armor and hasattr(equipped_armor, 'sprite') and equipped_armor.sprite:
            scaled_armor = pygame.transform.scale(equipped_armor.sprite, (56, 56))
            armor_rect = scaled_armor.get_rect()
            armor_rect.center = armor_slot.center
            inv_surface.blit(scaled_armor, armor_rect)
        
        # Inventory grid on the right
        grid_start_x = 120
        grid_start_y = 50
        slot_size = 40
        slots_per_row = 8
        
        # Draw inventory slots
        for i in range(self.max_size):
            row = i // slots_per_row
            col = i % slots_per_row
            
            slot_x = grid_start_x + col * (slot_size + 5)
            slot_y = grid_start_y + row * (slot_size + 5)
            
            slot_rect = pygame.Rect(slot_x, slot_y, slot_size, slot_size)
            
            # Highlight selected slot
            if i == self.selected_slot:
                pygame.draw.rect(inv_surface, (100, 100, 150), slot_rect)
            else:
                pygame.draw.rect(inv_surface, (70, 70, 70), slot_rect)
            
            pygame.draw.rect(inv_surface, (120, 120, 120), slot_rect, 2)
            
            # Draw item if present
            if i < len(self.items):
                item = self.items[i]
                # Use the actual item sprite if available
                if hasattr(item, 'sprite') and item.sprite:
                    # Scale down the sprite to fit in the inventory slot
                    scaled_sprite = pygame.transform.scale(item.sprite, (slot_size - 4, slot_size - 4))
                    sprite_rect = scaled_sprite.get_rect()
                    sprite_rect.center = (slot_x + slot_size // 2, slot_y + slot_size // 2 - 5)
                    inv_surface.blit(scaled_sprite, sprite_rect)
                else:
                    # Fallback to simple colored shapes
                    if item.item_type == "weapon":
                        pygame.draw.rect(inv_surface, (192, 192, 192), (slot_x + 10, slot_y + 5, 20, 30))
                    elif item.item_type == "armor":
                        pygame.draw.ellipse(inv_surface, (139, 69, 19), (slot_x + 10, slot_y + 10, 20, 20))
                    elif item.item_type == "consumable":
                        if "Health" in item.name:
                            color = (255, 0, 0)
                        else:
                            color = (0, 0, 255)
                        pygame.draw.ellipse(inv_surface, color, (slot_x + 10, slot_y + 10, 20, 20))
                
                # Item name (shortened to fit)
                item_text = small_font.render(item.name[:8], True, (255, 255, 255))
                inv_surface.blit(item_text, (slot_x + 2, slot_y + slot_size - 15))
        
        # Instructions
        instructions = [
            "Left Click: Select item",
            "Right Click: Use/Equip item", 
            "ESC/I: Close inventory"
        ]
        
        for i, instruction in enumerate(instructions):
            text = small_font.render(instruction, True, (200, 200, 200))
            inv_surface.blit(text, (10, inv_height - 80 + i * 20))
        
        # Selected item info
        if 0 <= self.selected_slot < len(self.items):
            item = self.items[self.selected_slot]
            info_y = inv_height - 120
            
            name_text = font.render(f"{item.name} ({item.item_type})", True, (255, 255, 255))
            inv_surface.blit(name_text, (grid_start_x, info_y))
            
            if item.effect:
                effect_text = small_font.render(f"Effect: {item.effect}", True, (200, 200, 200))
                inv_surface.blit(effect_text, (grid_start_x, info_y + 25))
        
        # Blit inventory to screen
        screen.blit(inv_surface, (inv_x, inv_y))
        
        # Store rects for click detection
        self.inventory_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)
        self.grid_start_pos = (inv_x + grid_start_x, inv_y + grid_start_y)
        self.slot_size = slot_size
        self.slots_per_row = slots_per_row
    
    def handle_input(self, event, audio_manager=None):
        """Handle inventory input with mouse support"""
        if not self.show:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check close button first
            if hasattr(self, 'close_button_rect') and self.close_button_rect.collidepoint(event.pos):
                if audio_manager:
                    audio_manager.play_ui_sound("inventory_close")
                self.show = False
                return None
            
            if hasattr(self, 'inventory_rect') and self.inventory_rect.collidepoint(event.pos):
                # Check if clicking on inventory grid
                if hasattr(self, 'grid_start_pos'):
                    grid_x, grid_y = self.grid_start_pos
                    click_x, click_y = event.pos
                    
                    # Calculate which slot was clicked
                    rel_x = click_x - grid_x
                    rel_y = click_y - grid_y
                    
                    if rel_x >= 0 and rel_y >= 0:
                        slot_col = rel_x // (self.slot_size + 5)
                        slot_row = rel_y // (self.slot_size + 5)
                        slot_index = slot_row * self.slots_per_row + slot_col
                        
                        if 0 <= slot_index < self.max_size:
                            if event.button == 1:  # Left click - select
                                self.selected_slot = slot_index
                                if audio_manager:
                                    audio_manager.play_ui_sound("click")
                            elif event.button == 3:  # Right click - use/equip
                                if slot_index < len(self.items):
                                    if audio_manager:
                                        audio_manager.play_ui_sound("click")
                                    return ("use", self.items[slot_index])
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_slot = max(0, self.selected_slot - self.slots_per_row)
                if audio_manager:
                    audio_manager.play_ui_sound("select")
            elif event.key == pygame.K_DOWN:
                self.selected_slot = min(self.max_size - 1, self.selected_slot + self.slots_per_row)
                if audio_manager:
                    audio_manager.play_ui_sound("select")
            elif event.key == pygame.K_LEFT:
                self.selected_slot = max(0, self.selected_slot - 1)
                if audio_manager:
                    audio_manager.play_ui_sound("select")
            elif event.key == pygame.K_RIGHT:
                self.selected_slot = min(self.max_size - 1, self.selected_slot + 1)
                if audio_manager:
                    audio_manager.play_ui_sound("select")
            elif event.key == pygame.K_e or event.key == pygame.K_RETURN:
                # Use/equip selected item
                if self.selected_slot < len(self.items):
                    if audio_manager:
                        audio_manager.play_ui_sound("click")
                    return ("use", self.items[self.selected_slot])
            elif event.key == pygame.K_d:
                # Drop selected item
                if self.selected_slot < len(self.items):
                    if audio_manager:
                        audio_manager.play_ui_sound("item_drop")
                    return ("drop", self.items[self.selected_slot])
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                if audio_manager:
                    audio_manager.play_ui_sound("inventory_close")
                self.show = False
        
        return None