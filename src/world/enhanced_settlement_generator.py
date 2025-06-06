"""
Enhanced Settlement Generator - Creates varied settlement layouts using building templates
Supports non-square settlements, multiple rows, and proper building template integration.
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from .building_template_manager import BuildingTemplateManager, BuildingTemplate


@dataclass
class SettlementBuilding:
    """Represents a placed building in a settlement"""
    template: BuildingTemplate
    x: int  # World position
    y: int  # World position
    rotation: int = 0  # 0, 90, 180, 270 degrees
    npc_assignments: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.npc_assignments is None:
            self.npc_assignments = []


@dataclass
class SettlementLayout:
    """Defines the overall layout structure of a settlement"""
    name: str
    shape: str  # "rectangular", "circular", "organic", "linear"
    min_size: Tuple[int, int]  # Minimum width, height
    max_size: Tuple[int, int]  # Maximum width, height
    building_density: float  # 0.0 to 1.0
    path_style: str  # "grid", "radial", "organic"
    central_feature: Optional[str] = None  # "plaza", "well", "market"


class EnhancedSettlementGenerator:
    """Enhanced settlement generator with template support and varied layouts"""
    
    # Define settlement layout templates
    LAYOUT_TEMPLATES = {
        'small_village': SettlementLayout(
            name="Small Village",
            shape="organic",
            min_size=(20, 20),
            max_size=(30, 30),
            building_density=0.3,
            path_style="organic",
            central_feature="well"
        ),
        'medium_village': SettlementLayout(
            name="Medium Village",
            shape="rectangular",
            min_size=(25, 25),
            max_size=(40, 35),
            building_density=0.4,
            path_style="grid",
            central_feature="plaza"
        ),
        'large_village': SettlementLayout(
            name="Large Village",
            shape="rectangular",
            min_size=(35, 30),
            max_size=(50, 45),
            building_density=0.5,
            path_style="grid",
            central_feature="market"
        ),
        'town': SettlementLayout(
            name="Town",
            shape="rectangular",
            min_size=(40, 40),
            max_size=(60, 55),
            building_density=0.6,
            path_style="grid",
            central_feature="plaza"
        ),
        'linear_outpost': SettlementLayout(
            name="Linear Outpost",
            shape="linear",
            min_size=(30, 15),
            max_size=(50, 20),
            building_density=0.4,
            path_style="linear",
            central_feature=None
        ),
        'circular_camp': SettlementLayout(
            name="Circular Camp",
            shape="circular",
            min_size=(25, 25),
            max_size=(35, 35),
            building_density=0.4,
            path_style="radial",
            central_feature="fire_pit"
        )
    }
    
    # Settlement type to layout mapping
    SETTLEMENT_LAYOUTS = {
        'VILLAGE': ['small_village', 'medium_village', 'large_village'],
        'TOWN': ['large_village', 'town'],
        'DESERT_OUTPOST': ['linear_outpost', 'circular_camp'],
        'SNOW_SETTLEMENT': ['circular_camp', 'linear_outpost'],
        'SWAMP_VILLAGE': ['linear_outpost', 'small_village'],
        'FOREST_CAMP': ['circular_camp', 'small_village'],
        'MINING_CAMP': ['linear_outpost', 'medium_village'],
        'FISHING_VILLAGE': ['linear_outpost', 'medium_village']
    }
    
    # Building type requirements by settlement type
    BUILDING_REQUIREMENTS = {
        'VILLAGE': {
            'required': ['house', 'shop'],
            'preferred': ['inn', 'blacksmith'],
            'optional': ['house', 'shop', 'generic']  # Allow duplicates
        },
        'TOWN': {
            'required': ['house', 'shop', 'inn', 'blacksmith'],
            'preferred': ['house', 'shop', 'generic'],  # Use available types
            'optional': ['house', 'shop', 'inn', 'blacksmith', 'generic']
        },
        'DESERT_OUTPOST': {
            'required': ['house', 'shop'],
            'preferred': ['house'],
            'optional': ['shop', 'generic']
        },
        'SNOW_SETTLEMENT': {
            'required': ['house', 'inn'],
            'preferred': ['shop'],
            'optional': ['house', 'generic']
        },
        'SWAMP_VILLAGE': {
            'required': ['house', 'shop'],
            'preferred': ['inn'],
            'optional': ['house', 'generic']
        },
        'FOREST_CAMP': {
            'required': ['house', 'shop'],
            'preferred': ['inn'],
            'optional': ['house', 'generic']
        },
        'MINING_CAMP': {
            'required': ['house', 'blacksmith'],
            'preferred': ['shop'],
            'optional': ['house', 'generic']
        },
        'FISHING_VILLAGE': {
            'required': ['house', 'shop'],
            'preferred': ['inn'],
            'optional': ['house', 'generic']
        }
    }
    
    def __init__(self, world_seed: int, templates_dir: str = "building_templates"):
        self.world_seed = world_seed
        self.building_manager = BuildingTemplateManager(templates_dir)
        self.placed_settlements = {}
        
    def generate_settlement(self, chunk_x: int, chunk_y: int, settlement_type: str, 
                          biome: str = "plains") -> Dict[str, Any]:
        """
        Generate an enhanced settlement with varied layout and building templates
        
        Args:
            chunk_x, chunk_y: Chunk coordinates
            settlement_type: Type of settlement
            biome: Biome type for template selection
            
        Returns:
            Settlement data with buildings, NPCs, and layout information
        """
        # Create deterministic random for this settlement
        settlement_seed = hash((self.world_seed, chunk_x, chunk_y, settlement_type)) % (2**31)
        settlement_random = random.Random(settlement_seed)
        
        # Select layout template
        layout_options = self.SETTLEMENT_LAYOUTS.get(settlement_type, ['medium_village'])
        layout_name = settlement_random.choice(layout_options)
        layout = self.LAYOUT_TEMPLATES[layout_name]
        
        # Determine settlement size
        width = settlement_random.randint(layout.min_size[0], layout.max_size[0])
        height = settlement_random.randint(layout.min_size[1], layout.max_size[1])
        
        # Calculate world position within chunk
        chunk_size = 64
        margin = 5
        max_width = chunk_size - 2 * margin
        max_height = chunk_size - 2 * margin
        
        # Ensure settlement fits in chunk with margin
        actual_width = min(width, max_width)
        actual_height = min(height, max_height)
        
        world_x = chunk_x * chunk_size + settlement_random.randint(margin, chunk_size - actual_width - margin)
        world_y = chunk_y * chunk_size + settlement_random.randint(margin, chunk_size - actual_height - margin)
        
        print(f"  🏘️  Generating {settlement_type} using {layout_name} layout ({width}x{height}) in {biome}")
        
        # Generate building placement areas based on layout shape
        building_areas = self._generate_building_areas(
            layout, width, height, settlement_random
        )
        
        # Select and place buildings
        buildings = self._place_buildings(
            settlement_type, building_areas, biome, settlement_random
        )
        
        # Generate pathways with biome-specific tiles
        pathways = self._generate_pathways(
            layout, width, height, buildings, settlement_random, biome
        )
        
        # Create central feature if specified
        central_feature = None
        if layout.central_feature:
            central_feature = self._create_central_feature(
                layout.central_feature, width, height, settlement_random
            )
        
        # Assign NPCs to buildings
        npcs = self._assign_npcs_to_buildings(buildings, settlement_type, settlement_random)
        
        settlement_data = {
            'type': settlement_type,
            'layout': layout_name,
            'chunk_x': chunk_x,
            'chunk_y': chunk_y,
            'world_x': world_x,
            'world_y': world_y,
            'width': actual_width,
            'height': actual_height,
            'shape': layout.shape,
            'buildings': [self._building_to_dict(b, world_x, world_y) for b in buildings],
            'pathways': pathways,
            'central_feature': central_feature,
            'npcs': npcs,
            'biome': biome,
            'total_buildings': len(buildings),
            'total_npcs': len(npcs),
            'shops': len([npc for npc in npcs if npc.get('has_shop', False)])
        }
        
        self.placed_settlements[(chunk_x, chunk_y)] = settlement_data
        print(f"  ✅ Settlement complete: {len(buildings)} buildings, {len(npcs)} NPCs, {len(pathways)} ground tiles")
        
        return settlement_data
    
    def _generate_building_areas(self, layout: SettlementLayout, width: int, height: int, 
                               rng: random.Random) -> List[Tuple[int, int, int, int]]:
        """Generate areas where buildings can be placed based on layout shape"""
        areas = []
        
        if layout.shape == "rectangular":
            # Grid-based rectangular layout with proper spacing
            rows = max(2, height // 20)  # Even more spacing
            cols = max(2, width // 20)   # Even more spacing
            
            # Calculate actual spacing needed
            row_height = height // rows
            col_width = width // cols
            
            for row in range(rows):
                for col in range(cols):
                    # Calculate area bounds with guaranteed non-overlap
                    area_width = min(15, col_width - 5)  # Leave 5-unit buffer
                    area_height = min(15, row_height - 5)  # Leave 5-unit buffer
                    
                    # Position with proper spacing
                    x = col * col_width + 3
                    y = row * row_height + 3
                    
                    # Ensure area stays within bounds
                    if x + area_width <= width - 3 and y + area_height <= height - 3:
                        areas.append((x, y, area_width, area_height))
        
        elif layout.shape == "circular":
            # Circular/radial layout
            center_x, center_y = width // 2, height // 2
            radius = min(width, height) // 2 - 3
            
            # Create concentric rings
            rings = max(2, radius // 8)
            for ring in range(rings):
                ring_radius = (ring + 1) * (radius // rings)
                buildings_in_ring = max(4, int(2 * math.pi * ring_radius / 10))
                
                for i in range(buildings_in_ring):
                    angle = (2 * math.pi * i) / buildings_in_ring
                    x = int(center_x + ring_radius * math.cos(angle))
                    y = int(center_y + ring_radius * math.sin(angle))
                    
                    # Ensure within bounds
                    if 2 <= x <= width - 12 and 2 <= y <= height - 12:
                        areas.append((x, y, 10, 10))
        
        elif layout.shape == "linear":
            # Linear layout along main axis
            if width > height:  # Horizontal linear
                rows = max(2, height // 10)
                buildings_per_row = width // 8
                
                for row in range(rows):
                    y = 2 + row * (height - 4) // max(1, rows - 1)
                    for i in range(buildings_per_row):
                        x = 2 + i * (width - 4) // max(1, buildings_per_row - 1)
                        if x <= width - 12:
                            areas.append((x, y, 10, 8))
            else:  # Vertical linear
                cols = max(2, width // 10)
                buildings_per_col = height // 8
                
                for col in range(cols):
                    x = 2 + col * (width - 4) // max(1, cols - 1)
                    for i in range(buildings_per_col):
                        y = 2 + i * (height - 4) // max(1, buildings_per_col - 1)
                        if y <= height - 12:
                            areas.append((x, y, 8, 10))
        
        elif layout.shape == "organic":
            # Organic/irregular layout with better spacing
            num_clusters = min(rng.randint(2, 4), len(building_areas) if hasattr(self, 'building_areas') else 4)
            min_distance = 15  # Minimum distance between buildings
            
            for cluster_idx in range(num_clusters):
                # Create cluster center with better spacing
                attempts = 0
                while attempts < 50:
                    # Ensure valid range for random generation
                    max_x = max(8, width - 15)
                    max_y = max(8, height - 15)
                    
                    if max_x <= 8:
                        cluster_x = width // 2  # Use center if too small
                    else:
                        cluster_x = rng.randint(8, max_x)
                    
                    if max_y <= 8:
                        cluster_y = height // 2  # Use center if too small
                    else:
                        cluster_y = rng.randint(8, max_y)
                    
                    # Check distance from existing areas
                    too_close = False
                    for existing_x, existing_y, _, _ in areas:
                        distance = math.sqrt((cluster_x - existing_x)**2 + (cluster_y - existing_y)**2)
                        if distance < min_distance:
                            too_close = True
                            break
                    
                    if not too_close:
                        break
                    attempts += 1
                
                # Add buildings around cluster center with spacing
                cluster_buildings = rng.randint(1, 3)  # 1-3 buildings per cluster
                for building_idx in range(cluster_buildings):
                    if building_idx == 0:
                        # First building at cluster center
                        x, y = cluster_x, cluster_y
                    else:
                        # Additional buildings with spacing
                        attempts = 0
                        while attempts < 30:
                            offset_x = rng.randint(-12, 12)
                            offset_y = rng.randint(-12, 12)
                            
                            x = cluster_x + offset_x
                            y = cluster_y + offset_y
                            
                            # Check bounds
                            if not (5 <= x <= width - 15 and 5 <= y <= height - 15):
                                attempts += 1
                                continue
                            
                            # Check distance from existing buildings
                            too_close = False
                            for existing_x, existing_y, _, _ in areas:
                                distance = math.sqrt((x - existing_x)**2 + (y - existing_y)**2)
                                if distance < min_distance:
                                    too_close = True
                                    break
                            
                            if not too_close:
                                break
                            attempts += 1
                        
                        # If we couldn't find a good spot, skip this building
                        if attempts >= 30:
                            continue
                    
                    # Add the building area
                    if 5 <= x <= width - 15 and 5 <= y <= height - 15:
                        areas.append((x, y, 12, 12))
        
        return areas
    
    def _place_buildings(self, settlement_type: str, building_areas: List[Tuple[int, int, int, int]], 
                        biome: str, rng: random.Random) -> List[SettlementBuilding]:
        """Place buildings in the designated areas using templates"""
        buildings = []
        requirements = self.BUILDING_REQUIREMENTS.get(settlement_type, {
            'required': ['house'], 'preferred': ['shop'], 'optional': []
        })
        
        # Determine settlement size category for template selection
        total_areas = len(building_areas)
        if total_areas <= 6:
            size_category = "small"
        elif total_areas <= 12:
            size_category = "medium"
        else:
            size_category = "large"
        
        # First, place required buildings
        building_types_to_place = []
        
        # Add required buildings (at least one of each)
        for building_type in requirements['required']:
            building_types_to_place.append(building_type)
        
        # Add preferred buildings (based on available space)
        preferred_count = min(len(requirements['preferred']), max(0, total_areas - len(requirements['required'])))
        selected_preferred = rng.sample(requirements['preferred'], min(preferred_count, len(requirements['preferred'])))
        building_types_to_place.extend(selected_preferred)
        
        # Fill remaining spaces with optional buildings and duplicates
        remaining_spaces = total_areas - len(building_types_to_place)
        if remaining_spaces > 0:
            # Add some optional buildings
            optional_count = min(len(requirements['optional']), remaining_spaces // 2)
            if optional_count > 0:
                selected_optional = rng.sample(requirements['optional'], optional_count)
                building_types_to_place.extend(selected_optional)
            
            # Fill remaining with duplicates of common types
            common_types = ['house', 'shop', 'workshop']
            while len(building_types_to_place) < total_areas:
                building_types_to_place.append(rng.choice(common_types))
        
        # Shuffle building placement order
        rng.shuffle(building_types_to_place)
        
        # Place buildings in areas
        placed_count = 0
        for i, (area_x, area_y, area_w, area_h) in enumerate(building_areas):
            if placed_count >= len(building_types_to_place):
                break
            
            building_type = building_types_to_place[placed_count]
            
            # Select appropriate template
            template = self.building_manager.select_random_template(
                building_type, size_category, biome, 
                seed=hash((settlement_type, i, building_type)) % (2**31)
            )
            
            if template:
                # Check if template fits in area (with some flexibility)
                if template.width <= area_w + 4 and template.height <= area_h + 4:
                    building = SettlementBuilding(
                        template=template,
                        x=area_x,
                        y=area_y,
                        rotation=rng.choice([0, 90, 180, 270]) if rng.random() < 0.1 else 0
                    )
                    buildings.append(building)
                    placed_count += 1
                else:
                    # Try to find a smaller template of the same type
                    smaller_templates = [
                        t for t in self.building_manager.get_templates_for_building_type(building_type, "small", biome)
                        if t.width <= area_w + 4 and t.height <= area_h + 4
                    ]
                    
                    if smaller_templates:
                        template = rng.choice(smaller_templates)
                        building = SettlementBuilding(
                            template=template,
                            x=area_x,
                            y=area_y,
                            rotation=0
                        )
                        buildings.append(building)
                        placed_count += 1
        
        print(f"    🏠 Placed {len(buildings)} buildings from {len(building_areas)} areas")
        return buildings
    
    def _generate_pathways(self, layout: SettlementLayout, width: int, height: int, 
                          buildings: List[SettlementBuilding], rng: random.Random, biome: str = "plains") -> List[Tuple[int, int, int]]:
        """Generate pathways and ground preparation with tile types"""
        pathways = []  # List of (x, y, tile_type) tuples
        
        # Get biome-appropriate tiles
        ground_tile, path_tile, plaza_tile = self._get_biome_tiles(biome)
        
        # First, prepare the ground around buildings
        for building in buildings:
            # Create a cleared area around each building
            padding = 2
            for y in range(max(0, building.y - padding), min(height, building.y + building.template.height + padding)):
                for x in range(max(0, building.x - padding), min(width, building.x + building.template.width + padding)):
                    # Don't overwrite building tiles, just prepare ground
                    if not (building.x <= x < building.x + building.template.width and 
                           building.y <= y < building.y + building.template.height):
                        pathways.append((x, y, ground_tile))  # Biome-appropriate ground
        
        # Generate main pathways based on layout style
        if layout.path_style == "grid":
            # Grid-based pathways with better spacing
            main_paths_x = []
            main_paths_y = []
            
            # Create main horizontal paths
            for y in range(3, height, max(8, height // 4)):
                main_paths_y.append(y)
                for x in range(width):
                    pathways.append((x, y, path_tile))  # Biome-appropriate path
                    # Add adjacent tiles for wider paths
                    if y + 1 < height:
                        pathways.append((x, y + 1, path_tile))
            
            # Create main vertical paths
            for x in range(3, width, max(8, width // 4)):
                main_paths_x.append(x)
                for y in range(height):
                    pathways.append((x, y, path_tile))  # Biome-appropriate path
                    # Add adjacent tiles for wider paths
                    if x + 1 < width:
                        pathways.append((x + 1, y, path_tile))
            
            # Connect buildings to nearest main paths
            for building in buildings:
                building_center_x = building.x + building.template.width // 2
                building_center_y = building.y + building.template.height // 2
                
                # Find nearest main path
                nearest_path_x = min(main_paths_x, key=lambda px: abs(px - building_center_x), default=building_center_x)
                nearest_path_y = min(main_paths_y, key=lambda py: abs(py - building_center_y), default=building_center_y)
                
                # Connect to nearest vertical path
                for x in range(min(building_center_x, nearest_path_x), max(building_center_x, nearest_path_x) + 1):
                    pathways.append((x, building_center_y, path_tile))
                
                # Connect to nearest horizontal path
                for y in range(min(building_center_y, nearest_path_y), max(building_center_y, nearest_path_y) + 1):
                    pathways.append((building_center_x, y, path_tile))
        
        elif layout.path_style == "radial":
            # Radial pathways from center
            center_x, center_y = width // 2, height // 2
            
            # Create central plaza area
            plaza_size = 4
            for y in range(center_y - plaza_size, center_y + plaza_size):
                for x in range(center_x - plaza_size, center_x + plaza_size):
                    if 0 <= x < width and 0 <= y < height:
                        pathways.append((x, y, plaza_tile))  # Biome-appropriate plaza
            
            # Add radial spokes to buildings
            for building in buildings:
                building_center_x = building.x + building.template.width // 2
                building_center_y = building.y + building.template.height // 2
                
                # Create path from center to building
                dx = building_center_x - center_x
                dy = building_center_y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    steps = int(distance)
                    for step in range(steps):
                        t = step / max(1, steps - 1)
                        x = int(center_x + t * dx)
                        y = int(center_y + t * dy)
                        if 0 <= x < width and 0 <= y < height:
                            pathways.append((x, y, path_tile))  # Biome-appropriate path
            
            # Add concentric rings
            for radius in range(8, min(width, height) // 2, 6):
                circumference = int(2 * math.pi * radius)
                for i in range(0, circumference, 2):
                    angle = (2 * math.pi * i) / circumference
                    x = int(center_x + radius * math.cos(angle))
                    y = int(center_y + radius * math.sin(angle))
                    if 0 <= x < width and 0 <= y < height:
                        pathways.append((x, y, path_tile))  # Biome-appropriate path
        
        elif layout.path_style == "linear":
            # Linear main path with connections
            if width > height:  # Horizontal main path
                main_y = height // 2
                # Create wide main path
                for x in range(width):
                    pathways.append((x, main_y, path_tile))  # Biome-appropriate path
                    if main_y + 1 < height:
                        pathways.append((x, main_y + 1, path_tile))
                    if main_y - 1 >= 0:
                        pathways.append((x, main_y - 1, path_tile))
                
                # Connect buildings to main path
                for building in buildings:
                    building_center_x = building.x + building.template.width // 2
                    building_center_y = building.y + building.template.height // 2
                    
                    # Create perpendicular connection
                    for y in range(min(building_center_y, main_y), max(building_center_y, main_y) + 1):
                        pathways.append((building_center_x, y, path_tile))
            else:  # Vertical main path
                main_x = width // 2
                # Create wide main path
                for y in range(height):
                    pathways.append((main_x, y, path_tile))  # Biome-appropriate path
                    if main_x + 1 < width:
                        pathways.append((main_x + 1, y, path_tile))
                    if main_x - 1 >= 0:
                        pathways.append((main_x - 1, y, path_tile))
                
                # Connect buildings to main path
                for building in buildings:
                    building_center_x = building.x + building.template.width // 2
                    building_center_y = building.y + building.template.height // 2
                    
                    # Create perpendicular connection
                    for x in range(min(building_center_x, main_x), max(building_center_x, main_x) + 1):
                        pathways.append((x, building_center_y, path_tile))
        
        elif layout.path_style == "organic":
            # Organic pathways with natural flow
            # Create a main gathering area
            center_x, center_y = width // 2, height // 2
            for y in range(center_y - 2, center_y + 3):
                for x in range(center_x - 2, center_x + 3):
                    if 0 <= x < width and 0 <= y < height:
                        pathways.append((x, y, ground_tile))  # Natural gathering area
            
            # Connect buildings with organic paths
            for i, building1 in enumerate(buildings):
                building1_center_x = building1.x + building1.template.width // 2
                building1_center_y = building1.y + building1.template.height // 2
                
                # Connect to center
                self._add_organic_path(pathways, building1_center_x, building1_center_y, center_x, center_y, width, height, ground_tile)
                
                # Connect to nearby buildings
                for j, building2 in enumerate(buildings[i+1:], i+1):
                    building2_center_x = building2.x + building2.template.width // 2
                    building2_center_y = building2.y + building2.template.height // 2
                    
                    distance = math.sqrt((building2_center_x - building1_center_x)**2 + (building2_center_y - building1_center_y)**2)
                    
                    # Connect nearby buildings
                    if distance < 20:
                        self._add_organic_path(pathways, building1_center_x, building1_center_y, 
                                             building2_center_x, building2_center_y, width, height, ground_tile)
        
        # Remove duplicates and return
        unique_pathways = list(set(pathways))
        print(f"    🛤️  Generated {len(unique_pathways)} pathway tiles using {layout.path_style} style for {biome}")
        return unique_pathways
    
    def _get_biome_tiles(self, biome: str) -> Tuple[int, int, int]:
        """Get appropriate tile types for ground, paths, and plazas based on biome"""
        biome_tiles = {
            'plains': (1, 2, 2),       # TILE_DIRT, TILE_STONE, TILE_STONE (no brick for plazas)
            'forest': (1, 2, 1),       # TILE_DIRT, TILE_STONE, TILE_DIRT
            'desert': (4, 4, 2),       # TILE_SAND, TILE_SAND, TILE_STONE
            'snow': (5, 2, 2),         # TILE_SNOW, TILE_STONE, TILE_STONE (no brick for plazas)
            'swamp': (1, 2, 1),        # TILE_DIRT, TILE_STONE, TILE_DIRT
            'mountain': (2, 2, 2),     # TILE_STONE, TILE_STONE, TILE_STONE
            'coast': (4, 2, 2),        # TILE_SAND, TILE_STONE, TILE_STONE (no brick for plazas)
            'tundra': (5, 2, 2),       # TILE_SNOW, TILE_STONE, TILE_STONE
            'hills': (1, 2, 2),        # TILE_DIRT, TILE_STONE, TILE_STONE
        }
        
        return biome_tiles.get(biome.lower(), (1, 2, 2))  # Default to plains (no brick for plazas)
    
    def _add_organic_path(self, pathways: List[Tuple[int, int, int]], x1: int, y1: int, x2: int, y2: int, 
                         width: int, height: int, tile_type: int):
        """Add an organic path between two points"""
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            steps = int(distance * 1.5)  # More steps for smoother path
            for step in range(steps):
                t = step / max(1, steps - 1)
                
                # Add some randomness for organic feel
                noise_x = int(math.sin(t * math.pi * 4) * 2)
                noise_y = int(math.cos(t * math.pi * 3) * 2)
                
                x = int(x1 + t * dx + noise_x)
                y = int(y1 + t * dy + noise_y)
                
                if 0 <= x < width and 0 <= y < height:
                    pathways.append((x, y, tile_type))  # Use specified tile type
    
    def _create_central_feature(self, feature_type: str, width: int, height: int, 
                              rng: random.Random) -> Dict[str, Any]:
        """Create a central feature for the settlement"""
        center_x, center_y = width // 2, height // 2
        
        features = {
            'plaza': {
                'type': 'plaza',
                'x': center_x - 3,
                'y': center_y - 3,
                'width': 6,
                'height': 6,
                'description': 'A central plaza where villagers gather'
            },
            'well': {
                'type': 'well',
                'x': center_x,
                'y': center_y,
                'width': 1,
                'height': 1,
                'description': 'A communal well providing fresh water'
            },
            'market': {
                'type': 'market',
                'x': center_x - 4,
                'y': center_y - 4,
                'width': 8,
                'height': 8,
                'description': 'A bustling market area with stalls'
            },
            'fire_pit': {
                'type': 'fire_pit',
                'x': center_x - 1,
                'y': center_y - 1,
                'width': 2,
                'height': 2,
                'description': 'A central fire pit for warmth and gathering'
            }
        }
        
        return features.get(feature_type, features['plaza'])
    
    def _assign_npcs_to_buildings(self, buildings: List[SettlementBuilding], 
                                settlement_type: str, rng: random.Random) -> List[Dict[str, Any]]:
        """Assign NPCs to buildings based on their templates"""
        npcs = []
        
        for building in buildings:
            # Get NPC spawns from building template
            for spawn_data in building.template.npc_spawns:
                # Calculate position relative to settlement (not world coordinates yet)
                relative_x = building.x + spawn_data['x']
                relative_y = building.y + spawn_data['y']
                
                npc_data = {
                    'name': spawn_data.get('name', 'Villager'),
                    'npc_type': spawn_data.get('npc_type', 'generic'),
                    'building': building.template.name,
                    'building_type': building.template.building_type,
                    'has_shop': spawn_data.get('has_shop', False),
                    'importance': spawn_data.get('importance', 'medium'),
                    'x': relative_x,  # Relative to settlement, not world
                    'y': relative_y,  # Relative to settlement, not world
                    'dialog': spawn_data.get('dialog', []),
                    'template_spawn': True  # Flag to indicate this came from a template
                }
                npcs.append(npc_data)
                
                # Store NPC assignment in building
                building.npc_assignments.append(npc_data)
        
        return npcs
    
    def _building_to_dict(self, building: SettlementBuilding, settlement_x: int, settlement_y: int) -> Dict[str, Any]:
        """Convert SettlementBuilding to dictionary for serialization"""
        return {
            'template_name': building.template.name,
            'building_type': building.template.building_type,
            'x': settlement_x + building.x,
            'y': settlement_y + building.y,
            'width': building.template.width,
            'height': building.template.height,
            'rotation': building.rotation,
            'tiles': building.template.tiles,
            'npc_spawns': building.template.npc_spawns,
            'furniture_positions': building.template.furniture_positions,
            'description': building.template.description
        }


def main():
    """Test the enhanced settlement generator"""
    generator = EnhancedSettlementGenerator(12345)
    
    # Test different settlement types
    test_settlements = [
        ('VILLAGE', 'plains'),
        ('TOWN', 'plains'),
        ('DESERT_OUTPOST', 'desert'),
        ('FOREST_CAMP', 'forest'),
        ('FISHING_VILLAGE', 'coast')
    ]
    
    for settlement_type, biome in test_settlements:
        print(f"\n=== Testing {settlement_type} in {biome} ===")
        settlement = generator.generate_settlement(0, 0, settlement_type, biome)
        
        print(f"Layout: {settlement['layout']} ({settlement['width']}x{settlement['height']})")
        print(f"Shape: {settlement['shape']}")
        print(f"Buildings: {settlement['total_buildings']}")
        print(f"NPCs: {settlement['total_npcs']}")
        print(f"Shops: {settlement['shops']}")
        
        # Show building types
        building_types = {}
        for building in settlement['buildings']:
            btype = building['building_type']
            building_types[btype] = building_types.get(btype, 0) + 1
        
        print("Building types:", ', '.join([f"{k}({v})" for k, v in building_types.items()]))


if __name__ == "__main__":
    main()