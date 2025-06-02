#!/usr/bin/env python3
"""
Test script for Goose Recipe Manager
Tests the recipe system with different NPC types
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from recipe_manager import GooseRecipeManager, RecipeBasedGooseIntegration

def test_recipe_manager():
    """Test the recipe manager functionality"""
    print("🧪 Testing Goose Recipe Manager for AI NPCs")
    print("=" * 50)
    
    # Initialize recipe manager
    recipe_manager = GooseRecipeManager("recipes")
    
    # List available recipes
    recipes = recipe_manager.list_recipes()
    print(f"📋 Available recipes: {recipes}")
    
    # Test each recipe type
    test_cases = [
        ("Village Elder", "Hello, who are you?"),
        ("Master Merchant", "What do you sell?"),
        ("Guard Captain", "Is it safe here?"),
        ("Tavern Keeper", "Any news from travelers?"),
        ("Blacksmith", "Can you repair my sword?"),
        ("Healer", "I need healing potions"),
    ]
    
    for npc_name, message in test_cases:
        print(f"\n🤖 Testing {npc_name}:")
        print(f"   Player: \"{message}\"")
        
        # Test recipe-based integration
        integration = RecipeBasedGooseIntegration(npc_name, "recipes")
        
        if integration.recipe_name:
            print(f"   Recipe: {integration.recipe_name}")
            try:
                response = integration.send_message(message, "Player is testing the AI system")
                print(f"   NPC: \"{response}\"")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"   ⚠️  No recipe found for {npc_name}")
    
    print("\n✅ Recipe manager test completed!")

if __name__ == "__main__":
    test_recipe_manager()