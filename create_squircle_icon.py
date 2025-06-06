#!/usr/bin/env python3
"""
Create a squircle (rounded square) version of the goose RPG icon
to match macOS app icon aesthetics.
"""

from PIL import Image, ImageDraw
import math

def create_squircle_mask(size, corner_radius_ratio=0.2):
    """
    Create a squircle mask using the superellipse formula.
    macOS uses approximately 20% corner radius ratio for app icons.
    """
    width, height = size
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    
    # Calculate corner radius based on the smaller dimension
    min_dimension = min(width, height)
    corner_radius = int(min_dimension * corner_radius_ratio)
    
    # Create rounded rectangle (approximation of squircle)
    # For a true squircle, we'd use the superellipse formula, but PIL's rounded rectangle
    # is close enough and more efficient
    draw.rounded_rectangle(
        [(0, 0), (width-1, height-1)],
        radius=corner_radius,
        fill=255
    )
    
    return mask

def create_squircle_icon(input_path, output_path):
    """
    Convert the existing icon to a squircle shape.
    """
    # Load the original icon
    original = Image.open(input_path)
    
    # Ensure it's in RGBA mode
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Get dimensions
    width, height = original.size
    print(f"Original icon size: {width}x{height}")
    
    # Create squircle mask
    mask = create_squircle_mask((width, height))
    
    # Create a new image with transparent background
    result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    
    # Apply the original image with the squircle mask
    result.paste(original, (0, 0))
    result.putalpha(mask)
    
    # Save the result
    result.save(output_path, 'PNG')
    print(f"✅ Squircle icon saved to: {output_path}")
    
    return result

def main():
    input_path = "assets/images/goose_rpg_icon_bg.png"
    output_path = "assets/images/goose_rpg_icon_bg_squircle.png"
    
    try:
        # Create the squircle version
        squircle_icon = create_squircle_icon(input_path, output_path)
        
        # Also create a backup of the original
        backup_path = "assets/images/goose_rpg_icon_bg_original_backup.png"
        original = Image.open(input_path)
        original.save(backup_path)
        print(f"📦 Original backed up to: {backup_path}")
        
        # Replace the original with the squircle version
        squircle_icon.save(input_path)
        print(f"🔄 Replaced original with squircle version")
        
        print("\n✅ Squircle icon creation complete!")
        print("The game will now use the squircle icon that matches macOS aesthetics.")
        
    except Exception as e:
        print(f"❌ Error creating squircle icon: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()