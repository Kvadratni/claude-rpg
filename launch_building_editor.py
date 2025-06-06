#!/usr/bin/env python3
"""
Building Template Editor Launcher
Launch the enhanced building template editor for creating and editing building templates.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    # Import the enhanced building editor
    from enhanced_building_editor import EnhancedBuildingEditor
    
    def main():
        print("🏗️  Enhanced Building Template Editor")
        print("=" * 50)
        print("🎯 New Features:")
        print("  📋 Template Browser (Ctrl+O)")
        print("  🏷️  Template Properties (Ctrl+P)")
        print("  🪟 Window Walls (Tool 2)")
        print("  👥 Advanced NPC Configuration")
        print("  🗑️  Easy NPC Removal")
        print()
        print("🎮 Controls:")
        print("  1-6: Select tools (Wall, Window, Door, Floor, NPC, Furniture)")
        print("  E: Erase tool")
        print("  Left Click: Place/Edit")
        print("  Right Click: Remove")
        print("  Drag: Paint mode")
        print("  Ctrl+N: New template")
        print("  Ctrl+O: Open template browser")
        print("  Ctrl+S: Save template")
        print("  Ctrl+P: Template properties")
        print("  ESC: Close dialogs")
        print("=" * 50)
        
        # Create and run the enhanced editor
        editor = EnhancedBuildingEditor(screen_width=1400, screen_height=900)
        editor.run()
        
        print("Enhanced building editor closed.")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Error importing enhanced building editor: {e}")
    print()
    print("🔧 Troubleshooting:")
    print("1. Make sure pygame is installed: pip install pygame")
    print("2. Try running directly: python enhanced_building_editor.py")
    print("3. Check that enhanced_building_editor.py exists in this directory")
    print()
    
    # Fallback to check if the basic building editor exists
    try:
        from src.ui.building_editor import BuildingEditor
        print("📋 Found basic building editor, launching that instead...")
        editor = BuildingEditor(screen_width=1400, screen_height=900)
        editor.run()
    except ImportError:
        print("❌ No building editor found. Please check your installation.")
        sys.exit(1)