#!/usr/bin/env python3
"""
Launch script for the Enhanced Building Template Editor
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the enhanced building editor
from enhanced_building_editor import main

if __name__ == "__main__":
    print("Starting Enhanced Building Template Editor...")
    print("Features:")
    print("- Template Browser (Ctrl+O)")
    print("- Template Properties (Ctrl+P)")
    print("- Window Walls (Tool 2)")
    print("- Advanced NPC Configuration")
    print("- NPC Removal")
    print("- Save/Load Templates")
    print()
    main()
EOF 2>&1
