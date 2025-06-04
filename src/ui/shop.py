"""
Shop system for the RPG
"""

import pygame
import random
from ..entities import Item

class Shop:
    """Shop system for buying and selling items"""
    
    def __init__(self, shop_name="General Store", asset_loader=None):
        self.name = shop_name
        self.asset_loader = asset_loader
        self.items = []
        self.show = False
        self.selected_item = None
        self.selected_side = "shop"  # "shop" or "player"
        
        # UI properties - much wider for side-by-side layout
        self.width = 1000  # Increased width for side-by-side
        self.height = 600  # Increased height for better display
        self.slot_size = 64
        self.slots_per_row = 6
        self.padding = 10
        
        # Generate shop inventory
        self.generate_shop_inventory()
    
    def generate_shop_inventory(self):
        """Generate items for the shop"""
        # Health potions (always in stock)
        for _ in range(5):
            item = Item(0, 0, "Health Potion", item_type="consumable", 
                       effect={"health": 50}, value=25, asset_loader=self.asset_loader)
            self.items.append(item)
        
        # Stamina potions
        for _ in range(3):
            item = Item(0, 0, "Stamina Potion", item_type="consumable", 
                       effect={"stamina": 30}, value=20, asset_loader=self.asset_loader)
            self.items.append(item)
        
        # New consumables (limited stock)
        new_consumables = [
            ("Mana Potion", {"mana": 40}, 30),
            ("Antidote", {"cure_poison": True}, 35),
            ("Strength Potion", {"damage_boost": 10, "duration": 60}, 50)
        ]
        
        for name, effect, price in new_consumables:
            if random.random() < 0.7:  # 70% chance each consumable is in stock
                item = Item(0, 0, name, item_type="consumable", 
                           effect=effect, value=price, asset_loader=self.asset_loader)
                self.items.append(item)
        
        # Weapons (random selection from expanded list)
        weapon_data = [
            ("Iron Sword", {"damage": 15}, 100),
            ("Steel Axe", {"damage": 20}, 150),
            ("Bronze Mace", {"damage": 12}, 80),
            ("Silver Dagger", {"damage": 18}, 120),
            ("War Hammer", {"damage": 25}, 200),
            ("Magic Bow", {"damage": 22}, 180),
            ("Crystal Staff", {"damage": 16, "spell_power": 10}, 220),
            ("Throwing Knife", {"damage": 14}, 90),
            ("Crossbow", {"damage": 19}, 160)
        ]
        
        for _ in range(3):
            weapon_name, effect, base_price = random.choice(weapon_data)
            # Add some price variation
            price = base_price + random.randint(-20, 20)
            item = Item(0, 0, weapon_name, item_type="weapon", 
                       effect=effect, value=price, asset_loader=self.asset_loader)
            self.items.append(item)
        
        # Armor (random selection from expanded list)
        armor_data = [
            ("Leather Armor", {"defense": 8}, 80),
            ("Chain Mail", {"defense": 12}, 120),
            ("Plate Armor", {"defense": 18}, 200),
            ("Studded Leather", {"defense": 10}, 100),
            ("Scale Mail", {"defense": 15}, 160),
            ("Dragon Scale Armor", {"defense": 20, "fire_resistance": 10}, 300),
            ("Mage Robes", {"defense": 6, "spell_power": 15}, 180),
            ("Royal Armor", {"defense": 22, "magic_resistance": 8}, 350)
        ]
        
        for _ in range(2):
            armor_name, effect, base_price = random.choice(armor_data)
            # Add some price variation
            price = base_price + random.randint(-15, 15)
            item = Item(0, 0, armor_name, item_type="armor", 
                       effect=effect, value=price, asset_loader=self.asset_loader)
            self.items.append(item)
        
        # Miscellaneous items (rare, expensive)
        misc_items = [
            ("Gold Ring", {"magic_resistance": 5}, 250),
            ("Magic Scroll", {"spell_power": 15}, 200),
            ("Crystal Gem", {"value": 100}, 150)  # Can be sold for profit
        ]
        
        for name, effect, price in misc_items:
            if random.random() < 0.3:  # 30% chance each misc item is in stock
                item = Item(0, 0, name, item_type="misc", 
                           effect=effect, value=price, asset_loader=self.asset_loader)
                self.items.append(item)
    
    def open_shop(self):
        """Open the shop interface"""
        self.show = True
        self.selected_item = None
        self.selected_side = "shop"
    
    def close_shop(self):
        """Close the shop interface"""
        self.show = False
        self.selected_item = None
        self.selected_side = "shop"
    
    def handle_click(self, pos, player):
        """Handle mouse clicks in the shop interface"""
        if not self.show:
            return False
        
        # Get shop window position
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        shop_x = (screen_width - self.width) // 2
        shop_y = (screen_height - self.height) // 2
        
        # Convert to relative position
        rel_x = pos[0] - shop_x
        rel_y = pos[1] - shop_y
        
        # Check if click is outside shop window
        if rel_x < 0 or rel_x > self.width or rel_y < 0 or rel_y > self.height:
            return False
        
        # Check close button
        close_button_rect = pygame.Rect(self.width - 30, 10, 20, 20)
        if close_button_rect.collidepoint(rel_x, rel_y):
            self.close_shop()
            return True
        
        # Check buy button
        buy_button_rect = pygame.Rect(self.width // 2 - 120, self.height - 50, 100, 35)
        if buy_button_rect.collidepoint(rel_x, rel_y) and self.selected_item and self.selected_side == "shop":
            return self.buy_item(self.selected_item, player)
        
        # Check sell button
        sell_button_rect = pygame.Rect(self.width // 2 + 20, self.height - 50, 100, 35)
        if sell_button_rect.collidepoint(rel_x, rel_y) and self.selected_item and self.selected_side == "player":
            return self.sell_item(self.selected_item, player)
        
        # Calculate panel dimensions
        panel_width = (self.width - 30) // 2  # Split width in half with margin
        items_start_y = 80
        
        # Check shop items (left side)
        if rel_x < panel_width:
            for i, item in enumerate(self.items):
                row = i // self.slots_per_row
                col = i % self.slots_per_row
                
                slot_x = self.padding + col * (self.slot_size + self.padding)
                slot_y = items_start_y + row * (self.slot_size + self.padding)
                
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                if slot_rect.collidepoint(rel_x, rel_y):
                    self.selected_item = item
                    self.selected_side = "shop"
                    return True
        
        # Check player items (right side)
        else:
            player_items = getattr(self, '_player_items', [])
            for i, item in enumerate(player_items):
                row = i // self.slots_per_row
                col = i % self.slots_per_row
                
                slot_x = panel_width + 15 + self.padding + col * (self.slot_size + self.padding)
                slot_y = items_start_y + row * (self.slot_size + self.padding)
                
                slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
                if slot_rect.collidepoint(rel_x, rel_y):
                    self.selected_item = item
                    self.selected_side = "player"
                    return True
        
        return True  # Consumed the click
    
    def buy_item(self, item, player):
        """Attempt to buy an item"""
        if not item or item not in self.items:
            return False
        
        # Check if player has enough gold
        if player.gold < item.value:
            if player.game_log:
                player.game_log.add_message("Not enough gold!", "system")
            return False
        
        # Check if player has inventory space
        if not player.add_item(item):
            if player.game_log:
                player.game_log.add_message("Inventory is full!", "system")
            return False
        
        # Complete the transaction
        player.gold -= item.value
        self.items.remove(item)
        self.selected_item = None
        
        # Play purchase sound
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        if audio:
            audio.play_ui_sound("coin")
        
        if player.game_log:
            player.game_log.add_message(f"Purchased {item.name} for {item.value} gold!", "item")
        
        # Update quest progress for purchases
        if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
            player.game.quest_manager.update_quest_progress("purchase", item.name)
            player.game.quest_manager.update_quest_progress("purchase", "any")
        
        return True
    
    def sell_item(self, item, player):
        """Attempt to sell an item"""
        if not item or item not in player.inventory.items:
            return False
        
        # Check if item can be sold
        if not self.can_sell_item(item):
            if player.game_log:
                player.game_log.add_message("This item cannot be sold here!", "system")
            return False
        
        # Calculate sell price (typically 50% of value)
        sell_price = max(1, item.value // 2)
        
        # Remove item from player inventory
        if player.remove_item(item):
            # Give player gold
            player.gold += sell_price
            self.selected_item = None
            
            # Play sell sound
            audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
            if audio:
                audio.play_ui_sound("coin")
            
            if player.game_log:
                player.game_log.add_message(f"Sold {item.name} for {sell_price} gold!", "item")
            
            return True
        
        return False
    
    def can_sell_item(self, item):
        """Check if an item can be sold"""
        # Don't allow selling equipped items
        if hasattr(item, 'equipped') and item.equipped:
            return False
        
        # Allow selling misc items, consumables, and unequipped weapons/armor
        sellable_types = ["misc", "consumable", "weapon", "armor"]
        return item.item_type in sellable_types
    
    def render(self, screen):
        """Render the shop interface with side-by-side layout"""
        if not self.show:
            return
        
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Calculate shop window position (centered)
        shop_x = (screen_width - self.width) // 2
        shop_y = (screen_height - self.height) // 2
        
        # Create shop surface
        shop_surface = pygame.Surface((self.width, self.height))
        shop_surface.fill((60, 60, 60))  # Dark gray background
        
        # Draw border
        pygame.draw.rect(shop_surface, (120, 120, 120), (0, 0, self.width, self.height), 3)
        
        # Shop title
        font = pygame.font.Font(None, 32)
        title_text = f"{self.name}"
        title_surface = font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.width // 2, 30))
        shop_surface.blit(title_surface, title_rect)
        
        # Close button
        close_button_rect = pygame.Rect(self.width - 30, 10, 20, 20)
        pygame.draw.rect(shop_surface, (200, 50, 50), close_button_rect)
        pygame.draw.rect(shop_surface, (255, 255, 255), close_button_rect, 2)
        close_font = pygame.font.Font(None, 20)
        close_text = close_font.render("X", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=close_button_rect.center)
        shop_surface.blit(close_text, close_text_rect)
        
        # Calculate panel dimensions
        panel_width = (self.width - 30) // 2  # Split width in half with margin
        items_start_y = 80
        
        # Draw vertical divider
        divider_x = panel_width + 7
        pygame.draw.line(shop_surface, (120, 120, 120), (divider_x, 60), (divider_x, self.height - 80), 2)
        
        # Left panel - Shop items
        shop_label_font = pygame.font.Font(None, 24)
        shop_label = shop_label_font.render("Shop Items", True, (255, 255, 255))
        shop_surface.blit(shop_label, (self.padding, 55))
        
        self.render_item_panel(shop_surface, self.items, 0, items_start_y, panel_width, "shop")
        
        # Right panel - Player items
        player_label = shop_label_font.render("Your Items", True, (255, 255, 255))
        shop_surface.blit(player_label, (panel_width + 15 + self.padding, 55))
        
        player_items = getattr(self, '_player_items', [])
        self.render_item_panel(shop_surface, player_items, panel_width + 15, items_start_y, panel_width, "player")
        
        # Item details panel
        if self.selected_item:
            self.render_item_details(shop_surface)
        
        # Action buttons
        self.render_action_buttons(shop_surface)
        
        # Instructions
        self.render_instructions(shop_surface)
        
        # Blit shop surface to main screen
        screen.blit(shop_surface, (shop_x, shop_y))
    
    def render_item_panel(self, surface, items, start_x, start_y, panel_width, panel_type):
        """Render a panel of items"""
        item_font = pygame.font.Font(None, 18)
        
        for i, item in enumerate(items):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_x = start_x + self.padding + col * (self.slot_size + self.padding)
            slot_y = start_y + row * (self.slot_size + self.padding)
            
            # Don't render if slot would go outside panel
            if slot_x + self.slot_size > start_x + panel_width:
                continue
            
            # Draw slot background
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            slot_color = (100, 100, 100)
            
            # Highlight selected item
            if item == self.selected_item and self.selected_side == panel_type:
                slot_color = (150, 150, 100)  # Yellow tint for selected
            
            # Special color for unsellable items in player panel
            if panel_type == "player" and not self.can_sell_item(item):
                slot_color = (80, 60, 60)  # Dark red tint for unsellable
            
            pygame.draw.rect(surface, slot_color, slot_rect)
            pygame.draw.rect(surface, (200, 200, 200), slot_rect, 2)
            
            # Draw item sprite
            if hasattr(item, 'sprite') and item.sprite:
                # Scale sprite to fit slot
                scaled_sprite = pygame.transform.scale(item.sprite, (self.slot_size - 8, self.slot_size - 8))
                sprite_rect = scaled_sprite.get_rect()
                sprite_rect.center = slot_rect.center
                surface.blit(scaled_sprite, sprite_rect)
            else:
                # Fallback colored rectangle
                item_colors = {
                    "weapon": (192, 192, 192),
                    "armor": (165, 42, 42),
                    "consumable": (255, 0, 0) if "Health" in item.name else (0, 0, 255) if "Stamina" in item.name else (0, 191, 255) if "Mana" in item.name else (0, 255, 0) if "Antidote" in item.name else (255, 165, 0),
                    "misc": (255, 215, 0)
                }
                color = item_colors.get(item.item_type, (255, 215, 0))
                inner_rect = pygame.Rect(slot_x + 8, slot_y + 8, self.slot_size - 16, self.slot_size - 16)
                pygame.draw.rect(surface, color, inner_rect)
            
            # Draw price
            if panel_type == "shop":
                price_text = item_font.render(f"{item.value}g", True, (255, 215, 0))
            else:
                sell_price = max(1, item.value // 2) if self.can_sell_item(item) else 0
                price_text = item_font.render(f"{sell_price}g", True, (255, 215, 0) if sell_price > 0 else (150, 150, 150))
            
            price_rect = price_text.get_rect()
            price_rect.bottomright = (slot_x + self.slot_size - 2, slot_y + self.slot_size - 2)
            surface.blit(price_text, price_rect)
    
    def render_item_details(self, surface):
        """Render selected item details"""
        details_start_y = self.height - 200
        
        # Item name
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(self.selected_item.name, True, (255, 255, 255))
        surface.blit(name_text, (self.padding, details_start_y))
        
        # Item effects
        effects_y = details_start_y + 25
        effect_font = pygame.font.Font(None, 20)
        
        for effect_name, effect_value in self.selected_item.effect.items():
            effect_text = f"{effect_name.title()}: +{effect_value}"
            effect_surface = effect_font.render(effect_text, True, (200, 200, 200))
            surface.blit(effect_surface, (self.padding, effects_y))
            effects_y += 20
        
        # Price info
        if self.selected_side == "shop":
            price_text = f"Buy Price: {self.selected_item.value} gold"
        else:
            sell_price = max(1, self.selected_item.value // 2) if self.can_sell_item(self.selected_item) else 0
            price_text = f"Sell Price: {sell_price} gold" if sell_price > 0 else "Cannot be sold"
        
        price_surface = effect_font.render(price_text, True, (255, 215, 0))
        surface.blit(price_surface, (self.padding, effects_y))
    
    def render_action_buttons(self, surface):
        """Render buy and sell buttons"""
        # Buy button
        buy_button_rect = pygame.Rect(self.width // 2 - 120, self.height - 50, 100, 35)
        buy_enabled = self.selected_item and self.selected_side == "shop"
        buy_color = (50, 150, 50) if buy_enabled else (100, 100, 100)
        
        pygame.draw.rect(surface, buy_color, buy_button_rect)
        pygame.draw.rect(surface, (255, 255, 255), buy_button_rect, 2)
        
        buy_font = pygame.font.Font(None, 24)
        buy_text = buy_font.render("Buy", True, (255, 255, 255))
        buy_text_rect = buy_text.get_rect(center=buy_button_rect.center)
        surface.blit(buy_text, buy_text_rect)
        
        # Sell button
        sell_button_rect = pygame.Rect(self.width // 2 + 20, self.height - 50, 100, 35)
        sell_enabled = (self.selected_item and self.selected_side == "player" and 
                       self.can_sell_item(self.selected_item))
        sell_color = (150, 100, 50) if sell_enabled else (100, 100, 100)
        
        pygame.draw.rect(surface, sell_color, sell_button_rect)
        pygame.draw.rect(surface, (255, 255, 255), sell_button_rect, 2)
        
        sell_font = pygame.font.Font(None, 24)
        sell_text = sell_font.render("Sell", True, (255, 255, 255))
        sell_text_rect = sell_text.get_rect(center=sell_button_rect.center)
        surface.blit(sell_text, sell_text_rect)
    
    def render_instructions(self, surface):
        """Render instructions"""
        instruction_font = pygame.font.Font(None, 18)
        instructions = [
            "Click shop items and press Buy to purchase",
            "Click your items and press Sell to sell them",
            "Red items in your inventory cannot be sold"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = instruction_font.render(instruction, True, (180, 180, 180))
            surface.blit(instruction_surface, (self.padding, self.height - 90 + i * 15))
    
    def set_player_items(self, player_items):
        """Set player items for sell mode"""
        self._player_items = player_items