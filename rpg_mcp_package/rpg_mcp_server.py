#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for RPG Game
Allows AI NPCs to interact with the game world through structured tools
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Resource,
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        CallToolRequest,
        CallToolResult,
        ListResourcesRequest,
        ListResourcesResult,
        ListToolsRequest,
        ListToolsResult,
        ReadResourceRequest,
        ReadResourceResult,
    )
except ImportError:
    print("MCP library not found. Install with: pip install mcp")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rpg-mcp-server")

@dataclass
class GameAction:
    """Represents an action that can be taken in the game"""
    action_type: str
    parameters: Dict[str, Any]
    npc_id: Optional[str] = None
    timestamp: Optional[float] = None

class RPGMCPServer:
    """MCP Server for RPG Game Integration"""
    
    def __init__(self):
        self.server = Server("rpg-game-server")
        
        # Use game directory for state files (not current working directory)
        game_dir = Path.cwd()
        # If we're running from a different location, try to find the game directory
        if not (game_dir / "src").exists():
            # Look for the game directory in common locations
            possible_dirs = [
                Path.home() / "Development" / "claude-rpg-goose-npcs",
                Path("/Users/mnovich/Development/claude-rpg-goose-npcs"),
            ]
            for possible_dir in possible_dirs:
                if possible_dir.exists() and (possible_dir / "src").exists():
                    game_dir = possible_dir
                    break
        
        self.game_state_file = game_dir / "game_state.json"
        self.actions_queue_file = game_dir / "mcp_actions_queue.json"
        self.world_data_file = game_dir / "world_data.json"
        
        # Initialize action queue
        self.pending_actions: List[GameAction] = []
        
        # Register tools
        self._register_tools()
        
        # Register resources
        self._register_resources()
    
    def _register_tools(self):
        """Register all available tools for NPCs"""
        
        @self.server.call_tool()
        async def open_shop(arguments: dict) -> List[TextContent]:
            """Open trading interface with specific NPC"""
            npc_id = arguments.get("npc_id")
            shop_type = arguments.get("shop_type", "general")
            
            if not npc_id:
                return [TextContent(type="text", text="Error: npc_id is required")]
            
            action = GameAction(
                action_type="open_shop",
                parameters={
                    "npc_id": npc_id,
                    "shop_type": shop_type
                },
                npc_id=npc_id
            )
            
            await self._queue_action(action)
            return [TextContent(type="text", text=f"Opening shop for NPC {npc_id}")]
        
        @self.server.call_tool()
        async def create_quest(arguments: dict) -> List[TextContent]:
            """Create and assign a quest to the player"""
            quest_title = arguments.get("title")
            quest_description = arguments.get("description")
            quest_type = arguments.get("type", "fetch")
            objectives = arguments.get("objectives", [])
            rewards = arguments.get("rewards", {})
            npc_id = arguments.get("npc_id")
            
            if not quest_title or not quest_description:
                return [TextContent(type="text", text="Error: title and description are required")]
            
            action = GameAction(
                action_type="create_quest",
                parameters={
                    "title": quest_title,
                    "description": quest_description,
                    "type": quest_type,
                    "objectives": objectives,
                    "rewards": rewards,
                    "giver_npc_id": npc_id
                },
                npc_id=npc_id
            )
            
            await self._queue_action(action)
            return [TextContent(type="text", text=f"Created quest: {quest_title}")]
        
        @self.server.call_tool()
        async def get_world_info(arguments: dict) -> List[TextContent]:
            """Get information about the game world"""
            info_type = arguments.get("type", "general")
            location = arguments.get("location")
            
            world_info = await self._get_world_data()
            
            if info_type == "locations":
                locations = world_info.get("locations", {})
                if location:
                    loc_data = locations.get(location, {})
                    return [TextContent(type="text", text=json.dumps(loc_data, indent=2))]
                else:
                    return [TextContent(type="text", text=json.dumps(list(locations.keys()), indent=2))]
            
            elif info_type == "npcs":
                npcs = world_info.get("npcs", {})
                return [TextContent(type="text", text=json.dumps(npcs, indent=2))]
            
            elif info_type == "quests":
                quests = world_info.get("active_quests", [])
                return [TextContent(type="text", text=json.dumps(quests, indent=2))]
            
            else:
                # General world info
                general_info = {
                    "current_location": world_info.get("player_location", "unknown"),
                    "time_of_day": world_info.get("time_of_day", "day"),
                    "weather": world_info.get("weather", "clear"),
                    "available_locations": list(world_info.get("locations", {}).keys()),
                    "nearby_npcs": world_info.get("nearby_npcs", [])
                }
                return [TextContent(type="text", text=json.dumps(general_info, indent=2))]
        
        @self.server.call_tool()
        async def get_player_info(arguments: dict) -> List[TextContent]:
            """Get information about the player"""
            info_type = arguments.get("type", "general")
            
            player_data = await self._get_player_data()
            
            if info_type == "stats":
                stats = {
                    "level": player_data.get("level", 1),
                    "hp": player_data.get("hp", 100),
                    "max_hp": player_data.get("max_hp", 100),
                    "experience": player_data.get("experience", 0),
                    "gold": player_data.get("gold", 0)
                }
                return [TextContent(type="text", text=json.dumps(stats, indent=2))]
            
            elif info_type == "inventory":
                inventory = player_data.get("inventory", [])
                return [TextContent(type="text", text=json.dumps(inventory, indent=2))]
            
            elif info_type == "equipment":
                equipment = player_data.get("equipment", {})
                return [TextContent(type="text", text=json.dumps(equipment, indent=2))]
            
            elif info_type == "quests":
                quests = player_data.get("active_quests", [])
                return [TextContent(type="text", text=json.dumps(quests, indent=2))]
            
            else:
                # General player info
                general_info = {
                    "name": player_data.get("name", "Player"),
                    "level": player_data.get("level", 1),
                    "location": player_data.get("location", "unknown"),
                    "hp": f"{player_data.get('hp', 100)}/{player_data.get('max_hp', 100)}",
                    "gold": player_data.get("gold", 0),
                    "inventory_count": len(player_data.get("inventory", [])),
                    "active_quests": len(player_data.get("active_quests", []))
                }
                return [TextContent(type="text", text=json.dumps(general_info, indent=2))]
        
        @self.server.call_tool()
        async def give_item(arguments: dict) -> List[TextContent]:
            """Give an item to the player"""
            item_id = arguments.get("item_id")
            item_name = arguments.get("item_name")
            quantity = arguments.get("quantity", 1)
            npc_id = arguments.get("npc_id")
            
            if not item_id and not item_name:
                return [TextContent(type="text", text="Error: item_id or item_name is required")]
            
            action = GameAction(
                action_type="give_item",
                parameters={
                    "item_id": item_id,
                    "item_name": item_name,
                    "quantity": quantity
                },
                npc_id=npc_id
            )
            
            await self._queue_action(action)
            item_desc = item_name or item_id
            return [TextContent(type="text", text=f"Giving {quantity}x {item_desc} to player")]
        
        @self.server.call_tool()
        async def trigger_event(arguments: dict) -> List[TextContent]:
            """Trigger a game event or cutscene"""
            event_type = arguments.get("event_type")
            event_data = arguments.get("event_data", {})
            npc_id = arguments.get("npc_id")
            
            if not event_type:
                return [TextContent(type="text", text="Error: event_type is required")]
            
            action = GameAction(
                action_type="trigger_event",
                parameters={
                    "event_type": event_type,
                    "event_data": event_data
                },
                npc_id=npc_id
            )
            
            await self._queue_action(action)
            return [TextContent(type="text", text=f"Triggered event: {event_type}")]
        
        @self.server.call_tool()
        async def spawn_entity(arguments: dict) -> List[TextContent]:
            """Spawn an entity in the game world"""
            entity_type = arguments.get("entity_type")
            entity_id = arguments.get("entity_id")
            location = arguments.get("location")
            properties = arguments.get("properties", {})
            npc_id = arguments.get("npc_id")
            
            if not entity_type:
                return [TextContent(type="text", text="Error: entity_type is required")]
            
            action = GameAction(
                action_type="spawn_entity",
                parameters={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "location": location,
                    "properties": properties
                },
                npc_id=npc_id
            )
            
            await self._queue_action(action)
            return [TextContent(type="text", text=f"Spawning {entity_type} at {location}")]
        
        @self.server.call_tool()
        async def get_npc_relationship(arguments: dict) -> List[TextContent]:
            """Get relationship status between NPCs or with player"""
            npc_id = arguments.get("npc_id")
            target_id = arguments.get("target_id", "player")
            
            world_data = await self._get_world_data()
            relationships = world_data.get("relationships", {})
            
            if npc_id in relationships:
                npc_relations = relationships[npc_id]
                if target_id in npc_relations:
                    relation_data = npc_relations[target_id]
                    return [TextContent(type="text", text=json.dumps(relation_data, indent=2))]
            
            # Default relationship
            default_relation = {
                "reputation": 0,
                "trust": 50,
                "last_interaction": None,
                "relationship_type": "neutral"
            }
            return [TextContent(type="text", text=json.dumps(default_relation, indent=2))]
    
    def _register_resources(self):
        """Register resources that NPCs can access"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources"""
            return [
                Resource(
                    uri="game://world-state",
                    name="World State",
                    description="Current state of the game world",
                    mimeType="application/json"
                ),
                Resource(
                    uri="game://player-data",
                    name="Player Data",
                    description="Current player information and stats",
                    mimeType="application/json"
                ),
                Resource(
                    uri="game://quest-templates",
                    name="Quest Templates",
                    description="Available quest templates and types",
                    mimeType="application/json"
                ),
                Resource(
                    uri="game://item-database",
                    name="Item Database",
                    description="Available items and their properties",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific resource"""
            if uri == "game://world-state":
                world_data = await self._get_world_data()
                return json.dumps(world_data, indent=2)
            
            elif uri == "game://player-data":
                player_data = await self._get_player_data()
                return json.dumps(player_data, indent=2)
            
            elif uri == "game://quest-templates":
                quest_templates = await self._get_quest_templates()
                return json.dumps(quest_templates, indent=2)
            
            elif uri == "game://item-database":
                item_db = await self._get_item_database()
                return json.dumps(item_db, indent=2)
            
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def _queue_action(self, action: GameAction):
        """Queue an action to be processed by the game"""
        import time
        action.timestamp = time.time()
        self.pending_actions.append(action)
        
        # Save to file for game to read
        try:
            actions_data = []
            if self.actions_queue_file.exists():
                with open(self.actions_queue_file, 'r') as f:
                    actions_data = json.load(f)
            
            actions_data.append({
                "action_type": action.action_type,
                "parameters": action.parameters,
                "npc_id": action.npc_id,
                "timestamp": action.timestamp
            })
            
            with open(self.actions_queue_file, 'w') as f:
                json.dump(actions_data, f, indent=2)
                
            logger.info(f"Queued action: {action.action_type}")
            
        except Exception as e:
            logger.error(f"Failed to queue action: {e}")
    
    async def _get_world_data(self) -> Dict[str, Any]:
        """Get current world data"""
        try:
            if self.world_data_file.exists():
                with open(self.world_data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load world data: {e}")
        
        # Return default world data
        return {
            "locations": {
                "village": {"name": "Village", "type": "settlement", "npcs": []},
                "forest": {"name": "Dark Forest", "type": "wilderness", "enemies": []},
                "dungeon": {"name": "Ancient Dungeon", "type": "dungeon", "levels": 3}
            },
            "npcs": {},
            "active_quests": [],
            "player_location": "village",
            "time_of_day": "day",
            "weather": "clear",
            "nearby_npcs": [],
            "relationships": {}
        }
    
    async def _get_player_data(self) -> Dict[str, Any]:
        """Get current player data"""
        try:
            if self.game_state_file.exists():
                with open(self.game_state_file, 'r') as f:
                    game_data = json.load(f)
                    return game_data.get("player", {})
        except Exception as e:
            logger.error(f"Failed to load player data: {e}")
        
        # Return default player data
        return {
            "name": "Player",
            "level": 1,
            "hp": 100,
            "max_hp": 100,
            "experience": 0,
            "gold": 0,
            "location": "village",
            "inventory": [],
            "equipment": {},
            "active_quests": []
        }
    
    async def _get_quest_templates(self) -> Dict[str, Any]:
        """Get available quest templates"""
        return {
            "fetch": {
                "name": "Fetch Quest",
                "description": "Retrieve specific items",
                "objectives_template": ["Collect {item_name} x{quantity}"],
                "rewards_template": {"gold": 50, "experience": 100}
            },
            "kill": {
                "name": "Elimination Quest",
                "description": "Defeat specific enemies",
                "objectives_template": ["Defeat {enemy_type} x{quantity}"],
                "rewards_template": {"gold": 100, "experience": 200}
            },
            "delivery": {
                "name": "Delivery Quest",
                "description": "Deliver items to specific NPCs",
                "objectives_template": ["Deliver {item_name} to {npc_name}"],
                "rewards_template": {"gold": 75, "experience": 150}
            },
            "exploration": {
                "name": "Exploration Quest",
                "description": "Discover new locations",
                "objectives_template": ["Explore {location_name}"],
                "rewards_template": {"gold": 25, "experience": 50}
            }
        }
    
    async def _get_item_database(self) -> Dict[str, Any]:
        """Get available items database"""
        return {
            "weapons": {
                "iron_sword": {"name": "Iron Sword", "type": "weapon", "damage": 10, "value": 50},
                "steel_sword": {"name": "Steel Sword", "type": "weapon", "damage": 15, "value": 100},
                "magic_staff": {"name": "Magic Staff", "type": "weapon", "damage": 12, "value": 80}
            },
            "armor": {
                "leather_armor": {"name": "Leather Armor", "type": "armor", "defense": 5, "value": 30},
                "chain_mail": {"name": "Chain Mail", "type": "armor", "defense": 10, "value": 75},
                "plate_armor": {"name": "Plate Armor", "type": "armor", "defense": 15, "value": 150}
            },
            "consumables": {
                "health_potion": {"name": "Health Potion", "type": "consumable", "effect": "heal_50", "value": 25},
                "mana_potion": {"name": "Mana Potion", "type": "consumable", "effect": "restore_mana", "value": 30},
                "bread": {"name": "Bread", "type": "consumable", "effect": "heal_10", "value": 5}
            },
            "materials": {
                "iron_ore": {"name": "Iron Ore", "type": "material", "value": 10},
                "wood": {"name": "Wood", "type": "material", "value": 5},
                "herbs": {"name": "Herbs", "type": "material", "value": 8}
            }
        }
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting RPG MCP Server...")
        
        async with stdio_server() as (read_stream, write_stream):
            # Create a basic ServerCapabilities object
            from mcp.server.models import ServerCapabilities
            capabilities = ServerCapabilities(
                tools={"listChanged": True},
                resources={"subscribe": True, "listChanged": True},
            )
            
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="rpg-game-server",
                    server_version="1.0.0",
                    capabilities=capabilities,
                ),
            )

async def async_main():
    """Async main entry point"""
    server = RPGMCPServer()
    await server.run()

def main():
    """Synchronous main entry point for console script"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()