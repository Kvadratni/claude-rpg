# Goose RPG - Audio Asset Manifest

## Overview
This manifest documents all audio assets organized and ready for use in the Goose RPG project.

**Total Audio Files**: 96 sound effects
**Primary Sources**: 
- OpenGameArt.org Fantasy Sound Effects Library (CC-BY 3.0)
- Kenney RPG Sound Effects Pack (CC0)

## Audio Categories

### 🏰 Ambient Sounds (4 files)
- `cave_ambience.wav` - Deep cave atmosphere (14.7MB)
- `metal_pot_1.ogg` - Metallic ambient sound
- `metal_pot_2.ogg` - Metallic ambient sound  
- `metal_pot_3.ogg` - Metallic ambient sound

### ⚔️ Combat Sounds (6 files)
- `axe_chop.ogg` - Axe striking sound
- `blade_slice_1.ogg` - Sword slicing sound
- `blade_slice_2.ogg` - Alternative sword slice
- `weapon_draw_1.ogg` - Drawing weapon from sheath
- `weapon_draw_2.ogg` - Alternative weapon draw
- `weapon_draw_3.ogg` - Third weapon draw variation

### 🐉 Creature Sounds (7 files)
- `dragon_growl_1.wav` - Deep dragon roar
- `dragon_growl_2.wav` - Alternative dragon roar
- `goblin_voice_1.wav` - Goblin vocalization
- `goblin_voice_2.wav` - Short goblin sound
- `goblin_voice_3.wav` - Goblin chatter
- `goblin_voice_4.wav` - Goblin grunt
- `goblin_voice_5.wav` - Goblin battle cry

### 🌍 Environment Sounds (39 files)
**Footsteps - Dirt (10 files)**:
- `Footstep_Dirt_00.wav` through `Footstep_Dirt_09.wav`

**Footsteps - Water (8 files)**:
- `Footstep_Water_00.wav` through `Footstep_Water_07.wav`

**Footsteps - Stone (10 files)**:
- `footstep_stone_1.ogg` through `footstep_stone_10.ogg`

**Doors (6 files)**:
- `door_open_1.ogg`, `door_open_2.ogg`
- `door_close_1.ogg` through `door_close_4.ogg`

**Environmental Effects (5 files)**:
- `trap_trigger_1.wav`, `trap_trigger_2.wav`, `trap_trigger_3.wav`
- `wood_creak_1.ogg`, `wood_creak_2.ogg`, `wood_creak_3.ogg`

### ✨ Magic Sounds (13 files)
**Spell Casting (5 files)**:
- `spell_cast_1.wav` through `spell_cast_5.wav`

**Spellbook Interactions (8 files)**:
- `spellbook_open.ogg`, `spellbook_close.ogg`
- `page_turn_1.ogg`, `page_turn_2.ogg`, `page_turn_3.ogg`
- `book_place_1.ogg`, `book_place_2.ogg`, `book_place_3.ogg`

### 🎮 UI Sounds (27 files)
**Menu & Interface (3 files)**:
- `menu_select.wav` - Menu selection sound
- `button_click.ogg` - UI button click
- `chest_latch.ogg` - Chest opening sound

**Inventory & Items (14 files)**:
- `inventory_open_1.wav`, `inventory_open_2.wav`
- `coin_pickup_1.wav` through `coin_pickup_5.wav`
- `coin_handle_1.ogg`, `coin_handle_2.ogg`
- `item_drop.ogg`
- `leather_item_1.ogg`, `leather_item_2.ogg`

**Equipment (8 files)**:
- `armor_equip_1.ogg`, `armor_equip_2.ogg`
- `belt_equip_1.ogg`, `belt_equip_2.ogg`
- `cloth_equip_1.ogg` through `cloth_equip_4.ogg`

**Game Events (3 files)**:
- `achievement.wav` - Achievement unlocked (1MB)
- `victory.wav` - Victory fanfare (2.9MB)
- `defeat.wav` - Game over sound (1.7MB)

## File Format Information
- **WAV Files**: High-quality uncompressed audio (from Fantasy Sound Effects Library)
- **OGG Files**: Compressed audio format, smaller file sizes (from Kenney RPG Pack)
- **Total Size**: Approximately 30MB

## Usage in Game Code
Recommended loading pattern:
```python
# Example audio loading structure
AUDIO_PATHS = {
    'combat': {
        'weapon_draw': ['combat/weapon_draw_1.ogg', 'combat/weapon_draw_2.ogg'],
        'blade_slice': ['combat/blade_slice_1.ogg', 'combat/blade_slice_2.ogg'],
        'axe_chop': 'combat/axe_chop.ogg'
    },
    'ui': {
        'menu_select': 'ui/menu_select.wav',
        'coin_pickup': ['ui/coin_pickup_1.wav', 'ui/coin_pickup_2.wav', ...],
        'achievement': 'ui/achievement.wav'
    },
    'environment': {
        'footstep_dirt': ['environment/Footstep_Dirt_00.wav', ...],
        'footstep_water': ['environment/Footstep_Water_00.wav', ...],
        'door_open': ['environment/door_open_1.ogg', 'environment/door_open_2.ogg']
    }
}
```

## Attribution Requirements
**Fantasy Sound Effects Library**: 
- License: CC-BY 3.0
- Attribution: "Sound effects by Little Robot Sound Factory (OpenGameArt.org)"

**Kenney RPG Sound Effects**:
- License: CC0 (Public Domain)
- Attribution: Optional but appreciated

## Integration Status
✅ **Downloaded and Organized**: All 96 audio files properly categorized
✅ **Documentation**: Complete manifest and category guides
✅ **Ready for Integration**: Organized structure ready for game audio system
🔄 **Next Step**: Integrate with game's audio loading system