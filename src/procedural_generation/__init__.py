"""
Procedural Generation System for Goose RPG

This package contains the complete procedural world generation system,
including biome generation, settlement placement, and building creation.

Main Components:
- ProceduralWorldGenerator: Main modular generation system
- BiomeGenerator: Biome map and tile generation
- SettlementGenerator: Settlement placement and building creation
- EntitySpawner: NPC, enemy, and object spawning
- Testing and debugging utilities

Usage:
    from procedural_generation import ProceduralWorldGenerator
    
    generator = ProceduralWorldGenerator(width=1000, height=1000, seed=12345)
    world_data = generator.generate_world(asset_loader)
    
    # Or use individual components:
    from procedural_generation import BiomeGenerator, SettlementGenerator
    
    biome_gen = BiomeGenerator(1000, 1000, 12345)
    biome_map = biome_gen.generate_biome_map()
"""

__version__ = "2.0.0"
__author__ = "Goose RPG Development Team"

# Import modular generator classes
from .src.modular_generator import ProceduralWorldGenerator, ProceduralGenerator
from .src.biome_generator import BiomeGenerator
from .src.settlement_generator import SettlementGenerator
from .src.entity_spawner import EntitySpawner

# Legacy compatibility - keep the old monolithic generator available
try:
    from .src.procedural_generator import ProceduralGenerator as LegacyProceduralGenerator
except ImportError:
    LegacyProceduralGenerator = None

__all__ = [
    'ProceduralWorldGenerator',
    'ProceduralGenerator',  # Main interface (alias to ProceduralWorldGenerator)
    'BiomeGenerator',
    'SettlementGenerator', 
    'EntitySpawner',
    'LegacyProceduralGenerator'
]