"""
Settings system for the RPG
"""

import json
import os

class Settings:
    """Game settings manager"""
    
    def __init__(self):
        self.settings_file = "settings.json"
        
        # Default settings
        self.defaults = {
            "window_width": 1024,
            "window_height": 768,
            "fullscreen": False,
            "field_of_view": 1.0,  # Multiplier for how much of the world to show
            "camera_zoom": 1.0,    # Camera zoom level
            "master_volume": 0.7,
            "sfx_volume": 0.8,
            "music_volume": 0.6,
            "show_fps": False,
            "vsync": True
        }
        
        # Available resolutions
        self.available_resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
            (2560, 1440)
        ]
        
        # Load settings
        self.settings = self.defaults.copy()
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                print("Settings loaded successfully")
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = self.defaults.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print("Settings saved successfully")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key):
        """Get a setting value"""
        return self.settings.get(key, self.defaults.get(key))
    
    def set(self, key, value):
        """Set a setting value"""
        if key in self.defaults:
            self.settings[key] = value
            return True
        return False
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.defaults.copy()
        return self.save_settings()
    
    def get_current_resolution(self):
        """Get current resolution as tuple"""
        return (self.get("window_width"), self.get("window_height"))
    
    def set_resolution(self, width, height):
        """Set resolution"""
        self.set("window_width", width)
        self.set("window_height", height)
        return self.save_settings()
    
    def get_available_resolutions(self):
        """Get list of available resolutions"""
        return self.available_resolutions
    
    def apply_audio_settings(self, audio_manager):
        """Apply audio settings to the audio manager"""
        if audio_manager:
            audio_manager.set_master_volume(self.get("master_volume"))
            audio_manager.set_sfx_volume(self.get("sfx_volume"))
            audio_manager.set_music_volume(self.get("music_volume"))