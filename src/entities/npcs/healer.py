"""
Healer AI NPC - Provides healing services and potions
"""

from ..ai_npc_base import BaseAINPC

class HealerNPC(BaseAINPC):
    """AI-powered Healer NPC"""
    
    # Recipe configuration
    recipe = {
        "file": "healer.yaml",
        "description": "Compassionate healer providing medical services"
    }
    
    def __init__(self, x: int, y: int, asset_loader=None, **kwargs):
        dialog = [
            "May the light guide you to wellness.",
            "I can heal your wounds and cure your ailments.",
            "The herbs I gather have powerful healing properties.",
            "Health is the greatest treasure of all."
        ]
        
        super().__init__(x, y, "Healer", dialog=dialog, 
                        asset_loader=asset_loader, **kwargs)
    
    def _get_sprite_name(self):
        """Get sprite name for Healer"""
        return "high_priest"  # Use high_priest sprite since no healer sprite exists
    
    def _get_npc_specific_responses(self):
        """Healer specific fallback responses"""
        return {
            "hello": "Greetings, child. How may I ease your suffering?",
            "heal": "Let me tend to your wounds with gentle care.",
            "potion": "I brew healing potions from the purest herbs.",
            "hurt": "Come, let me see where you are injured.",
            "sick": "I can cure most ailments with my remedies.",
            "herbs": "I gather healing herbs from the sacred grove.",
            "blessing": "May the divine light protect you on your journey.",
            "help": "Healing is my calling, I'm here to help.",
            "bye": "Go in peace, and may health follow you always.",
            "default": "*The Healer tends to her herbs with gentle hands*"
        }