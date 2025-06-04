"""
Item Registry System for Asset-Aware Quest Generation
Manages all available items and their assets for quest creation
"""

import random
import re
from typing import Dict, List, Optional, Tuple, Any


class ItemRegistry:
    """Central registry of all available items with their assets"""
    
    def __init__(self, asset_loader=None):
        self.asset_loader = asset_loader
        self.items = {}
        self.categories = {
            "weapons": [],
            "armor": [],
            "consumables": [],
            "misc": [],
            "quest_items": []
        }
        self.item_aliases = {}  # Maps alternative names to canonical names
        self._build_registry()
    
    def _build_registry(self):
        """Build registry from available assets and predefined items"""
        # Define all known items with their properties
        self.known_items = {
            # Weapons
            "Iron Sword": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "iron_sword",
                "effect": {"damage": 15},
                "value": 100,
                "aliases": ["sword", "blade", "iron blade"]
            },
            "Steel Axe": {
                "type": "weapon", 
                "category": "weapons",
                "sprite_key": "steel_axe",
                "effect": {"damage": 20},
                "value": 150,
                "aliases": ["axe", "steel blade"]
            },
            "Bronze Mace": {
                "type": "weapon",
                "category": "weapons", 
                "sprite_key": "bronze_mace",
                "effect": {"damage": 12},
                "value": 80,
                "aliases": ["mace", "club", "bronze weapon"]
            },
            "Silver Dagger": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "silver_dagger", 
                "effect": {"damage": 18},
                "value": 120,
                "aliases": ["dagger", "knife", "silver blade"]
            },
            "War Hammer": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "war_hammer",
                "effect": {"damage": 25},
                "value": 200,
                "aliases": ["hammer", "war weapon"]
            },
            "Magic Bow": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "magic_bow",
                "effect": {"damage": 22},
                "value": 180,
                "aliases": ["bow", "magic weapon"]
            },
            "Crystal Staff": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "crystal_staff",
                "effect": {"damage": 16, "spell_power": 10},
                "value": 220,
                "aliases": ["staff", "crystal weapon", "magic staff"]
            },
            "Throwing Knife": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "throwing_knife",
                "effect": {"damage": 14},
                "value": 90,
                "aliases": ["throwing weapon", "knife"]
            },
            "Crossbow": {
                "type": "weapon",
                "category": "weapons",
                "sprite_key": "crossbow",
                "effect": {"damage": 19},
                "value": 160,
                "aliases": ["bow", "ranged weapon"]
            },
            
            # Armor
            "Leather Armor": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "leather_armor",
                "effect": {"defense": 8},
                "value": 80,
                "aliases": ["armor", "leather protection"]
            },
            "Chain Mail": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "chain_mail",
                "effect": {"defense": 12},
                "value": 120,
                "aliases": ["mail", "chain armor"]
            },
            "Plate Armor": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "plate_armor",
                "effect": {"defense": 18},
                "value": 200,
                "aliases": ["plate", "heavy armor"]
            },
            "Studded Leather": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "studded_leather",
                "effect": {"defense": 10},
                "value": 100,
                "aliases": ["studded armor", "reinforced leather"]
            },
            "Scale Mail": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "scale_mail",
                "effect": {"defense": 15},
                "value": 160,
                "aliases": ["scale armor", "scaled protection"]
            },
            "Dragon Scale Armor": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "dragon_scale_armor",
                "effect": {"defense": 20, "fire_resistance": 10},
                "value": 300,
                "aliases": ["dragon armor", "magical armor"]
            },
            "Mage Robes": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "mage_robes",
                "effect": {"defense": 6, "spell_power": 15},
                "value": 180,
                "aliases": ["robes", "mage armor", "magical robes"]
            },
            "Royal Armor": {
                "type": "armor",
                "category": "armor",
                "sprite_key": "royal_armor",
                "effect": {"defense": 22, "magic_resistance": 8},
                "value": 350,
                "aliases": ["royal protection", "noble armor"]
            },
            
            # Consumables
            "Health Potion": {
                "type": "consumable",
                "category": "consumables",
                "sprite_key": "health_potion",
                "effect": {"health": 50},
                "value": 25,
                "aliases": ["potion", "healing potion", "red potion"]
            },
            "Stamina Potion": {
                "type": "consumable",
                "category": "consumables", 
                "sprite_key": "stamina_potion",
                "effect": {"stamina": 30},
                "value": 20,
                "aliases": ["energy potion", "blue potion"]
            },
            "Mana Potion": {
                "type": "consumable",
                "category": "consumables",
                "sprite_key": "mana_potion",
                "effect": {"mana": 40},
                "value": 30,
                "aliases": ["magic potion", "mana elixir"]
            },
            "Antidote": {
                "type": "consumable",
                "category": "consumables",
                "sprite_key": "antidote",
                "effect": {"cure_poison": True},
                "value": 35,
                "aliases": ["poison cure", "antidote potion"]
            },
            "Strength Potion": {
                "type": "consumable",
                "category": "consumables",
                "sprite_key": "strength_potion",
                "effect": {"damage_boost": 10, "duration": 60},
                "value": 50,
                "aliases": ["power potion", "strength elixir"]
            },
            
            # Miscellaneous/Quest Items
            "Gold Ring": {
                "type": "misc",
                "category": "quest_items",
                "sprite_key": "gold_ring",
                "effect": {"magic_resistance": 5},
                "value": 250,
                "aliases": ["ring", "golden ring", "jewelry"]
            },
            "Magic Scroll": {
                "type": "misc",
                "category": "quest_items",
                "sprite_key": "magic_scroll",
                "effect": {"spell_power": 15},
                "value": 200,
                "aliases": ["scroll", "tome", "document", "parchment"]
            },
            "Crystal Gem": {
                "type": "misc",
                "category": "quest_items",
                "sprite_key": "crystal_gem",
                "effect": {"value": 100},
                "value": 150,
                "aliases": ["gem", "crystal", "stone", "jewel"]
            }
        }
        
        # Build the registry
        for item_name, item_data in self.known_items.items():
            if self._verify_item_asset(item_name, item_data):
                self.register_item(item_name, item_data)
    
    def register_item(self, item_name: str, item_data: Dict[str, Any]):
        """Register an item in the registry"""
        self.items[item_name] = item_data
        
        # Add to category
        category = item_data.get("category", "misc")
        if category in self.categories:
            self.categories[category].append(item_name)
        
        # Register aliases
        for alias in item_data.get("aliases", []):
            self.item_aliases[alias.lower()] = item_name
    
    def _verify_item_asset(self, item_name: str, item_data: Dict[str, Any]) -> bool:
        """Verify that an item has proper assets"""
        if not self.asset_loader:
            return True  # Assume valid if no asset loader
        
        # Check if sprite exists
        sprite_key = item_data.get("sprite_key")
        if sprite_key and sprite_key in self.asset_loader.images:
            return True
        
        # Check alternative sprite naming
        alt_sprite_key = item_name.lower().replace(" ", "_")
        if alt_sprite_key in self.asset_loader.images:
            item_data["sprite_key"] = alt_sprite_key
            return True
        
        print(f"⚠️  [ItemRegistry] No sprite found for {item_name} (tried: {sprite_key}, {alt_sprite_key})")
        return False
    
    def get_random_item_by_category(self, category: str) -> Optional[str]:
        """Get a random item from a specific category"""
        items = self.categories.get(category, [])
        return random.choice(items) if items else None
    
    def find_similar_items(self, description: str) -> List[str]:
        """Find items that match a description using fuzzy matching"""
        description_lower = description.lower()
        matches = []
        
        # Direct name matches
        for item_name in self.items.keys():
            if description_lower in item_name.lower():
                matches.append(item_name)
        
        # Alias matches
        for alias, item_name in self.item_aliases.items():
            if alias in description_lower:
                if item_name not in matches:
                    matches.append(item_name)
        
        # Keyword matches
        keywords = description_lower.split()
        for keyword in keywords:
            for alias, item_name in self.item_aliases.items():
                if keyword in alias:
                    if item_name not in matches:
                        matches.append(item_name)
        
        return matches
    
    def get_item_data(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get full item data by name"""
        return self.items.get(item_name)
    
    def resolve_item_name(self, query: str) -> Optional[str]:
        """Resolve a query to a canonical item name"""
        query_lower = query.lower()
        
        # Direct match
        for item_name in self.items.keys():
            if query_lower == item_name.lower():
                return item_name
        
        # Alias match
        if query_lower in self.item_aliases:
            return self.item_aliases[query_lower]
        
        # Partial match
        similar_items = self.find_similar_items(query)
        return similar_items[0] if similar_items else None
    
    def get_suitable_quest_items(self, quest_type: str = "any") -> List[str]:
        """Get items suitable for quests of a specific type"""
        if quest_type == "collect":
            # Prefer quest items and consumables for collection quests
            return (self.categories.get("quest_items", []) + 
                   self.categories.get("consumables", []))
        elif quest_type == "equip":
            # Weapons and armor for equipment quests
            return (self.categories.get("weapons", []) + 
                   self.categories.get("armor", []))
        else:
            # All items for general quests
            return list(self.items.keys())
    
    def get_guaranteed_fallback_item(self) -> str:
        """Get a guaranteed item that should always exist"""
        # Try health potion first as it's most common
        if "Health Potion" in self.items:
            return "Health Potion"
        
        # Try any consumable
        consumables = self.categories.get("consumables", [])
        if consumables:
            return consumables[0]
        
        # Try any item
        if self.items:
            return list(self.items.keys())[0]
        
        # Last resort fallback
        return "Health Potion"
    
    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics about available items by category"""
        return {category: len(items) for category, items in self.categories.items()}
    
    def print_registry_info(self):
        """Print registry information for debugging"""
        print("🗃️  [ItemRegistry] Available Items:")
        for category, items in self.categories.items():
            if items:
                print(f"  {category.title()}: {len(items)} items")
                for item in items[:3]:  # Show first 3 items
                    print(f"    - {item}")
                if len(items) > 3:
                    print(f"    ... and {len(items) - 3} more")
        
        print(f"  Total Items: {len(self.items)}")
        print(f"  Total Aliases: {len(self.item_aliases)}")