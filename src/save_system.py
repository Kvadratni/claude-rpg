"""
Save system for the RPG
"""

import os
import json
import datetime

class SaveSystem:
    """Game save system"""
    
    def __init__(self):
        """Initialize the save system"""
        self.save_dir = "saves"
        
        # Create save directory if it doesn't exist
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_game(self, save_name, game_data):
        """Save game data to file"""
        try:
            # Add metadata
            game_data["metadata"] = {
                "save_name": save_name,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0"
            }
            
            # Save to file
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            with open(save_path, "w") as f:
                json.dump(game_data, f, indent=2)
            
            print(f"Game saved to {save_path}")
            return True
        
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_name):
        """Load game data from file"""
        try:
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            if not os.path.exists(save_path):
                print(f"Save file not found: {save_path}")
                return None
            
            with open(save_path, "r") as f:
                game_data = json.load(f)
            
            print(f"Game loaded from {save_path}")
            return game_data
        
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def list_saves(self):
        """List all save files"""
        try:
            if not os.path.exists(self.save_dir):
                return []
            
            saves = []
            for filename in os.listdir(self.save_dir):
                if filename.endswith(".json"):
                    save_name = filename[:-5]  # Remove .json extension
                    saves.append(save_name)
            
            return saves
        
        except Exception as e:
            print(f"Error listing saves: {e}")
            return []
    
    def delete_save(self, save_name):
        """Delete a save file"""
        try:
            save_path = os.path.join(self.save_dir, f"{save_name}.json")
            
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"Save file deleted: {save_path}")
                return True
            else:
                print(f"Save file not found: {save_path}")
                return False
        
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False