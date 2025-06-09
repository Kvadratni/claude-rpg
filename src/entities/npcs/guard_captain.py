"""
Guard Captain NPC with embedded AI recipe
"""

from ..ai_npc_base import BaseAINPC
from typing import Dict, Optional


class GuardCaptainNPC(BaseAINPC):
    """Village security leader with military training and knowledge of local threats"""
    
    recipe = {
        "version": "1.0.0",
        "title": "Guard Captain NPC",
        "description": "AI recipe for Guard Captain NPC - village protector and security expert",
        "prompt": """You are a Guard Captain in a fantasy RPG world. You are the leader of the village security forces, with military training and extensive knowledge of local threats. You are authoritative but fair, duty-bound, and focused on protecting the village and its people.

Key characteristics:
- You are a disciplined military leader and village protector
- You are authoritative but fair, with a strong sense of duty
- You have knowledge of local dangers, patrol routes, and security matters
- You are vigilant and always alert to potential threats
- You speak with military precision and authority

CURRENT CONTEXT: {{ context }}
PLAYER SAYS: "{{ message }}"

Respond as the Guard Captain in 1-2 sentences, staying true to your authoritative and duty-bound character.""",
        "parameters": [
            {
                "key": "message",
                "input_type": "text",
                "requirement": "user_prompt",
                "description": "The player's message to the Guard Captain"
            },
            {
                "key": "context",
                "input_type": "text",
                "requirement": "optional",
                "description": "Current game context and situation",
                "default": "Player is in the village"
            }
        ]
    }
    
    def __init__(self, x: int, y: int, asset_loader=None, unique_id=None, **kwargs):
        dialog = [
            "Halt! I am the Guard Captain. State your business in our village.",
            "I maintain order and security in this village.",
            "The roads have been dangerous lately. Stay alert, traveler."
        ]
        
        super().__init__(x, y, "Guard Captain", dialog=dialog, 
                        asset_loader=asset_loader, unique_id=unique_id, **kwargs)
    
    def _get_sprite_name(self) -> Optional[str]:
        """Get sprite name for Guard Captain"""
        return "guard_captain"
    
    def _create_generated_sprite(self, size: int):
        """Create Guard Captain sprite with steel blue colors and helmet"""
        import pygame
        
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Guard Captain appearance - steel blue with gray helmet
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, (70, 130, 180), center, size // 3)  # Steel blue uniform
        pygame.draw.circle(self.sprite, (255, 255, 255), center, size // 4)  # Face
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Border
        
        # Gray helmet
        pygame.draw.rect(self.sprite, (105, 105, 105), (size//2 - 10, 5, 20, 8))  # Helmet
        pygame.draw.rect(self.sprite, (169, 169, 169), (size//2 - 8, 8, 16, 4))   # Helmet detail
        
        # Create direction sprites
        self.direction_sprites = [
            self.sprite,  # Down (0)
            pygame.transform.flip(self.sprite, True, False),  # Left (1)
            self.sprite,  # Up (2)
            self.sprite   # Right (3)
        ]
    
    def _get_npc_specific_responses(self) -> Dict[str, str]:
        """Guard Captain specific fallback responses"""
        return {
            "hello": "Halt! I am the Guard Captain, protector of this village and its people.",
            "who": "I am the Guard Captain, leader of the village guard and keeper of the peace.",
            "help": "I maintain order here. Is there trouble you wish to report?",
            "danger": "The roads have been perilous lately. Bandits and worse creatures roam the wilderness.",
            "safe": "This village is under my protection. You may rest safely within our walls.",
            "threat": "Any threat to this village will be met with swift justice.",
            "patrol": "My guards patrol day and night to keep the peace.",
            "security": "Village security is my responsibility, and I take it seriously.",
            "order": "Order and discipline are the foundations of a safe community.",
            "protect": "I have sworn to protect these people, and I will not fail in that duty.",
            "enemy": "Our enemies will find no weakness in our defenses.",
            "bye": "Stay vigilant out there, traveler. Danger lurks in dark places.",
            "default": "I keep watch over this village day and night."
        }
    
    def interact(self, player):
        """Handle Guard Captain specific interactions"""
        # Update quest progress for talking to guards
        if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
            player.game.quest_manager.update_quest_progress("talk", self.name)
        
        # Call parent interaction
        super().interact(player)