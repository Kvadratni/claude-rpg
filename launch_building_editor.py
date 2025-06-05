#!/usr/bin/env python3
"""
Building Template Editor Launcher
Launch the building template editor for creating and editing building templates.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Import directly without relative imports
    import sys
    sys.path.append('src')
    from ui.building_editor import BuildingEditor
    
    def main():
        print("🏗️  Building Template Editor")
        print("=" * 40)
        print("Controls:")
        print("  1-5: Select tools (Wall, Door, Floor, NPC Spawn, Furniture)")
        print("  E: Erase tool")
        print("  Left Click: Place selected tool")
        print("  Right Click: Remove/erase")
        print("  Ctrl+S: Save template")
        print("  Ctrl+N: New template")
        print("  ESC: Close dialogs")
        print("=" * 40)
        
        # Create and run the editor
        editor = BuildingEditor(screen_width=1400, screen_height=900)
        editor.run()
        
        print("Building editor closed.")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"Error importing building editor: {e}")
    print("Make sure pygame is installed: pip install pygame")
    sys.exit(1)