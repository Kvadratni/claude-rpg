"""
Procedural Generation System for Goose RPG

This package contains the complete procedural world generation system,
including biome generation, settlement placement, and building creation.

Main Components:
- ProceduralGenerator: Core generation system
- Settlement templates and building generation
- Biome-based entity spawning
- Testing and debugging utilities

Usage:
    from procedural_generation.src.procedural_generator import ProceduralGenerator
    
    generator = ProceduralGenerator(width=200, height=200, seed=12345)
    tiles = generator.generate_tiles()
    settlements = generator.place_settlements(tiles)
"""

__version__ = "1.0.0"
__author__ = "Goose RPG Development Team"

from .src.procedural_generator import ProceduralGenerator

__all__ = ['ProceduralGenerator']