"""
Master Smith AI NPC - Weapon and armor crafting specialist
"""

from ..ai_npc_base import BaseAINPC

class MasterSmithNPC(BaseAINPC):
    """AI-powered Master Smith NPC"""
    
    # Recipe configuration
    recipe = {
        "file": "master_smith.yaml",
        "description": "Master craftsman specializing in weapons and armor"
    }
    
    def __init__(self, x: int, y: int, asset_loader=None, **kwargs):
        dialog = [
            "The forge burns hot today, perfect for crafting!",
            "I can craft weapons and armor from the finest materials.",
            "Bring me rare ores and I'll make you legendary equipment!",
            "Every blade I forge is a work of art."
        ]
        
        # Shop items for Master Smith
        shop_items = [
            {"name": "Steel Sword", "price": 300, "type": "weapon"},
            {"name": "Iron Shield", "price": 200, "type": "armor"},
            {"name": "Chain Mail", "price": 250, "type": "armor"},
            {"name": "Battle Axe", "price": 350, "type": "weapon"}
        ]
        
        super().__init__(x, y, "Master Smith", dialog=dialog, 
                        asset_loader=asset_loader, has_shop=True,
                        shop_items=shop_items, **kwargs)
    
    def _get_sprite_name(self):
        """Get sprite name for Master Smith"""
        return "master_smith"
    
    def _get_npc_specific_responses(self):
        """Master Smith specific fallback responses"""
        return {
            "hello": "Welcome to my forge! I craft the finest weapons and armor.",
            "forge": "My forge burns with ancient flames, perfect for legendary crafting.",
            "weapon": "I can craft any weapon you desire, given the right materials.",
            "armor": "My armor will protect you from the deadliest foes.",
            "craft": "Bring me materials and I'll craft something magnificent!",
            "repair": "I can repair any weapon or armor, good as new.",
            "materials": "I work with iron, steel, mithril, and even dragon scales.",
            "bye": "May your weapons stay sharp and your armor strong!",
            "default": "*The Master Smith hammers rhythmically at his anvil*"
        }