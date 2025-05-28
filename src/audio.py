"""
Audio system for Claude RPG
Manages loading and playing of sound effects and music
"""

import pygame
import os
import random
from pathlib import Path

class AudioManager:
    """Manages all audio playback for the game"""
    
    def __init__(self, sounds_dir="assets/sounds", enabled=True):
        """Initialize the audio manager"""
        self.enabled = enabled
        self.sounds_dir = Path(sounds_dir)
        self.sounds = {}
        self.volume_master = 1.0
        self.volume_sfx = 0.7
        self.volume_ui = 0.6
        self.volume_ambient = 0.4
        self.volume_music = 0.15  # Reduced from 0.3 to 0.15 (15% volume)
        
        # Music-related attributes
        self.current_music = None
        self.music_paused = False
        self.combat_music_active = False
        self.previous_music = None  # Store music to return to after combat
        
        if self.enabled:
            try:
                # Initialize pygame mixer
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                self.load_sounds()
                self.load_music()
                print("Audio system initialized successfully")
            except pygame.error as e:
                print(f"Failed to initialize audio: {e}")
                self.enabled = False
        else:
            print("Audio system disabled")
    
    def load_sounds(self):
        """Load all audio files into memory"""
        if not self.enabled:
            return
            
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
                'button_click': ['button_click.ogg'],
                'item_drop': ['item_drop.ogg']
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
                                'goblin_voice_4.wav', 'goblin_voice_5.wav'],
                'orc_growl': ['dragon_growl_1.wav', 'dragon_growl_2.wav'],  # Use dragon sounds for orc boss
                'orc_attack': ['dragon_growl_1.wav'],  # Deeper growl for attacks
                'orc_hurt': ['dragon_growl_2.wav']     # Different growl for taking damage
            },
            'ambient': {
                'cave_ambience': ['cave_ambience.wav'],
                'metal_pot': ['metal_pot_1.ogg', 'metal_pot_2.ogg', 'metal_pot_3.ogg']
            }
        }
        
        # Load sounds from each category
        sounds_loaded = 0
        for category, sound_groups in sound_categories.items():
            self.sounds[category] = {}
            category_path = self.sounds_dir / category
            
            if not category_path.exists():
                print(f"Warning: Sound category directory not found: {category_path}")
                continue
            
            for sound_name, filenames in sound_groups.items():
                loaded_sounds = []
                for filename in filenames:
                    file_path = category_path / filename
                    if file_path.exists():
                        try:
                            sound = pygame.mixer.Sound(str(file_path))
                            loaded_sounds.append(sound)
                            sounds_loaded += 1
                        except pygame.error as e:
                            print(f"Could not load {file_path}: {e}")
                    else:
                        print(f"Sound file not found: {file_path}")
                
                if loaded_sounds:
                    self.sounds[category][sound_name] = loaded_sounds
        
        print(f"Loaded {sounds_loaded} sound effects across {len(self.sounds)} categories")
    
    def load_music(self):
        """Load background music files"""
        if not self.enabled:
            return
            
        self.music_files = {}
        music_files = {
            'menu': 'menu_music.mp3',
            'game': 'game_music.mp3',
            'combat': 'combat_music.mp3'  # Added combat music
        }
        
        for music_name, filename in music_files.items():
            file_path = self.sounds_dir / filename
            if file_path.exists():
                self.music_files[music_name] = str(file_path)
                print(f"Loaded music: {music_name} -> {filename}")
            else:
                print(f"Music file not found: {file_path}")
        
        print(f"Loaded {len(self.music_files)} music files")
    
    def play_sound(self, category, sound_name, volume_override=None):
        """Play a sound effect"""
        if not self.enabled:
            return False
            
        if category in self.sounds and sound_name in self.sounds[category]:
            sounds = self.sounds[category][sound_name]
            if sounds:
                # Randomly select from available variations
                sound = random.choice(sounds)
                
                # Calculate volume based on category
                volume = self.volume_master
                if category == 'ui':
                    volume *= self.volume_ui
                elif category == 'ambient':
                    volume *= self.volume_ambient
                else:
                    volume *= self.volume_sfx
                
                # Apply volume override if provided
                if volume_override is not None:
                    volume = volume_override * self.volume_master
                
                sound.set_volume(volume)
                sound.play()
                return True
        return False
    
    def play_footstep(self, surface_type="dirt"):
        """Play appropriate footstep sound based on surface type"""
        footstep_map = {
            "dirt": "footstep_dirt",
            "water": "footstep_water", 
            "stone": "footstep_stone",
            "grass": "footstep_dirt",  # Use dirt sounds for grass
            "wall": "footstep_stone"   # Use stone sounds for walls
        }
        
        sound_name = footstep_map.get(surface_type, "footstep_dirt")
        return self.play_sound("environment", sound_name)
    
    def play_ui_sound(self, action):
        """Play UI-related sounds"""
        ui_sounds = {
            "select": "menu_select",
            "click": "button_click", 
            "coin": "coin_pickup",
            "inventory_open": "inventory_open",
            "inventory_close": "inventory_open",  # Same sound for close
            "achievement": "achievement",
            "victory": "victory",
            "defeat": "defeat",
            "item_drop": "item_drop"
        }
        
        if action in ui_sounds:
            return self.play_sound("ui", ui_sounds[action])
        return False
    
    def play_combat_sound(self, action):
        """Play combat-related sounds"""
        combat_sounds = {
            "draw_weapon": "weapon_draw",
            "sword_hit": "blade_slice",
            "axe_hit": "axe_chop",
            "weapon_hit": "blade_slice"  # Generic weapon hit
        }
        
        if action in combat_sounds:
            return self.play_sound("combat", combat_sounds[action])
        return False
    
    def play_magic_sound(self, action):
        """Play magic-related sounds"""
        magic_sounds = {
            "cast_spell": "spell_cast",
            "open_book": "spellbook_open",
            "close_book": "spellbook_close",
            "turn_page": "page_turn"
        }
        
        if action in magic_sounds:
            return self.play_sound("magic", magic_sounds[action])
        return False
    
    def play_creature_sound(self, creature_type, action="voice"):
        """Play creature-related sounds"""
        if creature_type == "dragon":
            return self.play_sound("creatures", "dragon_growl")
        elif creature_type == "goblin":
            return self.play_sound("creatures", "goblin_voice")
        elif creature_type == "orc" or creature_type == "orc_boss":
            if action == "attack":
                return self.play_sound("creatures", "orc_attack")
            elif action == "hurt":
                return self.play_sound("creatures", "orc_hurt")
            else:  # detection/voice
                return self.play_sound("creatures", "orc_growl")
        return False
    
    def play_environment_sound(self, action):
        """Play environment-related sounds"""
        env_sounds = {
            "door_open": "door_open",
            "door_close": "door_close",
            "trap": "trap_trigger"
        }
        
        if action in env_sounds:
            return self.play_sound("environment", env_sounds[action])
        return False
    
    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.volume_master = max(0.0, min(1.0, volume))
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.volume_sfx = max(0.0, min(1.0, volume))
    
    def set_ui_volume(self, volume):
        """Set UI sound volume (0.0 to 1.0)"""
        self.volume_ui = max(0.0, min(1.0, volume))
    
    def set_ambient_volume(self, volume):
        """Set ambient sound volume (0.0 to 1.0)"""
        self.volume_ambient = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.volume_music = max(0.0, min(1.0, volume))
        if self.enabled and pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume_music * self.volume_master)
    
    def play_music(self, music_name, loop=True, fade_in_ms=1000):
        """Play background music"""
        if not self.enabled or not hasattr(self, 'music_files'):
            return False
            
        if music_name in self.music_files:
            try:
                # Stop current music if playing
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.fadeout(500)  # Fade out over 500ms
                
                # Load and play new music
                pygame.mixer.music.load(self.music_files[music_name])
                pygame.mixer.music.set_volume(self.volume_music * self.volume_master)
                
                if fade_in_ms > 0:
                    pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_in_ms)
                else:
                    pygame.mixer.music.play(-1 if loop else 0)
                
                self.current_music = music_name
                self.music_paused = False
                print(f"Playing music: {music_name}")
                return True
            except pygame.error as e:
                print(f"Failed to play music {music_name}: {e}")
        else:
            print(f"Music not found: {music_name}")
        return False
    
    def stop_music(self, fade_out_ms=1000):
        """Stop background music"""
        if not self.enabled:
            return
            
        if pygame.mixer.music.get_busy():
            if fade_out_ms > 0:
                pygame.mixer.music.fadeout(fade_out_ms)
            else:
                pygame.mixer.music.stop()
        
        self.current_music = None
        self.music_paused = False
    
    def pause_music(self):
        """Pause background music"""
        if not self.enabled:
            return
            
        if pygame.mixer.music.get_busy() and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True
    
    def resume_music(self):
        """Resume paused background music"""
        if not self.enabled:
            return
            
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
    
    def is_music_playing(self):
        """Check if music is currently playing"""
        if not self.enabled:
            return False
        return pygame.mixer.music.get_busy() and not self.music_paused
    
    def get_current_music(self):
        """Get the name of currently playing music"""
        return self.current_music if self.is_music_playing() else None
    
    def toggle_audio(self):
        """Toggle audio on/off"""
        self.enabled = not self.enabled
        if not self.enabled:
            pygame.mixer.stop()
        return self.enabled
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds and music"""
        if self.enabled:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
            self.current_music = None
            self.music_paused = False
    
    def start_combat_music(self):
        """Start combat music, storing current music to return to later"""
        if not self.enabled or self.combat_music_active:
            return False
        
        # Store the current music to return to after combat
        if self.current_music and self.current_music != 'combat':
            self.previous_music = self.current_music
        
        # Start combat music
        if self.play_music('combat', loop=True, fade_in_ms=500):
            self.combat_music_active = True
            print("Combat music started")
            return True
        return False
    
    def end_combat_music(self):
        """End combat music and return to previous music"""
        if not self.enabled or not self.combat_music_active:
            return False
        
        self.combat_music_active = False
        
        # Return to previous music or default to game music
        music_to_play = self.previous_music if self.previous_music else 'game'
        
        if self.play_music(music_to_play, loop=True, fade_in_ms=1000):
            print(f"Combat ended, returning to {music_to_play} music")
            self.previous_music = None
            return True
        return False
    
    def is_combat_music_active(self):
        """Check if combat music is currently active"""
        return self.combat_music_active