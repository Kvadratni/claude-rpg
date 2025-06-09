"""
Settlement manager for chunk-based worlds
Handles settlement placement across infinite worlds with proper density
"""

import random
import math
from typing import List, Dict, Tuple, Optional, Any


class ChunkSettlementManager:
    """
    Manages settlements across chunk-based infinite worlds
    """
    
    # Enhanced settlement templates with varied building sizes and higher spawn rates
    SETTLEMENT_TEMPLATES = {
        'VILLAGE': {
            'size': (24, 24),  # Larger for more buildings
            'buildings': [
                {'name': 'General Store', 'size': (4, 4), 'npc': 'Master Merchant', 'has_shop': True, 'importance': 'high'},
                {'name': 'Inn', 'size': (5, 4), 'npc': 'Innkeeper', 'has_shop': False, 'importance': 'high'},
                {'name': 'Blacksmith', 'size': (4, 3), 'npc': 'Master Smith', 'has_shop': True, 'importance': 'high'},
                {'name': 'Elder House', 'size': (4, 4), 'npc': 'Village Elder', 'has_shop': False, 'importance': 'high'},
                {'name': 'Guard House', 'size': (3, 3), 'npc': 'Guard Captain', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Temple', 'size': (5, 5), 'npc': 'High Priest', 'has_shop': False, 'importance': 'high'},
                {'name': 'Market Stall', 'size': (3, 2), 'npc': 'Trader', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Tavern', 'size': (4, 3), 'npc': 'Barkeeper', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Stable', 'size': (6, 3), 'npc': 'Stable Master', 'has_shop': False, 'importance': 'low'},
                {'name': 'Cottage', 'size': (3, 3), 'npc': 'Villager', 'has_shop': False, 'importance': 'low'},
                {'name': 'Workshop', 'size': (3, 4), 'npc': 'Craftsman', 'has_shop': True, 'importance': 'medium'}
            ],
            'biomes': ['PLAINS', 'FOREST'],
            'spawn_chance': 0.04,  # Further reduced from 0.08 - 4% chance
            'min_distance': 8  # Increased from 4 for better spacing
        },
        'TOWN': {
            'size': (30, 30),  # New large settlement type
            'buildings': [
                {'name': 'Town Hall', 'size': (6, 5), 'npc': 'Mayor', 'has_shop': False, 'importance': 'high'},
                {'name': 'Grand Market', 'size': (8, 6), 'npc': 'Market Master', 'has_shop': True, 'importance': 'high'},
                {'name': 'Large Inn', 'size': (6, 5), 'npc': 'Inn Master', 'has_shop': False, 'importance': 'high'},
                {'name': 'Armory', 'size': (5, 4), 'npc': 'Weapon Master', 'has_shop': True, 'importance': 'high'},
                {'name': 'Magic Shop', 'size': (4, 4), 'npc': 'Court Wizard', 'has_shop': True, 'importance': 'high'},
                {'name': 'Cathedral', 'size': (7, 8), 'npc': 'Archbishop', 'has_shop': False, 'importance': 'high'},
                {'name': 'Barracks', 'size': (5, 6), 'npc': 'Commander', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Library', 'size': (5, 4), 'npc': 'Librarian', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Bank', 'size': (4, 3), 'npc': 'Banker', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Guildhall', 'size': (6, 4), 'npc': 'Guild Master', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Noble House', 'size': (5, 5), 'npc': 'Noble', 'has_shop': False, 'importance': 'low'},
                {'name': 'Merchant House', 'size': (4, 4), 'npc': 'Rich Merchant', 'has_shop': True, 'importance': 'low'}
            ],
            'biomes': ['PLAINS', 'FOREST'],
            'spawn_chance': 0.03,  # Drastically reduced from 0.15 - 3% chance (rare but significant)
            'min_distance': 12  # Increased from 8 - towns need even more space
        },
        'DESERT_OUTPOST': {
            'size': (18, 18),  # Slightly larger
            'buildings': [
                {'name': 'Trading Post', 'size': (5, 4), 'npc': 'Caravan Master', 'has_shop': True, 'importance': 'high'},
                {'name': 'Water Cistern', 'size': (4, 4), 'npc': 'Water Keeper', 'has_shop': False, 'importance': 'high'},
                {'name': 'Caravan Rest', 'size': (6, 3), 'npc': 'Desert Guide', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Oasis Keeper Hut', 'size': (3, 3), 'npc': 'Oasis Keeper', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Sand Shelter', 'size': (4, 3), 'npc': 'Desert Nomad', 'has_shop': False, 'importance': 'low'},
                {'name': 'Supply Cache', 'size': (3, 2), 'importance': 'low'}  # No NPC
            ],
            'biomes': ['DESERT'],
            'spawn_chance': 0.06,  # Further reduced from 0.12 - 6% chance
            'min_distance': 6  # Increased from 3
        },
        'SNOW_SETTLEMENT': {
            'size': (16, 16),  # Slightly larger
            'buildings': [
                {'name': 'Ranger Station', 'size': (4, 4), 'npc': 'Forest Ranger', 'has_shop': False, 'importance': 'high'},
                {'name': 'Herbalist Hut', 'size': (3, 3), 'npc': 'Master Herbalist', 'has_shop': True, 'importance': 'high'},
                {'name': 'Warm Lodge', 'size': (5, 4), 'npc': 'Lodge Keeper', 'has_shop': False, 'importance': 'high'},
                {'name': 'Hunter Cabin', 'size': (3, 4), 'npc': 'Hunter', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Fur Trader', 'size': (3, 3), 'npc': 'Fur Trader', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Ice House', 'size': (4, 3), 'npc': 'Ice Keeper', 'has_shop': False, 'importance': 'low'},
                {'name': 'Woodshed', 'size': (3, 2), 'importance': 'low'}  # No NPC
            ],
            'biomes': ['SNOW', 'TUNDRA'],
            'spawn_chance': 0.10,  # Drastically reduced from 0.50 - 10% chance
            'min_distance': 6  # Increased from 3
        },
        'SWAMP_VILLAGE': {
            'size': (20, 20),  # Larger for more buildings
            'buildings': [
                {'name': 'Alchemist Hut', 'size': (4, 4), 'npc': 'Swamp Alchemist', 'has_shop': True, 'importance': 'high'},
                {'name': 'Fisherman Dock', 'size': (5, 3), 'npc': 'Fisherman', 'has_shop': False, 'importance': 'high'},
                {'name': 'Witch Hut', 'size': (3, 4), 'npc': 'Swamp Witch', 'has_shop': True, 'importance': 'high'},
                {'name': 'Boat Builder', 'size': (4, 6), 'npc': 'Boat Builder', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Herb Gatherer', 'size': (3, 3), 'npc': 'Herb Gatherer', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Stilted House', 'size': (3, 3), 'npc': 'Swamp Dweller', 'has_shop': False, 'importance': 'low'},
                {'name': 'Mushroom Farm', 'size': (4, 3), 'npc': 'Mushroom Farmer', 'has_shop': True, 'importance': 'low'}
            ],
            'biomes': ['SWAMP'],
            'spawn_chance': 0.08,  # Drastically reduced from 0.40 - 8% chance
            'min_distance': 6  # Increased from 3
        },
        'FOREST_CAMP': {
            'size': (14, 14),  # Slightly larger
            'buildings': [
                {'name': 'Woodcutter Lodge', 'size': (4, 3), 'npc': 'Master Woodcutter', 'has_shop': True, 'importance': 'high'},
                {'name': 'Druid Circle', 'size': (5, 5), 'npc': 'Forest Druid', 'has_shop': False, 'importance': 'high'},
                {'name': 'Scout Post', 'size': (3, 3), 'npc': 'Scout Leader', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Tree House', 'size': (3, 3), 'npc': 'Tree Keeper', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Lumber Mill', 'size': (4, 5), 'npc': 'Miller', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Forest Shrine', 'size': (3, 3), 'npc': 'Forest Priest', 'has_shop': False, 'importance': 'low'}
            ],
            'biomes': ['FOREST'],
            'spawn_chance': 0.07,  # Drastically reduced from 0.35 - 7% chance
            'min_distance': 6  # Increased from 3
        },
        'MINING_CAMP': {
            'size': (16, 16),  # New settlement type
            'buildings': [
                {'name': 'Mine Entrance', 'size': (4, 3), 'npc': 'Mine Foreman', 'has_shop': False, 'importance': 'high'},
                {'name': 'Ore Processing', 'size': (5, 4), 'npc': 'Ore Master', 'has_shop': True, 'importance': 'high'},
                {'name': 'Miners Barracks', 'size': (6, 3), 'npc': 'Barracks Chief', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Tool Shop', 'size': (3, 3), 'npc': 'Tool Maker', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Assay Office', 'size': (3, 3), 'npc': 'Assayer', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Miner Hut', 'size': (3, 3), 'npc': 'Veteran Miner', 'has_shop': False, 'importance': 'low'},
                {'name': 'Supply Shed', 'size': (3, 2), 'importance': 'low'}  # No NPC
            ],
            'biomes': ['MOUNTAIN', 'HILLS'],
            'spawn_chance': 0.06,  # Reduced from 0.30 - 6% chance
            'min_distance': 7  # Increased from 4
        },
        'FISHING_VILLAGE': {
            'size': (18, 18),  # New settlement type
            'buildings': [
                {'name': 'Harbor Master', 'size': (4, 3), 'npc': 'Harbor Master', 'has_shop': False, 'importance': 'high'},
                {'name': 'Fish Market', 'size': (5, 4), 'npc': 'Fish Merchant', 'has_shop': True, 'importance': 'high'},
                {'name': 'Boat Dock', 'size': (6, 4), 'npc': 'Dock Master', 'has_shop': False, 'importance': 'high'},
                {'name': 'Net Maker', 'size': (3, 3), 'npc': 'Net Weaver', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Fisherman Hut', 'size': (3, 3), 'npc': 'Old Fisherman', 'has_shop': False, 'importance': 'medium'},
                {'name': 'Smokehouse', 'size': (4, 3), 'npc': 'Smoke Master', 'has_shop': True, 'importance': 'medium'},
                {'name': 'Sailor Lodge', 'size': (4, 4), 'npc': 'Sailor', 'has_shop': False, 'importance': 'low'}
            ],
            'biomes': ['COAST', 'PLAINS'],  # Near water
            'spawn_chance': 0.05,  # Reduced from 0.25 - 5% chance
            'min_distance': 7  # Increased from 4
        }
    }
    
    def __init__(self, world_seed: int):
        """Initialize settlement manager"""
        self.world_seed = world_seed
        self.placed_settlements = {}  # Track settlements by chunk coordinates
        
    def should_generate_settlement(self, chunk_x: int, chunk_y: int, biome_data: Dict[str, int]) -> Optional[str]:
        """
        Determine if a settlement should be generated in this chunk
        
        Args:
            chunk_x, chunk_y: Chunk coordinates
            biome_data: Dictionary of biome -> tile_count in this chunk
            
        Returns:
            Settlement type to generate, or None
        """
        # Create deterministic random for this chunk
        chunk_seed = hash((self.world_seed, chunk_x, chunk_y, "settlement")) % (2**31)
        chunk_random = random.Random(chunk_seed)
        
        # Find dominant biome in chunk
        if not biome_data:
            return None
            
        dominant_biome = max(biome_data.items(), key=lambda x: x[1])[0]
        
        # Check each settlement type for compatibility
        for settlement_type, config in self.SETTLEMENT_TEMPLATES.items():
            if dominant_biome in config['biomes']:
                # Check spawn chance
                if chunk_random.random() < config['spawn_chance']:
                    # Check minimum distance from other settlements of same type
                    if self._check_minimum_distance(chunk_x, chunk_y, settlement_type, config['min_distance']):
                        return settlement_type
        
        return None
    
    def _check_minimum_distance(self, chunk_x: int, chunk_y: int, settlement_type: str, min_distance: int) -> bool:
        """Check if minimum distance requirement is met"""
        for (cx, cy), placed_type in self.placed_settlements.items():
            if placed_type == settlement_type:
                distance = max(abs(cx - chunk_x), abs(cy - chunk_y))
                if distance < min_distance:
                    return False
        return True
    
    def generate_settlement_in_chunk(self, chunk_x: int, chunk_y: int, settlement_type: str) -> Dict[str, Any]:
        """
        Generate a settlement in the specified chunk with integrated NPCs
        
        Args:
            chunk_x, chunk_y: Chunk coordinates
            settlement_type: Type of settlement to generate
            
        Returns:
            Settlement data dictionary with properly positioned NPCs
        """
        config = self.SETTLEMENT_TEMPLATES[settlement_type]
        
        # Create deterministic random for this settlement
        settlement_seed = hash((self.world_seed, chunk_x, chunk_y, settlement_type)) % (2**31)
        settlement_random = random.Random(settlement_seed)
        
        # Calculate world position within chunk (center-ish)
        chunk_size = 64  # From Chunk.CHUNK_SIZE
        world_x = chunk_x * chunk_size + settlement_random.randint(10, chunk_size - config['size'][0] - 10)
        world_y = chunk_y * chunk_size + settlement_random.randint(10, chunk_size - config['size'][1] - 10)
        
        # Generate NPCs for this settlement with proper building assignment
        npcs = []
        building_assignments = {}  # Track which buildings have NPCs
        
        # Sort buildings by importance to assign NPCs to most important buildings first
        buildings_with_npcs = [b for b in config['buildings'] if 'npc' in b]
        buildings_with_npcs.sort(key=lambda b: {'high': 3, 'medium': 2, 'low': 1}.get(b.get('importance', 'low'), 1), reverse=True)
        
        # Scale NPCs based on settlement size - split between interactive and background
        npc_limits = {
            'VILLAGE': (3, 4),           # 3 interactive + 4 background = 7 total
            'TOWN': (6, 8),              # 6 interactive + 8 background = 14 total  
            'DESERT_OUTPOST': (2, 2),    # 2 interactive + 2 background = 4 total
            'SNOW_SETTLEMENT': (3, 3),   # 3 interactive + 3 background = 6 total
            'SWAMP_VILLAGE': (3, 3),     # 3 interactive + 3 background = 6 total
            'FOREST_CAMP': (2, 2),       # 2 interactive + 2 background = 4 total
            'MINING_CAMP': (3, 4),       # 3 interactive + 4 background = 7 total
            'FISHING_VILLAGE': (4, 4)    # 4 interactive + 4 background = 8 total
        }
        max_interactive, max_background = npc_limits.get(settlement_type, (2, 2))
        
        # First, place interactive NPCs (the important ones with shops/services)
        interactive_npcs_to_place = min(len(buildings_with_npcs), max_interactive)
        
        print(f"  👥 Settlement {settlement_type}: placing {interactive_npcs_to_place} interactive + {max_background} background NPCs")
        
        for i, building in enumerate(buildings_with_npcs[:interactive_npcs_to_place]):
            if 'npc' in building:
                # Calculate NPC position within the building
                building_center_x = world_x + settlement_random.randint(2, config['size'][0] - 2)
                building_center_y = world_y + settlement_random.randint(2, config['size'][1] - 2)
                
                npc_data = {
                    'name': building['npc'],
                    'building': building['name'],
                    'building_type': building.get('type', 'generic'),
                    'has_shop': building.get('has_shop', False),
                    'importance': building.get('importance', 'medium'),
                    'x': building_center_x,
                    'y': building_center_y,
                    'dialog': self._generate_npc_dialog(building['npc'], settlement_type, building['name'])
                }
                npcs.append(npc_data)
                building_assignments[building['name']] = npc_data
        
        # Second, add background NPCs (simple villagers for atmosphere - non-interactive)
        background_npc_names = [
            "Villager", "Farmer", "Worker", "Resident", "Citizen", 
            "Peasant", "Local", "Townsperson", "Settler", "Dweller"
        ]
        
        for i in range(max_background):
            # Place background NPCs in random locations within the settlement
            bg_npc_x = world_x + settlement_random.randint(3, config['size'][0] - 3)
            bg_npc_y = world_y + settlement_random.randint(3, config['size'][1] - 3)
            
            # Choose a random background NPC name
            bg_npc_name = settlement_random.choice(background_npc_names)
            if i > 0:  # Add numbers to avoid duplicate names
                bg_npc_name = f"{bg_npc_name} {i+1}"
            
            bg_npc_data = {
                'name': bg_npc_name,
                'building': 'Settlement',
                'has_shop': False,
                'x': bg_npc_x,
                'y': bg_npc_y,
                'is_background': True,  # Flag to identify background NPCs (non-interactive)
                'dialog': []  # No dialog - they won't be interactive
            }
            npcs.append(bg_npc_data)
            
        print(f"  👤 Added {interactive_npcs_to_place} interactive + {max_background} background NPCs")
        
        settlement_data = {
            'type': settlement_type,
            'chunk_x': chunk_x,
            'chunk_y': chunk_y,
            'world_x': world_x,
            'world_y': world_y,
            'size': config['size'],
            'buildings': config['buildings'],
            'npcs': npcs,
            'building_assignments': building_assignments,
            'biomes': config['biomes'],
            'total_npcs': len(npcs),
            'shops': len([npc for npc in npcs if npc['has_shop']])
        }
        
        # Record this settlement
        self.placed_settlements[(chunk_x, chunk_y)] = settlement_type
        
        return settlement_data
    
    def _get_max_npcs_for_settlement(self, settlement_type: str) -> int:
        """
        Determine maximum NPCs for settlement type based on size and importance
        Returns tuple: (interactive_npcs, background_npcs)
        
        Args:
            settlement_type: Type of settlement
            
        Returns:
            Maximum number of NPCs to place
        """
        # Format: (interactive NPCs, background villagers)
        npc_limits = {
            'VILLAGE': (3, 4),           # 3 interactive + 4 background = 7 total
            'TOWN': (6, 8),              # 6 interactive + 8 background = 14 total  
            'DESERT_OUTPOST': (2, 2),    # 2 interactive + 2 background = 4 total
            'SNOW_SETTLEMENT': (3, 3),   # 3 interactive + 3 background = 6 total
            'SWAMP_VILLAGE': (3, 3),     # 3 interactive + 3 background = 6 total
            'FOREST_CAMP': (2, 2),       # 2 interactive + 2 background = 4 total
            'MINING_CAMP': (3, 4),       # 3 interactive + 4 background = 7 total
            'FISHING_VILLAGE': (4, 4)    # 4 interactive + 4 background = 8 total
        }
        interactive, background = npc_limits.get(settlement_type, (2, 2))
        return interactive + background  # Return total for now, we'll split the logic below
    
    def _generate_npc_dialog(self, npc_name: str, settlement_type: str, building_name: str) -> List[str]:
        """Generate contextual dialog for NPCs based on their role and settlement"""
        
        # Base dialog templates by NPC type
        dialog_templates = {
            # Merchants and Shopkeepers
            'Master Merchant': [
                "Welcome to the finest goods in the region!",
                "I have wares from distant lands.",
                "Trade is the lifeblood of our settlement.",
                "Looking for something specific? I might have it."
            ],
            'Market Master': [
                "The grand market has everything you need!",
                "Merchants from across the realm trade here.",
                "Our market is the heart of commerce.",
                "Quality goods at fair prices, always!"
            ],
            'Caravan Master': [
                "The desert routes are treacherous but profitable.",
                "My caravans travel to the far oases.",
                "Water and supplies are precious here.",
                "The sands hold many secrets, traveler."
            ],
            
            # Innkeepers and Hospitality
            'Innkeeper': [
                "Welcome, weary traveler! Rest your bones here.",
                "The beds are clean and the ale is cold.",
                "Many tales are shared by our hearth.",
                "A good night's rest prepares you for the road."
            ],
            'Inn Master': [
                "Our establishment serves the finest guests!",
                "Nobles and merchants alike stay here.",
                "The grand suite is available for distinguished visitors.",
                "We pride ourselves on exceptional service."
            ],
            'Lodge Keeper': [
                "The cold winds bite fierce out there.",
                "Our lodge provides warmth and shelter.",
                "Hot soup and warm beds await the weary.",
                "The mountain passes are dangerous in winter."
            ],
            
            # Crafters and Specialists
            'Master Smith': [
                "The forge burns hot today!",
                "I craft weapons worthy of heroes.",
                "Bring me rare metals and I'll work wonders.",
                "A good blade can save your life."
            ],
            'Weapon Master': [
                "Only the finest weapons grace my armory.",
                "Each blade is tested and proven in battle.",
                "A warrior is only as good as their steel.",
                "I've armed knights and adventurers alike."
            ],
            'Master Herbalist': [
                "Nature provides all the healing we need.",
                "These herbs can cure what ails you.",
                "The forest spirits guide my gathering.",
                "A wise healer knows every plant's purpose."
            ],
            
            # Authority Figures
            'Village Elder': [
                "Welcome to our peaceful settlement.",
                "I've watched this place grow for decades.",
                "The old ways still have wisdom to offer.",
                "May your journey bring you enlightenment."
            ],
            'Mayor': [
                "Our town prospers under good governance.",
                "Citizens' welfare is my highest priority.",
                "We welcome honest traders and travelers.",
                "Progress and tradition must balance."
            ],
            'Guard Captain': [
                "I keep the peace in these parts.",
                "Bandits know to avoid our patrols.",
                "The roads are safer with vigilant guards.",
                "Report any trouble to me immediately."
            ],
            'Commander': [
                "Our forces stand ready to defend the town.",
                "Military discipline keeps order.",
                "We've faced threats and emerged victorious.",
                "A strong defense ensures peaceful trade."
            ],
            
            # Religious and Mystical
            'High Priest': [
                "The divine light guides all who seek it.",
                "Faith provides strength in dark times.",
                "Our temple welcomes all faithful souls.",
                "Blessings upon your journey, child."
            ],
            'Archbishop': [
                "The cathedral stands as beacon of hope.",
                "Divine providence watches over our town.",
                "Great ceremonies unite our community.",
                "The sacred texts hold ancient wisdom."
            ],
            'Forest Druid': [
                "The ancient woods speak to those who listen.",
                "Nature's balance must be preserved.",
                "The old magic still flows through these lands.",
                "Respect the forest and it will protect you."
            ],
            'Court Wizard': [
                "Magic serves those who understand its price.",
                "Ancient knowledge requires careful study.",
                "Spells and potions aid the worthy.",
                "The arcane arts demand respect and wisdom."
            ],
            
            # Specialized Workers
            'Mine Foreman': [
                "The mines run deep into the mountain heart.",
                "We've struck rich veins of precious ore.",
                "Mining is dangerous work, but rewarding.",
                "The earth yields its treasures to the bold."
            ],
            'Harbor Master': [
                "Ships from distant ports dock here daily.",
                "The harbor is the gateway to the world.",
                "Tides and weather dictate our schedule.",
                "Many fortunes are made and lost at sea."
            ],
            'Forest Ranger': [
                "I know every trail in these ancient woods.",
                "The forest has its own laws and dangers.",
                "Wildlife must be protected and respected.",
                "Few can navigate these paths without guidance."
            ]
        }
        
        # Get base dialog or create generic dialog
        base_dialog = dialog_templates.get(npc_name, [
            f"Greetings, I am {npc_name}.",
            f"Welcome to our {building_name}.",
            f"How may I assist you today?",
            f"Our {settlement_type.lower()} is a fine place."
        ])
        
        # Add settlement-specific context
        settlement_context = {
            'VILLAGE': ["Our village is peaceful and welcoming.", "Simple folk live simple lives here."],
            'TOWN': ["Our town is a center of commerce and culture.", "Many opportunities await in a place like this."],
            'DESERT_OUTPOST': ["The desert is harsh but we endure.", "Water and shade are precious commodities."],
            'SNOW_SETTLEMENT': ["The cold keeps the weak away.", "We're hardy folk who thrive in winter."],
            'SWAMP_VILLAGE': ["The swamp provides for those who know its ways.", "Outsiders find this place unwelcoming."],
            'FOREST_CAMP': ["The forest is our home and protector.", "We live in harmony with the ancient trees."],
            'MINING_CAMP': ["The mountain's riches fuel our community.", "Hard work in the mines builds character."],
            'FISHING_VILLAGE': ["The sea provides all we need.", "Fishing has been our way of life for generations."]
        }
        
        # Combine base dialog with settlement context
        combined_dialog = base_dialog.copy()
        if settlement_type in settlement_context:
            combined_dialog.extend(settlement_context[settlement_type])
        
        return combined_dialog
