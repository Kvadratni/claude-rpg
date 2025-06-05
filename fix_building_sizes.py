#!/usr/bin/env python3
"""
Script to automatically fix all building sizes in settlement patterns
Ensures all buildings have minimum 5x5 total size for 3x3 interior
"""

import re

def fix_building_sizes(file_path):
    """Fix all building sizes in the settlement patterns file"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match building definitions
    # Matches: {'x': 1, 'y': 1, 'width': 3, 'height': 3, 'type': 'house'}
    building_pattern = r"{'x': (\d+), 'y': (\d+), 'width': (\d+), 'height': (\d+), 'type': '([^']+)'}"
    
    def fix_building(match):
        x, y, width, height, building_type = match.groups()
        x, y, width, height = int(x), int(y), int(width), int(height)
        
        # Ensure minimum 5x5 size
        new_width = max(5, width)
        new_height = max(5, height)
        
        return f"{{'x': {x}, 'y': {y}, 'width': {new_width}, 'height': {new_height}, 'type': '{building_type}'}}"
    
    # Fix all building definitions
    fixed_content = re.sub(building_pattern, fix_building, content)
    
    # Also need to increase settlement sizes to accommodate larger buildings
    size_pattern = r"size = \((\d+), (\d+)\)"
    
    def fix_size(match):
        width, height = match.groups()
        width, height = int(width), int(height)
        
        # Increase size if too small for the buildings
        new_width = max(width, 20)  # Minimum 20x20 for proper settlements
        new_height = max(height, 20)
        
        return f"size = ({new_width}, {new_height})"
    
    fixed_content = re.sub(size_pattern, fix_size, fixed_content)
    
    # Fix the tile generation loops to match new sizes
    def fix_tile_loops(content):
        """Fix the tile generation loops to use the new sizes"""
        lines = content.split('\n')
        fixed_lines = []
        current_size = None
        
        for line in lines:
            # Track current size
            if 'size = (' in line:
                size_match = re.search(r'size = \((\d+), (\d+)\)', line)
                if size_match:
                    current_size = (int(size_match.group(1)), int(size_match.group(2)))
            
            # Fix hardcoded ranges in tile generation
            if current_size and 'for y in range(' in line and 'for x in range(' in line:
                # This is a nested loop line, skip it for now
                pass
            elif current_size and 'for y in range(' in line:
                # Fix y range
                line = re.sub(r'for y in range\(\d+\)', f'for y in range({current_size[1]})', line)
            elif current_size and 'for x in range(' in line:
                # Fix x range  
                line = re.sub(r'for x in range\(\d+\)', f'for x in range({current_size[0]})', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    fixed_content = fix_tile_loops(fixed_content)
    
    # Write back the fixed content
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"Fixed building sizes in {file_path}")

if __name__ == "__main__":
    fix_building_sizes("/Users/mnovich/Development/claude-rpg/src/world/settlement_patterns.py")
    print("All building sizes have been fixed to minimum 5x5!")