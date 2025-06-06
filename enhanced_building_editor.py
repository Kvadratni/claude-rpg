"""
Enhanced Building Template Editor - Advanced UI-based editor for creating building templates
with comprehensive features including template browser, NPC configuration, and window support.
"""

import pygame
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class EditorTool(Enum):
    """Available tools in the building editor"""
    WALL = "wall"
    WINDOW = "window"  # New window tool
    DOOR = "door"
    FLOOR = "floor"
    NPC_SPAWN = "npc_spawn"
    FURNITURE = "furniture"
    ERASE = "erase"
    SELECT = "select"


class TileType(Enum):
    """Tile types for building templates"""
    EMPTY = 0
    WALL = 1
    DOOR = 2
    FLOOR = 3
    FURNITURE = 4
    NPC_SPAWN = 5
    WINDOW = 6  # New window type


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
        self.npc_spawns = []  # List of NPCSpawnPoint objects
        self.furniture_positions = []  # List of (x, y, furniture_type) tuples
        self.description = ""
        self.building_type = "generic"  # house, shop, inn, etc.
        
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BuildingTemplate':
        """Create template from dictionary"""
        template = cls(data['name'], data['width'], data['height'])
        template.description = data.get('description', '')
        template.building_type = data.get('building_type', 'generic')
        
        # Load tiles
        for y, row in enumerate(data['tiles']):
            for x, tile_value in enumerate(row):
                template.tiles[y][x] = TileType(tile_value)
        
        # Load NPC spawns
        for spawn_data in data.get('npc_spawns', []):
            spawn = NPCSpawnPoint(
                spawn_data['x'], 
                spawn_data['y'], 
                spawn_data.get('npc_type', 'generic'),
                spawn_data.get('name', '')
            )
            spawn.has_shop = spawn_data.get('has_shop', False)
            spawn.dialog = spawn_data.get('dialog', [])
            spawn.importance = spawn_data.get('importance', 'medium')
            template.npc_spawns.append(spawn)
        
        template.furniture_positions = data.get('furniture_positions', [])
        return template


class EnhancedBuildingEditor:
    """Main building template editor UI"""
    
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
        self.grid_offset_x = 200  # Space for toolbar
        self.grid_offset_y = 100  # Space for top menu
        
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
            'window': (135, 206, 235),  # Sky blue for windows
            'door': (101, 67, 33),
            'floor': (205, 133, 63),
            'npc_spawn': (255, 0, 0),
            'furniture': (160, 82, 45),
            'empty': (20, 20, 20)
        }
        
        # UI state
        self.selected_npc_spawn = None
        self.show_npc_dialog = False
        self.show_template_browser = False  # New template browser state
        self.selected_template_in_browser = None
        self.template_browser_scroll = 0
        self.npc_dialog_input = ""
        
        # Create templates directory
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load existing templates
        self.template_list = self.load_template_list()
        
        # Create default template
        self.create_new_template("New Building", 15, 15)
    
    def create_new_template(self, name: str, width: int, height: int):
        """Create a new building template"""
        self.current_template = BuildingTemplate(name, width, height)
        
        # Add basic walls around the perimeter
        for x in range(width):
            self.current_template.set_tile(x, 0, TileType.WALL)  # Top wall
            self.current_template.set_tile(x, height-1, TileType.WALL)  # Bottom wall
        for y in range(height):
            self.current_template.set_tile(0, y, TileType.WALL)  # Left wall
            self.current_template.set_tile(width-1, y, TileType.WALL)  # Right wall
        
        # Fill interior with floor
        for y in range(1, height-1):
            for x in range(1, width-1):
                self.current_template.set_tile(x, y, TileType.FLOOR)
        
        # Add a door in the front wall
        door_x = width // 2
        self.current_template.set_tile(door_x, height-1, TileType.DOOR)
    
    def load_template_list(self) -> List[str]:
        """Load list of available templates"""
        templates = []
        if os.path.exists(self.templates_dir):
            for filename in os.listdir(self.templates_dir):
                if filename.endswith('.json'):
                    templates.append(filename[:-5])  # Remove .json extension
        return templates
    
    def save_template(self, filename: str):
        """Save current template to file"""
        if self.current_template:
            filepath = os.path.join(self.templates_dir, f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(self.current_template.to_dict(), f, indent=2)
            
            # Update template list
            if filename not in self.template_list:
                self.template_list.append(filename)
            
            print(f"Template saved: {filepath}")
    
    def load_template(self, filename: str):
        """Load template from file"""
        filepath = os.path.join(self.templates_dir, f"{filename}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.current_template = BuildingTemplate.from_dict(data)
            print(f"Template loaded: {filepath}")
    
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
                if pygame.mouse.get_pressed()[0]:  # Left mouse held
                    self.handle_mouse_drag(event)
    
    def handle_keydown(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_s and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Ctrl+S: Save template
            if self.current_template:
                self.save_template(self.current_template.name)
        
        elif event.key == pygame.K_n and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Ctrl+N: New template
            self.create_new_template("New Building", 15, 15)
        
        elif event.key == pygame.K_o and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Ctrl+O: Open template browser
            self.show_template_browser = True
            self.template_list = self.load_template_list()  # Refresh list
        
        elif event.key == pygame.K_1:
            self.current_tool = EditorTool.WALL
        elif event.key == pygame.K_2:
            self.current_tool = EditorTool.WINDOW  # New window tool
        elif event.key == pygame.K_3:
            self.current_tool = EditorTool.DOOR
        elif event.key == pygame.K_4:
            self.current_tool = EditorTool.FLOOR
        elif event.key == pygame.K_5:
            self.current_tool = EditorTool.NPC_SPAWN
        elif event.key == pygame.K_6:
            self.current_tool = EditorTool.FURNITURE
        elif event.key == pygame.K_e:
            self.current_tool = EditorTool.ERASE
        elif event.key == pygame.K_ESCAPE:
            self.show_npc_dialog = False
            self.show_template_browser = False  # Close template browser
            self.selected_npc_spawn = None
    
    def handle_mouse_click(self, event):
        """Handle mouse clicks"""
        mouse_x, mouse_y = event.pos
        
        # Handle template browser clicks first
        if self.show_template_browser:
            self.handle_template_browser_click(mouse_x, mouse_y, event.button)
            return
        
        # Check if click is in grid area
        if self.is_in_grid_area(mouse_x, mouse_y):
            grid_x, grid_y = self.screen_to_grid(mouse_x, mouse_y)
            self.handle_grid_click(grid_x, grid_y, event.button)
        
        # Check toolbar clicks
        elif self.is_in_toolbar_area(mouse_x, mouse_y):
            self.handle_toolbar_click(mouse_x, mouse_y)
    
    def handle_mouse_drag(self, event):
        """Handle mouse dragging for painting"""
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
                # Check if there's already an NPC spawn here
                existing_spawn = self.current_template.get_npc_spawn_at(grid_x, grid_y)
                if existing_spawn:
                    self.selected_npc_spawn = existing_spawn
                    self.show_npc_dialog = True
                else:
                    # Add new NPC spawn
                    spawn = self.current_template.add_npc_spawn(grid_x, grid_y)
                    self.selected_npc_spawn = spawn
                    self.show_npc_dialog = True
            else:
                self.apply_tool(grid_x, grid_y)
        
        elif button == 3:  # Right click
            # Remove/erase
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
        elif self.current_tool == EditorTool.WINDOW:
            self.current_template.set_tile(grid_x, grid_y, TileType.WINDOW)
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
        # Tool buttons (vertical layout)
        tool_y_start = 120
        tool_height = 40
        tool_spacing = 50
        
        tools = [
            EditorTool.WALL,
            EditorTool.WINDOW,  # New window tool
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
    
    def handle_template_browser_click(self, mouse_x: int, mouse_y: int, button: int):
        """Handle clicks in the template browser"""
        browser_width = 600
        browser_height = 500
        browser_x = (self.screen_width - browser_width) // 2
        browser_y = (self.screen_height - browser_height) // 2
        
        # Close button
        close_x = browser_x + browser_width - 40
        close_y = browser_y + 10
        if close_x <= mouse_x <= close_x + 30 and close_y <= mouse_y <= close_y + 30:
            self.show_template_browser = False
            return
        
        # Template list area
        list_x = browser_x + 20
        list_y = browser_y + 60
        list_width = browser_width - 40
        list_height = 300
        
        if list_x <= mouse_x <= list_x + list_width and list_y <= mouse_y <= list_y + list_height:
            # Calculate which template was clicked
            item_height = 40
            clicked_index = (mouse_y - list_y) // item_height
            
            if 0 <= clicked_index < len(self.template_list):
                template_name = self.template_list[clicked_index]
                
                if button == 1:  # Left click - select
                    self.selected_template_in_browser = template_name
                elif button == 3:  # Right click - load immediately
                    self.load_template(template_name)
                    self.show_template_browser = False
        
        # Load button
        load_button_x = browser_x + 20
        load_button_y = browser_y + browser_height - 80
        load_button_width = 100
        load_button_height = 30
        
        if (load_button_x <= mouse_x <= load_button_x + load_button_width and 
            load_button_y <= mouse_y <= load_button_y + load_button_height and
            self.selected_template_in_browser):
            self.load_template(self.selected_template_in_browser)
            self.show_template_browser = False
        
        # Delete button
        delete_button_x = browser_x + 140
        delete_button_y = browser_y + browser_height - 80
        delete_button_width = 100
        delete_button_height = 30
        
        if (delete_button_x <= mouse_x <= delete_button_x + delete_button_width and 
            delete_button_y <= mouse_y <= delete_button_y + delete_button_height and
            self.selected_template_in_browser):
            self.delete_template(self.selected_template_in_browser)
            self.template_list = self.load_template_list()  # Refresh list
            self.selected_template_in_browser = None
        
        # Refresh button
        refresh_button_x = browser_x + 260
        refresh_button_y = browser_y + browser_height - 80
        refresh_button_width = 100
        refresh_button_height = 30
        
        if (refresh_button_x <= mouse_x <= refresh_button_x + refresh_button_width and 
            refresh_button_y <= mouse_y <= refresh_button_y + refresh_button_height):
            self.template_list = self.load_template_list()  # Refresh list
            self.selected_template_in_browser = None
    
    def delete_template(self, template_name: str):
        """Delete a template file"""
        filepath = os.path.join(self.templates_dir, f"{template_name}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Template deleted: {template_name}")
                return True
            except Exception as e:
                print(f"Error deleting template: {e}")
        return False
    
    def is_in_grid_area(self, x: int, y: int) -> bool:
        """Check if coordinates are in the grid area"""
        return x >= self.grid_offset_x and y >= self.grid_offset_y
    
    def is_in_toolbar_area(self, x: int, y: int) -> bool:
        """Check if coordinates are in the toolbar area"""
        return x < self.grid_offset_x
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates"""
        grid_x = (screen_x - self.grid_offset_x) // self.grid_size
        grid_y = (screen_y - self.grid_offset_y) // self.grid_size
        return grid_x, grid_y
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen coordinates"""
        screen_x = self.grid_offset_x + grid_x * self.grid_size
        screen_y = self.grid_offset_y + grid_y * self.grid_size
        return screen_x, screen_y
    
    def draw(self):
        """Draw the editor interface"""
        self.screen.fill(self.colors['background'])
        
        # Draw toolbar
        self.draw_toolbar()
        
        # Draw grid and template
        if self.current_template:
            self.draw_grid()
            self.draw_template()
        
        # Draw top menu
        self.draw_top_menu()
        
        # Draw NPC dialog if open
        if self.show_npc_dialog and self.selected_npc_spawn:
            self.draw_npc_dialog()
        
        # Draw template browser if open
        if self.show_template_browser:
            self.draw_template_browser()
        
        pygame.display.flip()
    
    def draw_toolbar(self):
        """Draw the left toolbar"""
        # Toolbar background
        toolbar_rect = pygame.Rect(0, 0, self.grid_offset_x, self.screen_height)
        pygame.draw.rect(self.screen, self.colors['toolbar'], toolbar_rect)
        
        # Title
        title_text = self.font.render("Building Editor", True, self.colors['text'])
        self.screen.blit(title_text, (10, 10))
        
        # Tool buttons
        tool_y_start = 120
        tool_height = 40
        tool_spacing = 50
        
        tools = [
            (EditorTool.WALL, "Wall (1)"),
            (EditorTool.WINDOW, "Window (2)"),  # New window tool
            (EditorTool.DOOR, "Door (3)"),
            (EditorTool.FLOOR, "Floor (4)"),
            (EditorTool.NPC_SPAWN, "NPC Spawn (5)"),
            (EditorTool.FURNITURE, "Furniture (6)"),
            (EditorTool.ERASE, "Erase (E)")
        ]
        
        for i, (tool, label) in enumerate(tools):
            button_y = tool_y_start + i * tool_spacing
            button_rect = pygame.Rect(10, button_y, 170, tool_height)
            
            # Button color based on selection
            if tool == self.current_tool:
                color = self.colors['button_active']
            else:
                color = self.colors['button']
            
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.colors['text'], button_rect, 2)
            
            # Button text
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
            "Ctrl+O: Browse Templates",  # New instruction
            "1-6: Select Tool",
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
        
        # Template name (editable)
        if self.current_template:
            name_text = self.font.render(f"Template: {self.current_template.name}", 
                                       True, self.colors['text'])
            self.screen.blit(name_text, (self.grid_offset_x + 10, 10))
            
            # Building type
            type_text = self.small_font.render(f"Type: {self.current_template.building_type}", 
                                             True, self.colors['text'])
            self.screen.blit(type_text, (self.grid_offset_x + 10, 35))
            
            # Description
            desc_text = self.small_font.render(f"Description: {self.current_template.description}", 
                                             True, self.colors['text'])
            self.screen.blit(desc_text, (self.grid_offset_x + 10, 55))
    
    def draw_grid(self):
        """Draw the grid lines"""
        if not self.current_template:
            return
        
        # Grid lines
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
                
                # Choose color based on tile type
                if tile_type == TileType.WALL:
                    color = self.colors['wall']
                elif tile_type == TileType.WINDOW:
                    color = self.colors['window']
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
                
                # Draw NPC spawn indicators
                if tile_type == TileType.NPC_SPAWN:
                    spawn = self.current_template.get_npc_spawn_at(x, y)
                    if spawn:
                        # Draw NPC icon/text
                        npc_text = self.small_font.render("NPC", True, (255, 255, 255))
                        text_rect = npc_text.get_rect(center=tile_rect.center)
                        self.screen.blit(npc_text, text_rect)
                elif tile_type == TileType.WINDOW:
                    # Draw window cross pattern
                    center_x = screen_x + self.grid_size // 2
                    center_y = screen_y + self.grid_size // 2
                    pygame.draw.line(self.screen, (255, 255, 255), 
                                   (screen_x + 4, center_y), (screen_x + self.grid_size - 4, center_y), 2)
                    pygame.draw.line(self.screen, (255, 255, 255), 
                                   (center_x, screen_y + 4), (center_x, screen_y + self.grid_size - 4), 2)
    
    def draw_npc_dialog(self):
        """Draw the NPC configuration dialog"""
        if not self.selected_npc_spawn:
            return
        
        # Dialog background
        dialog_width = 400
        dialog_height = 300
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(self.screen, self.colors['toolbar'], dialog_rect)
        pygame.draw.rect(self.screen, self.colors['text'], dialog_rect, 2)
        
        # Dialog title
        title_text = self.font.render("NPC Configuration", True, self.colors['text'])
        self.screen.blit(title_text, (dialog_x + 10, dialog_y + 10))
        
        # NPC info
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
        
        # Close button
        close_text = self.small_font.render("Press ESC to close", True, self.colors['text'])
        self.screen.blit(close_text, (dialog_x + 10, dialog_y + dialog_height - 30))
    
    def draw_template_browser(self):
        """Draw the template browser dialog"""
        browser_width = 600
        browser_height = 500
        browser_x = (self.screen_width - browser_width) // 2
        browser_y = (self.screen_height - browser_height) // 2
        
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Browser background
        browser_rect = pygame.Rect(browser_x, browser_y, browser_width, browser_height)
        pygame.draw.rect(self.screen, self.colors['toolbar'], browser_rect)
        pygame.draw.rect(self.screen, self.colors['text'], browser_rect, 3)
        
        # Title
        title_text = self.font.render("Template Browser", True, self.colors['text'])
        self.screen.blit(title_text, (browser_x + 20, browser_y + 15))
        
        # Close button
        close_x = browser_x + browser_width - 40
        close_y = browser_y + 10
        close_rect = pygame.Rect(close_x, close_y, 30, 30)
        pygame.draw.rect(self.screen, (180, 60, 60), close_rect)
        pygame.draw.rect(self.screen, self.colors['text'], close_rect, 2)
        close_text = self.font.render("X", True, self.colors['text'])
        close_text_rect = close_text.get_rect(center=close_rect.center)
        self.screen.blit(close_text, close_text_rect)
        
        # Instructions
        instructions = [
            "Left click: Select template",
            "Right click: Load template immediately", 
            "Load button: Load selected template",
            "Delete button: Remove selected template"
        ]
        
        inst_y = browser_y + 50
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, self.colors['text'])
            self.screen.blit(inst_text, (browser_x + 20, inst_y))
            inst_y += 18
        
        # Template list
        list_y = browser_y + 140
        item_height = 40
        
        for i, template_name in enumerate(self.template_list):
            item_y = list_y + i * item_height
            item_rect = pygame.Rect(browser_x + 20, item_y, browser_width - 40, item_height - 2)
            
            # Highlight selected template
            if template_name == self.selected_template_in_browser:
                pygame.draw.rect(self.screen, self.colors['button_active'], item_rect)
            else:
                pygame.draw.rect(self.screen, self.colors['button'], item_rect)
            
            pygame.draw.rect(self.screen, self.colors['text'], item_rect, 1)
            
            # Template info
            try:
                # Load template info for preview
                filepath = os.path.join(self.templates_dir, f"{template_name}.json")
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Template name
                name_text = self.font.render(template_name, True, self.colors['text'])
                self.screen.blit(name_text, (item_rect.x + 10, item_rect.y + 5))
                
                # Template details
                size_text = f"{data.get('width', '?')}x{data.get('height', '?')}"
                type_text = data.get('building_type', 'unknown')
                npc_count = len(data.get('npc_spawns', []))
                
                details = f"{size_text} | {type_text} | {npc_count} NPCs"
                details_text = self.small_font.render(details, True, self.colors['text'])
                self.screen.blit(details_text, (item_rect.x + 10, item_rect.y + 22))
                
            except Exception as e:
                # Fallback if template can't be loaded
                name_text = self.font.render(f"{template_name} (error)", True, (255, 100, 100))
                self.screen.blit(name_text, (item_rect.x + 10, item_rect.y + 10))
        
        # Action buttons
        button_y = browser_y + browser_height - 80
        
        # Load button
        load_button = pygame.Rect(browser_x + 20, button_y, 100, 30)
        load_color = self.colors['button_active'] if self.selected_template_in_browser else self.colors['button']
        pygame.draw.rect(self.screen, load_color, load_button)
        pygame.draw.rect(self.screen, self.colors['text'], load_button, 2)
        load_text = self.font.render("Load", True, self.colors['text'])
        load_text_rect = load_text.get_rect(center=load_button.center)
        self.screen.blit(load_text, load_text_rect)
        
        # Delete button
        delete_button = pygame.Rect(browser_x + 140, button_y, 100, 30)
        delete_color = (180, 60, 60) if self.selected_template_in_browser else self.colors['button']
        pygame.draw.rect(self.screen, delete_color, delete_button)
        pygame.draw.rect(self.screen, self.colors['text'], delete_button, 2)
        delete_text = self.font.render("Delete", True, self.colors['text'])
        delete_text_rect = delete_text.get_rect(center=delete_button.center)
        self.screen.blit(delete_text, delete_text_rect)
        
        # Refresh button
        refresh_button = pygame.Rect(browser_x + 260, button_y, 100, 30)
        pygame.draw.rect(self.screen, self.colors['button'], refresh_button)
        pygame.draw.rect(self.screen, self.colors['text'], refresh_button, 2)
        refresh_text = self.font.render("Refresh", True, self.colors['text'])
        refresh_text_rect = refresh_text.get_rect(center=refresh_button.center)
        self.screen.blit(refresh_text, refresh_text_rect)
        
        # Status text
        status_y = browser_y + browser_height - 40
        if self.selected_template_in_browser:
            status_text = f"Selected: {self.selected_template_in_browser}"
        else:
            status_text = f"Found {len(self.template_list)} templates"
        
        status_rendered = self.small_font.render(status_text, True, self.colors['text'])
        self.screen.blit(status_rendered, (browser_x + 20, status_y))
    
    def run(self):
        """Main editor loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.draw()
            clock.tick(60)
        
        pygame.quit()


def main():
    """Run the enhanced building editor"""
    editor = EnhancedBuildingEditor()
    editor.run()


if __name__ == "__main__":
    main()