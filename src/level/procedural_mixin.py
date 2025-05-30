"""
Procedural Generation Mixin for Level System
Adds procedural world generation capability to the refactored Level architecture
"""

import random
from ..procedural_generation import ProceduralWorldGenerator


class ProceduralGenerationMixin:
    """
    Mixin to add procedural generation capability to Level class
    Integrates with the existing mixin-based Level architecture
    """
    
    def generate_procedural_level(self, seed=None):
        """
        Generate a procedural level using the modular system
        
        Args:
            seed: Random seed for deterministic generation
        """
        print(f"Generating procedural level with seed: {seed}")
        
        # Create the procedural generator
        generator = ProceduralWorldGenerator(self.width, self.height, seed)
        
        # Generate the complete world
        world_data = generator.generate_world(self.asset_loader)
        
        # Replace template-generated data with procedural data
        self.tiles = world_data['tiles']
        
        # Clear existing entities before adding procedural ones
        if hasattr(self, 'npcs'):
            self.npcs.clear()
        else:
            self.npcs = []
            
        if hasattr(self, 'enemies'):
            self.enemies.clear()
        else:
            self.enemies = []
            
        if hasattr(self, 'objects'):
            self.objects.clear()
        else:
            self.objects = []
            
        if hasattr(self, 'items'):
            self.items.clear()
        else:
            self.items = []
            
        if hasattr(self, 'chests'):
            self.chests.clear()
        else:
            self.chests = []
        
        # Add procedural entities
        self.npcs.extend(world_data['npcs'])
        self.enemies.extend(world_data['enemies'])
        self.objects.extend(world_data['objects'])
        self.chests.extend(world_data['chests'])  # Chests go to chests list
        
        # Update walkable grid
        self.walkable = world_data['walkable_grid']
        
        # Store procedural info for save/load
        self.procedural_info = {
            'is_procedural': True,
            'seed': world_data['seed'],
            'settlements': world_data['settlements'],
            'safe_zones': world_data['safe_zones'],
            'player_spawn': world_data.get('player_spawn', (self.width // 2, self.height // 2))
        }
        
        # Regenerate heightmap for new tiles
        if hasattr(self, 'generate_heightmap'):
            self.heightmap = self.generate_heightmap()
        
        # Update tile sprites for new tiles
        if hasattr(self, 'create_tile_sprites'):
            self.create_tile_sprites()
        
        # Log generation results
        stats = generator.get_world_stats()
        print(f"Procedural world generated:")
        print(f"  Seed: {world_data['seed']}")
        print(f"  Settlements: {len(world_data['settlements'])}")
        print(f"  NPCs: {len(world_data['npcs'])}")
        print(f"  Enemies: {len(world_data['enemies'])}")
        print(f"  Objects: {len(world_data['objects'])}")
        print(f"  Chests: {len(world_data['chests'])}")
        
        # Add message to game log if available
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'game_log'):
            self.game.game_log.add_message(f"Procedural world generated (Seed: {world_data['seed']})", "system")
            self.game.game_log.add_message(f"Discovered {len(world_data['settlements'])} settlements", "exploration")
    
    def is_procedural_level(self):
        """
        Check if this level was procedurally generated
        
        Returns:
            bool: True if procedural, False if template-based
        """
        return hasattr(self, 'procedural_info') and self.procedural_info.get('is_procedural', False)
    
    def get_procedural_seed(self):
        """
        Get the seed used for procedural generation
        
        Returns:
            int or None: Seed if procedural, None if template-based
        """
        if self.is_procedural_level():
            return self.procedural_info.get('seed')
        return None
    
    def get_procedural_settlements(self):
        """
        Get information about procedurally generated settlements
        
        Returns:
            list: Settlement information if procedural, empty list otherwise
        """
        if self.is_procedural_level():
            return self.procedural_info.get('settlements', [])
        return []
    
    def regenerate_procedural_level(self):
        """
        Regenerate the procedural level with the same seed
        Useful for debugging or resetting the world
        """
        if self.is_procedural_level():
            seed = self.get_procedural_seed()
            print(f"Regenerating procedural level with seed: {seed}")
            self.generate_procedural_level(seed)
        else:
            print("Cannot regenerate: Level is not procedurally generated")
    
    def get_procedural_save_data(self):
        """
        Get save data for procedural levels (minimal - just seed)
        
        Returns:
            dict: Procedural save data
        """
        if self.is_procedural_level():
            return {
                'procedural_info': self.procedural_info
            }
        return {}
    
    def load_procedural_save_data(self, save_data):
        """
        Load procedural level from save data
        
        Args:
            save_data: Save data containing procedural info
        """
        if 'procedural_info' in save_data:
            procedural_info = save_data['procedural_info']
            if procedural_info.get('is_procedural'):
                seed = procedural_info.get('seed')
                print(f"Loading procedural level from save data (seed: {seed})")
                self.generate_procedural_level(seed)
                return True
        return False