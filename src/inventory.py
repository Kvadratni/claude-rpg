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
        self.selected_index = 0
    
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
    
    def render(self, screen):
        """Render inventory UI"""
        if not self.show:
            return
        
        # Create semi-transparent background
        screen_width, screen_height = screen.get_width(), screen.get_height()
        inventory_width, inventory_height = 400, 300
        
        inventory_surface = pygame.Surface((inventory_width, inventory_height), pygame.SRCALPHA)
        inventory_surface.fill((0, 0, 0, 200))
        
        # Draw inventory title
        font = pygame.font.Font(None, 28)
        title_text = font.render("Inventory", True, (255, 255, 255))
        inventory_surface.blit(title_text, (10, 10))
        
        # Draw items
        item_font = pygame.font.Font(None, 20)
        for i, item in enumerate(self.items):
            # Highlight selected item
            if i == self.selected_index:
                pygame.draw.rect(inventory_surface, (100, 100, 255, 100), 
                               (5, 45 + i * 25, inventory_width - 10, 25))
            
            item_text = item_font.render(f"{i+1}. {item.name}", True, (255, 255, 255))
            inventory_surface.blit(item_text, (20, 50 + i * 25))
            
            # Draw item type and effects
            if item.item_type == "weapon":
                effect_text = item_font.render(f"Weapon: +{item.effect.get('damage', 0)} DMG", True, (200, 200, 255))
            elif item.item_type == "armor":
                effect_text = item_font.render(f"Armor: +{item.effect.get('defense', 0)} DEF", True, (200, 255, 200))
            elif item.item_type == "consumable":
                effect = ""
                if "health" in item.effect:
                    effect += f"+{item.effect['health']} HP "
                if "mana" in item.effect:
                    effect += f"+{item.effect['mana']} MP"
                effect_text = item_font.render(f"Consumable: {effect}", True, (255, 200, 255))
            else:
                effect_text = item_font.render(f"Misc", True, (200, 200, 200))
            
            inventory_surface.blit(effect_text, (180, 50 + i * 25))
        
        # Draw instructions
        if self.items:
            instructions = [
                "E: Equip/Use selected item",
                "D: Drop selected item",
                "↑/↓: Navigate items"
            ]
        else:
            instructions = ["Inventory is empty"]
        
        for i, instruction in enumerate(instructions):
            instr_text = item_font.render(instruction, True, (200, 200, 200))
            inventory_surface.blit(instr_text, (20, inventory_height - 80 + i * 20))
        
        # Draw inventory on screen
        screen.blit(inventory_surface, (screen_width//2 - inventory_width//2, 
                                      screen_height//2 - inventory_height//2))
    
    def handle_input(self, event):
        """Handle inventory input"""
        if not self.show:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
            elif event.key == pygame.K_e:
                # Use/equip selected item
                selected_item = self.get_item(self.selected_index)
                if selected_item:
                    return ("use", selected_item)
            elif event.key == pygame.K_d:
                # Drop selected item
                selected_item = self.get_item(self.selected_index)
                if selected_item:
                    return ("drop", selected_item)
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.show = False
        
        return None