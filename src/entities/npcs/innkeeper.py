"""
Innkeeper AI NPC - Provides rest, food, and local information
"""

from ..ai_npc_base import BaseAINPC

class InnkeeperNPC(BaseAINPC):
    """AI-powered Innkeeper NPC"""
    
    # Recipe configuration
    recipe = {
        "file": "innkeeper.yaml",
        "description": "Friendly innkeeper providing rest and local information"
    }
    
    def __init__(self, x: int, y: int, asset_loader=None, **kwargs):
        dialog = [
            "Welcome to the Sleeping Dragon Inn!",
            "We have the finest rooms and meals in the village.",
            "Travelers from all lands stop here for rest.",
            "I hear many interesting tales from my guests."
        ]
        
        super().__init__(x, y, "Innkeeper", dialog=dialog, 
                        asset_loader=asset_loader, **kwargs)
    
    def _get_sprite_name(self):
        """Get sprite name for Innkeeper"""
        return "innkeeper"
    
    def _get_npc_specific_responses(self):
        """Innkeeper specific fallback responses"""
        return {
            "hello": "Welcome to the Sleeping Dragon Inn! How can I help you?",
            "room": "Our rooms are clean and comfortable, perfect for weary travelers.",
            "food": "We serve the best stew and ale in the village!",
            "rest": "A good night's sleep will restore your strength.",
            "news": "I hear many tales from travelers who pass through.",
            "local": "I know everything that happens in this village.",
            "drink": "Our ale is brewed from the finest hops!",
            "stay": "You're welcome to stay as long as you need.",
            "bye": "Safe travels, and come back anytime!",
            "default": "*The Innkeeper wipes down a mug with a warm smile*"
        }