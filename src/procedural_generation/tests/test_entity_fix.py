#!/usr/bin/env python3
"""
Quick test to verify the entity spawner fix
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_entity_imports():
    """Test that entity classes can be imported correctly"""
    print("Testing entity imports...")
    
    try:
        # Test direct import
        from src.entities import Entity, NPC, Enemy, Item, Chest
        print("✅ Direct entity imports successful")
        
        # Test entity creation
        entity = Entity(10, 10, "Test Entity")
        print(f"✅ Entity created: {entity.name} at ({entity.x}, {entity.y})")
        
        # Test update method signature
        if hasattr(entity, 'update'):
            import inspect
            sig = inspect.signature(entity.update)
            params = list(sig.parameters.keys())
            print(f"✅ Entity.update() parameters: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ Entity import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_spawner_imports():
    """Test that EntitySpawner can import entity classes"""
    print("\nTesting EntitySpawner imports...")
    
    try:
        from src.procedural_generation.src.entity_spawner import EntitySpawner
        
        spawner = EntitySpawner(50, 50, 12345)
        print("✅ EntitySpawner created successfully")
        
        # Test dialog generation
        dialog = spawner.get_npc_dialog("Master Merchant")
        print(f"✅ NPC dialog generated: {len(dialog)} lines")
        
        return True
        
    except Exception as e:
        print(f"❌ EntitySpawner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the tests"""
    print("Entity Compatibility Test")
    print("=" * 40)
    
    test1 = test_entity_imports()
    test2 = test_entity_spawner_imports()
    
    if test1 and test2:
        print("\n🎉 All tests passed!")
        print("The entity spawner fix should resolve the update() error.")
        return True
    else:
        print("\n❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)