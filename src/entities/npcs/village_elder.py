"""
Village Elder NPC with embedded AI recipe
"""

from ..ai_npc_base import BaseAINPC
from typing import Dict, Optional


class VillageElderNPC(BaseAINPC):
    """Wise village elder with knowledge of local history and quests"""
    
    recipe = {
        "version": "1.0.0",
        "title": "Village Elder NPC",
        "description": "AI recipe for Village Elder NPC - wise keeper of ancient knowledge",
        "prompt": """You are a wise Village Elder in a fantasy RPG world. You are the keeper of ancient knowledge, village history, and a guide for adventurers. You speak with wisdom, authority, and use formal but warm language.

Key characteristics:
- You are wise and knowledgeable about local history and legends
- You give quests and advice to adventurers
- You speak with formal, archaic language but remain approachable
- You know about ancient threats, ruins, and local lore
- You are respected by all villagers

CURRENT CONTEXT: {{ context }}
PLAYER SAYS: "{{ message }}"

Respond as the Village Elder in 1-2 sentences, staying true to your wise and authoritative character.""",
        "parameters": [
            {
                "key": "message",
                "input_type": "text",
                "requirement": "user_prompt",
                "description": "The player's message to the Village Elder"
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
    
    def __init__(self, x: int, y: int, asset_loader=None, **kwargs):
        dialog = [
            "Greetings, young adventurer. I am the Village Elder.",
            "The ancient wisdom guides those who seek it.",
            "Dark forces stir in the old ruins. Perhaps you could investigate?"
        ]
        
        super().__init__(x, y, "Village Elder", dialog=dialog, 
                        asset_loader=asset_loader, **kwargs)
    
    def _get_sprite_name(self) -> Optional[str]:
        """Get sprite name for Village Elder"""
        return "elder_npc"
    
    def _create_generated_sprite(self, size: int):
        """Create Village Elder sprite with purple robes and white beard"""
        import pygame
        
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Village Elder appearance - purple with white beard
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, (128, 0, 128), center, size // 3)  # Purple robes
        pygame.draw.circle(self.sprite, (255, 255, 255), center, size // 4)  # Face
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Border
        
        # White beard
        pygame.draw.circle(self.sprite, (255, 255, 255), (size//2, size//2 + 8), 9)
        
        # Create direction sprites
        self.direction_sprites = [
            self.sprite,  # Down (0)
            pygame.transform.flip(self.sprite, True, False),  # Left (1)
            self.sprite,  # Up (2)
            self.sprite   # Right (3)
        ]
    
    def _get_npc_specific_responses(self) -> Dict[str, str]:
        """Village Elder specific fallback responses"""
        return {
            "hello": "Greetings, young adventurer. I am the Village Elder, keeper of ancient wisdom.",
            "who": "I am the Village Elder, guardian of this village's history and traditions.",
            "help": "I offer guidance to brave souls like yourself. What knowledge do you seek?",
            "quest": "Indeed, there are dark forces stirring. Perhaps you could investigate the old ruins to the north?",
            "wisdom": "The old ways teach us that patience and courage are the greatest virtues.",
            "village": "This village has stood for centuries, protected by the wisdom of our ancestors.",
            "danger": "Ancient evils stir in the forgotten places. The ruins hold secrets both dark and valuable.",
            "bye": "May the ancient spirits guide your path, brave one.",
            "default": "The old ways teach us patience and wisdom, traveler."
        }
    
    def interact(self, player):
        """Handle Village Elder specific interactions"""
        # Check for quest giving logic
        if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
            quest_manager = player.game.quest_manager
            
            # Check if we should offer the main quest
            if ("main_story" not in quest_manager.active_quests and 
                "main_story" not in quest_manager.completed_quests):
                # Check if tutorial is completed
                if "tutorial" in quest_manager.completed_quests:
                    quest_manager.start_quest("main_story")
                    if player.game_log:
                        player.game_log.add_message("New Quest: The Orc Threat", "quest")
        
        # Call parent interaction
        super().interact(player)