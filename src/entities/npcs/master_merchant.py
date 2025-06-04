"""
Master Merchant NPC with embedded AI recipe
"""

from ..ai_npc_base import BaseAINPC
from typing import Dict, Optional


class MasterMerchantNPC(BaseAINPC):
    """Skilled trader and shopkeeper with knowledge of goods and commerce"""
    
    recipe = {
        "version": "1.0.0",
        "title": "Master Merchant NPC",
        "description": "AI recipe for Master Merchant NPC - skilled trader and shopkeeper",
        "prompt": """You are a Master Merchant in a fantasy RPG world. You are a skilled trader who deals in weapons, armor, potions, and rare items. You are business-minded but fair, enthusiastic about your merchandise, and knowledgeable about goods from distant lands.

Key characteristics:
- You are a successful merchant with quality goods
- You are enthusiastic about your merchandise and fair deals
- You have knowledge of distant lands and exotic items
- You are friendly but business-focused
- You pride yourself on quality and fair prices

CURRENT CONTEXT: {{ context }}
PLAYER SAYS: "{{ message }}"

Respond as the Master Merchant in 1-2 sentences, staying true to your enthusiastic and business-minded character.""",
        "parameters": [
            {
                "key": "message",
                "input_type": "text",
                "requirement": "user_prompt",
                "description": "The player's message to the Master Merchant"
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
            "Welcome, welcome! I am the Master Merchant, purveyor of fine goods!",
            "Quality merchandise at fair prices - that's my motto!",
            "I have potions, weapons, and rare artifacts from distant lands!"
        ]
        
        # Shop items for Master Merchant
        shop_items = [
            {"name": "Health Potion", "price": 50, "type": "consumable"},
            {"name": "Iron Sword", "price": 200, "type": "weapon"},
            {"name": "Leather Armor", "price": 150, "type": "armor"}
        ]
        
        super().__init__(x, y, "Master Merchant", dialog=dialog, 
                        asset_loader=asset_loader, has_shop=True, 
                        shop_items=shop_items, **kwargs)
    
    def _get_sprite_name(self) -> Optional[str]:
        """Get sprite name for Master Merchant"""
        return "npc_shopkeeper"
    
    def _create_generated_sprite(self, size: int):
        """Create Master Merchant sprite with gold colors and merchant hat"""
        import pygame
        
        self.sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Master Merchant appearance - gold with brown hat
        center = (size // 2, size // 2)
        pygame.draw.circle(self.sprite, (255, 215, 0), center, size // 3)  # Gold clothes
        pygame.draw.circle(self.sprite, (255, 255, 255), center, size // 4)  # Face
        pygame.draw.circle(self.sprite, (0, 0, 0), center, size // 3, 3)  # Border
        
        # Brown merchant hat
        pygame.draw.rect(self.sprite, (139, 69, 19), (size//2 - 12, 3, 24, 12))
        
        # Create direction sprites
        self.direction_sprites = [
            self.sprite,  # Down (0)
            pygame.transform.flip(self.sprite, True, False),  # Left (1)
            self.sprite,  # Up (2)
            self.sprite   # Right (3)
        ]
    
    def _get_npc_specific_responses(self) -> Dict[str, str]:
        """Master Merchant specific fallback responses"""
        return {
            "hello": "Welcome, welcome! I am the Master Merchant, purveyor of fine goods!",
            "who": "I am the Master Merchant, trader of exotic wares from distant lands.",
            "help": "I have potions, weapons, and rare artifacts! What catches your eye?",
            "buy": "Ah, excellent choice! My prices are fair for such quality goods.",
            "sell": "I might be interested in your wares. What do you have to offer?",
            "shop": "My shop has the finest merchandise this side of the kingdom!",
            "weapon": "I have blades forged by master smiths and enchanted by skilled mages.",
            "armor": "My armor will protect you from the fiercest of beasts!",
            "potion": "These potions are brewed from the rarest herbs and magical ingredients.",
            "price": "My prices are fair - quality goods deserve quality payment!",
            "trade": "I've traveled far and wide to bring you these exceptional items.",
            "bye": "Safe travels, and remember - quality goods at fair prices!",
            "default": "Business is good when adventurers like you visit my shop!"
        }
    
    def interact(self, player):
        """Handle Master Merchant specific interactions"""
        # Handle shop interaction
        if self.has_shop:
            print(f"🔧 [MasterMerchant] Opening shop for {self.name}")
            
            # Create shop if needed
            if not hasattr(self, 'shop') or not self.shop:
                try:
                    from ...ui.shop import Shop
                    self.shop = Shop(f"{self.name}'s Shop", self.asset_loader)
                except ImportError:
                    print(f"❌ [MasterMerchant] Could not import Shop class")
            
            if hasattr(self, 'shop') and self.shop:
                self.shop.open_shop()
                if player.game_log:
                    player.game_log.add_message(f"{self.name}: Welcome to my shop!", "dialog")
        
        # Update quest progress for talking to shopkeeper
        if hasattr(player, 'game') and hasattr(player.game, 'quest_manager'):
            player.game.quest_manager.update_quest_progress("talk", self.name)
        
        # Call parent interaction
        super().interact(player)