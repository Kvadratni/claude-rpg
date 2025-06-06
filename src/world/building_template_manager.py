"""
Building Template Manager - Manages building templates for settlement generation
Integrates with the building editor and provides templates for procedural generation.
"""

import json
import os
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class BuildingTemplate:
    """Represents a building template for settlement generation"""
    name: str
    width: int
    height: int
    building_type: str  # house, shop, inn, blacksmith, etc.
    tiles: List[List[int]]  # 2D array of tile types
    npc_spawns: List[Dict[str, Any]]  # NPC spawn points
    furniture_positions: List[Tuple[int, int, str]]  # Furniture positions
    description: str = ""
    min_settlement_size: str = "small"  # small, medium, large
    biome_compatibility: List[str] = None  # Compatible biomes
    importance: str = "medium"  # low, medium, high
    
    def __post_init__(self):
        if self.biome_compatibility is None:
            self.biome_compatibility = ["all"]


class BuildingTemplateManager:
    """Manages building templates for settlement generation"""
    
    def __init__(self, templates_dir: str = "building_templates"):
        self.templates_dir = templates_dir
        self.templates = {}  # Dict[str, BuildingTemplate]
        self.templates_by_type = {}  # Dict[str, List[BuildingTemplate]]
        
        # Ensure templates directory exists
        os.makedirs(templates_dir, exist_ok=True)
        
        # Load existing templates
        self.load_all_templates()
        
        # Create default templates if none exist
        if not self.templates:
            self.create_default_templates()
    
    def load_all_templates(self):
        """Load all building templates from the templates directory"""
        if not os.path.exists(self.templates_dir):
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_name = filename[:-5]  # Remove .json extension
                self.load_template(template_name)
        
        # Organize templates by type
        self.organize_templates_by_type()
        print(f"Loaded {len(self.templates)} building templates")
    
    def load_template(self, template_name: str) -> Optional[BuildingTemplate]:
        """Load a specific template from file"""
        filepath = os.path.join(self.templates_dir, f"{template_name}.json")
        
        if not os.path.exists(filepath):
            print(f"Template file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            template = BuildingTemplate(
                name=data['name'],
                width=data['width'],
                height=data['height'],
                building_type=data.get('building_type', 'generic'),
                tiles=data['tiles'],
                npc_spawns=data.get('npc_spawns', []),
                furniture_positions=data.get('furniture_positions', []),
                description=data.get('description', ''),
                min_settlement_size=data.get('min_settlement_size', 'small'),
                biome_compatibility=data.get('biome_compatibility', ['all']),
                importance=data.get('importance', 'medium')
            )
            
            self.templates[template_name] = template
            return template
            
        except Exception as e:
            print(f"Error loading template {template_name}: {e}")
            return None
    
    def save_template(self, template: BuildingTemplate):
        """Save a template to file"""
        filepath = os.path.join(self.templates_dir, f"{template.name}.json")
        
        data = {
            'name': template.name,
            'width': template.width,
            'height': template.height,
            'building_type': template.building_type,
            'tiles': template.tiles,
            'npc_spawns': template.npc_spawns,
            'furniture_positions': template.furniture_positions,
            'description': template.description,
            'min_settlement_size': template.min_settlement_size,
            'biome_compatibility': template.biome_compatibility,
            'importance': template.importance
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.templates[template.name] = template
            self.organize_templates_by_type()
            print(f"Template saved: {filepath}")
            
        except Exception as e:
            print(f"Error saving template {template.name}: {e}")
    
    def organize_templates_by_type(self):
        """Organize templates by building type for easier access"""
        self.templates_by_type = {}
        
        for template in self.templates.values():
            building_type = template.building_type
            if building_type not in self.templates_by_type:
                self.templates_by_type[building_type] = []
            self.templates_by_type[building_type].append(template)
    
    def get_templates_for_building_type(self, building_type: str, 
                                      settlement_size: str = "medium",
                                      biome: str = "plains") -> List[BuildingTemplate]:
        """Get suitable templates for a specific building type"""
        templates = self.templates_by_type.get(building_type, [])
        
        # Filter by settlement size and biome compatibility
        suitable_templates = []
        for template in templates:
            # Check settlement size compatibility
            size_compatible = self._is_size_compatible(template.min_settlement_size, settlement_size)
            
            # Check biome compatibility
            biome_compatible = (
                "all" in template.biome_compatibility or
                biome.lower() in [b.lower() for b in template.biome_compatibility]
            )
            
            if size_compatible and biome_compatible:
                suitable_templates.append(template)
        
        return suitable_templates
    
    def _is_size_compatible(self, min_size: str, settlement_size: str) -> bool:
        """Check if template size requirements are met"""
        size_hierarchy = {"small": 1, "medium": 2, "large": 3}
        min_level = size_hierarchy.get(min_size, 1)
        settlement_level = size_hierarchy.get(settlement_size, 2)
        return settlement_level >= min_level
    
    def select_random_template(self, building_type: str, 
                             settlement_size: str = "medium",
                             biome: str = "plains",
                             seed: int = None) -> Optional[BuildingTemplate]:
        """Select a random template for a building type"""
        suitable_templates = self.get_templates_for_building_type(
            building_type, settlement_size, biome
        )
        
        if not suitable_templates:
            # Fallback to any template of the type
            suitable_templates = self.templates_by_type.get(building_type, [])
        
        if not suitable_templates:
            return None
        
        # Use seed for deterministic selection if provided
        if seed is not None:
            random.seed(seed)
        
        return random.choice(suitable_templates)
    
    def create_default_templates(self):
        """Create default building templates"""
        print("Creating default building templates...")
        
        # Small House Template
        small_house = self._create_small_house_template()
        self.save_template(small_house)
        
        # Shop Template
        shop = self._create_shop_template()
        self.save_template(shop)
        
        # Inn Template
        inn = self._create_inn_template()
        self.save_template(inn)
        
        # Blacksmith Template
        blacksmith = self._create_blacksmith_template()
        self.save_template(blacksmith)
        
        # Large House Template
        large_house = self._create_large_house_template()
        self.save_template(large_house)
        
        print("Default templates created!")
    
    def _create_small_house_template(self) -> BuildingTemplate:
        """Create a small house template"""
        width, height = 7, 7
        
        # Create basic house layout
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    if x == width//2 and y == height-1:
                        row.append(2)  # Door
                    else:
                        row.append(1)  # Wall
                else:
                    row.append(3)  # Floor
            tiles.append(row)
        
        # Add NPC spawn point in center
        npc_spawns = [{
            'x': width//2,
            'y': height//2,
            'npc_type': 'villager',
            'name': 'Resident',
            'has_shop': False,
            'dialog': ['Welcome to my home!', 'It\'s a simple life here.'],
            'importance': 'low'
        }]
        
        return BuildingTemplate(
            name="small_house",
            width=width,
            height=height,
            building_type="house",
            tiles=tiles,
            npc_spawns=npc_spawns,
            furniture_positions=[(2, 2, 'bed'), (4, 2, 'table')],
            description="A small residential house for villagers",
            min_settlement_size="small",
            biome_compatibility=["all"],
            importance="low"
        )
    
    def _create_shop_template(self) -> BuildingTemplate:
        """Create a shop template"""
        width, height = 9, 7
        
        # Create shop layout
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    if x == width//2 and y == height-1:
                        row.append(2)  # Door
                    else:
                        row.append(1)  # Wall
                else:
                    row.append(3)  # Floor
            tiles.append(row)
        
        # Add counter (furniture)
        for x in range(2, 7):
            tiles[2][x] = 4  # Furniture (counter)
        
        # Add NPC spawn point behind counter
        npc_spawns = [{
            'x': width//2,
            'y': 1,
            'npc_type': 'merchant',
            'name': 'Shopkeeper',
            'has_shop': True,
            'dialog': ['Welcome to my shop!', 'I have the finest goods!', 'What can I get for you?'],
            'importance': 'high'
        }]
        
        return BuildingTemplate(
            name="general_shop",
            width=width,
            height=height,
            building_type="shop",
            tiles=tiles,
            npc_spawns=npc_spawns,
            furniture_positions=[(1, 4, 'shelf'), (7, 4, 'shelf'), (3, 5, 'chest')],
            description="A general store with merchant and goods",
            min_settlement_size="small",
            biome_compatibility=["all"],
            importance="high"
        )
    
    def _create_inn_template(self) -> BuildingTemplate:
        """Create an inn template"""
        width, height = 11, 9
        
        # Create inn layout
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    if x == width//2 and y == height-1:
                        row.append(2)  # Door
                    else:
                        row.append(1)  # Wall
                else:
                    row.append(3)  # Floor
            tiles.append(row)
        
        # Add internal walls to create rooms
        for y in range(1, height-1):
            tiles[y][6] = 1  # Vertical wall divider
        
        # Add door in internal wall
        tiles[4][6] = 2  # Door
        
        # Add NPC spawn point in main area
        npc_spawns = [{
            'x': 3,
            'y': 4,
            'npc_type': 'innkeeper',
            'name': 'Innkeeper',
            'has_shop': True,
            'dialog': ['Welcome to the inn!', 'Rest and refreshment await!', 'A room for the night?'],
            'importance': 'high'
        }]
        
        return BuildingTemplate(
            name="village_inn",
            width=width,
            height=height,
            building_type="inn",
            tiles=tiles,
            npc_spawns=npc_spawns,
            furniture_positions=[(2, 2, 'table'), (8, 2, 'bed'), (8, 6, 'bed'), (1, 6, 'bar')],
            description="A cozy inn with rooms and common area",
            min_settlement_size="medium",
            biome_compatibility=["all"],
            importance="high"
        )
    
    def _create_blacksmith_template(self) -> BuildingTemplate:
        """Create a blacksmith template"""
        width, height = 8, 8
        
        # Create blacksmith layout
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    if x == width//2 and y == height-1:
                        row.append(2)  # Door
                    else:
                        row.append(1)  # Wall
                else:
                    row.append(3)  # Floor
            tiles.append(row)
        
        # Add forge area
        tiles[2][2] = 4  # Forge (furniture)
        tiles[2][3] = 4  # Anvil (furniture)
        
        # Add NPC spawn point near forge
        npc_spawns = [{
            'x': 3,
            'y': 3,
            'npc_type': 'blacksmith',
            'name': 'Blacksmith',
            'has_shop': True,
            'dialog': ['The forge burns hot today!', 'I craft the finest weapons and armor!', 'What do you need forged?'],
            'importance': 'high'
        }]
        
        return BuildingTemplate(
            name="village_blacksmith",
            width=width,
            height=height,
            building_type="blacksmith",
            tiles=tiles,
            npc_spawns=npc_spawns,
            furniture_positions=[(5, 2, 'weapon_rack'), (6, 5, 'tool_rack'), (1, 5, 'storage')],
            description="A blacksmith shop with forge and crafting area",
            min_settlement_size="medium",
            biome_compatibility=["all"],
            importance="high"
        )
    
    def _create_large_house_template(self) -> BuildingTemplate:
        """Create a large house template"""
        width, height = 10, 8
        
        # Create large house layout
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    if x == width//2 and y == height-1:
                        row.append(2)  # Door
                    else:
                        row.append(1)  # Wall
                else:
                    row.append(3)  # Floor
            tiles.append(row)
        
        # Add internal walls to create multiple rooms
        for x in range(1, width-1):
            if x != 5:  # Leave opening
                tiles[4][x] = 1  # Horizontal wall divider
        
        # Add door in internal wall
        tiles[4][5] = 2  # Door
        
        # Add NPC spawn points
        npc_spawns = [
            {
                'x': 3,
                'y': 2,
                'npc_type': 'noble',
                'name': 'House Owner',
                'has_shop': False,
                'dialog': ['Welcome to my estate!', 'I am a person of some standing in this community.'],
                'importance': 'medium'
            },
            {
                'x': 7,
                'y': 6,
                'npc_type': 'servant',
                'name': 'House Servant',
                'has_shop': False,
                'dialog': ['Good day to you!', 'I maintain this fine household.'],
                'importance': 'low'
            }
        ]
        
        return BuildingTemplate(
            name="large_house",
            width=width,
            height=height,
            building_type="house",
            tiles=tiles,
            npc_spawns=npc_spawns,
            furniture_positions=[(2, 2, 'fancy_bed'), (7, 2, 'desk'), (2, 6, 'kitchen'), (8, 6, 'storage')],
            description="A large house for wealthy residents with multiple rooms",
            min_settlement_size="medium",
            biome_compatibility=["all"],
            importance="medium"
        )
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a template"""
        template = self.templates.get(template_name)
        if not template:
            return None
        
        return {
            'name': template.name,
            'size': f"{template.width}x{template.height}",
            'type': template.building_type,
            'description': template.description,
            'npc_count': len(template.npc_spawns),
            'min_settlement_size': template.min_settlement_size,
            'biome_compatibility': template.biome_compatibility,
            'importance': template.importance
        }
    
    def list_templates(self) -> List[str]:
        """Get list of all template names"""
        return list(self.templates.keys())
    
    def list_templates_by_type(self) -> Dict[str, List[str]]:
        """Get templates organized by building type"""
        result = {}
        for building_type, templates in self.templates_by_type.items():
            result[building_type] = [t.name for t in templates]
        return result
    
    def delete_template(self, template_name: str) -> bool:
        """Delete a template"""
        if template_name not in self.templates:
            return False
        
        # Remove from memory
        del self.templates[template_name]
        
        # Remove file
        filepath = os.path.join(self.templates_dir, f"{template_name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Reorganize
        self.organize_templates_by_type()
        return True


def main():
    """Test the building template manager"""
    manager = BuildingTemplateManager()
    
    print("Available templates:")
    for template_name in manager.list_templates():
        info = manager.get_template_info(template_name)
        print(f"  {template_name}: {info['size']} {info['type']} - {info['description']}")
    
    print("\nTemplates by type:")
    for building_type, template_names in manager.list_templates_by_type().items():
        print(f"  {building_type}: {', '.join(template_names)}")
    
    # Test template selection
    print("\nTesting template selection:")
    for building_type in ["house", "shop", "inn", "blacksmith"]:
        template = manager.select_random_template(building_type, "medium", "plains")
        if template:
            print(f"  {building_type}: Selected '{template.name}' ({template.width}x{template.height})")
        else:
            print(f"  {building_type}: No suitable template found")


if __name__ == "__main__":
    main()