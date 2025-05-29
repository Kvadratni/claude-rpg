"""
Chest entities for the RPG
"""

import pygame
import math
import random
from .base import Entity
from .item import Item

class Chest(Entity):
    """Chest entity that can be opened for loot"""
    
    def __init__(self, x, y, chest_type="wooden", asset_loader=None):
        super().__init__(x, y, f"{chest_type.title()} Chest", "chest", blocks_movement=True, asset_loader=asset_loader)
        self.chest_type = chest_type  # wooden, iron, gold, magical
        self.is_opened = False
        self.loot_items = []
        self.asset_loader = asset_loader
        
        # Generate loot based on chest type
        self.generate_loot()
        
        # Create chest sprite
        self.create_chest_sprite()
    
    def create_chest_sprite(self):
        """Create chest sprite using separate closed/open assets"""
        size = 48
        
        # Try to use loaded sprite first
        if self.asset_loader:
            # Determine sprite name based on chest type and state
            if self.is_opened:
                sprite_name = f"{self.chest_type}_chest_open"
            else:
                sprite_name = f"{self.chest_type}_chest_closed"
            
            chest_image = self.asset_loader.get_image(sprite_name)
            if chest_image:
                self.sprite = pygame.transform.scale(chest_image, (size, size))
                return
        
        # Fallback to generated sprite (same as before)
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Different colors for different chest types
        if self.chest_type == "wooden":
            color = (139, 69, 19)  # Brown
            accent_color = (160, 82, 45)  # Saddle brown
        elif self.chest_type == "iron":
            color = (105, 105, 105)  # Dim gray
            accent_color = (169, 169, 169)  # Dark gray
        elif self.chest_type == "gold":
            color = (255, 215, 0)  # Gold
            accent_color = (255, 255, 0)  # Yellow
        elif self.chest_type == "magical":
            color = (138, 43, 226)  # Blue violet
            accent_color = (147, 112, 219)  # Medium purple
        else:
            color = (139, 69, 19)  # Default brown
            accent_color = (160, 82, 45)
        
        # Draw chest body
        chest_body = pygame.Rect(size//6, size//3, 2*size//3, 2*size//3)
        pygame.draw.rect(self.sprite, color, chest_body)
        pygame.draw.rect(self.sprite, (0, 0, 0), chest_body, 2)
        
        # Draw chest lid
        if not self.is_opened:
            lid_rect = pygame.Rect(size//6, size//4, 2*size//3, size//3)
            pygame.draw.rect(self.sprite, accent_color, lid_rect)
            pygame.draw.rect(self.sprite, (0, 0, 0), lid_rect, 2)
            
            # Draw lock/latch
            lock_rect = pygame.Rect(size//2 - 3, size//2 - 2, 6, 4)
            pygame.draw.rect(self.sprite, (255, 215, 0), lock_rect)
            pygame.draw.rect(self.sprite, (0, 0, 0), lock_rect, 1)
        else:
            # Opened chest - lid is up
            lid_rect = pygame.Rect(size//6, size//8, 2*size//3, size//4)
            pygame.draw.rect(self.sprite, accent_color, lid_rect)
            pygame.draw.rect(self.sprite, (0, 0, 0), lid_rect, 2)
            
            # Draw interior
            interior_rect = pygame.Rect(size//6 + 2, size//3 + 2, 2*size//3 - 4, 2*size//3 - 4)
            pygame.draw.rect(self.sprite, (101, 67, 33), interior_rect)  # Dark brown interior
    
    def generate_loot(self):
        """Generate loot based on chest type with proper rarity matching"""
        self.loot_items = []
        
        if self.chest_type == "wooden":
            # Basic loot - 1-2 common items, low value
            num_items = random.randint(1, 2)
            for _ in range(num_items):
                item_type = random.choice(["consumable", "consumable", "consumable", "misc"])  # Heavily favor consumables
                if item_type == "consumable":
                    # Only basic potions
                    potion_types = ["Health Potion", "Stamina Potion"]
                    potion_name = random.choice(potion_types)
                    if potion_name == "Health Potion":
                        item = Item(self.x, self.y, "Health Potion", item_type="consumable", 
                                  effect={"health": 30}, value=15, asset_loader=self.asset_loader)  # Reduced healing and value
                    else:
                        item = Item(self.x, self.y, "Stamina Potion", item_type="consumable", 
                                  effect={"stamina": 20}, value=12, asset_loader=self.asset_loader)  # Reduced effect and value
                else:  # misc - only low-value items
                    item = Item(self.x, self.y, "Crystal Gem", item_type="misc", 
                              effect={"value": 25}, value=50, asset_loader=self.asset_loader)  # Much lower value
                
                self.loot_items.append(item)
        
        elif self.chest_type == "iron":
            # Mid-tier loot - 2-3 items, moderate value
            num_items = random.randint(2, 3)
            for _ in range(num_items):
                item_type = random.choice(["consumable", "weapon", "armor", "misc"])
                if item_type == "consumable":
                    # Basic to mid-tier potions
                    potion_types = ["Health Potion", "Stamina Potion", "Mana Potion"]
                    potion_name = random.choice(potion_types)
                    if potion_name == "Health Potion":
                        item = Item(self.x, self.y, "Health Potion", item_type="consumable", 
                                  effect={"health": 40}, value=20, asset_loader=self.asset_loader)  # Standard healing
                    elif potion_name == "Stamina Potion":
                        item = Item(self.x, self.y, "Stamina Potion", item_type="consumable", 
                                  effect={"stamina": 25}, value=15, asset_loader=self.asset_loader)
                    else:
                        item = Item(self.x, self.y, "Mana Potion", item_type="consumable", 
                                  effect={"mana": 30}, value=18, asset_loader=self.asset_loader)
                elif item_type == "weapon":
                    # Basic to mid-tier weapons
                    weapons = ["Iron Sword", "Bronze Mace", "Silver Dagger"]
                    weapon_name = random.choice(weapons)
                    damage = random.randint(12, 16)  # Moderate damage
                    value = random.randint(80, 120)  # Moderate value
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage}, value=value, asset_loader=self.asset_loader)
                elif item_type == "armor":
                    # Basic to mid-tier armor
                    armors = ["Leather Armor", "Studded Leather"]
                    armor_name = random.choice(armors)
                    defense = random.randint(6, 10)  # Moderate defense
                    value = random.randint(60, 100)  # Moderate value
                    item = Item(self.x, self.y, armor_name, item_type="armor", 
                              effect={"defense": defense}, value=value, asset_loader=self.asset_loader)
                else:  # misc
                    # Mid-tier misc items
                    misc_items = [("Magic Scroll", {"spell_power": 8}), ("Crystal Gem", {"value": 50})]
                    item_name, effect = random.choice(misc_items)
                    value = random.randint(100, 150)  # Moderate value
                    item = Item(self.x, self.y, item_name, item_type="misc", 
                              effect=effect, value=value, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
        
        elif self.chest_type == "gold":
            # High-tier loot - 3-4 items, high value
            num_items = random.randint(3, 4)
            for _ in range(num_items):
                item_type = random.choice(["weapon", "armor", "consumable", "misc"])
                if item_type == "weapon":
                    # High-tier weapons
                    weapons = ["Steel Axe", "War Hammer", "Magic Bow", "Crossbow"]
                    weapon_name = random.choice(weapons)
                    damage = random.randint(18, 24)  # High damage
                    value = random.randint(150, 220)  # High value
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage}, value=value, asset_loader=self.asset_loader)
                elif item_type == "armor":
                    # High-tier armor
                    armors = ["Chain Mail", "Scale Mail", "Plate Armor"]
                    armor_name = random.choice(armors)
                    defense = random.randint(12, 18)  # High defense
                    value = random.randint(120, 200)  # High value
                    item = Item(self.x, self.y, armor_name, item_type="armor", 
                              effect={"defense": defense}, value=value, asset_loader=self.asset_loader)
                elif item_type == "consumable":
                    # High-quality consumables
                    consumables = ["Strength Potion", "Mana Potion", "Antidote"]
                    consumable_name = random.choice(consumables)
                    if consumable_name == "Strength Potion":
                        item = Item(self.x, self.y, "Strength Potion", item_type="consumable", 
                                  effect={"damage_boost": 12, "duration": 75}, value=45, asset_loader=self.asset_loader)
                    elif consumable_name == "Mana Potion":
                        item = Item(self.x, self.y, "Mana Potion", item_type="consumable", 
                                  effect={"mana": 50}, value=35, asset_loader=self.asset_loader)
                    else:
                        item = Item(self.x, self.y, "Antidote", item_type="consumable", 
                                  effect={"cure_poison": True}, value=40, asset_loader=self.asset_loader)
                else:  # misc
                    # High-value misc items
                    item = Item(self.x, self.y, "Gold Ring", item_type="misc", 
                              effect={"magic_resistance": 6}, value=200, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
        
        elif self.chest_type == "magical":
            # Legendary loot - 2-3 rare magical items with enhanced effects
            num_items = random.randint(2, 3)
            for _ in range(num_items):
                item_type = random.choice(["weapon", "armor", "misc"])
                if item_type == "weapon":
                    # Legendary magical weapons
                    weapons = ["Crystal Staff", "Throwing Knife"]  # Only the most magical weapons
                    weapon_name = random.choice(weapons)
                    damage = random.randint(22, 30)  # Very high damage
                    spell_power = random.randint(15, 25)  # High spell power
                    value = random.randint(250, 350)  # Very high value
                    item = Item(self.x, self.y, weapon_name, item_type="weapon", 
                              effect={"damage": damage, "spell_power": spell_power}, value=value, asset_loader=self.asset_loader)
                elif item_type == "armor":
                    # Legendary magical armor
                    armors = ["Dragon Scale Armor", "Mage Robes", "Royal Armor"]
                    armor_name = random.choice(armors)
                    defense = random.randint(20, 28)  # Very high defense
                    magic_resist = random.randint(10, 18)  # High magic resistance
                    value = random.randint(300, 450)  # Very high value
                    item = Item(self.x, self.y, armor_name, item_type="armor", 
                              effect={"defense": defense, "magic_resistance": magic_resist}, value=value, asset_loader=self.asset_loader)
                else:  # misc
                    # Legendary misc items
                    misc_items = [
                        ("Magic Scroll", {"spell_power": 30}),  # Very powerful scroll
                        ("Crystal Gem", {"value": 150}),  # Valuable gem
                        ("Gold Ring", {"magic_resistance": 15})  # Very powerful ring
                    ]
                    item_name, effect = random.choice(misc_items)
                    value = random.randint(300, 500)  # Very high value
                    item = Item(self.x, self.y, item_name, item_type="misc", 
                              effect=effect, value=value, asset_loader=self.asset_loader)
                
                self.loot_items.append(item)
    
    def interact(self, player):
        """Open the chest and give loot to player"""
        if self.is_opened:
            if player.game_log:
                player.game_log.add_message("This chest is already empty.", "system")
            return
        
        # Check if player is close enough
        dist = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        if dist > 1.5:
            if player.game_log:
                player.game_log.add_message("You need to be closer to open the chest.", "system")
            return
        
        # Get audio manager
        audio = getattr(self.asset_loader, 'audio_manager', None) if self.asset_loader else None
        
        # Play chest opening sound
        if audio:
            audio.play_ui_sound("achievement")  # Use achievement sound for chest opening
        
        self.is_opened = True
        
        # Update sprite to show opened chest
        self.create_chest_sprite()
        
        # Give loot to player
        items_received = []
        items_dropped = []
        
        for item in self.loot_items:
            if player.add_item(item):
                items_received.append(item.name)
            else:
                # Drop item on ground if inventory is full
                item.x = self.x + random.uniform(-0.5, 0.5)
                item.y = self.y + random.uniform(-0.5, 0.5)
                items_dropped.append(item)
        
        # Add dropped items to level
        if hasattr(player, 'game') and hasattr(player.game, 'level'):
            player.game.level.items.extend(items_dropped)
        
        # Show messages
        if player.game_log:
            player.game_log.add_message(f"Opened {self.name}!", "item")
            if items_received:
                for item_name in items_received:
                    player.game_log.add_message(f"Found {item_name}!", "item")
            if items_dropped:
                player.game_log.add_message(f"{len(items_dropped)} items dropped (inventory full)", "system")
    
    def get_save_data(self):
        """Get data for saving"""
        data = super().get_save_data()
        data.update({
            "chest_type": self.chest_type,
            "is_opened": self.is_opened,
            "loot_items": [item.get_save_data() for item in self.loot_items]
        })
        return data
    
    @classmethod
    def from_save_data(cls, data, asset_loader=None):
        """Create chest from save data"""
        chest = cls(data["x"], data["y"], data["chest_type"], asset_loader)
        chest.is_opened = data["is_opened"]
        chest.loot_items = []
        for item_data in data["loot_items"]:
            item = Item.from_save_data(item_data, asset_loader)
            chest.loot_items.append(item)
        return chest


