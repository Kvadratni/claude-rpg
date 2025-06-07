"""
Entities module for the RPG

This module contains all game entities including the base Entity class,
NPCs, enemies, items, chests, and furniture.
"""

from .base import Entity
from .npc import NPC
from .enemy import Enemy, RangedEnemy
from .item import Item
from .chest import Chest
from .furniture import Furniture

__all__ = [
    'Entity',
    'NPC', 
    'Enemy',
    'RangedEnemy',
    'Item',
    'Chest',
    'Furniture'
]
