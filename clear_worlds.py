#!/usr/bin/env python3
"""
Clear existing world data to test new settlement patterns
"""

import os
import shutil

def clear_world_data():
    """Clear existing world data to force regeneration with new patterns"""
    
    worlds_dir = "saves/worlds"
    
    if not os.path.exists(worlds_dir):
        print("No worlds directory found")
        return
    
    print("🗑️  Available worlds to clear:")
    worlds = [d for d in os.listdir(worlds_dir) if os.path.isdir(os.path.join(worlds_dir, d)) and d.startswith('procedural_')]
    
    for i, world in enumerate(worlds):
        chunk_count = len([f for f in os.listdir(os.path.join(worlds_dir, world)) if f.endswith('.json')])
        print(f"  {i+1}. {world} ({chunk_count} chunks)")
    
    print(f"  {len(worlds)+1}. Clear ALL procedural worlds")
    print(f"  0. Cancel")
    
    try:
        choice = int(input("\nSelect world to clear (number): "))
        
        if choice == 0:
            print("Cancelled")
            return
        elif choice == len(worlds) + 1:
            # Clear all procedural worlds
            for world in worlds:
                world_path = os.path.join(worlds_dir, world)
                shutil.rmtree(world_path)
                print(f"✅ Cleared {world}")
            print(f"🎉 Cleared {len(worlds)} procedural worlds")
        elif 1 <= choice <= len(worlds):
            # Clear specific world
            world_to_clear = worlds[choice - 1]
            world_path = os.path.join(worlds_dir, world_to_clear)
            shutil.rmtree(world_path)
            print(f"✅ Cleared {world_to_clear}")
        else:
            print("Invalid choice")
            return
        
        print("\n🎮 Next steps:")
        print("1. Start Goose RPG")
        print("2. Create a new procedural world")
        print("3. Look for settlements with new pattern layouts!")
        print("4. Use F6 to test chunk regeneration")
        
    except ValueError:
        print("Invalid input")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Clear World Data for Pattern Testing ===")
    clear_world_data()