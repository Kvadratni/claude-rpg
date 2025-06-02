"""
Event handling and input processing
"""

import pygame


class EventHandlingMixin:
    """Mixin class for event handling functionality"""
    
    def handle_event(self, event):
        """Handle level events"""
        # Check if dialogue window is open and handle its events first
        if self.player.current_dialogue and self.player.current_dialogue.show:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.player.current_dialogue.handle_click(event.pos):
                    return  # Dialogue consumed the event
        
        # Check if any shop is open and handle shop events
        for npc in self.npcs:
            if hasattr(npc, 'shop') and npc.shop and npc.shop.show:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if npc.shop.handle_click(event.pos, self.player):
                        return  # Shop consumed the event
        
        # Handle mouse clicks for interaction and movement
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos)
            elif event.button == 3:  # Right click
                self.handle_right_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                print("Zoom in (not implemented)")
            elif event.button == 5:  # Mouse wheel down
                print("Zoom out (not implemented)")
    
    def handle_click(self, pos):
        """Handle mouse click at position"""
        # Check if clicking on inventory button
        if hasattr(self, 'inventory_button_rect') and self.inventory_button_rect.collidepoint(pos):
            # Toggle inventory
            self.player.inventory.show = not self.player.inventory.show
            if self.player.game_log:
                if self.player.inventory.show:
                    self.player.game_log.add_message("Inventory opened", "system")
                else:
                    self.player.game_log.add_message("Inventory closed", "system")
            return
        
        # Convert screen position to world position
        world_x, world_y = self.iso_renderer.screen_to_world(pos[0], pos[1], self.camera_x, self.camera_y)
        
        # Let the player handle the click
        self.player.handle_mouse_click(world_x, world_y, self)
    
    def handle_right_click(self, pos):
        """Handle right mouse click for context actions"""
        # Convert screen position to world position
        world_x, world_y = self.iso_renderer.screen_to_world(pos[0], pos[1], self.camera_x, self.camera_y)
        
        # Check what was right-clicked
        clicked_entity = None
        
        # Check enemies for info
        for enemy in self.enemies:
            if abs(world_x - enemy.x) < 1.2 and abs(world_y - enemy.y) < 1.2:
                if self.player.game_log:
                    self.player.game_log.add_message(f"{enemy.name}: Health {enemy.health}/{enemy.max_health}, Damage {enemy.damage}", "system")
                clicked_entity = enemy
                break
        
        # Check NPCs for info
        if not clicked_entity:
            for npc in self.npcs:
                if abs(world_x - npc.x) < 1.2 and abs(world_y - npc.y) < 1.2:
                    if self.player.game_log:
                        # Just show NPC info on right-click, not dialog
                        npc_info = f"{npc.name}"
                        if npc.has_shop:
                            npc_info += " (Shopkeeper)"
                        self.player.game_log.add_message(npc_info, "system")
                    clicked_entity = npc
                    break
        
        # Check chests for info
        if not clicked_entity:
            for chest in self.chests:
                if abs(world_x - chest.x) < 1.2 and abs(world_y - chest.y) < 1.2:
                    if self.player.game_log:
                        status = "Empty" if chest.is_opened else "Unopened"
                        chest_info = f"{chest.name} ({status})"
                        if not chest.is_opened:
                            chest_info += f" - {len(chest.loot_items)} items inside"
                        self.player.game_log.add_message(chest_info, "system")
                    clicked_entity = chest
                    break
        
        # Check items for info
        if not clicked_entity:
            for item in self.items:
                if abs(world_x - item.x) < 1.2 and abs(world_y - item.y) < 1.2:
                    effect_str = ", ".join([f"{k}: {v}" for k, v in item.effect.items()])
                    if self.player.game_log:
                        self.player.game_log.add_message(f"{item.name} ({item.item_type}): {effect_str}", "item")
                    clicked_entity = item
                    break
        
        if not clicked_entity:
            # Show tile info
            tile_x = int(world_x)
            tile_y = int(world_y)
            if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
                tile_names = {
                    self.TILE_GRASS: "Grass",
                    self.TILE_DIRT: "Dirt",
                    self.TILE_STONE: "Stone Path",
                    self.TILE_WATER: "Water",
                    self.TILE_WALL: "Wall",
                    self.TILE_DOOR: "Door",
                    self.TILE_BRICK: "Brick Floor",
                    self.TILE_SAND: "Sand",
                    self.TILE_SNOW: "Snow",
                    self.TILE_FOREST_FLOOR: "Forest Floor",
                    self.TILE_SWAMP: "Swamp"
                }
                tile_type = self.get_tile(tile_x, tile_y) if hasattr(self, 'get_tile') else self.tiles[tile_y][tile_x]
                tile_name = tile_names.get(tile_type, "Unknown")
                walkable_value = self.walkable[tile_y][tile_x]
                if walkable_value <= 0:
                    walkable = "blocked"
                elif walkable_value < 1:
                    walkable = f"restricted ({walkable_value:.1f})"
                else:
                    walkable = "walkable"
                if self.player.game_log:
                    self.player.game_log.add_message(f"Tile ({tile_x}, {tile_y}): {tile_name} ({walkable})", "system")