"""
MCP-compliant SSE Server for RPG Game

This implements the proper Model Context Protocol over Server-Sent Events
as expected by Goose and other MCP clients.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
import random
from typing import Dict, Any, Optional, List

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    StreamingResponse = None
    CORSMiddleware = None
    uvicorn = None

logger = logging.getLogger(__name__)

class MCPSSEServer:
    """MCP-compliant SSE server for the RPG game"""
    
    def __init__(self, game_instance, host: str = "localhost", port: int = 39301):
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI and uvicorn are required for MCP server. Install with: pip install fastapi uvicorn")
        
        self.game = game_instance
        self.host = host
        self.port = port
        self.app = FastAPI(title="RPG Game MCP Server", version="1.0.0")
        self.active_connections = {}
        self.server_thread = None
        self.server_info = None
        
        # Initialize item registry for asset-aware quest generation
        self.item_registry = None
        self._initialize_item_registry()
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_tools()
    
    def _initialize_item_registry(self):
        """Initialize the item registry with game assets"""
        try:
            from .item_registry import ItemRegistry
            asset_loader = getattr(self.game, 'asset_loader', None)
            self.item_registry = ItemRegistry(asset_loader)
            self.item_registry.print_registry_info()
            print("✅ [MCP] Item registry initialized for asset-aware quests")
        except Exception as e:
            print(f"⚠️  [MCP] Failed to initialize item registry: {e}")
            self.item_registry = None
    
    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup HTTP routes for MCP protocol"""
        
        @self.app.get("/")
        async def root():
            return {
                "name": "RPG Game MCP Server",
                "version": "1.0.0",
                "protocol": "mcp/2024-11-05",
                "capabilities": {
                    "tools": True,
                    "resources": False,
                    "prompts": False
                }
            }
        
        @self.app.get("/model_context_protocol/2024-11-05/sse")
        async def sse_endpoint(request: Request):
            """Server-Sent Events endpoint for MCP communication"""
            return StreamingResponse(
                self._mcp_sse_stream(request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        
        @self.app.post("/model_context_protocol/2024-11-05/sse")
        async def sse_post_endpoint(request: Request):
            """Handle MCP messages sent via POST to SSE endpoint"""
            try:
                message = await request.json()
                response = await self._handle_mcp_message(message)
                return response
            except Exception as e:
                logger.error(f"Error handling MCP message: {e}")
                return {"error": str(e)}
    
    def _setup_tools(self):
        """Define available MCP tools"""
        self.tools = {
            "get_player_info": {
                "name": "get_player_info",
                "description": "Get current player stats, inventory, and status",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "open_shop": {
                "name": "open_shop",
                "description": "Open the shop interface for trading items",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "shop_type": {
                            "type": "string",
                            "description": "Type of shop (general, weapons, armor, potions)",
                            "default": "general"
                        }
                    },
                    "required": []
                }
            },
            "give_item": {
                "name": "give_item",
                "description": "Give an item to the player",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Name of the item to give"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of items to give",
                            "default": 1
                        }
                    },
                    "required": ["item_name"]
                }
            },
            "create_quest": {
                "name": "create_quest",
                "description": "Create a quest that you've heard about from travelers. Use this IMMEDIATELY when players accept quests from you.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Quest title (e.g., 'Retrieve the Stolen Ring')"
                        },
                        "description": {
                            "type": "string", 
                            "description": "Quest description mentioning the location and direction (e.g., 'Bandits to the north have stolen a merchant's ring')"
                        },
                        "objectives": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of quest objectives (e.g., ['Collect 1 ring', 'Defeat bandits'])"
                        },
                        "reward": {
                            "type": "string",
                            "description": "Quest reward description (e.g., '50 gold and experience')"
                        }
                    },
                    "required": ["title", "description", "objectives"]
                }
            },
            "get_world_info": {
                "name": "get_world_info",
                "description": "Get information about the current game world and location",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "send_message": {
                "name": "send_message",
                "description": "Send a message to the game log",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to display"
                        },
                        "type": {
                            "type": "string",
                            "description": "Message type (info, warning, error)",
                            "default": "info"
                        }
                    },
                    "required": ["message"]
                }
            }
        }
    
    async def _mcp_sse_stream(self, request: Request):
        """Generate MCP-compliant Server-Sent Events stream"""
        connection_id = str(uuid.uuid4())
        connection_queue = asyncio.Queue()
        self.active_connections[connection_id] = connection_queue
        
        try:
            # Send MCP initialization message
            init_response = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    },
                    "serverInfo": {
                        "name": "RPG Game MCP Server",
                        "version": "1.0.0"
                    }
                }
            }
            
            yield f"data: {json.dumps(init_response)}\n\n"
            
            # Keep connection alive and handle messages
            while True:
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(connection_queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield "data: {}\n\n"
                
        except Exception as e:
            logger.error(f"SSE stream error: {e}")
        finally:
            self.active_connections.pop(connection_id, None)
    
    async def _handle_mcp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP messages"""
        try:
            method = message.get("method")
            params = message.get("params", {})
            msg_id = message.get("id")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": False
                            }
                        },
                        "serverInfo": {
                            "name": "RPG Game MCP Server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name not in self.tools:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                
                try:
                    result = await self._call_tool(tool_name, arguments)
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution error: {str(e)}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling MCP message: {e}")
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        if tool_name == "get_player_info":
            return await self._get_player_info()
        elif tool_name == "open_shop":
            return await self._open_shop(arguments.get("shop_type", "general"))
        elif tool_name == "give_item":
            return await self._give_item(arguments["item_name"], arguments.get("quantity", 1))
        elif tool_name == "create_quest":
            return await self._create_quest(arguments)
        elif tool_name == "get_world_info":
            return await self._get_world_info()
        elif tool_name == "send_message":
            return await self._send_message(arguments["message"], arguments.get("type", "info"))
        else:
            raise ValueError(f"Tool {tool_name} not implemented")
    
    # Tool implementation methods (same as before)
    async def _get_player_info(self) -> Dict[str, Any]:
        """Get player information"""
        if not hasattr(self.game, 'player') or self.game.player is None:
            return {"error": "Player not available", "success": False}
        
        player = self.game.player
        
        # Get inventory count safely
        inventory_count = 0
        if hasattr(player, 'inventory'):
            if hasattr(player.inventory, 'items'):
                inventory_count = len(player.inventory.items)
            elif hasattr(player.inventory, '__len__'):
                inventory_count = len(player.inventory)
        
        # Get equipped items safely
        equipped_items = {}
        if hasattr(player, 'equipped_weapon') and player.equipped_weapon:
            equipped_items['weapon'] = player.equipped_weapon.name
        if hasattr(player, 'equipped_armor') and player.equipped_armor:
            equipped_items['armor'] = player.equipped_armor.name
        
        return {
            "success": True,
            "player": {
                "health": getattr(player, 'health', 100),
                "max_health": getattr(player, 'max_health', 100),
                "level": getattr(player, 'level', 1),
                "experience": getattr(player, 'experience', 0),
                "gold": getattr(player, 'gold', 0),
                "attack_damage": getattr(player, 'attack_damage', 25),
                "defense": getattr(player, 'defense', 5),
                "stamina": getattr(player, 'stamina', 50),
                "max_stamina": getattr(player, 'max_stamina', 50),
                "position": {
                    "x": getattr(player, 'x', 0),
                    "y": getattr(player, 'y', 0)
                },
                "inventory_count": inventory_count,
                "equipped_items": equipped_items
            }
        }
    
    async def _open_shop(self, shop_type: str) -> Dict[str, Any]:
        """Open shop interface"""
        print(f"🛒 [MCP] open_shop called with type: {shop_type}")
        
        # Signal the game to open the shop UI
        if hasattr(self.game, 'player') and self.game.player:
            # Create a shop window for the player
            try:
                from .ui.shop import Shop
                shop_name = f"{shop_type.title()} Shop"
                shop = Shop(shop_name, self.game.asset_loader)
                
                # Set the current shop on the player
                self.game.player.current_shop = shop
                shop.open_shop()  # Actually open the shop UI
                print(f"✅ [MCP] Shop UI opened: {shop_name}")
                
                return {
                    "success": True,
                    "message": f"The {shop_type} shop is now open! Browse the available items and make your selections.",
                    "shop_type": shop_type,
                    "ui_opened": True
                }
            except Exception as e:
                print(f"❌ [MCP] Failed to open shop UI: {e}")
                return {
                    "success": True,
                    "message": f"The shop is open and ready for you to browse our selection of goods and services. Feel free to take your time and see what catches your interest!",
                    "shop_type": shop_type,
                    "ui_opened": False
                }
        else:
            print(f"⚠️ [MCP] No player available for shop UI")
            return {
                "success": True,
                "message": f"The shop is open and ready for you to browse our selection of goods and services. Feel free to take your time and see what catches your interest!",
                "shop_type": shop_type,
                "ui_opened": False
            }
    
    async def _give_item(self, item_name: str, quantity: int) -> Dict[str, Any]:
        """Give item to player"""
        if not hasattr(self.game, 'player') or self.game.player is None:
            return {"error": "Player not available", "success": False}
        
        player = self.game.player
        
        try:
            # Try to create and give the item
            from .entities.item import Item
            
            # Create item based on name
            item_data = self._get_item_data(item_name)
            
            for _ in range(quantity):
                # Create item with proper parameters
                item = Item(
                    x=player.x, 
                    y=player.y, 
                    name=item_name,
                    item_type=item_data["type"],
                    effect=item_data.get("effect", {}),
                    value=item_data.get("value", 10),
                    asset_loader=self.game.asset_loader
                )
                
                # Add to player inventory using the player's add_item method
                if hasattr(player, 'add_item'):
                    success = player.add_item(item)
                    if not success:
                        return {
                            "success": False,
                            "error": "Player inventory is full",
                            "item_name": item_name,
                            "quantity": quantity
                        }
                else:
                    # Fallback - try direct inventory access
                    if hasattr(player, 'inventory') and hasattr(player.inventory, 'add_item'):
                        success = player.inventory.add_item(item)
                        if not success:
                            return {
                                "success": False,
                                "error": "Player inventory is full",
                                "item_name": item_name,
                                "quantity": quantity
                            }
                    else:
                        return {
                            "success": False,
                            "error": "Could not access player inventory",
                            "item_name": item_name,
                            "quantity": quantity
                        }
            
            # Send message to game log
            if hasattr(self.game, 'game_log') and self.game.game_log:
                self.game.game_log.add_message(f"Received {quantity} {item_name}")
            
            print(f"✅ [MCP] Gave {quantity} {item_name} to player")
            
            return {
                "success": True,
                "message": f"Gave {quantity} {item_name} to player",
                "item_name": item_name,
                "quantity": quantity,
                "action": "item_given"
            }
            
        except Exception as e:
            print(f"❌ [MCP] Failed to give item: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to give {item_name}: {str(e)}",
                "item_name": item_name,
                "quantity": quantity
            }
    
    def _get_item_data(self, item_name: str) -> Dict[str, Any]:
        """Get item data based on item name - now uses item registry"""
        # Try to use item registry first
        if self.item_registry:
            # Resolve the item name to canonical form
            canonical_name = self.item_registry.resolve_item_name(item_name)
            if canonical_name:
                item_data = self.item_registry.get_item_data(canonical_name)
                if item_data:
                    return {
                        "type": item_data["type"],
                        "effect": item_data["effect"],
                        "value": item_data["value"]
                    }
        
        # Fallback to legacy item mapping
        item_map = {
            "health potion": {"type": "consumable", "effect": {"health": 50}, "value": 25},
            "mana potion": {"type": "consumable", "effect": {"mana": 30}, "value": 20},
            "stamina potion": {"type": "consumable", "effect": {"stamina": 30}, "value": 20},
            "sword": {"type": "weapon", "effect": {"damage": 10}, "value": 100},
            "iron sword": {"type": "weapon", "effect": {"damage": 15}, "value": 150},
            "shield": {"type": "armor", "effect": {"defense": 5}, "value": 80},
            "leather armor": {"type": "armor", "effect": {"defense": 8}, "value": 120},
            "gold": {"type": "currency", "effect": {"value": 1}, "value": 1},
            "bread": {"type": "consumable", "effect": {"health": 10}, "value": 5},
            "apple": {"type": "consumable", "effect": {"health": 5}, "value": 2},
            "key": {"type": "key", "effect": {"opens": "door"}, "value": 50},
            "antidote": {"type": "consumable", "effect": {"cure_poison": True}, "value": 35},
            "strength potion": {"type": "consumable", "effect": {"damage_boost": 10, "duration": 60}, "value": 50},
            "gold ring": {"type": "misc", "effect": {"magic_resistance": 5}, "value": 250},
            "magic scroll": {"type": "misc", "effect": {"spell_power": 15}, "value": 200},
            "crystal gem": {"type": "misc", "effect": {"value": 100}, "value": 150},
        }
        
        # Default to consumable if not found
        return item_map.get(item_name.lower(), {"type": "consumable", "effect": {"health": 10}, "value": 10})
    
    async def _create_quest(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quest with dynamic spawning support"""
        import re  # Import re module at the top of the function
        
        try:
            # Get quest manager from game
            quest_manager = getattr(self.game, 'quest_manager', None)
            if not quest_manager:
                return {
                    "success": False,
                    "error": "Quest system not available",
                    "quest": quest_data
                }
            
            # Parse quest data and add spawn information
            title = quest_data.get("title", "Unknown Quest")
            description = quest_data.get("description", "A mysterious quest...")
            objectives = quest_data.get("objectives", [])
            reward = quest_data.get("reward", "experience and gold")
            
            # Convert objectives from string list to proper format
            formatted_objectives = []
            spawn_data = {"spawns": []}
            
            for obj_text in objectives:
                obj_lower = obj_text.lower()
                
                if "collect" in obj_lower or "bring" in obj_lower or "find" in obj_lower:
                    # Extract item name and quantity
                    numbers = re.findall(r'\d+', obj_text)
                    quantity = int(numbers[0]) if numbers else 1
                    
                    # Use asset-aware item selection
                    item_name = self._select_quest_item(obj_text, "collect")
                    
                    formatted_objectives.append({
                        "type": "collect",
                        "target": item_name,
                        "count": quantity
                    })
                    
                    # Determine spawn location based on quest description
                    direction = "North"  # Default
                    if "north" in description.lower() or "northern" in description.lower():
                        direction = "North"
                    elif "south" in description.lower() or "southern" in description.lower():
                        direction = "South"
                    elif "east" in description.lower() or "eastern" in description.lower():
                        direction = "East"
                    elif "west" in description.lower() or "western" in description.lower():
                        direction = "West"
                    elif "northeast" in description.lower():
                        direction = "Northeast"
                    elif "northwest" in description.lower():
                        direction = "Northwest"
                    elif "southeast" in description.lower():
                        direction = "Southeast"
                    elif "southwest" in description.lower():
                        direction = "Southwest"
                    
                    # Also check the objective text for direction clues
                    if "north" in obj_lower or "northern" in obj_lower:
                        direction = "North"
                    elif "south" in obj_lower or "southern" in obj_lower:
                        direction = "South"
                    elif "east" in obj_lower or "eastern" in obj_lower:
                        direction = "East"
                    elif "west" in obj_lower or "western" in obj_lower:
                        direction = "West"
                    
                    # Determine what to spawn based on context
                    if "bandit" in description.lower() or "thief" in description.lower():
                        spawn_data["spawns"].append({
                            "type": "bandit",
                            "count": 1,
                            "direction": direction,
                            "distance": (25, 45),
                            "items": [item_name]
                        })
                    else:
                        # Spawn item directly or in a chest
                        spawn_data["spawns"].append({
                            "type": "chest",
                            "count": 1,
                            "direction": direction,
                            "distance": (20, 35),
                            "items": [item_name]
                        })
                
                elif "kill" in obj_lower or "defeat" in obj_lower:
                    # Extract enemy type and quantity
                    numbers = re.findall(r'\d+', obj_text)
                    quantity = int(numbers[0]) if numbers else 1
                    
                    enemy_type = "bandit"  # Default
                    if "bandit" in obj_lower:
                        enemy_type = "bandit"
                    elif "goblin" in obj_lower:
                        enemy_type = "goblin"
                    elif "orc" in obj_lower:
                        enemy_type = "orc"
                    
                    formatted_objectives.append({
                        "type": "kill",
                        "target": enemy_type,
                        "count": quantity
                    })
                    
                    # Spawn enemies
                    direction = "North"  # Default
                    if "north" in description.lower() or "northern" in description.lower():
                        direction = "North"
                    elif "south" in description.lower() or "southern" in description.lower():
                        direction = "South"
                    elif "east" in description.lower() or "eastern" in description.lower():
                        direction = "East"
                    elif "west" in description.lower() or "western" in description.lower():
                        direction = "West"
                    elif "northeast" in description.lower():
                        direction = "Northeast"
                    elif "northwest" in description.lower():
                        direction = "Northwest"
                    elif "southeast" in description.lower():
                        direction = "Southeast"
                    elif "southwest" in description.lower():
                        direction = "Southwest"
                    
                    # Also check the objective text for direction clues
                    if "north" in obj_lower or "northern" in obj_lower:
                        direction = "North"
                    elif "south" in obj_lower or "southern" in obj_lower:
                        direction = "South"
                    elif "east" in obj_lower or "eastern" in obj_lower:
                        direction = "East"
                    elif "west" in obj_lower or "western" in obj_lower:
                        direction = "West"
                    
                    spawn_data["spawns"].append({
                        "type": enemy_type,
                        "count": quantity,
                        "direction": direction,
                        "distance": (30, 50),
                        "items": []
                    })
            
            # Parse rewards
            formatted_rewards = {}
            if "gold" in reward.lower():
                numbers = re.findall(r'\d+', reward)
                formatted_rewards["gold"] = int(numbers[0]) if numbers else 50
            else:
                formatted_rewards["gold"] = 50
            
            if "experience" in reward.lower():
                numbers = re.findall(r'\d+', reward)
                formatted_rewards["experience"] = int(numbers[0]) if numbers else 100
            else:
                formatted_rewards["experience"] = 100
            
            if "potion" in reward.lower():
                formatted_rewards["item"] = "health potion"
            
            # Create the quest
            quest_info = {
                "title": title,
                "description": description,
                "objectives": formatted_objectives,
                "rewards": formatted_rewards,
                "spawn_data": spawn_data
            }
            
            quest_id = quest_manager.create_dynamic_quest(quest_info)
            
            # Return information including spawn directions for AI context
            spawn_directions = []
            for spawn in spawn_data.get("spawns", []):
                spawn_directions.append(f"{spawn['type']} {spawn['direction'].lower()}")
            
            direction_text = ", ".join(spawn_directions) if spawn_directions else "nearby"
            
            return {
                "success": True,
                "message": f"Created quest: {title}",
                "quest_id": quest_id,
                "quest": quest_info,
                "spawn_info": f"Spawned {direction_text}",
                "action": "quest_created"
            }
            
        except Exception as e:
            print(f"❌ [MCP] Failed to create quest: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to create quest: {str(e)}",
                "quest": quest_data
            }
    
    def _select_quest_item(self, objective_text: str, quest_type: str = "collect") -> str:
        """Select an appropriate item for a quest using asset-aware matching"""
        if not self.item_registry:
            # Fallback to old hardcoded system
            return self._fallback_item_selection(objective_text)
        
        try:
            # Extract potential item mentions from the objective text
            extracted_item = self._extract_item_from_text(objective_text)
            
            if extracted_item:
                # Try to find matching items in registry
                matching_items = self.item_registry.find_similar_items(extracted_item)
                
                if matching_items:
                    # Use the best match
                    selected_item = matching_items[0]
                    print(f"🎯 [MCP] Matched '{extracted_item}' to existing item: {selected_item}")
                    return selected_item
            
            # If no specific match, select by category
            suitable_items = self.item_registry.get_suitable_quest_items(quest_type)
            if suitable_items:
                # Prefer quest items for collection quests
                if quest_type == "collect":
                    quest_items = [item for item in suitable_items if "quest_items" in self.item_registry.get_item_data(item).get("category", "")]
                    if quest_items:
                        selected_item = random.choice(quest_items)
                        print(f"🎲 [MCP] Selected random quest item: {selected_item}")
                        return selected_item
                
                # Otherwise pick any suitable item
                selected_item = random.choice(suitable_items)
                print(f"🎲 [MCP] Selected random suitable item: {selected_item}")
                return selected_item
            
            # Last resort: guaranteed fallback
            fallback_item = self.item_registry.get_guaranteed_fallback_item()
            print(f"⚠️  [MCP] Using fallback item: {fallback_item}")
            return fallback_item
            
        except Exception as e:
            print(f"❌ [MCP] Error in item selection: {e}")
            return self.item_registry.get_guaranteed_fallback_item() if self.item_registry else "Health Potion"
    
    def _extract_item_from_text(self, text: str) -> Optional[str]:
        """Extract item intent from quest text using keyword matching"""
        text_lower = text.lower()
        
        # Direct item mentions with priority order
        item_keywords = {
            # Weapons (high priority for combat-related quests)
            "sword": ["sword", "blade", "steel", "iron sword"],
            "axe": ["axe", "hatchet"],
            "dagger": ["dagger", "knife", "blade"],
            "bow": ["bow", "crossbow", "ranged"],
            "staff": ["staff", "rod", "wand"],
            "hammer": ["hammer", "mace", "club"],
            
            # Armor
            "armor": ["armor", "protection", "mail", "plate"],
            "shield": ["shield", "buckler"],
            
            # Consumables  
            "potion": ["potion", "elixir", "brew", "drink"],
            "health potion": ["health", "healing", "red potion"],
            "mana potion": ["mana", "magic potion", "blue potion"],
            "antidote": ["antidote", "poison cure"],
            
            # Quest items (high priority)
            "ring": ["ring", "band", "jewelry", "golden ring"],
            "scroll": ["scroll", "tome", "document", "parchment", "letter"],
            "gem": ["gem", "crystal", "stone", "jewel"],
            "key": ["key", "opener"],
            
            # Generic categories
            "weapon": ["weapon", "armament"],
            "treasure": ["treasure", "valuable", "precious"]
        }
        
        # Find the best match with longest keyword match first
        best_match = None
        best_length = 0
        
        for item_type, keywords in item_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if len(keyword) > best_length:
                        best_match = item_type
                        best_length = len(keyword)
        
        return best_match
    
    def _fallback_item_selection(self, objective_text: str) -> str:
        """Fallback item selection when registry is not available"""
        obj_lower = objective_text.lower()
        
        # Old hardcoded system
        if "ring" in obj_lower:
            return "Gold Ring"
        elif "sword" in obj_lower:
            return "Iron Sword"
        elif "potion" in obj_lower:
            return "Health Potion"
        elif "scroll" in obj_lower:
            return "Magic Scroll"
        elif "gem" in obj_lower or "crystal" in obj_lower:
            return "Crystal Gem"
        else:
            return "Health Potion"  # Safe fallback
    
    async def _get_world_info(self) -> Dict[str, Any]:
        """Get world information"""
        return {
            "success": True,
            "world": {
                "current_level": "Town Square",
                "time_of_day": "Day",
                "weather": "Clear",
                "nearby_npcs": [],
                "nearby_items": [],
                "available_actions": ["move", "interact", "inventory"]
            }
        }
    
    async def _send_message(self, message: str, msg_type: str) -> Dict[str, Any]:
        """Send message to game log"""
        if hasattr(self.game, 'game_log') and self.game.game_log:
            self.game.game_log.add_message(message)
        
        return {
            "success": True,
            "message": message,
            "type": msg_type,
            "action": "message_sent"
        }
    
    def start_server(self):
        """Start the MCP server in a background thread"""
        if self.server_thread and self.server_thread.is_alive():
            logger.warning("MCP server already running")
            return
        
        def run_server():
            try:
                logger.info(f"Starting MCP server on {self.host}:{self.port}")
                uvicorn.run(
                    self.app,
                    host=self.host,
                    port=self.port,
                    log_level="info",
                    access_log=False
                )
            except Exception as e:
                logger.error(f"MCP server error: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # Give server time to start
        time.sleep(1)
        
        self.server_info = {
            "host": self.host,
            "port": self.port,
            "url": f"http://{self.host}:{self.port}",
            "sse_endpoint": f"http://{self.host}:{self.port}/model_context_protocol/2024-11-05/sse"
        }
        
        logger.info(f"MCP server started: {self.server_info['sse_endpoint']}")
    
    def stop_server(self):
        """Stop the MCP server"""
        logger.info("MCP server stop requested")
    
    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get server connection information"""
        return self.server_info

# Alias for backward compatibility
GameMCPServer = MCPSSEServer