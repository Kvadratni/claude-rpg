# Claude RPG

An isometric RPG game built with Python and Pygame, featuring mouse-driven gameplay, combat systems, and exploration mechanics.

## Features

- **Isometric Graphics**: Beautiful diamond-tile based isometric rendering
- **Mouse-Driven Controls**: Pure mouse navigation and interaction system
- **Combat System**: Click-to-attack combat with balanced enemy AI
- **RPG Mechanics**: Leveling, experience, equipment, and inventory systems
- **Rich World**: Large 120x120 tile world with varied terrain and structures
- **Loot System**: 35+ items including weapons, armor, and consumables
- **Asset Integration**: PNG sprite support with procedural fallbacks

## Controls

- **Left Click**: Move, interact with NPCs, attack enemies, pick up items
- **Right Click**: Inspect entities and tiles for information
- **Spacebar**: Attack nearby enemies
- **I**: Toggle inventory
- **Cmd+Shift+F**: Toggle fullscreen (Mac)
- **ESC**: Pause menu

## Installation

### Prerequisites
- Python 3.8+
- uv (Python package manager)

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd claude-rpg
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the game:
   ```bash
   uv run claude-rpg
   ```

## Game Mechanics

### Character System
- **Health**: Player health with regeneration mechanics
- **Mana**: Magical energy system
- **Experience**: Gain XP by defeating enemies
- **Leveling**: Automatic stat increases on level up
- **Equipment**: Weapons and armor with stat bonuses

### Combat
- **Click-to-Attack**: Click on enemies to engage in combat
- **Attack Range**: Melee combat with 1.2 tile range
- **Damage Calculation**: Base damage + weapon bonuses - enemy defense
- **Enemy AI**: Enemies detect, chase, and attack the player

### World
- **Large Map**: 120x120 tile procedurally generated world
- **Terrain Types**: Grass, dirt, stone paths, water, walls
- **Structures**: Buildings with doors and varied layouts
- **Objects**: Trees and rocks that block movement
- **NPCs**: Shopkeepers and quest givers

### Items
- **Weapons**: Swords, axes, maces with damage bonuses (10-25)
- **Armor**: Various armor types with defense bonuses (5-15)
- **Consumables**: Health potions (50 HP) and mana potions (30 MP)
- **Inventory**: 20-slot inventory system with drag-and-drop

## Technical Details

### Architecture
- **Modular Design**: Separate modules for game logic, rendering, entities
- **Asset System**: Flexible asset loading with fallback generation
- **Save System**: JSON-based save/load functionality
- **Settings**: Configurable game settings with persistence

### Performance
- **Optimized Rendering**: Large render distance with efficient culling
- **Collision Detection**: Precise tile and object collision system
- **Entity Management**: Efficient spawning and updating of game objects

### Graphics
- **Sprite Sizes**: 
  - Player: 48px
  - NPCs: 48px
  - Enemies: 48px (regular), 60px (bosses)
  - Items: 36px
  - Objects: 48px
- **Tile System**: 64x32 isometric tiles
- **Asset Support**: PNG images with automatic scaling

### Audio Assets
- **Primary Source**: OpenGameArt.org Fantasy Sound Effects Library
- **License**: CC-BY 3.0 (Attribution Required)
- **Collection**: 45 comprehensive fantasy sound effects
- **Categories**: Combat, magic spells, creature sounds, ambient effects, UI sounds
- **Installation**: Download from [Fantasy Sound Effects Library](https://lpc.opengameart.org/content/fantasy-sound-effects-library)
- **Directory Structure**: Organized by sound type in `assets/sounds/`

## Development

### Project Structure
```
claude-rpg/
├── src/
│   ├── __init__.py
│   ├── main.py          # Entry point
│   ├── game.py          # Main game controller
│   ├── player.py        # Player character logic
│   ├── level.py         # Level generation and management
│   ├── entity.py        # NPCs, enemies, items, objects
│   ├── isometric.py     # Isometric rendering utilities
│   ├── inventory.py     # Inventory system
│   ├── assets.py        # Asset loading and management
│   ├── save_system.py   # Save/load functionality
│   ├── settings.py      # Game settings
│   ├── game_log.py      # In-game messaging system
│   └── menu.py          # Menu systems
├── assets/
│   ├── images/          # Game sprites and tiles
│   └── sounds/          # Audio assets and sound effects
├── pyproject.toml       # Project configuration
├── README.md
└── .gitignore
```

### Key Classes
- **Game**: Main game controller and state manager
- **Player**: Player character with movement, combat, and inventory
- **Level**: World generation, tile management, and entity spawning
- **Entity**: Base class for NPCs, enemies, items, and objects
- **IsometricRenderer**: Coordinate conversion and rendering utilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Acknowledgments

- Built with Python and Pygame
- Isometric graphics inspired by classic RPG games
- Asset system designed for easy sprite replacement
- Developed with AI assistance for rapid prototyping

## Version History

### v1.0.0 - Initial Release
- Complete isometric RPG with mouse controls
- Full combat and inventory systems
- Large procedurally generated world
- 35+ items and balanced gameplay
- Asset integration with fallback generation
- Save/load functionality
- Configurable settings system