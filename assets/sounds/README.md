# Goose RPG - Audio Assets

## Primary Audio Dependency: OpenGameArt.org Fantasy Sound Effects Library

### Resource Information
- **Source**: OpenGameArt.org Fantasy Sound Effects Library
- **URL**: https://lpc.opengameart.org/content/fantasy-sound-effects-library
- **License**: CC-BY 3.0 (Attribution Required)
- **Collection Size**: 45 comprehensive fantasy sound effects
- **Format**: Various (typically .wav, .ogg)

### Included Sound Categories
- **Ambiences**: Environmental background sounds
- **Dragon Growls**: Various dragon vocalizations
- **Footsteps**: Character movement sounds
- **Goblin Voices**: NPC creature sounds
- **Inventory Sounds**: Item interaction audio
- **Jingles**: UI and achievement sounds
- **Spell Effects**: Magic system audio
- **Trap Sounds**: Dungeon mechanism audio

### Attribution Requirements
This project uses sound effects from the Fantasy Sound Effects Library by OpenGameArt.org, licensed under CC-BY 3.0.

### Installation Instructions
1. Download the sound pack from: https://lpc.opengameart.org/content/fantasy-sound-effects-library
2. Extract files to appropriate subdirectories in this folder
3. Update the audio file paths in the game configuration

### Directory Structure
```
sounds/
├── ambient/          # Background environmental sounds
├── combat/           # Weapon and combat effects
├── creatures/        # Monster and NPC sounds
├── magic/            # Spell and magical effects
├── ui/               # Interface and menu sounds
└── environment/      # World interaction sounds
```

### Additional Resources
- **Backup Source**: Freesound.org (CC licensed sounds)
- **Music**: Kevin MacLeod's royalty-free library
- **Ambient**: Ambient-Mixer.com fantasy soundscapes

### Usage in Code
Audio files should be loaded through the game's audio manager system and referenced by category and name for easy organization.