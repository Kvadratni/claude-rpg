"""
AI Test World - Simplified test environment for AI NPCs
"""

import pygame
from .entities.npc import NPC
from .ai_integration import GameContext

class AITestWorld:
    """Simplified test world that bypasses complex template systems"""
    
    def __init__(self, game):
        self.game = game
        self.player = game.player
        
        # Simple 20x20 world with basic tiles
        self.world_map = [['grass' for _ in range(20)] for _ in range(20)]
        
        # Set up game context for AI first
        self.game_context = GameContext(self.player, self)
        
        # Create test NPCs with AI enabled
        self.create_test_npcs()
    
    def create_test_npcs(self):
        """Create test NPCs with different personalities"""
        self.npcs = []
        
        # Create a Village Elder with AI
        elder = NPC(x=5, y=5, name="Village Elder", 
                   dialog=["Greetings, traveler. I have much wisdom to share."],
                   asset_loader=self.game.asset_loader)
        
        # Create a Shopkeeper with AI
        shopkeeper = NPC(x=8, y=5, name="Master Merchant",
                        dialog=["Welcome to my shop! I have the finest wares."],
                        asset_loader=self.game.asset_loader,
                        has_shop=True)
        
        # Create a Guard with AI
        guard = NPC(x=5, y=8, name="Guard Captain",
                   dialog=["I protect this village from all threats."],
                   asset_loader=self.game.asset_loader)
        
        self.npcs = [elder, shopkeeper, guard]
        
        # Enable AI for all NPCs
        for npc in self.npcs:
            npc.enable_ai(self.player, self.game_context)
            print(f"🤖 AI enabled for {npc.name}")
    
    def get_tile_at(self, x, y):
        """Get tile type at coordinates"""
        if 0 <= x < 20 and 0 <= y < 20:
            return self.world_map[y][x]
        return 'void'
    
    def is_walkable(self, x, y):
        """Check if position is walkable"""
        tile = self.get_tile_at(x, y)
        return tile in ['grass', 'dirt', 'stone']
    
    def get_npcs_near(self, x, y, radius=3):
        """Get NPCs near a position"""
        nearby = []
        for npc in self.npcs:
            distance = ((npc.x - x) ** 2 + (npc.y - y) ** 2) ** 0.5
            if distance <= radius:
                nearby.append(npc)
        return nearby
    
    def render(self, screen):
        """Simple rendering for test world"""
        # Clear screen
        screen.fill((34, 139, 34))  # Forest green background
        
        # Draw simple grid
        tile_size = 32
        for y in range(20):
            for x in range(20):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                pygame.draw.rect(screen, (50, 205, 50), rect, 1)  # Light green grid
        
        # Draw NPCs
        for npc in self.npcs:
            npc_rect = pygame.Rect(npc.x * tile_size, npc.y * tile_size, tile_size, tile_size)
            if hasattr(npc, 'sprite') and npc.sprite:
                screen.blit(npc.sprite, npc_rect)
            else:
                pygame.draw.circle(screen, (255, 255, 0), npc_rect.center, tile_size // 3)
        
        # Draw player
        if self.player:
            player_rect = pygame.Rect(self.player.x * tile_size, self.player.y * tile_size, tile_size, tile_size)
            pygame.draw.circle(screen, (0, 100, 255), player_rect.center, tile_size // 3)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "AI Test World - Move with arrow keys",
            "Press SPACE near NPCs to interact",
            "AI NPCs will open chat windows",
            f"NPCs: {', '.join([npc.name for npc in self.npcs])}"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            screen.blit(text, (10, 10 + i * 25))
    
    def handle_event(self, event):
        """Handle events for test world"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Check for nearby NPCs to interact with
                nearby_npcs = self.get_npcs_near(self.player.x, self.player.y, 2)
                if nearby_npcs:
                    # Interact with the first nearby NPC
                    nearby_npcs[0].interact(self.player)
            elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                # Simple movement
                new_x, new_y = self.player.x, self.player.y
                
                if event.key == pygame.K_UP:
                    new_y -= 1
                elif event.key == pygame.K_DOWN:
                    new_y += 1
                elif event.key == pygame.K_LEFT:
                    new_x -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x += 1
                
                # Check bounds and walkability
                if 0 <= new_x < 20 and 0 <= new_y < 20 and self.is_walkable(new_x, new_y):
                    self.player.x = new_x
                    self.player.y = new_y
    
    def update(self, dt):
        """Update the test world"""
        # Simple update - could add NPC movement here
        pass
    
    # Add entity_manager attribute for compatibility
    @property
    def entity_manager(self):
        """Provide entity_manager interface for compatibility"""
        class MockEntityManager:
            def __init__(self, npcs):
                self.npcs = npcs
        
        return MockEntityManager(self.npcs)
EOF 2>&1
