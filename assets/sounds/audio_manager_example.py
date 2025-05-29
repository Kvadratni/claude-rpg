"""
Goose RPG - Audio System Integration Example

This module provides an example of how to integrate the organized sound effects
into your game's audio system using pygame.mixer.
"""

import pygame
import os
import random
from pathlib import Path

class AudioManager:
    """Manages loading and playing of game audio assets."""
    
    def __init__(self, sounds_dir="assets/sounds"):
        """Initialize the audio manager."""
        pygame.mixer.init()
        self.sounds_dir = Path(sounds_dir)
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Load all audio files into memory."""
        # Define sound categories and their files
        sound_categories = {
            'combat': {
                'weapon_draw': ['weapon_draw_1.ogg', 'weapon_draw_2.ogg', 'weapon_draw_3.ogg'],
                'blade_slice': ['blade_slice_1.ogg', 'blade_slice_2.ogg'],
                'axe_chop': ['axe_chop.ogg']
            },
            'ui': {
                'menu_select': ['menu_select.wav'],
                'coin_pickup': ['coin_pickup_1.wav', 'coin_pickup_2.wav', 'coin_pickup_3.wav', 
                               'coin_pickup_4.wav', 'coin_pickup_5.wav'],
                'achievement': ['achievement.wav'],
                'victory': ['victory.wav'],
                'defeat': ['defeat.wav'],
                'inventory_open': ['inventory_open_1.wav', 'inventory_open_2.wav'],
                'button_click': ['button_click.ogg']
            },
            'environment': {
                'footstep_dirt': [f'Footstep_Dirt_0{i}.wav' for i in range(10)],
                'footstep_water': [f'Footstep_Water_0{i}.wav' for i in range(8)],
                'footstep_stone': [f'footstep_stone_{i}.ogg' for i in range(1, 11)],
                'door_open': ['door_open_1.ogg', 'door_open_2.ogg'],
                'door_close': ['door_close_1.ogg', 'door_close_2.ogg', 'door_close_3.ogg', 'door_close_4.ogg'],
                'trap_trigger': ['trap_trigger_1.wav', 'trap_trigger_2.wav', 'trap_trigger_3.wav']
            },
            'magic': {
                'spell_cast': ['spell_cast_1.wav', 'spell_cast_2.wav', 'spell_cast_3.wav', 
                              'spell_cast_4.wav', 'spell_cast_5.wav'],
                'spellbook_open': ['spellbook_open.ogg'],
                'spellbook_close': ['spellbook_close.ogg'],
                'page_turn': ['page_turn_1.ogg', 'page_turn_2.ogg', 'page_turn_3.ogg']
            },
            'creatures': {
                'dragon_growl': ['dragon_growl_1.wav', 'dragon_growl_2.wav'],
                'goblin_voice': ['goblin_voice_1.wav', 'goblin_voice_2.wav', 'goblin_voice_3.wav',
                                'goblin_voice_4.wav', 'goblin_voice_5.wav']
            },
            'ambient': {
                'cave_ambience': ['cave_ambience.wav'],
                'metal_pot': ['metal_pot_1.ogg', 'metal_pot_2.ogg', 'metal_pot_3.ogg']
            }
        }
        
        # Load sounds from each category
        for category, sound_groups in sound_categories.items():
            self.sounds[category] = {}
            category_path = self.sounds_dir / category
            
            for sound_name, filenames in sound_groups.items():
                loaded_sounds = []
                for filename in filenames:
                    file_path = category_path / filename
                    if file_path.exists():
                        try:
                            sound = pygame.mixer.Sound(str(file_path))
                            loaded_sounds.append(sound)
                        except pygame.error as e:
                            print(f"Could not load {file_path}: {e}")
                
                if loaded_sounds:
                    self.sounds[category][sound_name] = loaded_sounds
                    print(f"Loaded {len(loaded_sounds)} sounds for {category}/{sound_name}")
    
    def play_sound(self, category, sound_name, volume=1.0):
        """Play a sound effect."""
        if category in self.sounds and sound_name in self.sounds[category]:
            sounds = self.sounds[category][sound_name]
            if sounds:
                # Randomly select from available variations
                sound = random.choice(sounds)
                sound.set_volume(volume)
                sound.play()
                return True
        return False
    
    def play_footstep(self, surface_type="dirt", volume=0.5):
        """Play appropriate footstep sound based on surface type."""
        footstep_map = {
            "dirt": "footstep_dirt",
            "water": "footstep_water", 
            "stone": "footstep_stone"
        }
        
        sound_name = footstep_map.get(surface_type, "footstep_dirt")
        return self.play_sound("environment", sound_name, volume)
    
    def play_ui_sound(self, action, volume=0.7):
        """Play UI-related sounds."""
        ui_sounds = {
            "select": "menu_select",
            "click": "button_click",
            "coin": "coin_pickup",
            "inventory": "inventory_open",
            "achievement": "achievement",
            "victory": "victory",
            "defeat": "defeat"
        }
        
        if action in ui_sounds:
            return self.play_sound("ui", ui_sounds[action], volume)
        return False
    
    def play_combat_sound(self, action, volume=0.8):
        """Play combat-related sounds."""
        combat_sounds = {
            "draw_weapon": "weapon_draw",
            "sword_hit": "blade_slice",
            "axe_hit": "axe_chop"
        }
        
        if action in combat_sounds:
            return self.play_sound("combat", combat_sounds[action], volume)
        return False
    
    def play_magic_sound(self, action, volume=0.6):
        """Play magic-related sounds."""
        magic_sounds = {
            "cast_spell": "spell_cast",
            "open_book": "spellbook_open",
            "close_book": "spellbook_close",
            "turn_page": "page_turn"
        }
        
        if action in magic_sounds:
            return self.play_sound("magic", magic_sounds[action], volume)
        return False

# Example usage:
if __name__ == "__main__":
    # Initialize audio manager
    audio = AudioManager()
    
    # Example sound playback
    print("Playing menu select sound...")
    audio.play_ui_sound("select")
    
    print("Playing footstep on dirt...")
    audio.play_footstep("dirt")
    
    print("Playing spell cast...")
    audio.play_magic_sound("cast_spell")
    
    print("Playing coin pickup...")
    audio.play_ui_sound("coin")