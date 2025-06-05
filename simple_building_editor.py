#!/usr/bin/env python3
"""
Standalone Building Template Editor
A simple version that works without complex imports
"""

import pygame
import json
import os
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any


class EditorTool(Enum):
    """Available tools in the building editor"""
    WALL = "wall"
    DOOR = "door"
    FLOOR = "floor"
    NPC_SPAWN = "npc_spawn"
    FURNITURE = "furniture"
    ERASE = "erase"


class TileType(Enum):
    """Tile types for building templates"""
    EMPTY = 0
    WALL = 1
    DOOR = 2
    FLOOR = 3
    FURNITURE = 4
    NPC_SPAWN = 5


class NPCSpawnPoint:
    """Represents an NPC spawn point in a building"""
    
    def __init__(self, x: int, y: int, npc_type: str = "generic", name: str = ""):
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.name = name
        self.has_shop = False
        self.dialog = []
        self.importance = "medium"


class BuildingTemplate:
    """Represents a building template with layout and spawn points"""
    
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        self.width = width
        self.height = height
        self.tiles = [[TileType.EMPTY for _ in range(width)] for _ in range(height)]
        self.npc_spawns = []
        self.furniture_positions = []
        self.description = ""
        self.building_type = "generic"
        
    def get_tile(self, x: int, y: int) -> TileType:
        """Get tile type at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TileType.EMPTY
    
    def set_tile(self, x: int, y: int, tile_type: TileType):
        """Set tile type at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_type
    
    def add_npc_spawn(self, x: int, y: int, npc_type: str = "generic", name: str = ""):
        """Add NPC spawn point"""
        spawn = NPCSpawnPoint(x, y, npc_type, name)
        self.npc_spawns.append(spawn)
        self.set_tile(x, y, TileType.NPC_SPAWN)
        return spawn
    
    def remove_npc_spawn(self, x: int, y: int):
        """Remove NPC spawn point at position"""
        self.npc_spawns = [spawn for spawn in self.npc_spawns 
                          if not (spawn.x == x and spawn.y == y)]
        if self.get_tile(x, y) == TileType.NPC_SPAWN:
            self.set_tile(x, y, TileType.FLOOR)
    
    def get_npc_spawn_at(self, x: int, y: int) -> Optional[NPCSpawnPoint]:
        """Get NPC spawn point at position"""
        for spawn in self.npc_spawns:
            if spawn.x == x and spawn.y == y:
                return spawn
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for saving"""
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'description': self.description,
            'building_type': self.building_type,
            'tiles': [[tile.value for tile in row] for row in self.tiles],
            'npc_spawns': [
                {
                    'x': spawn.x,
                    'y': spawn.y,
                    'npc_type': spawn.npc_type,
                    'name': spawn.name,
                    'has_shop': spawn.has_shop,
                    'dialog': spawn.dialog,
                    'importance': spawn.importance
                }
                for spawn in self.npc_spawns
            ],
            'furniture_positions': self.furniture_positions
        }


class SimpleBuildingEditor:
    """Simplified building template editor"""
    
    def __init__(self, screen_width: int = 1200, screen_height: int = 800):
        pygame.init()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Building Template Editor")
        
        # Editor state
        self.running = True
        self.current_tool = EditorTool.WALL
        self.current_template = None
        self.templates_dir = "building_templates"
        self.grid_size = 32
        self.grid_offset_x = 200
        self.grid_offset_y = 100
        
        # UI elements
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'background': (40, 40, 40),
            'grid': (80, 80, 80),
            'toolbar': (60, 60, 60),
            'button': (100, 100, 100),
            'button_hover': (120, 120, 120),
            'button_active': (140, 140, 140),
            'text': (255, 255, 255),
            'wall': (139, 69, 19),
            'door': (101, 67, 33),
            'floor': (205, 133, 63),
            'npc_spawn': (255, 0, 0),
            'furniture': (160, 82, 45),
            'empty': (20, 20, 20)
        }
        
        # UI state
        self.selected_npc_spawn = None
        self.show_npc_dialog = False
        
        # Create templates directory
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Create default template
        self.create_new_template("New Building", 15, 15)
    
    def create_new_template(self, name: str, width: int, height: int):
        """Create a new building template"""
        self.current_template = BuildingTemplate(name, width, height)
        
        # Add basic walls around the perimeter
        for x in range(width):
            self.current_template.set_tile(x, 0, TileType.WALL)
            self.current_template.set_tile(x, height-1, TileType.WALL)
        for y in range(height):
            self.current_template.set_tile(0, y, TileType.WALL)
            self.current_template.set_tile(width-1, y, TileType.WALL)
        
        # Fill interior with floor
        for y in range(1, height-1):
            for x in range(1, width-1):
                self.current_template.set_tile(x, y, TileType.FLOOR)
        
        # Add a door in the front wall
        door_x = width // 2
        self.current_template.set_tile(door_x, height-1, TileType.DOOR)
    
    def save_template(self, filename: str):
        """Save current template to file"""
        if self.current_template:
            filepath = os.path.join(self.templates_dir, f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(self.current_template.to_dict(), f, indent=2)
            print(f"Template saved: {filepath}")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event)
            
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    self.handle_mouse_drag(event)
    
    def handle_keydown(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
            if self.current_template:
                self.save_template(self.current_template.name)
        
        elif event.key == pygame.K_n and pygame.key.get_pressed()[pygame.K_LCTRL]:
            self.create_new_template("New Building", 15, 15)
        
        elif event.key == pygame.K_1:
            self.current_tool = EditorTool.WALL
        elif event.key == pygame.K_2:
            self.current_tool = EditorTool.DOOR
        elif event.key == pygame.K_3:
            self.current_tool = EditorTool.FLOOR
        elif event.key == pygame.K_4:
            self.current_tool = EditorTool.NPC_SPAWN
        elif event.key == pygame.K_5:
            self.current_tool = EditorTool.FURNITURE
        elif event.key == pygame.K_e:
            self.current_tool = EditorTool.ERASE
        elif event.key == pygame.K_ESCAPE:
            self.show_npc_dialog = False
            self.selected_npc_spawn = None
    
    def handle_mouse_click(self, event):
        """Handle mouse clicks"""
        mouse_x, mouse_y = event.pos
        
        if self.is_in_grid_area(mouse_x, mouse_y):
            grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
            self.handle_grid_click(grid_x, grid_y, event.button)
        elif self.is_in_toolbar_area(mouse_x, mouse_y):
            self.handle_toolbar_click(mouse_x, mouse_y)
    
    def handle_mouse_drag(self, event):
        """Handle mouse dragging"""
        mouse_x, mouse_y = event.pos
        if self.is_in_grid_area(mouse_x, mouse_y):
            grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
            self.apply_tool(grid_x, grid_y)
    
    def handle_grid_click(self, grid_x: int, grid_y: int, button: int):
        """Handle clicks on the grid"""
        if not self.current_template:
            return
        
        if button == 1:  # Left click
            if self.current_tool == EditorTool.NPC_SPAWN:
                existing_spawn = self.current_template.get_npc_spawn_at(grid_x, grid_y)
                if existing_spawn:
                    self.selected_npc_spawn = existing_spawn
                    self.show_npc_dialog = True
                else:
                    spawn = self.current_template.add_npc_spawn(grid_x, grid_y)
                    spawn.name = "New NPC"
                    spawn.npc_type = "generic"
                    self.selected_npc_spawn = spawn
                    self.show_npc_dialog = True
            else:
                self.apply_tool(grid_x, grid_y)
        
        elif button == 3:  # Right click
            if self.current_template.get_tile(grid_x, grid_y) == TileType.NPC_SPAWN:
                self.current_template.remove_npc_spawn(grid_x, grid_y)
            else:
                self.current_template.set_tile(grid_x, grid_y, TileType.EMPTY)
    
    def apply_tool(self, grid_x: int, grid_y: int):
        """Apply the current tool to a grid position"""
        if not self.current_template:
            return
        
        if self.current_tool == EditorTool.WALL:
            self.current_template.set_tile(grid_x, grid_y, TileType.WALL)
        elif self.current_tool == EditorTool.DOOR:
            self.current_template.set_tile(grid_x, grid_y, TileType.DOOR)
        elif self.current_tool == EditorTool.FLOOR:
            self.current_template.set_tile(grid_x, grid_y, TileType.FLOOR)
        elif self.current_tool == EditorTool.FURNITURE:
            self.current_template.set_tile(grid_x, grid_y, TileType.FURNITURE)
        elif self.current_tool == EditorTool.ERASE:
            if self.current_template.get_tile(grid_x, grid_y) == TileType.NPC_SPAWN:
                self.current_template.remove_npc_spawn(grid_x, grid_y)
            else:
                self.current_template.set_tile(grid_x, grid_y, TileType.EMPTY)
    
    def handle_toolbar_click(self, mouse_x: int, mouse_y: int):
        """Handle clicks on the toolbar"""
        tool_y_start = 120
        tool_height = 40
        tool_spacing = 50
        
        tools = [
            EditorTool.WALL,
            EditorTool.DOOR,
            EditorTool.FLOOR,
            EditorTool.NPC_SPAWN,
            EditorTool.FURNITURE,
            EditorTool.ERASE
        ]
        
        for i, tool in enumerate(tools):
            button_y = tool_y_start + i * tool_spacing
            if 10 <= mouse_x <= 180 and button_y <= mouse_y <= button_y + tool_height:
                self.current_tool = tool
                break
    
    def is_in_grid_area(self, x: int, y: int) -> bool:
        return x >= self.grid_offset_x and y >= self.grid_offset_y
    
    def is_in_toolbar_area(self, x: int, y: int) -> bool:
        return x < self.grid_offset_x
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        grid_x = (screen_x - self.grid_offset_x) // self.grid_size
        grid_y = (screen_y - self.grid_offset_y) // self.grid_size
        return grid_x, grid_y
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        screen_x = self.grid_offset_x + grid_x * self.grid_size
        screen_y = self.grid_offset_y + grid_y * self.grid_size
        return screen_x, screen_y
    
    def draw(self):
        """Draw the editor interface"""
        self.screen.fill(self.colors['background'])
        
        self.draw_toolbar()
        
        if self.current_template:
            self.draw_grid()
            self.draw_template()
        
        self.draw_top_menu()
        
        if self.show_npc_dialog and self.selected_npc_spawn:
            self.draw_npc_dialog()
        
        pygame.display.flip()
    
    def draw_toolbar(self):
        """Draw the left toolbar"""
        toolbar_rect = pygame.Rect(0, 0, self.grid_offset_x, self.screen_height)
        pygame.draw.rect(self.screen, self.colors['toolbar'], toolbar_rect)
        
        title_text = self.font.render("Building Editor", True, self.colors['text'])
        self.screen.blit(title_text, (10, 10))
        
        tool_y_start = 120
        tool_height = 40
        tool_spacing = 50
        
        tools = [
            (EditorTool.WALL, "Wall (1)"),
            (EditorTool.DOOR, "Door (2)"),
            (EditorTool.FLOOR, "Floor (3)"),
            (EditorTool.NPC_SPAWN, "NPC Spawn (4)"),
            (EditorTool.FURNITURE, "Furniture (5)"),
            (EditorTool.ERASE, "Erase (E)")
        ]
        
        for i, (tool, label) in enumerate(tools):
            button_y = tool_y_start + i * tool_spacing
            button_rect = pygame.Rect(10, button_y, 170, tool_height)
            
            if tool == self.current_tool:
                color = self.colors['button_active']
            else:
                color = self.colors['button']
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.colors['text'], button_rect, 2)
            
            text = self.small_font.render(label, True, self.colors['text'])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
        
        # Template info
        if self.current_template:
            info_y = 450
            info_text = [
                f"Template: {self.current_template.name}",
                f"Size: {self.current_template.width}x{self.current_template.height}",
                f"NPCs: {len(self.current_template.npc_spawns)}",
                f"Type: {self.current_template.building_type}"
            ]
            
            for i, text in enumerate(info_text):
                rendered = self.small_font.render(text, True, self.colors['text'])
                self.screen.blit(rendered, (10, info_y + i * 20))
        
        # Instructions
        instructions_y = 600
        instructions = [
            "Left Click: Place",
            "Right Click: Remove",
            "Ctrl+S: Save",
            "Ctrl+N: New",
            "1-5: Select Tool",
            "E: Erase Tool"
        ]
        
        for i, instruction in enumerate(instructions):
            rendered = self.small_font.render(instruction, True, self.colors['text'])
            self.screen.blit(rendered, (10, instructions_y + i * 18))
    
    def draw_top_menu(self):
        """Draw the top menu bar"""
        menu_rect = pygame.Rect(self.grid_offset_x, 0, 
                               self.screen_width - self.grid_offset_x, 
                               self.grid_offset_y)
        pygame.draw.rect(self.screen, self.colors['toolbar'], menu_rect)
        
        if self.current_template:
            name_text = self.font.render(f"Template: {self.current_template.name}", 
                                       True, self.colors['text'])
            self.screen.blit(name_text, (self.grid_offset_x + 10, 10))
            
            type_text = self.small_font.render(f"Type: {self.current_template.building_type}", 
                                             True, self.colors['text'])
            self.screen.blit(type_text, (self.grid_offset_x + 10, 35))
    
    def draw_grid(self):
        """Draw the grid lines"""
        if not self.current_template:
            return
        
        for x in range(self.current_template.width + 1):
            start_x = self.grid_offset_x + x * self.grid_size
            start_y = self.grid_offset_y
            end_y = self.grid_offset_y + self.current_template.height * self.grid_size
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (start_x, start_y), (start_x, end_y))
        
        for y in range(self.current_template.height + 1):
            start_y = self.grid_offset_y + y * self.grid_size
            start_x = self.grid_offset_x
            end_x = self.grid_offset_x + self.current_template.width * self.grid_size
            pygame.draw.line(self.screen, self.colors['grid'], 
                           (start_x, start_y), (end_x, start_y))
    
    def draw_template(self):
        """Draw the current template"""
        if not self.current_template:
            return
        
        for y in range(self.current_template.height):
            for x in range(self.current_template.width):
                tile_type = self.current_template.get_tile(x, y)
                screen_x, screen_y = self.grid_to_screen(x, y)
                tile_rect = pygame.Rect(screen_x, screen_y, self.grid_size, self.grid_size)
                
                if tile_type == TileType.WALL:
                    color = self.colors['wall']
                elif tile_type == TileType.DOOR:
                    color = self.colors['door']
                elif tile_type == TileType.FLOOR:
                    color = self.colors['floor']
                elif tile_type == TileType.NPC_SPAWN:
                    color = self.colors['npc_spawn']
                elif tile_type == TileType.FURNITURE:
                    color = self.colors['furniture']
                else:
                    color = self.colors['empty']
                
                pygame.draw.rect(self.screen, color, tile_rect)
                
                if tile_type == TileType.NPC_SPAWN:
                    npc_text = self.small_font.render("NPC", True, (255, 255, 255))
                    text_rect = npc_text.get_rect(center=tile_rect.center)
                    self.screen.blit(npc_text, text_rect)
    
    def draw_npc_dialog(self):
        """Draw the NPC configuration dialog"""
        if not self.selected_npc_spawn:
            return
        
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, self.colors['toolbar'], dialog_rect)
        pygame.draw.rect(self.screen, self.colors['text'], dialog_rect, 2)
        
        title_text = self.font.render("NPC Configuration", True, self.colors['text'])
        self.screen.blit(title_text, (dialog_x + 10, dialog_y + 10))
        
        spawn = self.selected_npc_spawn
        info_y = dialog_y + 50
        
        info_texts = [
            f"Position: ({spawn.x}, {spawn.y})",
            f"Type: {spawn.npc_type}",
            f"Name: {spawn.name}",
            f"Has Shop: {spawn.has_shop}",
            f"Importance: {spawn.importance}"
        ]
        
        for i, text in enumerate(info_texts):
            rendered = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(rendered, (dialog_x + 10, info_y + i * 25))
        
        close_text = self.small_font.render("Press ESC to close", True, self.colors['text'])
        self.screen.blit(close_text, (dialog_x + 10, dialog_y + dialog_height - 30))
    
    def run(self):
        """Main editor loop"""
        clock = pygame.time.Clock()
        
        print("🏗️  Building Template Editor Started!")
        print("Controls:")
        print("  1-5: Select tools (Wall, Door, Floor, NPC Spawn, Furniture)")
        print("  E: Erase tool")
        print("  Left Click: Place tool")
        print("  Right Click: Remove")
        print("  Ctrl+S: Save template")
        print("  Ctrl+N: New template")
        
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)
        
        pygame.quit()
        print("Building editor closed.")


def main():
    """Run the building editor"""
    try:
        editor = SimpleBuildingEditor(screen_width=1400, screen_height=900)
        editor.run()
    except Exception as e:
        print(f"Error running building editor: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()