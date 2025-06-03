"""
MCP Integration for RPG Game
Handles communication between the game and the MCP server
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

class MCPActionHandler:
    """Handles MCP actions from AI NPCs"""
    
    def __init__(self, game_instance=None):
        self.game = game_instance
        self.actions_queue_file = Path("mcp_actions_queue.json")
        self.game_state_file = Path("game_state.json")
        self.world_data_file = Path("world_data.json")
        
        # Track processed actions to avoid duplicates
        self.processed_actions = set()
    
    def update_world_data(self, player=None, level=None, npcs=None):
        """Update world data file for MCP server"""
        try:
            world_data = {
                "timestamp": time.time(),
                "locations": self._get_locations_data(level),
                "npcs": self._get_npcs_data(npcs),
                "active_quests": self._get_active_quests(player),
                "player_location": self._get_player_location(player, level),
                "time_of_day": "day",  # TODO: Implement day/night cycle
                "weather": "clear",    # TODO: Implement weather system
                "nearby_npcs": self._get_nearby_npcs(player, npcs),
                "relationships": self._get_relationships(player)
            }
            
            with open(self.world_data_file, 'w') as f:
                json.dump(world_data, f, indent=2)
                
        except Exception as e:
            print(f"Error updating world data: {e}")
    
    def update_game_state(self, player=None):
        """Update game state file for MCP server"""
        try:
            if not player:
                return
                
            player_data = {
                "name": getattr(player, 'name', 'Player'),
                "level": getattr(player, 'level', 1),
                "hp": getattr(player, 'hp', 100),
                "max_hp": getattr(player, 'max_hp', 100),
                "experience": getattr(player, 'experience', 0),
                "gold": getattr(player, 'gold', 0),
                "location": "village",  # TODO: Get actual location
                "inventory": self._get_inventory_data(player),
                "equipment": self._get_equipment_data(player),
                "active_quests": self._get_active_quests(player)
            }
            
            game_state = {
                "timestamp": time.time(),
                "player": player_data
            }
            
            with open(self.game_state_file, 'w') as f:
                json.dump(game_state, f, indent=2)
                
        except Exception as e:
            print(f"Error updating game state: {e}")
    
    def process_pending_actions(self, player=None, level=None):
        """Process pending MCP actions"""
        if not self.actions_queue_file.exists():
            return
        
        try:
            with open(self.actions_queue_file, 'r') as f:
                actions = json.load(f)
            
            processed_any = False
            remaining_actions = []
            
            for action_data in actions:
                action_id = f"{action_data.get('timestamp', 0)}_{action_data.get('action_type', '')}"
                
                if action_id in self.processed_actions:
                    continue
                
                if self._process_action(action_data, player, level):
                    self.processed_actions.add(action_id)
                    processed_any = True
                    print(f"✅ Processed MCP action: {action_data.get('action_type')}")
                else:
                    # Keep unprocessed actions for retry
                    remaining_actions.append(action_data)
            
            # Update actions file with remaining actions
            if processed_any:
                with open(self.actions_queue_file, 'w') as f:
                    json.dump(remaining_actions, f, indent=2)
                    
        except Exception as e:
            print(f"Error processing MCP actions: {e}")
    
    def _process_action(self, action_data: Dict[str, Any], player=None, level=None) -> bool:
        """Process a single MCP action"""
        action_type = action_data.get('action_type')
        parameters = action_data.get('parameters', {})
        npc_id = action_data.get('npc_id')
        
        try:
            if action_type == "open_shop":
                return self._handle_open_shop(parameters, player, npc_id)
            
            elif action_type == "create_quest":
                return self._handle_create_quest(parameters, player, npc_id)
            
            elif action_type == "give_item":
                return self._handle_give_item(parameters, player, npc_id)
            
            elif action_type == "trigger_event":
                return self._handle_trigger_event(parameters, player, level)
            
            elif action_type == "spawn_entity":
                return self._handle_spawn_entity(parameters, level)
            
            else:
                print(f"Unknown MCP action type: {action_type}")
                return False
                
        except Exception as e:
            print(f"Error processing action {action_type}: {e}")
            return False
    
    def _handle_open_shop(self, parameters: Dict[str, Any], player=None, npc_id=None) -> bool:
        """Handle opening shop interface"""
        if not player or not hasattr(player, 'current_shop'):
            return False
        
        try:
            # Find the NPC to open shop for
            npc = self._find_npc_by_id(npc_id)
            if not npc:
                print(f"NPC not found: {npc_id}")
                return False
            
            # Create shop interface (this would need to be implemented in the UI system)
            shop_type = parameters.get('shop_type', 'general')
            
            # For now, just set a flag that the UI can check
            if hasattr(player, 'pending_shop_npc'):
                player.pending_shop_npc = npc_id
                player.pending_shop_type = shop_type
                print(f"🛒 Shop interface requested for NPC {npc_id}")
                return True
            
        except Exception as e:
            print(f"Error opening shop: {e}")
        
        return False
    
    def _handle_create_quest(self, parameters: Dict[str, Any], player=None, npc_id=None) -> bool:
        """Handle quest creation"""
        if not player:
            return False
        
        try:
            quest_data = {
                "id": f"quest_{int(time.time())}",
                "title": parameters.get('title', 'Untitled Quest'),
                "description": parameters.get('description', 'No description'),
                "type": parameters.get('type', 'fetch'),
                "objectives": parameters.get('objectives', []),
                "rewards": parameters.get('rewards', {}),
                "giver_npc_id": npc_id,
                "status": "active",
                "created_at": time.time()
            }
            
            # Add quest to player's active quests
            if not hasattr(player, 'active_quests'):
                player.active_quests = []
            
            player.active_quests.append(quest_data)
            
            # Show quest notification (this would need UI integration)
            if hasattr(player, 'pending_quest_notification'):
                player.pending_quest_notification = quest_data
            
            print(f"📜 Created quest: {quest_data['title']}")
            return True
            
        except Exception as e:
            print(f"Error creating quest: {e}")
        
        return False
    
    def _handle_give_item(self, parameters: Dict[str, Any], player=None, npc_id=None) -> bool:
        """Handle giving items to player"""
        if not player or not hasattr(player, 'inventory'):
            return False
        
        try:
            item_id = parameters.get('item_id')
            item_name = parameters.get('item_name')
            quantity = parameters.get('quantity', 1)
            
            # Create item data
            item_data = {
                "id": item_id or item_name.lower().replace(' ', '_'),
                "name": item_name or item_id,
                "quantity": quantity,
                "source": f"npc_{npc_id}",
                "received_at": time.time()
            }
            
            # Add to player inventory
            if hasattr(player.inventory, 'add_item'):
                player.inventory.add_item(item_data)
            else:
                # Fallback: add to inventory list
                if not hasattr(player, 'inventory_items'):
                    player.inventory_items = []
                player.inventory_items.append(item_data)
            
            # Show item notification
            if hasattr(player, 'pending_item_notification'):
                player.pending_item_notification = item_data
            
            print(f"🎁 Gave {quantity}x {item_name or item_id} to player")
            return True
            
        except Exception as e:
            print(f"Error giving item: {e}")
        
        return False
    
    def _handle_trigger_event(self, parameters: Dict[str, Any], player=None, level=None) -> bool:
        """Handle triggering game events"""
        try:
            event_type = parameters.get('event_type')
            event_data = parameters.get('event_data', {})
            
            # Store event for game to process
            if not hasattr(player, 'pending_events'):
                player.pending_events = []
            
            event = {
                "type": event_type,
                "data": event_data,
                "timestamp": time.time()
            }
            
            player.pending_events.append(event)
            print(f"⚡ Triggered event: {event_type}")
            return True
            
        except Exception as e:
            print(f"Error triggering event: {e}")
        
        return False
    
    def _handle_spawn_entity(self, parameters: Dict[str, Any], level=None) -> bool:
        """Handle spawning entities"""
        if not level:
            return False
        
        try:
            entity_type = parameters.get('entity_type')
            entity_id = parameters.get('entity_id')
            location = parameters.get('location')
            properties = parameters.get('properties', {})
            
            # Store spawn request for level to process
            if not hasattr(level, 'pending_spawns'):
                level.pending_spawns = []
            
            spawn_data = {
                "type": entity_type,
                "id": entity_id,
                "location": location,
                "properties": properties,
                "timestamp": time.time()
            }
            
            level.pending_spawns.append(spawn_data)
            print(f"🎭 Requested spawn: {entity_type} at {location}")
            return True
            
        except Exception as e:
            print(f"Error spawning entity: {e}")
        
        return False
    
    def _find_npc_by_id(self, npc_id: str):
        """Find NPC by ID (this would need proper game integration)"""
        # TODO: Implement proper NPC lookup
        return None
    
    def _get_locations_data(self, level=None) -> Dict[str, Any]:
        """Get locations data for world state"""
        # TODO: Extract actual location data from level
        return {
            "village": {"name": "Village", "type": "settlement", "npcs": []},
            "forest": {"name": "Dark Forest", "type": "wilderness", "enemies": []},
            "dungeon": {"name": "Ancient Dungeon", "type": "dungeon", "levels": 3}
        }
    
    def _get_npcs_data(self, npcs=None) -> Dict[str, Any]:
        """Get NPCs data for world state"""
        if not npcs:
            return {}
        
        npcs_data = {}
        for npc in npcs:
            if hasattr(npc, 'name'):
                npcs_data[npc.name.lower().replace(' ', '_')] = {
                    "name": npc.name,
                    "type": getattr(npc, 'npc_type', 'generic'),
                    "location": getattr(npc, 'location', 'village'),
                    "dialogue_available": True
                }
        
        return npcs_data
    
    def _get_active_quests(self, player=None) -> List[Dict[str, Any]]:
        """Get active quests for world state"""
        if not player or not hasattr(player, 'active_quests'):
            return []
        
        return getattr(player, 'active_quests', [])
    
    def _get_player_location(self, player=None, level=None) -> str:
        """Get player's current location"""
        # TODO: Implement proper location detection
        return "village"
    
    def _get_nearby_npcs(self, player=None, npcs=None) -> List[str]:
        """Get list of nearby NPCs"""
        if not npcs:
            return []
        
        # TODO: Implement proximity detection
        return [npc.name for npc in npcs if hasattr(npc, 'name')][:5]
    
    def _get_relationships(self, player=None) -> Dict[str, Any]:
        """Get relationship data"""
        # TODO: Implement relationship system
        return {}
    
    def _get_inventory_data(self, player=None) -> List[Dict[str, Any]]:
        """Get player inventory data"""
        if not player or not hasattr(player, 'inventory'):
            return []
        
        # TODO: Convert inventory to proper format
        inventory_items = []
        if hasattr(player.inventory, 'items'):
            for item in player.inventory.items:
                inventory_items.append({
                    "id": getattr(item, 'id', 'unknown'),
                    "name": getattr(item, 'name', 'Unknown Item'),
                    "quantity": getattr(item, 'quantity', 1),
                    "type": getattr(item, 'type', 'misc')
                })
        
        return inventory_items
    
    def _get_equipment_data(self, player=None) -> Dict[str, Any]:
        """Get player equipment data"""
        if not player:
            return {}
        
        # TODO: Extract equipment data
        return {
            "weapon": getattr(player, 'equipped_weapon', None),
            "armor": getattr(player, 'equipped_armor', None),
            "accessory": getattr(player, 'equipped_accessory', None)
        }