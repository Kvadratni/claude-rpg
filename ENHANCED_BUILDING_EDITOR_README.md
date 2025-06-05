# Enhanced Building Template Editor

A comprehensive building template editor for creating and managing building templates for settlement generation in the RPG game.

## Features

### ✨ **New Enhanced Features**

1. **📋 Template Browser (Inspector)**
   - Browse all existing building templates
   - Load templates with a single click
   - Delete unwanted templates
   - Visual template selection interface
   - Keyboard shortcut: `Ctrl+O`

2. **🏷️ Template Naming & Properties**
   - Edit template names and descriptions
   - Set building types and properties
   - Configure settlement size requirements
   - Biome compatibility settings
   - Keyboard shortcut: `Ctrl+P`

3. **🪟 Window Walls**
   - New window tile type for realistic buildings
   - Visual window indicators with cross pattern
   - Windows provide light and aesthetic appeal
   - Tool shortcut: `2` or click Window tool

4. **👥 Advanced NPC Configuration**
   - Comprehensive NPC setup dialog
   - Configure NPC names, types, and dialog
   - Set shop status and importance levels
   - Movement patterns and patrol points
   - Multiple dialog lines support

5. **🗑️ NPC Management**
   - Easy NPC removal with dedicated button
   - Right-click to quickly remove NPCs
   - Visual confirmation before deletion
   - Undo-friendly operations

### 🎨 **Core Editor Features**

- **Grid-based Building Design**: Visual tile-by-tile building creation
- **Multiple Tile Types**: Walls, windows, doors, floors, furniture, NPC spawns
- **Real-time Preview**: See your building as you create it
- **Save/Load System**: Persistent template storage
- **Intuitive Interface**: Easy-to-use tools and shortcuts

## How to Use

### 🚀 **Getting Started**

1. **Launch the Editor**:
   ```bash
   python enhanced_building_editor.py
   # or
   python launch_enhanced_building_editor.py
   ```

2. **Create a New Template**:
   - Press `Ctrl+N` or click "New" button
   - Enter template name and size (5-50 tiles)
   - Click "Create" to start designing

3. **Load Existing Template**:
   - Press `Ctrl+O` or click "Open" button
   - Select template from the browser
   - Click "Load" to open it

### 🛠️ **Building Tools**

| Tool | Shortcut | Description |
|------|----------|-------------|
| Wall | `1` | Create solid walls |
| Window | `2` | Add windows to walls |
| Door | `3` | Place doors for entry/exit |
| Floor | `4` | Interior flooring |
| NPC Spawn | `5` | Add NPC spawn points |
| Furniture | `6` | Place furniture items |
| Erase | `E` | Remove any tile |

### 🎮 **Controls**

| Action | Control | Description |
|--------|---------|-------------|
| Place Tile | Left Click | Place selected tool |
| Remove Tile | Right Click | Remove tile at cursor |
| Paint Mode | Left Drag | Paint multiple tiles |
| Edit NPC | Left Click on NPC | Open NPC configuration |
| New Template | `Ctrl+N` | Create new template |
| Open Template | `Ctrl+O` | Browse templates |
| Save Template | `Ctrl+S` | Save current work |
| Properties | `Ctrl+P` | Edit template properties |
| Close Dialog | `ESC` | Close any open dialog |

### 👥 **NPC Configuration**

When you place an NPC spawn point or click on an existing one:

1. **Basic Info**:
   - **Name**: Display name for the NPC
   - **Type**: NPC category (villager, merchant, guard, etc.)

2. **Dialog System**:
   - Enter multiple dialog lines (one per line)
   - NPCs will randomly select from available dialog
   - Support for conversation trees

3. **Properties**:
   - **Has Shop**: Whether NPC runs a shop
   - **Importance**: Low/Medium/High (affects spawn priority)
   - **Movement**: Stationary/Patrol/Random patterns

4. **Actions**:
   - **Save**: Apply changes to NPC
   - **Remove**: Delete the NPC spawn point

### 🏗️ **Template Properties**

Access via `Ctrl+P` or Properties button:

- **Name**: Template identifier
- **Description**: Detailed description
- **Building Type**: house, shop, inn, blacksmith, etc.
- **Settlement Requirements**: Minimum settlement size
- **Biome Compatibility**: Which biomes support this building
- **Importance**: Building priority in settlements

## File Format

Templates are saved as JSON files in the `building_templates/` directory:

```json
{
  "name": "village_shop",
  "width": 9,
  "height": 7,
  "building_type": "shop",
  "tiles": [[1,1,1,...], ...],
  "npc_spawns": [
    {
      "x": 4,
      "y": 2,
      "npc_type": "merchant",
      "name": "Shopkeeper",
      "has_shop": true,
      "dialog": ["Welcome!", "What can I get you?"],
      "importance": "high"
    }
  ],
  "furniture_positions": [[2,3,"counter"], ...],
  "description": "A general store with merchant",
  "min_settlement_size": "small",
  "biome_compatibility": ["all"],
  "importance": "high"
}
```

## Tile Types

| Type | Value | Color | Description |
|------|-------|-------|-------------|
| Empty | 0 | Dark Gray | Unused space |
| Wall | 1 | Brown | Solid walls |
| Door | 2 | Dark Brown | Entry/exit points |
| Floor | 3 | Tan | Interior flooring |
| Furniture | 4 | Wood Brown | Tables, chairs, etc. |
| NPC Spawn | 5 | Red | NPC spawn points |
| Window | 6 | Sky Blue | Windows in walls |

## Tips for Good Building Design

### 🏠 **Residential Buildings**
- Use windows for natural light
- Include furniture for realism
- Place NPCs in logical locations
- Consider room layouts

### 🏪 **Commercial Buildings**
- Add counters and shop furniture
- Place merchant NPCs strategically
- Include storage areas
- Design customer flow paths

### 🏛️ **Public Buildings**
- Larger spaces for gatherings
- Multiple NPCs for services
- Clear entry/exit points
- Appropriate furniture placement

### 🎨 **Aesthetic Considerations**
- Balance walls and windows
- Use furniture to define spaces
- Consider building proportions
- Plan NPC placement carefully

## Integration with Settlement System

Templates created in this editor are automatically available to:

- **Settlement Generator**: Procedural village creation
- **Building Template Manager**: Template organization
- **World Generation**: Biome-appropriate building placement
- **NPC System**: Automatic NPC spawning and configuration

## Troubleshooting

### Common Issues

1. **Template Won't Save**:
   - Check file permissions in `building_templates/` directory
   - Ensure template name is valid (no special characters)

2. **NPC Dialog Not Working**:
   - Make sure dialog lines are separated by newlines
   - Check that NPC name and type are set

3. **Template Browser Empty**:
   - Verify `building_templates/` directory exists
   - Check that template files have `.json` extension

4. **Editor Crashes**:
   - Ensure Pygame is installed: `pip install pygame`
   - Check Python version compatibility (3.7+)

### Performance Tips

- Keep template sizes reasonable (under 30x30)
- Limit NPC spawns per building (1-3 recommended)
- Use descriptive names for easy identification
- Regularly save your work with `Ctrl+S`

## Advanced Features

### Template Validation
- Automatic door placement validation
- NPC spawn point accessibility checking
- Building structural integrity verification

### Batch Operations
- Import/export multiple templates
- Template conversion utilities
- Bulk property updates

### Integration Tools
- Direct testing in game world
- Settlement preview generation
- Template performance metrics

---

**Happy Building!** 🏗️

Create amazing settlements with detailed, functional buildings that bring your RPG world to life!
EOF 2>&1
