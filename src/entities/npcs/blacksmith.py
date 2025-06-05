"""
Blacksmith AI NPC - Basic weapon and tool crafting
"""

from ..ai_npc_base import BaseAINPC

class BlacksmithNPC(BaseAINPC):
    """AI-powered Blacksmith NPC"""
    
    # Recipe configuration
    recipe = {
        "file": "blacksmith.yaml",
        "description": "Village blacksmith for basic crafting and repairs"
    }
    
    def __init__(self, x: int, y: int, asset_loader=None, **kwargs):
        dialog = [
            "The forge is always ready for honest work.",
            "I can repair your weapons and craft basic tools.",
            "Iron and steel are my trade, simple but reliable.",
            "Every village needs a good blacksmith."
        ]
        
        super().__init__(x, y, "Blacksmith", dialog=dialog, 
                        asset_loader=asset_loader, **kwargs)
    
    def _get_sprite_name(self):
        """Get sprite name for Blacksmith"""
        return "master_smith"  # Use master_smith sprite since no blacksmith sprite exists
    
    def _get_npc_specific_responses(self):
        """Blacksmith specific fallback responses"""
        return {
            "hello": "Welcome to my smithy! What can I forge for you?",
            "repair": "I can fix any weapon or tool, good as new.",
            "craft": "I craft honest tools and weapons for honest folk.",
            "iron": "Iron is strong and dependable, like the people here.",
            "weapon": "I make sturdy weapons that won't fail you in battle.",
            "tool": "Every farmer and craftsman needs good tools.",
            "forge": "My forge has been burning for twenty years.",
            "work": "Hard work at the anvil keeps me strong.",
            "bye": "May your tools serve you well!",
            "default": "*The Blacksmith strikes his hammer against the anvil*"
        }