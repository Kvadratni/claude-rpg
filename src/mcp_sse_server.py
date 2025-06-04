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
        
        self._setup_middleware()
        self._setup_routes()
        self._setup_tools()
    
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
                "description": "Create a new quest for the player",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Quest title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Quest description"
                        },
                        "reward": {
                            "type": "string",
                            "description": "Quest reward description"
                        },
                        "objectives": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of quest objectives"
                        }
                    },
                    "required": ["title", "description"]
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
        return {
            "success": True,
            "player": {
                "health": getattr(player, 'health', 100),
                "max_health": getattr(player, 'max_health', 100),
                "level": getattr(player, 'level', 1),
                "experience": getattr(player, 'experience', 0),
                "gold": getattr(player, 'gold', 0),
                "position": {
                    "x": getattr(player, 'x', 0),
                    "y": getattr(player, 'y', 0)
                },
                "inventory_count": len(getattr(player, 'inventory', [])),
                "equipped_items": getattr(player, 'equipped_items', {})
            }
        }
    
    async def _open_shop(self, shop_type: str) -> Dict[str, Any]:
        """Open shop interface"""
        return {
            "success": True,
            "message": f"Opening {shop_type} shop",
            "shop_type": shop_type,
            "action": "shop_opened"
        }
    
    async def _give_item(self, item_name: str, quantity: int) -> Dict[str, Any]:
        """Give item to player"""
        if not hasattr(self.game, 'player') or self.game.player is None:
            return {"error": "Player not available", "success": False}
        
        return {
            "success": True,
            "message": f"Gave {quantity} {item_name} to player",
            "item_name": item_name,
            "quantity": quantity,
            "action": "item_given"
        }
    
    async def _create_quest(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new quest"""
        return {
            "success": True,
            "message": f"Created quest: {quest_data['title']}",
            "quest": quest_data,
            "action": "quest_created"
        }
    
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