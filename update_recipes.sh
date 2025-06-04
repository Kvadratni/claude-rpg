#!/bin/bash

# Script to update all recipe files from stdio-based MCP to HTTP-based MCP

RECIPES_DIR="/Users/mnovich/Development/claude-rpg-goose-npcs/recipes"

echo "🔄 Updating recipe files to use HTTP-based MCP server..."

# Find all YAML files in recipes directory
for recipe_file in "$RECIPES_DIR"/*.yaml; do
    if [[ -f "$recipe_file" ]]; then
        filename=$(basename "$recipe_file")
        echo "  📝 Updating $filename..."
        
        # Create backup
        cp "$recipe_file" "$recipe_file.backup"
        
        # Update the extensions section to use HTTP-based MCP
        python3 << EOF
import yaml
import sys

recipe_file = "$recipe_file"

try:
    with open(recipe_file, 'r') as f:
        data = yaml.safe_load(f)
    
    # Update extensions to use HTTP-based MCP
    if 'extensions' in data:
        for ext in data['extensions']:
            if ext.get('name') == 'rpg-game-server' or 'rpg' in ext.get('name', '').lower():
                # Convert to HTTP-based MCP
                ext['type'] = 'remote'
                ext['display_name'] = 'RPG Game Actions'
                ext['url'] = 'http://localhost:39301/model_context_protocol/2024-11-05/sse'
                ext['timeout'] = 30
                # Remove old stdio fields
                ext.pop('cmd', None)
                ext.pop('args', None)
                ext.pop('bundled', None)
                break
    
    # Write updated file
    with open(recipe_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"    ✅ Updated {recipe_file}")

except Exception as e:
    print(f"    ❌ Error updating {recipe_file}: {e}")
    # Restore backup on error
    import shutil
    shutil.copy(f"{recipe_file}.backup", recipe_file)

EOF
    fi
done

echo "🎉 Recipe update complete!"
echo ""
echo "📋 Updated recipes now use:"
echo "   Type: remote"
echo "   URL: http://localhost:39301/model_context_protocol/2024-11-05/sse"
echo "   Timeout: 30 seconds"
echo ""
echo "🚀 To use updated recipes:"
echo "   1. Start the game: cd /Users/mnovich/Development/claude-rpg && uv run goose-rpg"
echo "   2. The HTTP MCP server will start automatically"
echo "   3. Use any recipe file with Goose CLI"