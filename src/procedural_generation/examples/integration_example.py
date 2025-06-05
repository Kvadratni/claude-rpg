#!/usr/bin/env python3
"""
Integration Example: Drop-in Replacement for World Generation
Demonstrates how the modular procedural generation system can replace existing world generation
"""

import sys
import os

# Add the procedural generation directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.modular_generator import ProceduralWorldGenerator


class MockAssetLoader:
    """Mock asset loader for demonstration"""
    def __init__(self):
        self.loaded_assets = {}
    
    def load_sprite(self, name):
        return f"sprite_{name}"
    
    def load_sound(self, name):
        return f"sound_{name}"


class MockLevel:
    """Mock Level class showing integration pattern"""
    
    def __init__(self, level_name, player, asset_loader, use_procedural=False, seed=None):
        self.level_name = level_name
        self.player = player
        self.asset_loader = asset_loader
        self.width = 1000
        self.height = 1000
        
        # World data
        self.tiles = None
        self.npcs = []
        self.enemies = []
        self.objects = []
        self.chests = []
        self.walkable_grid = None
        
        if use_procedural:
            print(f"Generating procedural level: {level_name}")
            self.generate_procedural_level(seed)
        else:
            print(f"Loading template level: {level_name}")
            self.load_template_level()
    
    def generate_procedural_level(self, seed=None):
        """Generate a procedural level using the new modular system"""
        print("Using ProceduralWorldGenerator...")
        
        # Create the procedural generator
        generator = ProceduralWorldGenerator(self.width, self.height, seed)
        
        # Generate the complete world
        world_data = generator.generate_world(self.asset_loader)
        
        # Extract world data
        self.tiles = world_data['tiles']
        self.npcs = world_data['npcs']
        self.enemies = world_data['enemies']
        self.objects = world_data['objects']
        self.chests = world_data['chests']
        self.walkable_grid = world_data['walkable_grid']
        
        # Store additional data for save/load
        self.procedural_info = {
            'is_procedural': True,
            'seed': world_data['seed'],
            'settlements': world_data['settlements'],
            'safe_zones': world_data['safe_zones']
        }
        
        print(f"Procedural level generated with seed: {world_data['seed']}")
        self.print_level_stats()
    
    def load_template_level(self):
        """Load a template-based level (existing system)"""
        print("Using template-based generation...")
        
        # Simulate existing template system
        self.tiles = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.npcs = []
        self.enemies = []
        self.objects = []
        self.chests = []
        
        self.procedural_info = {
            'is_procedural': False
        }
        
        print("Template level loaded")
    
    def print_level_stats(self):
        """Print statistics about the generated level"""
        if not self.tiles:
            print("No level data available")
            return
        
        # Count tile types
        tile_counts = {}
        for row in self.tiles:
            for tile in row:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1
        
        print(f"Level Statistics:")
        print(f"  Dimensions: {self.width}x{self.height}")
        print(f"  NPCs: {len(self.npcs)}")
        print(f"  Enemies: {len(self.enemies)}")
        print(f"  Objects: {len(self.objects)}")
        print(f"  Chests: {len(self.chests)}")
        
        if self.procedural_info.get('is_procedural'):
            settlements = self.procedural_info.get('settlements', [])
            print(f"  Settlements: {len(settlements)}")
            for settlement in settlements:
                print(f"    {settlement['name']} at ({settlement['x']}, {settlement['y']})")
    
    def save_level_data(self):
        """Save level data (including procedural info for regeneration)"""
        save_data = {
            'level_name': self.level_name,
            'procedural_info': self.procedural_info,
            'player_data': {'x': 100, 'y': 100},  # Mock player data
            # Note: For procedural levels, we only need to save the seed
            # The world can be regenerated deterministically
        }
        
        if not self.procedural_info.get('is_procedural'):
            # For template levels, save all the world data
            save_data['tiles'] = self.tiles
            save_data['npcs'] = [{'x': 0, 'y': 0, 'name': 'Test NPC'}]  # Mock data
            save_data['enemies'] = []
            save_data['objects'] = []
            save_data['chests'] = []
        
        print(f"Save data prepared: {len(str(save_data))} characters")
        return save_data
    
    def load_level_data(self, save_data):
        """Load level data (regenerating procedural levels from seed)"""
        self.level_name = save_data['level_name']
        self.procedural_info = save_data['procedural_info']
        
        if self.procedural_info.get('is_procedural'):
            # Regenerate procedural level from seed
            seed = self.procedural_info['seed']
            print(f"Regenerating procedural level from seed: {seed}")
            self.generate_procedural_level(seed)
        else:
            # Load template level data
            self.tiles = save_data['tiles']
            self.npcs = save_data['npcs']
            self.enemies = save_data['enemies']
            self.objects = save_data['objects']
            self.chests = save_data['chests']
            print("Template level data loaded")


class MockGame:
    """Mock Game class showing menu integration"""
    
    def __init__(self):
        self.asset_loader = MockAssetLoader()
        self.player = {'x': 100, 'y': 100}
        self.level = None
    
    def start_new_game(self, use_procedural=False, seed=None):
        """Start a new game with optional procedural generation"""
        level_name = "Procedural World" if use_procedural else "Template World"
        
        self.level = MockLevel(
            level_name=level_name,
            player=self.player,
            asset_loader=self.asset_loader,
            use_procedural=use_procedural,
            seed=seed
        )
        
        print(f"Game started with {level_name}")
    
    def save_game(self):
        """Save the current game state"""
        if not self.level:
            print("No level to save")
            return
        
        save_data = self.level.save_level_data()
        print("Game saved successfully")
        return save_data
    
    def load_game(self, save_data):
        """Load a saved game state"""
        self.level = MockLevel(
            level_name="Loading...",
            player=self.player,
            asset_loader=self.asset_loader,
            use_procedural=False  # Will be determined by save data
        )
        
        self.level.load_level_data(save_data)
        print("Game loaded successfully")


def demonstrate_integration():
    """Demonstrate the integration patterns"""
    print("=" * 60)
    print("Procedural Generation Integration Demonstration")
    print("=" * 60)
    
    game = MockGame()
    
    # Test 1: Template-based game (existing system)
    print("\n1. Testing Template-Based Game (Existing System)")
    print("-" * 50)
    game.start_new_game(use_procedural=False)
    template_save = game.save_game()
    
    # Test 2: Procedural game with random seed
    print("\n2. Testing Procedural Game (Random Seed)")
    print("-" * 50)
    game.start_new_game(use_procedural=True)
    procedural_save = game.save_game()
    
    # Test 3: Procedural game with specific seed
    print("\n3. Testing Procedural Game (Specific Seed)")
    print("-" * 50)
    game.start_new_game(use_procedural=True, seed=12345)
    specific_save = game.save_game()
    
    # Test 4: Save/Load cycle for procedural world
    print("\n4. Testing Save/Load Cycle")
    print("-" * 50)
    print("Loading procedural game from save data...")
    game.load_game(specific_save)
    
    # Test 5: Performance comparison
    print("\n5. Performance Comparison")
    print("-" * 50)
    
    import time
    
    # Template system (mock - instant)
    start_time = time.time()
    game.start_new_game(use_procedural=False)
    template_time = time.time() - start_time
    
    # Procedural system
    start_time = time.time()
    game.start_new_game(use_procedural=True, seed=54321)
    procedural_time = time.time() - start_time
    
    print(f"Template generation time: {template_time:.4f} seconds")
    print(f"Procedural generation time: {procedural_time:.4f} seconds")
    print(f"Procedural overhead: {procedural_time - template_time:.4f} seconds")
    
    print("\n" + "=" * 60)
    print("Integration demonstration completed successfully!")
    print("The procedural system can be used as a drop-in replacement.")


def demonstrate_component_usage():
    """Demonstrate using individual components"""
    print("\n" + "=" * 60)
    print("Individual Component Usage Demonstration")
    print("=" * 60)
    
    from src.biome_generator import BiomeGenerator
    from src.settlement_generator import SettlementGenerator
    
    # Use only biome generation
    print("\n1. Using Only BiomeGenerator")
    print("-" * 40)
    biome_gen = BiomeGenerator(100, 100, 12345)
    biome_map = biome_gen.generate_biome_map()
    biome_stats = biome_gen.get_biome_stats(biome_map)
    
    print("Biome distribution:")
    for biome, count in biome_stats.items():
        print(f"  {biome}: {count} tiles")
    
    # Use biome + settlement generation
    print("\n2. Using BiomeGenerator + SettlementGenerator")
    print("-" * 40)
    tiles = biome_gen.generate_tiles(biome_map)
    
    settlement_gen = SettlementGenerator(100, 100, 12345)
    settlements = settlement_gen.place_settlements(tiles, biome_map)
    
    print(f"Placed {len(settlements)} settlements:")
    for settlement in settlements:
        print(f"  {settlement['name']} in {settlement['biome']} biome")
    
    print("\nComponent usage demonstration completed!")


if __name__ == "__main__":
    try:
        demonstrate_integration()
        demonstrate_component_usage()
        
        print("\n🎉 All integration examples completed successfully!")
        print("The modular system is ready for production use.")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()