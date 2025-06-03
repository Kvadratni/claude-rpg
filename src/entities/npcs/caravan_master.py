"""
Caravan Master AI NPC - Trade routes and distant lands expert
"""

from ..ai_npc_base import BaseAINPC

class CaravanMasterNPC(BaseAINPC):
    """AI-powered Caravan Master NPC"""
    
    # Recipe configuration
    recipe = {
        "file": "caravan_master.yaml",
        "description": "Experienced trader managing caravan routes"
    }
    
    def __init__(self, x: int, y: int, asset_loader=None, **kwargs):
        dialog = [
            "The roads are long but profitable for those who dare.",
            "I've traveled every trade route from here to the capital.",
            "My caravans carry goods across dangerous lands.",
            "Adventure and profit go hand in hand."
        ]
        
        super().__init__(x, y, "Caravan Master", dialog=dialog, 
                        asset_loader=asset_loader, **kwargs)
    
    def _get_sprite_name(self):
        """Get sprite name for Caravan Master"""
        return "caravan_master"
    
    def _get_npc_specific_responses(self):
        """Caravan Master specific fallback responses"""
        return {
            "hello": "Greetings, traveler! Looking to join a caravan?",
            "trade": "Trade is the lifeblood of civilization.",
            "caravan": "My caravans are well-guarded and profitable.",
            "road": "I know every road, path, and shortcut in the realm.",
            "danger": "The roads are perilous, but that's where profit lies.",
            "goods": "I trade in everything from spices to steel.",
            "travel": "Want to see distant lands? Join my next expedition.",
            "route": "I can tell you the safest routes to any city.",
            "bye": "Safe travels, and may the roads be kind to you!",
            "default": "*The Caravan Master studies his route maps*"
        }